#This file stores all of the classes used by "main.py" and some of the other
#files

#The main classes are Airplane, ControllerChannel, Cloud, Bush, Balloon,
#Button, CheckBox, TextBox, InputBox, ToolBox 


import random
import math
from vectors import *
from extraneous import *
from cmu_112_graphics_modified import *
from renderingFunctions import *
from bisect import bisect_left


#Creates the airplane class
class Airplane(object):
    #Initializes airplane variables
    def __init__(self, name, d1, d2, position):
        self.name = name
        self.parts = []
        self.partNames = []
        self.center = position
        self.d1 = d1
        self.d2 = d2
        self.velocity = 0
        self.propRotRate = 0
        self.justTouchedGround = False

    #Generates a list of all the 3D parts in the plane in their proper position
    def getPartsInPosition(self):
        partsInPosition = []
        for part in self.parts:
            length, width, height = (part["length"], part["width"], part["height"])
            name, color = (part["name"], part["color"])
            partCenter = self.getPartCenter(part)
            d1, d2 = self.d1, self.d2
            if "d1Rotation" in part:
                d1Rot = part["d1Rotation"]
                d2 = rotateVector(d2, d1, d1Rot)  
            if "d2Rotation" in part:
                d2Rot = part["d2Rotation"]
                d1 = rotateVector(d1, d2, d2Rot)
            #Uses my format for representing 3D shapes
            partsInPosition.append((name, partCenter, d1, d2, length, height, width, color))
        return partsInPosition

    #Calculates the position of the center of an object using the part data
    #and the orientation of the plane
    def getPartCenter(self, part):
        d1Offset = part["d1Offset"]
        d2Offset = part["d2Offset"]
        d3Offset = part["d3Offset"]
        d3 = crossProduct(self.d1, self.d2)
        partCenter = addVectorToPoint(self.center, self.d1, d1Offset)
        partCenter = addVectorToPoint(partCenter, self.d2, d2Offset)
        partCenter = addVectorToPoint(partCenter, d3, d3Offset)
        return partCenter

    #Adds a part to the plane
    def addPart(self, part):
        self.parts.append(part)
        self.partNames.append(part["name"])

    #Creates a hitbox for the plane
    def createHitbox(self, hitbox):
        self.hitbox = hitbox

    #Generates the corners of the hitbox using the orientation and position of the plane
    def getHitboxCorners(self, mode):
        hitbox = self.hitbox
        length, width, height = (hitbox["length"], hitbox["width"], hitbox["height"])
        hitboxCenter = self.getPartCenter(hitbox)
        return getVertices(mode, (hitboxCenter, self.d1, self.d2, length, height, width))


    ################
    #User Control
    ################
    def roll(self, amount):
        self.d2 = rotateVector(self.d2, self.d1, amount)

    def pitch(self, amount):
        d3 = crossProduct(self.d1, self.d2)
        self.d1 = rotateVector(self.d1, d3, amount)
        self.d2 = rotateVector(self.d2, d3, amount)
    
    def yaw(self, amount):
        self.d1 = rotateVector(self.d1, self.d2, amount)

    def moveForward(self, amount):
        self.center = addVectorToPoint(self.center, self.d1, amount)

    def rotatePropeller(self, amount):
        index = self.partNames.index("prop")
        self.propRotRate += amount * 75
        self.propRotRate *= .97
        self.parts[index]["d1Rotation"] = (self.parts[index]["d1Rotation"] + self.propRotRate) % 360

    #Performs the inputs given by the controller
    #Note that the odd coefficients out front of some of these equations just scale the 
    #user's input values to make the input boxes more user-friendly
    def performControllerInputs(self, mode):
        throttle = mode.app.channelAssignment["throttle"].getValue(mode.app)
        self.rotatePropeller(throttle / mode.framerate)

        self.velocity += .3 * mode.app.inputBoxVars["throttleStrength"] * throttle / mode.framerate

        prevD1 = self.d1
        #Performs the controller inputs
        controlAuthority = self.getControlAuthority(mode, throttle)
        pitch = mode.app.channelAssignment["pitch"].getValue(mode.app)
        self.pitch(1/10 * mode.app.inputBoxVars["pitchRate"] * controlAuthority * pitch / mode.framerate)
        yaw = mode.app.channelAssignment["yaw"].getValue(mode.app)
        self.yaw(-1/10 * mode.app.inputBoxVars["yawRate"] * controlAuthority * yaw / mode.framerate)
        roll = mode.app.channelAssignment["roll"].getValue(mode.app)
        self.roll(1/10* mode.app.inputBoxVars["rollRate"] * controlAuthority * roll / mode.framerate)
        
        #Decreases plane's as a function of how hard the plane is turning
        self.velocity -= 1/30 * mode.app.inputBoxVars["turningDrag"] * self.velocity * magnitude(crossProduct(prevD1, self.d1)) / mode.framerate

    #Determines how much control the user has of the plane at high speeds
    #this should be almost completely dependent on velocity, but at low speeds, 
    #the air moving over the wings due to the throttle value makes a difference
    def getControlAuthority(self, mode, throttle):
        return (self.velocity + .25 * throttle)
    

    ###############
    #Physics
    ###############

    def performPhysics(self, mode):
        #print(self.velocity)

        #CITATION: Relation between velocity and drag from
        #https://wright.nasa.gov/airplane/drageq.html#:~:text=The%20drag%20equation%20states%20that,the%20wing%20area%20(A).
        #Applies drag to the plane proportional to velocity squared
        if self.velocity > 0:
            self.velocity -= 1/10**4 * mode.app.inputBoxVars["drag"] * self.velocity ** 2 / mode.framerate
        else:
            self.velocity += 1/10**4 * mode.app.inputBoxVars["drag"] * self.velocity ** 2 / mode.framerate

        #Drop center of plane due to gravity. Only drops by 1/5 of gravity since this value represents
        #the terminal velocity of the plane while level, which should be quite low
        self.center = (self.center[0], self.center[1], self.center[2] - mode.gravity / mode.framerate / 5)

        lift = self.getLift(mode)
        self.center = addVectorToPoint(self.center, self.d2, lift / mode.framerate)
        self.moveForward(self.velocity / mode.framerate)

        cornersOnGround = self.getCornersOnGround(mode)
        #Checks if the plane is touching the ground
        if len(cornersOnGround) == 0:
            self.stall(mode)
            self.velocity += dotProduct(self.d1, (0, 0, -1)) * mode.gravity / mode.framerate
            self.justTouchedGround = False
        else:
            if not self.justTouchedGround:
                self.checkCrash(mode)
                self.justTouchedGround = True
            self.fixAirplanePosition(mode, cornersOnGround)
            verticalVelocity = self.velocity * dotProduct(self.d1, (0, 0, 1))
            #Quickly reduces the vertical velocity of the plane when it is on the ground
            self.velocity = (self.velocity ** 2 - (.5 * verticalVelocity) ** 2) ** .5

    #Checks if the plane is oriented incorrectly or landed at too high of a speed
    def checkCrash(self, mode):
        if dotProduct(self.d2, (0, 0, 1)) < .95 or self.velocity * dotProduct(self.d1, (0, 0, 1)) > 1:
            mode.crashed = True

    #CITATION: Relation between velocity and lift from 
    #https://www.grc.nasa.gov/www/k-12/airplane/lifteq.html
    #Calculates the list as a function of velocity squared
    def getLift(self, mode):
        return 1/(2*10**4) * mode.app.inputBoxVars["liftCoeff"] * self.velocity**2

    #Creates a list of all the corners of the hitbox that are below the ground
    def getCornersOnGround(self, mode):
        cornersOnGround = []
        corners = self.getHitboxCorners(mode)
        for corner in corners.values():
            if corner[2] <= 0:
                cornersOnGround.append(corner)
        return cornersOnGround

    #Rotates and/or lifts the plane until no vertices are in the ground
    def fixAirplanePosition(self, mode, cornersOnGround):
        while len(cornersOnGround) > 0:
            self.center = (self.center[0], self.center[1], self.center[2] + .005)
            if len(cornersOnGround) < 3:
                for corner in cornersOnGround:
                    self.fixAirplanePositionHelper(mode, corner)
            cornersOnGround = self.getCornersOnGround(mode)

    #Rotates the plane in a way that lifts up the corners below the ground
    #This creates the appearance that a corner of the plane has hit the ground and can no longer go lower 
    def fixAirplanePositionHelper(self, mode, corner):
        vectorToCenter = vectorSum(corner, 1, self.center, -1)
        unitVectorToCenter = makeUnitVector(vectorToCenter)
        mag = magnitude(vectorToCenter)
        rotationAxis = makeUnitVector(crossProduct(vectorToCenter, (0, 0, 1)))
        while addVectorToPoint(self.center, unitVectorToCenter, mag)[2] < 0:
            #Rotates the plane just slightly until the corner is no longer below the ground
            self.d1 = rotateVector(self.d1, rotationAxis, -.05)
            self.d2 = rotateVector(self.d2, rotationAxis, -.05)
            unitVectorToCenter = makeUnitVector(rotateVector(unitVectorToCenter, rotationAxis, -.05))
            
    #Forces the nose of the plane down as the velocity goes below the stall speed
    def stall(self, mode):
        maxRotationRate = 180
        stallVelocity = mode.app.inputBoxVars["stallSpeed"]

        rotationAxis = makeUnitVector(crossProduct(self.d1, (0, 0, 1)))
        rotationAmount = maxRotationRate * (1 - self.velocity / stallVelocity) / mode.framerate
        if rotationAmount > 0:
            self.d1 = rotateVector(self.d1, rotationAxis, rotationAmount)
            self.d2 = rotateVector(self.d2, rotationAxis, rotationAmount)

    def reset(self, mode):
        self.velocity, self.center = 0, (-15, 5, 0)
        self.propRotRate = 0
        self.d1, self.d2 = (1, 0, 0), (0, 0, 1)
        mode.prev = time.time()
        mode.crashed = False


    ############
    #Drawing
    ############

    #Draws all the parts that make up the plane
    def draw(self, mode, canvas):
        allFaces = {}
        renderedFaces = {}
        for part in self.getPartsInPosition():
            getFaces(mode, part, allFaces)
            renderFaces(mode, part, renderedFaces)
        
        drawShapes(mode, canvas, renderedFaces, allFaces, self.partNames)




class Quad(Airplane):
    def __init__(self, name, d1, d2, position):
        super().__init__(name, d1, d2, position)
        self.velocity = [0, 0, 0]
        self.center = (5, 0, 0)

    
    def rotatePropellers(self, amount):
        #self.propRotRate += amount * 100
        self.propRotRate = amount * 250
        for prop in ["prop1", "prop2", "prop3", "prop4"]:
            index = self.partNames.index(prop)
            if prop[-1] == "1" or prop[-1] == "4": sign = -1
            else: sign = 1
            self.parts[index]["d2Rotation"] = (self.parts[index]["d2Rotation"] + self.propRotRate * sign) % 360

    #Performs the inputs given by the controller
    #Note that the odd coefficients out front of some of these equations just scale the 
    #user's input values to make the input boxes more user-friendly
    def performControllerInputs(self, mode):

        idleThrottle = .05

        throttle = mode.app.channelAssignment["throttle"].getValue(mode.app)
        throttle = (idleThrottle + throttle * (1 - idleThrottle)) * mode.app.inputBoxVars["throttleStrength"] * 1.75
        self.rotatePropellers(throttle / mode.framerate)
        self.velocity = vectorSum(self.velocity, 1, self.d2, throttle/mode.framerate)

        #self.velocity += .3 * mode.app.inputBoxVars["throttleStrength"] * throttle / mode.framerate

        #prevD1 = self.d1
        #Performs the controller inputs
       # controlAuthority = self.getControlAuthority(mode, throttle)
        pitch = mode.app.channelAssignment["pitch"].getValue(mode.app)
        self.pitch(3 * mode.app.inputBoxVars["pitchRate"] * pitch / mode.framerate)
        yaw = mode.app.channelAssignment["yaw"].getValue(mode.app)
        self.yaw(-3 * mode.app.inputBoxVars["yawRate"] * yaw / mode.framerate)
        roll = mode.app.channelAssignment["roll"].getValue(mode.app)
        self.roll(3 * mode.app.inputBoxVars["rollRate"] * roll / mode.framerate)
        
    

    def performPhysics(self, mode):

        cornersOnGround = self.getCornersOnGround(mode)
        #Checks if the plane is touching the ground
        if len(cornersOnGround) == 0:
            drag = mode.app.inputBoxVars["drag"]/4000
            self.velocity[2] -= mode.gravity/mode.framerate
            self.center = addVectorToPoint(self.center, self.velocity, 1/mode.framerate)

            self.velocity = vectorSum(self.velocity, 1, makeUnitVector(self.velocity), -drag / mode.framerate * magnitude(self.velocity)**2)

        else:
            if not self.justTouchedGround:
                self.checkCrash(mode)
                self.justTouchedGround = True
            if len(cornersOnGround) < 3:
                self.velocity[2] -= magnitude(crossProduct(self.d2, (0, 0, -1))) * mode.gravity/mode.framerate
                self.center = addVectorToPoint(self.center, self.velocity, 1/mode.framerate)
            self.velocity[2] *= magnitude(crossProduct(self.d2, (0, 0, -1)))
            self.velocity[1] *= .8
            self.velocity[0] *= .8
            self.fixAirplanePosition(mode, cornersOnGround)
            self.center = addVectorToPoint(self.center, (0, 0, -1), .1/mode.framerate)


    #Checks if the plane is oriented incorrectly or landed at too high of a speed
    def checkCrash(self, mode):
        if dotProduct(self.d2, (0, 0, 1)) < .95 or magnitude(self.velocity) * dotProduct(self.d1, (0, 0, 1)) > 1:
            mode.crashed = True


    def reset(self, mode):
        self.velocity, self.center = [0, 0, 0], (5, 0, 0)
        self.propRotRate = 0
        self.d1, self.d2 = (1, 0, 0), (0, 0, 1)
        mode.prev = time.time()
        mode.crashed = False









#Creates the Cloud Class
class Cloud(object):
    #Initializes a random position for an instance of a cloud
    def __init__(self):
        minX, maxX = -10000, 10000
        minY, maxY = -10000, 10000
        minZ, maxZ = 500, 5000
        self.position = (random.randint(minX, maxX), random.randint(minY, maxY), random.randint(minZ, maxZ))
        self.cloudParts = []
        self.generateCloudParts()

    #Creates all the parts of a cloud
    def generateCloudParts(self):
        numOfParts = random.randint(3, 12)
        for i in range(numOfParts):
            self.generateCloudPart()

    #Creates a single part of the cloud
    def generateCloudPart(self):
        minR, maxR = 100, 250
        maxDist = 150
        partPosition = (random.randint(self.position[0] - maxDist, self.position[0] + maxDist),
                        random.randint(self.position[1] - maxDist, self.position[1] + maxDist), 
                        random.randint(self.position[2] - maxDist, self.position[2] + maxDist))
        partR = (random.randint(minR, maxR), random.randint(minR, maxR))
        self.cloudParts.append((partPosition, partR))


    #Draws a provided part of a cloud
    @staticmethod
    def drawCloudPart(part, mode, canvas, color):
        position, rx, ry = part[0], part[1][0], part[1][1]
        x, y = getXandY(mode, position)
        if x != None:
            dist = distance(position, mode.observer)
            scaledRX = rx / dist * mode.width
            scaledRY = ry / dist * mode.width
            canvas.create_oval(x - scaledRX, y - scaledRY, x + scaledRX, y + scaledRY, fill = color, width = 0)

    #Draws the instance of a cloud. Color depends on time of day
    def drawCloud(self, mode, canvas):
        if mode.app.inputBoxVars["isDaytime"]:
            color = "white"
        else:
            color = rgbString((50, 50, 90))

        for part in self.cloudParts:
            Cloud.drawCloudPart(part, mode, canvas, color)

    #Draws all clouds in a provided list of clouds
    @staticmethod
    def drawAllClouds(clouds, mode, canvas):
        for cloud in clouds:
            cloud.drawCloud(mode, canvas)
            



#Creates the bush class
class Bush(object):
    #initializes the position of the bush
    def __init__(self, mode):
        minX, maxX = -2000, 2000
        minY, maxY = -2000, 2000
        self.r = random.uniform(1, 3)
        self.position = None
        while self.position == None:
            pos = (random.randint(minX, maxX), random.randint(minY, maxY), self.r * .8)
            if distance(pos, (0, 0, 0)) > 50:
                self.position = pos
        Bush.observerPosCopy = mode.observer

    #Defines the "<" operation so the list can be sorted by distance to the observer
    def __lt__(self, other):
        if isinstance(other, float):
            return distance(Bush.observerPosCopy, self.position) < other
        return distance(Bush.observerPosCopy, self.position) < distance(Bush.observerPosCopy, other.position)
        
    #Draws the instance of a bush with radius scaled by the distance from the user
    def draw(self, mode, canvas):
        drawCircle(mode, canvas, self, (25, 100, 25), 0)

    #Draw all the bushes in a provided list of bushes
    @staticmethod
    def drawAll(bushes, mode, canvas, inFront):
        for bush in bushes:
            if not distance(bush.position, mode.observer) > mode.app.inputBoxVars["viewRange"]:
                isInFront = distance(mode.observer, bush.position) < distance(mode.observer, mode.app.airplane.center)
                if isInFront == inFront:
                    bush.draw(mode, canvas)

    #Draw all the shadows of the bushes in a provided list of bushes
    @staticmethod
    def drawAllShadows(bushes, mode, canvas):
        for bush in bushes:
            if not distance(bush.position, mode.observer) > mode.app.inputBoxVars["viewRange"]:
                drawShadow(mode, canvas, bush.r, bush.position)

    #Checks if the airplane is touching a bush
    @staticmethod
    def touchingABush(bushes, objectPos, mode):
        Bush.observerPosCopy = mode.observer
        for bush in bushes:
            if distance(bush.position, objectPos) < bush.r:
                mode.crashed = True


#Creates the balloon class
class Balloon(object):

    
    #Initializes the balloon position and color
    def __init__(self, mode):
        minX, maxX = -100, 100
        minY, maxY = -100, 100
        minZ, maxZ = 2, 20
        self.r = 1
        self.position = (random.randint(minX, maxX), random.randint(minY, maxY), random.randint(minZ, maxZ))
        self.color = [random.randint(50, 255) for i in range(3)]
        self.observerPosCopy = mode.observer
        Balloon.observerPosCopy = mode.observer

    #Defines the "<" operation so the list can be sorted by distance to the observer
    def __lt__(self, other):
        return distance(Balloon.observerPosCopy, self.position) < distance(Balloon.observerPosCopy, other.position)

    #Draws the instance of a balloon
    def draw(self, mode, canvas):
        drawCircle(mode, canvas, self, self.color)

    def drawString(self, mode, canvas):
        p1 = getXandY(mode, self.position)
        p2 = getXandY(mode, (self.position[0], self.position[1], 0))
        if p1[0] != None and p2[0] != None:
            canvas.create_line(p1, p2, width = 1)
        
    def drawStringShadow(self, mode, canvas):
        shadowX, shadowY = getShadowPosition(mode, self.position)
        shadowPos1Rendered = getXandY(mode, (shadowX, shadowY, 0))
        shadowPos2Rendered = getXandY(mode, (self.position[0], self.position[1], 0))
        if shadowPos1Rendered[0] != None and shadowPos2Rendered[0] != None:
            color = scaleColorByTimeOfDay(mode, (30, 80, 30), 1/3)
            canvas.create_line(shadowPos1Rendered, shadowPos2Rendered, width = 1, fill = color)

    #Draws all the balloons in a provided list
    #Sorts the balloons by distance to the observer
    @staticmethod
    def drawAll(balloons, mode, canvas, inFront):
        for balloon in reversed(sorted(balloons)):
            if not distance(balloon.position, mode.observer) > mode.app.inputBoxVars["viewRange"]:
                isInFront = distance(mode.observer, balloon.position) < distance(mode.observer, mode.app.airplane.center)
                if isInFront == inFront:
                    balloon.drawString(mode, canvas)
                    balloon.draw(mode, canvas)

    #Draws all the shadows of the balloons in a provided list
    @staticmethod
    def drawAllShadows(balloons, mode, canvas):
        for balloon in balloons:
            if not distance(balloon.position, mode.observer) > mode.app.inputBoxVars["viewRange"]:
                balloon.drawStringShadow(mode, canvas)
                drawShadow(mode, canvas, balloon.r, balloon.position)
            



    #Checks if any corner of the balloons hitbox is insider the balloon
    def touchingPlane(self, mode):
        Balloon.observerPosCopy = mode.observer
        #preliminary distance check. Reduces the load on the second more complex check
        if distance(self.position, mode.app.airplane.center) < 3 * self.r:
            #Main collision check
            for corner in mode.app.airplane.getHitboxCorners(mode).values():
                if distance(corner, self.position) < self.r:
                    return True
        return False

    #Pops any balloons that the plane is touching
    @staticmethod
    def popBalloons(mode, balloons):
        i = 0
        while i < len(balloons):
            balloon = balloons[i]
            if balloon.touchingPlane(mode):
                #The pop function is quite fitting here
                balloons.pop(i)
            else: i += 1



#Creates the balloon class
class Tree(object):
    #Initializes the balloon position and color
    def __init__(self, mode):
        minX, maxX = -2000, 2000
        minY, maxY = -2000, 2000
        self.r = random.randint(2, 6)
        self.position = None
        while self.position == None:
            pos = (random.randint(minX, maxX), random.randint(minY, maxY), random.randint(int(1.5 * self.r), int(2.5 * self.r)))
            if distance(pos, (0, 0, 0)) > 50:
                self.position = pos
        self.color = [50, 150, 50]
        Tree.observerPosCopy = mode.observer

    #Defines the "<" operation so the list can be sorted by distance to the observer
    def __lt__(self, other):
        if isinstance(other, float):
            return distance(Tree.observerPosCopy, self.position) < other
        return distance(Tree.observerPosCopy, self.position) < distance(Tree.observerPosCopy, other.position)

    #Draws the instance of a tree
    def draw(self, mode, canvas):
        if mode.observer[2] < self.position[2] - self.r:
            drawCircle(mode, canvas, self, self.color)
            self.drawTrunk(mode, canvas)
        else:
            self.drawTrunk(mode, canvas)
            drawCircle(mode, canvas, self, self.color)
            
    """
    def drawTrunk(self, mode, canvas):
        radius = getRadius(mode, self.position, self.r / 5)
        p1 = getXandY(mode, (self.position[0], self.position[1], self.position[2] - .9 * self.r))
        p2 = getXandY(mode, (self.position[0], self.position[1], 0))
        if p1[0] != None and p2[0] != None and radius != None:
            canvas.create_line(p1, p2, width = radius[0], fill = "brown")
    """

    def drawTrunk(self, mode, canvas):
        top = (self.position[0], self.position[1], self.position[2] - .9 * self.r)
        bottom = (self.position[0], self.position[1], 0)
        tempVector = vectorSum(bottom, 1, mode.observer, -1)
        horVector = makeUnitVector(crossProduct(tempVector, (0, 0, 1)))
        bottom1 = addVectorToPoint(bottom, horVector, self.r/5)
        bottom2 = addVectorToPoint(bottom, horVector, -self.r/5)
        top2 = addVectorToPoint(top, horVector, -self.r/5)
        top1 = addVectorToPoint(top, horVector, self.r/5)
        poly = []
        for point in [bottom1, bottom2, top2, top1]:
            renderedPoint = getXandY(mode, point)
            if renderedPoint[0] == None:
                return
            poly.append(renderedPoint)
        drawPolyFace(mode, canvas, [poly, (200, 120, 120)])
        
    def drawTrunkShadow(self, mode, canvas):
        shadowX, shadowY = getShadowPosition(mode, self.position)
        shadowPos1Rendered = getXandY(mode, (shadowX, shadowY, 0))
        shadowPos2Rendered = getXandY(mode, (self.position[0], self.position[1], 0))
        radius = getRadius(mode, self.position, self.r / 5)
        if shadowPos1Rendered[0] != None and shadowPos2Rendered[0] != None and radius != None:
            radius = radius[0]
            r1 = makeUnitVector(crossProduct(vectorSum((shadowX, shadowY, 0), 1, (self.position[0], self.position[1], 0), -1), (0, 0, 1)))
            #r1 = makeUnitVector(vectorSum((shadowX, shadowY, 0), 1, (self.position[0], self.position[1], 0), -1))
            #print(r1)
            #pos3 = getXandY(mode, addVectorToPoint((shadowX, shadowY, 0), r1, 1))
            #print(mode.app.airplane.center)
            #pos4 = getXandY(mode, addVectorToPoint((shadowX, shadowY, 0),  vectorSum((shadowX, shadowY, 0), -1, mode.app.airplane.center, 1), 1))
            #print(magnitude(crossProduct(r1, makeUnitVector(vectorSum((shadowX, shadowY, 0), 1, mode.observer, -1)))))
            radius *= (magnitude(crossProduct(r1, makeUnitVector(vectorSum((shadowX, shadowY, 0), 1, mode.observer, -1)))))**2
            #print(magnitude(crossProduct(r1, makeUnitVector(vectorSum((shadowX, shadowY, 0), 1, mode.observer, -1)))))
            color = scaleColorByTimeOfDay(mode, (30, 80, 30), 1/3)
            canvas.create_line(shadowPos1Rendered, shadowPos2Rendered, width = radius, fill = color)
            #if pos3[0] != None:
            #    canvas.create_line(shadowPos1Rendered, pos3, width = 2, fill = "red")
            #if pos4[0] != None:
             #   canvas.create_line(shadowPos1Rendered, pos4, width = 2, fill = "red")
                #print("wow")


    #Draws all the shadows of the balloons in a provided list
    @staticmethod
    def drawAllShadows(trees, mode, canvas):
        for tree in trees:
            if not distance(tree.position, mode.observer) > mode.app.inputBoxVars["viewRange"]:
                drawShadow(mode, canvas, tree.r, tree.position)
                tree.drawTrunkShadow(mode, canvas)
            

    #Checks if any corner of the balloons hitbox is insider the balloon
    def touchingPlane(self, mode):
        #preliminary distance check. Reduces the load on the second more complex check
        if distance(self.position, mode.app.airplane.center) < 3 * self.r:
            #Main collision check
            for corner in mode.app.airplane.getHitboxCorners(mode).values():
                if distance(corner, self.position) < self.r:
                    return True
        return False

    @staticmethod
    def isTreeTouchingPlane(trees, mode):
        Tree.observerPosCopy = mode.observer
        for tree in trees:
            if tree.touchingPlane(mode):
                mode.crashed = True



def drawAllTreesAndBushes(objects, mode, canvas):
    for currObject in objects:
        currObject.draw(mode, canvas)


def getTreesAndBushesInOrder(mode, objects):
    inRangeObjects = []
    for currObject in objects:
        if distance(currObject.position, mode.observer) < mode.app.inputBoxVars["viewRange"]:
            inRangeObjects.append(currObject)
    sortedObjects = sorted(inRangeObjects)
    #https://stackoverflow.com/questions/3556496/python-binary-search-like-function-to-find-first-number-in-sorted-list-greater-t/27453748
    i = bisect_left(sortedObjects, distance(mode.observer, mode.app.airplane.center))
    inFrontObjects = reversed(sortedObjects[:i])
    inBackObjects = reversed(sortedObjects[i:])
    return inFrontObjects, inBackObjects


    
#Draws a circle on the screen scaled by how far away from the observer it is    
def drawCircle(mode, canvas, circle, color, outline = 1):
    color = scaleColorByTimeOfDay(mode, color, 1/3)
    output = getRadius(mode, circle.position, circle.r)
    if output != None:
        circleR, p0 = output
        canvas.create_oval(p0[0] - circleR, p0[1] - circleR, p0[0] + circleR, p0[1] + circleR, fill = color, width = outline)


def getRadius(mode, position, radius):
    p0 = getXandY(mode, position)
    if p0[0] == None: return
    tempVector = crossProduct(vectorSum(position, 1, mode.observer, -1), (0, 0, -1))
    if magnitude(tempVector) == 0:
        rVector = (1, 0, 0)
    else:
        rVector = makeUnitVector(tempVector)
    p1 = getXandY(mode, addVectorToPoint(position, rVector, radius))
    if p1[0] == None: return
    circleR1 = ((p1[1] - p0[1])**2 + (p1[0] - p0[0])**2)**.5
    p2 = getXandY(mode, addVectorToPoint(position, rVector, -radius))
    if p2[0] == None: return
    circleR2 = ((p2[1] - p0[1])**2 + (p2[0] - p0[0])**2)**.5
    return min(circleR1, circleR2), p0





#CITATION: Controller reading code modified from 
#http://yameb.blogspot.com/2013/01/gamepad-input-in-python.html
#Reads the controller inputs and stores them to a list
def getControllerInputs(mode):
        controllerInputs = []
        for i in range(0, mode.gameController.get_numaxes()):
            controllerInputs.append(mode.gameController.get_axis(i))
        for i in range(0, mode.gameController.get_numbuttons()):
            controllerInputs.append(mode.gameController.get_button(i))
        return controllerInputs

#Maps a given value in a range to a different range. Also reverse the channel
#and applies a deadzone to the channel
def mapValue(channel, value, minTarget, maxTarget, deadzone):
        minVal, maxVal = channel.minVal, channel.maxVal
        if maxVal - minVal != 0 and maxTarget - minTarget != 0:
            output = (value - minVal) * (maxTarget - minTarget) / (maxVal - minVal) + minTarget
            error = abs(output - (minTarget + maxTarget) / 2)
            if channel.name != "throttle" and error / ((maxTarget - minTarget) / 2) < deadzone:
                return 0
        else:
            return 0
        if channel.isReversed:
            return maxTarget - (output - minTarget)
        else:
            return output


#Creates the ControllerChannel class
class ControllerChannel(object):
    #A default value for my controller
    deadzone = .01
    #initializes the controller channel
    def __init__(self, inputIndex, name):
        self.index = inputIndex
        self.minVal = -.68
        self.maxVal = .68
        self.isReversed = False
        self.name = name

    #Updates the deadzone used by the controller channels
    @staticmethod
    def updateDeadzone(value):
        ControllerChannel.deadzone = value / 100

    #Gets the value of a controllerChannel instance using the current state of
    #the controller
    def getValue(self, mode, noDeadzone = False):
        deadzone = ControllerChannel.deadzone if not noDeadzone else 0

        value = mode.controllerInputs[self.index]
        if self.name == "throttle":
            return mapValue(self, value, 0, 1, deadzone)
        else:
            return mapValue(self, value, -1, 1, deadzone)

    def reverseChannel(self, app):
        self.isReversed = not self.isReversed

    #Resets the calibration of all channels
    @staticmethod
    def resetAll(mode):
        for channel in mode.app.channels:
            channel.resetCalibration()

    #Resets the calibration of a controllerChannel
    def resetCalibration(self):     
        self.minVal = 0
        self.maxVal = 0

    #Calibrates all the controller channels
    @staticmethod
    def calibrateAll(mode):
        for channel in mode.channels:
            channel.calibrate(mode)

    #Draws all the currently initialized channel sliders
    @staticmethod
    def drawAllSliders(mode, canvas):
        for channel in mode.app.channels:
            channel.drawSlider(mode.app, canvas)

    #Changes the min and max values for a channel according to if the value read goes
    #above or below the current min/max
    def calibrate(self, mode):
        inputVal = mode.controllerInputs[self.index]
        if inputVal < self.minVal:
            self.minVal = inputVal
        if inputVal > self.maxVal:
            self.maxVal = inputVal

    #Initializes a joystick slider for a controllerChannel
    def initializeSlider(self, x, y, width, height):
        self.x = x
        self.y = y
        self.sliderWidth = width
        self.sliderHeight = height
        self.sliderCenter = x + width / 2
        self.sliderMargin = 2

    #Draws a controllerChannel slider
    def drawSlider(self, mode, canvas):
        canvas.create_rectangle(self.x - self.sliderMargin, self.y - self.sliderMargin, 
                                self.x + self.sliderWidth + self.sliderMargin, 
                                self.y + self.sliderHeight + self.sliderMargin, fill = "black")
        if self.name == "throttle":
            sliderValue = self.getValue(mode, True) * self.sliderWidth
            canvas.create_rectangle(self.x, self.y, self.x + sliderValue, self.y + self.sliderHeight, fill = "orange")
        else:
            sliderValue = self.getValue(mode, True) * self.sliderWidth / 2
            canvas.create_rectangle(self.sliderCenter, self.y, self.sliderCenter + sliderValue, 
                                                    self.y + self.sliderHeight, fill = "orange")
            if self.deadzone != 0:
                x0 = self.sliderCenter - self.deadzone / 2 * self.sliderWidth
                canvas.create_line(x0, self.y - self.sliderMargin, x0, self.y +self.sliderHeight + self.sliderMargin, 
                                                                            fill = "red", width = self.sliderMargin)
                x1 = self.sliderCenter + self.deadzone / 2 * self.sliderWidth
                canvas.create_line(x1, self.y - self.sliderMargin, x1, self.y +self.sliderHeight + self.sliderMargin, 
                                                                            fill = "red", width = self.sliderMargin)





#Creates an interactable button Class
class Button(object):
    #Initializes a button using the inputted values
    def __init__(self, bounds, text, color, action, fontSize = None, textColor = "black"):
        (self.x0, self.y0), (self.x1, self.y1) = bounds
        self.text = text
        self.color = color
        self.action = action
        self.textColor = textColor

        if fontSize == None:
            fontSize = int(min(.8 * (self.y1 - self.y0), 1.5 * .8 / len(self.text) * (self.x1 -self.x0)))
        self.font = f"Arial {fontSize}"

    #Checks all buttons for being pressed
    @staticmethod
    def checkAll(mode, x, y, buttons):
        for button in buttons:
            button.isPressed(mode, x, y)

    #Draws all buttons in a provided list
    @staticmethod
    def drawAll(buttons, canvas):
        for button in buttons:
            button.draw(canvas)

    #Draw an instance of a button
    def draw(self, canvas):
        color = self.color
        if isinstance(color, tuple):
            color = rgbString(color)
        canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, fill = color, width = 2)
        canvas.create_text((self.x0 + self.x1)/2, (self.y0 + self.y1)/2, text = self.text, 
                                                  font = self.font, fill = self.textColor)

    #Performs the button's action if it is pressed
    def isPressed(self, mode, clickX, clickY):
        if self.x0 <= clickX <= self.x1 and self.y0 <= clickY <= self.y1:
            self.action(mode)


#Creates an interactable checkBox class
class CheckBox(Button):
    #Initializes the checkBox using the inputted values
    def __init__(self, mode, center, size, color, varName, textColor = "black"):
        self.x0, self.y0 = center[0] - size / 2, center[1] - size / 2
        self.x1, self.y1 = center[0] + size / 2, center[1] + size / 2
        self.color = color
        self.varName = varName
        self.textColor = textColor

        varStatus = mode.app.inputBoxVars[self.varName]
        self.updateText(mode, varStatus)
        fontSize = int(min(.8 * (self.y1 - self.y0), 1.5 * .8 / len(self.text) * (self.x1 -self.x0)))
        self.font = f"Arial {fontSize}"

    #Checks if the checkBox has been pressed
    def isPressed(self, mode, clickX, clickY):
        if self.x0 <= clickX <= self.x1 and self.y0 <= clickY <= self.y1:
            varStatus = not mode.app.inputBoxVars[self.varName]
            mode.app.inputBoxVars[self.varName] = varStatus
            self.updateText(mode, varStatus)

    #Updates the text inside the checkBox when clicked
    def updateText(self, mode, varStatus):
        if varStatus: self.text = "X"
        else: self.text = " "




#Creates a TextBox class
class TextBox(object):
    #Initializes the text box using inputted values
    def __init__(self, bounds, text, anchor, color = "black", font = "Arial"):
        (self.x0, self.y0), (self.x1, self.y1) = bounds
        self.text = text
        self.anchor = anchor
        self.color = color
        fontSize = int(min(.8 * (self.y1 - self.y0), 1.5 / len(self.text) * (self.x1 -self.x0)))
        self.font = f"{font} {fontSize}"

    #Draws all the text boxes in an inputted list
    @staticmethod
    def drawAll(textBoxes, canvas):
        for textBox in textBoxes:
            textBox.draw(canvas)

    #Draws an instance of a text box
    def draw(self, canvas):
        if self.anchor == W: textX = self.x0
        elif self.anchor == E: textX = self.x1
        elif self.anchor == CENTER: textX = (self.x0 + self.x1) / 2
        canvas.create_text(textX, (self.y0 + self.y1)/2, text = self.text, 
                    font = self.font, anchor = self.anchor, fill = self.color)




#Creates an interactable box
class InputBox(object):
    #stores the currently highlighted box
    activeBox = None
    #Initializes the inputBox using the inputted values
    def __init__(self, mode, bounds, color, varName, minVal, maxVal, maxLen, numType):
        (self.x0, self.y0), (self.x1, self.y1) = bounds
        self.varName = varName
        self.text = str(mode.app.inputBoxVars[self.varName])
        self.color = color
        self.maxLen = maxLen
        self.numType = numType
        self.minVal, self.maxVal = minVal, maxVal
        fontSize = min(int((self.x1 - self.x0) * 1.5 / maxLen), int((self.y1 - self.y0) * .75))
        self.font = f"Arial {fontSize}"

    #Checks if any of the boxes in a list are pressed
    @staticmethod
    def checkAll(mode, x, y, boxes):
        previous = InputBox.activeBox
        InputBox.activeBox = None
        for box in boxes:
            box.isPressed(mode, x, y)
        if previous is not InputBox.activeBox:
            if previous != None:
                previous.finalizeInput(mode)
        
    #Draws all the inputBoxes in a inputted list
    @staticmethod
    def drawAll(boxes, canvas):
        for box in boxes:
            box.draw(canvas)
        
    #Updates the text in the active inputBox
    @staticmethod
    def keyIsPressed(mode, key):
        currentBox = InputBox.activeBox
        if currentBox == None:
            return
        elif key == "Enter":
            currentBox.finalizeInput(mode)
            InputBox.activeBox = None
        elif (key.isdigit() or key == ".") and len(currentBox.text) < currentBox.maxLen:
            currentBox.text += key
        elif key == "Backspace":
            if len(currentBox.text) > 0:
                currentBox.text = currentBox.text[:-1]

    #Checks if an instance of InputBox is clicked
    def isPressed(self, mode, clickX, clickY):
        if self.x0 <= clickX <= self.x1 and self.y0 <= clickY <= self.y1:
            InputBox.activeBox = self

    #Finalize the input value when the user clicks off the box or presses "enter"
    #Stores the value to a variable if the input is valid
    def finalizeInput(self, mode):
        try:
            value = float(self.text)  
            if not(self.numType == int and int(value) != value) and self.minVal <= value <= self.maxVal:
                if self.numType == int:
                    value = int(value)
                mode.app.inputBoxVars[self.varName] = value
            else:
                self.text = str(mode.app.inputBoxVars[self.varName])
        except:
            self.text = str(mode.app.inputBoxVars[self.varName])
        
    #Draws an instance of an inputBox
    def draw(self, canvas):
        color = self.color
        if self is InputBox.activeBox:
            color = rgbScale(color, 1.5)
        color = rgbString(color)
        canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, fill = color, width = 2)
        canvas.create_text((self.x1 + self.x0)/2, (self.y0 + self.y1)/2, text = self.text, font = self.font)


#Creates a ToolBox that shows a selection of variables to the user 
class ToolBox(object):
    #Initializes the toolBox and the values it can display
    def __init__(self, mode):
        self.dataReadouts = ["velocityReading", "altitudeReading", 
                       "attitudeReading", "distanceReading", "framerateReading"]
        self.updateReadouts(mode)
        self.width = mode.width / 6
        self.fontSize = int(self.width / 16)
        self.font = f"Arial {self.fontSize}"

    #Updates the data values currently being displayed to the user
    def updateReadouts(self, mode):
        text = "Data Readouts:\n"
        for readout in self.dataReadouts:
            #Checks if this readout is enabled
            if mode.app.inputBoxVars[readout]:
                if readout == "velocityReading":
                    velocity = mode.app.airplane.velocity
                    if isinstance(mode.app.airplane.velocity, list):
                        velocity = magnitude(velocity)
                    text += f"Velocity: {round(velocity, 1)} m/s\n"
                elif readout == "altitudeReading":
                    text += f"Altitude: {round(mode.app.airplane.center[2], 1)} m\n"
                elif readout == "attitudeReading":
                    attitude = math.asin(dotProduct(mode.app.airplane.d1, (0, 0, 1))) * 180 / math.pi
                    text += f"Attitude: {round(attitude, 1)} degrees\n"
                elif readout == "distanceReading":
                    text += f"Distance: {round(distance(mode.app.airplane.center, (0, 0, 0)), 1)} m\n"
                elif readout == "framerateReading":
                    text += f"Framerate: {round(mode.framerate, 1)} fps\n"
        self.text = text[:-1]

    #Draws a box of all the active data readouts on the screen
    def draw(self, mode, canvas):
        if not mode.app.inputBoxVars["displayData"]:
            return
        lines = self.text.count("\n") + 1
        height = 2 * lines * self.fontSize
        canvas.create_rectangle(0, mode.height / 2 - height / 2, self.width, mode.height / 2 + height / 2, 
                                                fill = "black", outline = rgbString((75, 75, 75)), width = mode.width / 128)
        canvas.create_text(mode.width / 64, mode.height / 2, text = self.text, anchor = W, fill = "white", font = self.font)



class Runway(object):
    def __init__(self):
        self.yCount = 4
        self.xCount = 30
        self.ySize = 6
        self.xSize = 45
        self.position = (0, 5, 0)
        self.color = (50, 50, 50)

        self.startPos = (self.position[0] - self.xSize/2, self.position[1] - self.ySize/2)
        self.dx = self.xSize / self.xCount
        self.dy = self.ySize / self.yCount

    def draw(self, mode, canvas):
        for i in range(self.xCount):
            x = self.startPos[0] + i*self.dx
            for j in range(self.yCount):
                y = self.startPos[1] + j*self.dy
                Runway.drawRunwayTile(mode, canvas, (x, y), self.dx, self.dy, self.color)


    @staticmethod
    def drawRunwayTile(mode, canvas, cornerPos, dx, dy, color):   
        poly = []
        for point in [(cornerPos[0], cornerPos[1], 0), (cornerPos[0] + dx, cornerPos[1], 0), 
                    (cornerPos[0] + dx, cornerPos[1] + dy, 0), (cornerPos[0], cornerPos[1] + dy, 0)]:
            (x,y) = getXandY(mode, point)
            if x == None:
                return
            poly.append((x,y))
        drawPolyFace(mode, canvas, (poly, color), True, 0)
    
                