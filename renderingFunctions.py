#This file contains the functions used to project points from the 3D space 
#onto the screen. Also stores the code used to sort the faces of the airplane

import time
import math
from vectors import *
from extraneous import *
from collections import defaultdict
from shapely.geometry import Point, Polygon
import random

#Sets mode.viewDirection to be a unit vector looking at the airplane
def lookAtPlane(mode):
        planeCenter = mode.airplane.center
        observer = mode.observer
        vector = []
        for i in range(len(planeCenter)):
            vector.append(planeCenter[i] - observer[i])
        mode.viewDirection = makeUnitVector(vector)

#Initializes the ground as a dictionary with keys as (row, col) and the color of
#that piece of ground as the value
def createGround(mode):
    mode.grassSize = 20
    mode.grassRange = 2000
    mode.floor = {}
    mode.grassCount = int(mode.grassRange / mode.grassSize)
    for row in range(-mode.grassCount, mode.grassCount):
        for col in range(-mode.grassCount, mode.grassCount):
            mode.floor[(row, col)] = ((50, random.randint(150, 175), 50))
        

#Moves the user towards the plane to create the appearance of the camera 
#trailing the plane
def followPlane(mode):
    vertOffset = math.sin(mode.app.inputBoxVars["cameraAngle"] * math.pi / 180)
    dist = (distance(mode.observer, mode.airplane.center) - mode.app.inputBoxVars["followDistance"])
    moveDist = 5 * dist / mode.framerate
    if moveDist > 50: moveDist = 50
    mode.observer = addVectorToPoint(mode.observer, mode.viewDirection, moveDist)
    mode.observer = addVectorToPoint(mode.observer, (0, 0, 1), moveDist * vertOffset)

#Moves the user towards (0, 0, 2) in a smoother motion than just setting the
#position to (0, 0, 2)
def gotoOrigin(mode):
    origin = (0, 0, 2)
    dist = distance(origin, mode.observer)
    if dist < .3:
        return
    moveDist = 5 * dist / mode.framerate
    if moveDist > 50: moveDist = 50
    r = vectorSum(origin, 1, mode.observer, -1)
    if magnitude(r) != 0:  
        mode.observer = addVectorToPoint(mode.observer, makeUnitVector(r), moveDist)



#CITATION: General idea for the following function developed while talking
#with Professor Kosbie

#Finds the point on a plane perpendicular to the viewDirection that a ray drawn
#between the point in space and the observer intersects this plane
def getProjectionPoint(mode, point):
    x0, y0, z0 = mode.observer
    x1, y1, z1 = point
    nx, ny, nz = mode.viewDirection
    denom = nx * (x1 - x0) + ny * (y1 - y0) + nz * (z1 - z0)
    if denom == 0:
        return None
    else:
        t = 1 / denom
    if t <= 0:
        return None
    intersectionPoint = (x0 + t * (x1 - x0), y0 + t * (y1 - y0), z0 + t * (z1 - z0))
    return intersectionPoint

#Converts the result of getProjectionPoint into a position on the computer screen
def getXandY(mode, point):
    intersectPoint = getProjectionPoint(mode, point)
    if intersectPoint == None:
        return None, None
    horizontalV = (-1 * mode.viewDirection[1], mode.viewDirection[0], 0)
    planeCenter = (mode.observer[0] + mode.viewDirection[0],
                mode.observer[1] + mode.viewDirection[1],
                mode.observer[2] + mode.viewDirection[2])
    r = (intersectPoint[0] - planeCenter[0], intersectPoint[1] - planeCenter[1], intersectPoint[2] - planeCenter[2])
    xOffset = dotProduct(horizontalV, r) / magnitude(horizontalV)
    maxXOffset = math.tan(mode.fov / 2)
    x = xOffset / maxXOffset * mode.width / 2 + mode.width / 2

    if abs(xOffset) > maxXOffset * 2:
        return None, None

    verticalV = crossProduct(mode.viewDirection, horizontalV)
    yOffset = dotProduct(verticalV, r) / magnitude(verticalV)
    maxYOffset = math.tan(mode.fov / 2) * mode.height / mode.width
    y = -1 * yOffset / maxYOffset * mode.height / 2 + mode.height / 2
    return x,y

#Converts from a point on the screen to the point on the plane perpendicular
#to the view direction. Reverse of getXandY
def XandYToProjectionPoint(mode, point):
    x, y = point
    planeCenter = (mode.observer[0] + mode.viewDirection[0],
                mode.observer[1] + mode.viewDirection[1],
                mode.observer[2] + mode.viewDirection[2])
    maxXOffset = math.tan(mode.fov / 2)
    maxYOffset = math.tan(mode.fov / 2) * mode.height / mode.width
    horizontalV = (-1 * mode.viewDirection[1], mode.viewDirection[0], 0)
    verticalV = crossProduct(mode.viewDirection, horizontalV)
    yOffset = (y - mode.height/2) / (mode.height/2) * maxYOffset * -1
    xOffset = (x - mode.width/2)/ (mode.width/2) * maxXOffset
    projectionPoint = addVectorToPoint(planeCenter, horizontalV, xOffset / magnitude(horizontalV))
    projectionPoint = addVectorToPoint(projectionPoint, verticalV, yOffset / magnitude(verticalV))
    return projectionPoint

#Uses the point on the plane perpendicular to the view direction and solves
#for when a ray starting at the observer and passing through this point will
#intersect the face
def getTValue(mode, projectionPoint, face):
    r = vectorSum(projectionPoint, 1, mode.observer, -1)
    n = crossProduct(vectorSum(face[2], 1, face[1], -1), vectorSum(face[3], 1, face[1], -1))
    numerator = dotProduct(n, vectorSum(face[0], 1, mode.observer, -1))
    denom = dotProduct(n, r)
    if denom == 0:
        return None
    return numerator / denom

#Solves for the corner of 3D object given 3 direction-identifying vectors and 
#the offset of the point from the center in each of these directions
def getCorner(mode, point, v1, s1, v2, s2, v3, s3):
    x, y, z = (point[0], point[1], point[2])
    r1x, r1y, r1z = (v1[0] * s1, v1[1] * s1, v1[2] * s1)
    r2x, r2y, r2z = (v2[0] * s2, v2[1] * s2, v2[2] * s2)
    r3x, r3y, r3z = (v3[0] * s3, v3[1] * s3, v3[2] * s3)
    return (x + r1x + r2x + r3x, y + r1y + r2y + r3y, z + r1z + r2z + r3z)


#Generates all the faces of an object and adds them to a dictionary
def getFaces(mode, shape, allFaces):
    name = shape[0]
    color = shape[-1]
    vertices = getVertices(mode, shape[1:-1])
    for i in range(6):
        makeFaceUsingVertices(mode, mode.faceSetups[i], vertices, allFaces, name, color, i)

#Creates a single face of the object and adds it to a dictionary
def makeFaceUsingVertices(mode, faceVertices, allVertices, allFaces, name, color, faceNum):
    face = []
    for vertex in faceVertices:
        face.append(allVertices[f"c{vertex}"])
    allFaces[f"{name}f{faceNum}"] = (face, color)

#Creates a dictionary of all the corners of an object. 
#Could be a list, but having a dictionary made referencing the corners easier
def getVertices(mode, shape):    
    d1, d2, d3 = (shape[1], shape[2], crossProduct(shape[1], shape[2]))
    length, height, width = (shape[3], shape[4], shape[5])
    center = shape[0]
    vertices = { }   
    vertices["c1"] = getCorner(mode, center, d1, length/2, d2, height/2, d3, width/2)
    vertices["c2"] = getCorner(mode, center, d1, length/2, d2, -height/2, d3, width/2)
    vertices["c3"] = getCorner(mode, center, d1, -length/2, d2, -height/2, d3, width/2)
    vertices["c4"] = getCorner(mode, center, d1, -length/2, d2, height/2, d3, width/2)
    vertices["c5"] = getCorner(mode, center, d1, length/2, d2, height/2, d3, -width/2)
    vertices["c6"] = getCorner(mode, center, d1, -length/2, d2, height/2, d3, -width/2)
    vertices["c7"] = getCorner(mode, center, d1, -length/2, d2, -height/2, d3, -width/2)
    vertices["c8"] = getCorner(mode, center, d1, length/2, d2, -height/2, d3, -width/2)
    return vertices

#Converts all the 3D faces of the object into 2D polygons
def renderFaces(mode, shape, renderedFaces):
    name = shape[0]
    color = shape[-1]
    vertices = getVertices(mode, shape[1:-1])
    renderedVertices = renderVertices(mode, vertices)
    for i in range(6):
        renderFace(mode, mode.faceSetups[i], renderedVertices, renderedFaces, name, color, i)

#Converts a single 3D face into a 2D polygon if all of this vertices are on the screen
def renderFace(mode, faceVertices, allRenderedVertices, renderedFaces, name, color, faceNum):
    renderedFace = []
    for vertex in faceVertices:
        point = allRenderedVertices[f"c{vertex}"]
        if point == None:
            return None
        else:
            renderedFace.append(point)
    if areaOfPolygon(renderedFace) != 0:
        renderedFaces[f"{name}f{faceNum}"] = (renderedFace, color)

#Evaluates the area of a polygon using a list of inputted vertices
def areaOfPolygon(L):
    result = 0
    for vertex in range(0, len(L)):
        x0, y0 = L[vertex]
        #if there are no more vertices in the list, cycle x1 and y1 back to
        #the first vertex
        if vertex + 1 >= len(L):
            x1, y1 = L[0]
        else:
            x1, y1 = L[vertex + 1]
        #CITATION: Used the formula from 
        #https://www.mathopenref.com/coordpolygonarea.html to evaluate the area
        result += x0 * y1 - y0 * x1
    return abs(result / 2)

#Converts all the corners of an object in 3D space into a point on the screen
def renderVertices(mode, vertices):
    renderedVertices = {}
    for vertex in vertices:
        point = vertices[vertex]
        renderedPoint = getXandY(mode, point)
        if renderedPoint[0] == None:
            renderedVertices[vertex] = None
        else:
            renderedVertices[vertex] = renderedPoint
    return renderedVertices




###############
#Face Sorting
###############

#Professor Kosbie helped me come up with the general idea for this function
#Compares two faces and returns True if the first face is in front of the second
def isFaceInFront(mode, faceName1, faceName2, allFaces, renderedFaces):
    face1, face2 = allFaces[faceName1][0], allFaces[faceName2][0]
    rendered1, rendered2 = renderedFaces[faceName1][0], renderedFaces[faceName2][0]
    if mode.app.inputBoxVars["useShapely"]:
        point = shapelyGetMiddleOfOverlap(mode, rendered1, rendered2)
    else:
        point = myGetMiddleOfOverlap(mode, rendered1, rendered2)
    if point == None:
        return None
    projectionPoint = XandYToProjectionPoint(mode, point)
    t1 = getTValue(mode, projectionPoint, face1)
    t2 = getTValue(mode, projectionPoint, face2)
    if t1 == None or t2 == None or almostEqual(t1, t2):
        return None
    return t2 > t1

#Draws all of the shapes that are a part of the plane in the proper order
def drawShapes(mode, canvas, renderedFaces, allFaces, planeNames):
    def drawShape(shape):
        if drawnShapes[shape]:
            return
        #Draw all the lower shapes before drawing this one
        for lowerShape in lowerShapes(mode, shape, renderedFaces, allFaces, drawnShapes, planeNames):
            drawShape(lowerShape)
        drawFaces(mode, canvas, allFaces, shape, renderedFaces)
        drawnShapes[shape] = True

    drawnShapes = defaultdict(lambda: False)
    for shape in planeNames:
        drawShape(shape)

#Generates a list of all the shapes that should be drawn before the current shape
def lowerShapes(mode, mainShape, renderedFaces, allFaces, drawnShapes, planeNames):
    lowerShapeList = []
    for shape in planeNames:
        if not drawnShapes[shape] and shape != mainShape and isShapeInFront(mode, mainShape, shape, allFaces, renderedFaces):
            lowerShapeList.append(shape)
    return lowerShapeList

#Determines if a shape as a whole is in front of another shape
def isShapeInFront(mode, mainShape, shape, allFaces, renderedFaces):
    mainShapeFaces = getShapeFaces(mode, mainShape, renderedFaces)
    shapeFaces = getShapeFaces(mode, shape, renderedFaces)
    for mainShapeFace in mainShapeFaces:
        for shapeFace in shapeFaces:
            isShapeCloser =  isFaceInFront(mode, mainShapeFace, shapeFace, allFaces, renderedFaces)
            if isShapeCloser:
                return True
            elif isShapeCloser == False:
                return False
    return False

#CITATION: Professor Kosbie helped me come up with the general structure of this function
#Draws all of the faces that make up a shape in the proper order
def drawFaces(mode, canvas, allFaces, shapeName, renderedFaces):
    shapeFaces = getShapeFaces(mode, shapeName, renderedFaces)
    def drawFace(face):
        if drawnFaces[face]:
            return
        #Draws all the lower faces before drawing the current face
        for lowerFace in lowerFaces(mode, face, shapeFaces, allFaces, drawnFaces, renderedFaces):
            drawFace(lowerFace)
        drawPolyFace(mode, canvas, renderedFaces[face])
        #Creates the binocular view plane if binoculars are enabled
        if mode.app.inputBoxVars["binoculars"] and not mode.followPlaneMode:
            drawBinocularFace(mode, canvas, renderedFaces[face])
        drawnFaces[face] = True
    drawnFaces = defaultdict(lambda: False)
    for face in shapeFaces:
        drawFace(face)

#Generates a list of all the faces in a shape that should be drawn before the 
#current face
def lowerFaces(mode, mainFace, shapeFaces, allFaces, drawnFaces, renderedFaces):
    lowerFaceList = []
    for face in shapeFaces:
        if not drawnFaces[face] and face != mainFace and isFaceInFront(mode, mainFace, face, allFaces, renderedFaces):
            lowerFaceList.append(face) 
    return lowerFaceList

#Creates a list of the faces that make up a shape
def getShapeFaces(mode, shapeName, renderedFaces):
    faces = []
    for i in range(6):
        if f"{shapeName}f{i}" in renderedFaces:
            faces.append(f"{shapeName}f{i}")
    return faces


##################
#Drawing
##################

#Draws a provided face on the screen
def drawPolyFace(mode, canvas, face, scaleColor = True):
        poly = face[0]
        color = face[-1]
        if scaleColor:
            color = scaleColorByTimeOfDay(mode, color, 1/3)
        else:
            color = rgbString(color)
        canvas.create_polygon(poly, fill = color, width = 1, outline = "black")

#Takes a face and draws the binocular view of the face
def drawBinocularFace(mode, canvas, face):
    color = face[-1]
    scaledFace = []
    width = mode.width / 6
    height = mode.height / 6
    bWidth = mode.binocularWidth
    bHeight = bWidth * height / width 
    for x, y in face[0]:
        newX = mode.width - (mode.width/2 + bWidth/2 - x) * width / bWidth
        newY = (y - (mode.height/2 - bHeight/2)) * height / bHeight
        scaledFace.append((newX, newY))
    drawPolyFace(mode, canvas, (scaledFace, color), False)

#Finds the width of an imaginary box surrounding the plane used to generate the
#binocular view
def getBinocularWidth(mode):
    dist = distance(mode.airplane.center, mode.observer)
    mode.binocularWidth = 1.5 * mode.airplaneSize * mode.width / dist

#Creates the background for the binocular view
def drawBinocularBackground(mode, canvas):
    width = mode.width / 6
    height = mode.height / 6
    canvas.create_rectangle((mode.width - width, height), (mode.width, 0), fill = rgbString((150, 150, 150)), width = mode.width/256)
    
#Draws the floor tiles that are close enough to the user
def drawFloor(mode, canvas):
    viewRange = mode.app.inputBoxVars["viewRange"]
    minCol, maxCol = (int(mode.observer[0] / mode.grassSize - viewRange / mode.grassSize), 
                     int(mode.observer[0] // mode.grassSize + viewRange / mode.grassSize))
    minRow, maxRow = (int(mode.observer[1] // mode.grassSize - viewRange / mode.grassSize), 
                     int(mode.observer[1] // mode.grassSize + viewRange / mode.grassSize))
    for row in range(minRow, maxRow):
        for col in range(minCol, maxCol):
            if (-mode.grassCount < row < mode.grassCount and -mode.grassCount < col < mode.grassCount and
                not(-2 < row < 2 and -2 < col < 2)):
                drawGrassSquare(mode, canvas, row, col)

#Draws a grass square at a given row and column
def drawGrassSquare(mode, canvas, row, col):
    poly = []
    for point in getGrassCorners(mode, row, col):
        (x,y) = getXandY(mode, point)
        if x == None:
            break
        poly.append((x,y))
    if len(poly) == 4:
        color = mode.floor[(row, col)]
        colorString = scaleColorByTimeOfDay(mode, color, 1/3)
        canvas.create_polygon(poly[0][0], poly[0][1], poly[1][0], poly[1][1],
                    poly[2][0], poly[2][1], poly[3][0], poly[3][1], fill = colorString)

#Generates a list of the corners of a grass square
def getGrassCorners(mode, row, col):
    x0, y0 = col * mode.grassSize, row * mode.grassSize
    x1, y1 = x0 + mode.grassSize, y0 + mode.grassSize
    return ((x0, y0, 0), (x0, y1, 0), (x1, y1, 0), (x1, y0, 0))

#Draws the shadow of a provided object. Defaults to the airplane
def drawShadow(mode, canvas, r = "default", objectPosition = "default"):
    if r == "default":
        r = mode.airplaneSize * .75
    shadowX, shadowY = getShadowPosition(mode, objectPosition)
    cx, cy = getXandY(mode, (shadowX, shadowY, 0))
    if cx == None:
        return
    horizontalViewDirection = makeUnitVector((mode.viewDirection[0], mode.viewDirection[1], 0))
    topX, topY = getXandY(mode, addVectorToPoint((shadowX, shadowY, 0), horizontalViewDirection, r))
    
    sideX, sideY = getXandY(mode, addVectorToPoint((shadowX, shadowY, 0), crossProduct(horizontalViewDirection, (0, 0, 1)), r))
    if topX == None or sideX == None:
        return
    
    horR = (sideX - cx)
    vertR = (topY - cy)
    color = scaleColorByTimeOfDay(mode, (30, 80, 30), 1/3)
    canvas.create_oval(cx - horR, cy - vertR, cx + horR, cy + vertR, fill = color, width = 0)

#Solves for the position of the shadown on the ground using the sun/moon position
def getShadowPosition(mode, position):
    if position == "default":
        position = mode.airplane.center
    r = vectorSum(mode.sunPos, 1, position, -1)
    t = -position[2] / r[2]
    x = position[0] + r[0] * t
    y = position[1] + r[1] * t
    return (x, y)

#Draws the sun (or moon) in the sky
def drawSun(mode, canvas):
    x, y = getXandY(mode, mode.sunPos)
    r = 20
    if x != None:
        if mode.app.inputBoxVars["isDaytime"]:
            color = "yellow"
        else:
            color = rgbString((200, 200, 200))
        canvas.create_oval(x - r, y - r, x + r, y + r, fill = color)

#Draws the horzion on the screen
def drawHorizon(mode, canvas):
    observerPoint = (mode.observer[0], mode.observer[1], 0)
    horizontalViewDirection = makeUnitVector((mode.viewDirection[0], mode.viewDirection[1], 0))
    horizonPoint = addVectorToPoint(observerPoint, horizontalViewDirection, 100000)
    _, horizonY = getXandY(mode, horizonPoint)
    if horizonY != None:
        color = scaleColorByTimeOfDay(mode, (50, 155, 50), 1/3)
        canvas.create_rectangle(0, horizonY, mode.width, mode.height, fill = color)

#Sets the background color to the color of the sky
def drawSky(mode, canvas):
    if mode.app.inputBoxVars["isDaytime"]:
        color = rgbString((168, 220, 255))
    else:
        color = rgbString((30, 30, 70))
    canvas.create_rectangle(0, 0, mode.width, mode.height, fill = color)

#Alters the a color based on the time of day
def scaleColorByTimeOfDay(mode, color, scale):
    if not mode.app.inputBoxVars["isDaytime"]:
        color = rgbScale(color, scale)
    colorString = rgbString(color)
    return colorString

#Displays the crash text on the screen and prompts the user to press "r"
def displayCrashText(mode, canvas):
    cx = mode.width / 2
    cy = mode.height / 2
    labelWidth = mode.width / 4
    labelHeight = mode.height / 6
    canvas.create_rectangle(cx - labelWidth / 2, cy - labelHeight / 2, cx + labelWidth / 2, cy + labelHeight / 2, fill = "black")
    font = f"Arial {int(labelHeight / 5)}"
    canvas.create_text(cx, cy, font = font, fill = "yellow", text = """\
   You Crashed!
Press "r" to Reset""")

#Draw the timer for some of the training modes at the top of the screen
def drawTimer(mode, canvas):
    timeLeft = round(mode.timerEnd - time.time(), 1)
    text = f"Time Left: {timeLeft}"
    fontSize = int(mode.width / 36)
    font = f"Arial {fontSize}"
    boxWidth = fontSize * len(text) / 1.5
    boxHeight = fontSize * 2
    canvas.create_rectangle(mode.width/2 - boxWidth/2, 0, mode.width/2 + boxWidth/2, boxHeight, fill = "black")
    canvas.create_text(mode.width/2, boxHeight/2, text = text, font = font, fill = "white")






###################
#Shape Intersection
###################

#Shapely Function (more efficient)
def shapelyGetMiddleOfOverlap(mode, rendered1, rendered2):
    poly1 = Polygon(rendered1)
    poly2 = Polygon(rendered2)
    overlap = poly1.intersection(poly2)
    if not overlap.is_empty:
        center = overlap.centroid
        return (center.x, center.y)
    return None



#My Shape Intersection

#Finds the middle of the overlapping region between two polygons
def myGetMiddleOfOverlap(app, shape1, shape2):
    points = getAllIntersects(app, shape1, shape2)
    xSum = 0
    ySum = 0
    if len(points) <= 2:
        return None
    for (x, y) in points:
        xSum += x
        ySum += y
    return (xSum / len(points), ySum / len(points))

#Finds the slope of the line
def getSlope(line):
    return (line[1][1] - line[0][1]) / (line[1][0] - line[0][0])

#Returns the midddle of the region shared by two line segments
def getMiddleOfLine(lA, lB):
    xAmin, xAmax = (min(lA[0][0], lA[1][0]), max(lA[0][0], lA[1][0]))
    xBmin, xBmax = (min(lB[0][0], lB[1][0]), max(lB[0][0], lB[1][0]))
    xLower, xUpper = (max(xAmin, xBmin), min(xAmax, xBmax))

    yAmin, yAmax = (min(lA[0][1], lA[1][1]), max(lA[0][1], lA[1][1]))
    yBmin, yBmax = (min(lB[0][1], lB[1][1]), max(lB[0][1], lB[1][1]))
    yLower, yUpper = (max(yAmin, yBmin), min(yAmax, yBmax))
    if max(xAmin, xBmin) > min(xAmax, xBmax) or max(yAmin, yBmin) > min(yAmax, yBmax):
        return None
    return ((xLower + xUpper) / 2, (yLower + yUpper) / 2)

#Finds the intersection between a vertical line and a non-vertical line
def verticalIntersect(vertLine, line):
    x = vertLine[0][0]
    ymin, ymax = (min(vertLine[0][1], vertLine[1][1]), max(vertLine[0][1], vertLine[1][1]))
    xmin, xmax = (min(line[0][0], line[1][0]), max(line[0][0], line[1][0]))
    m = getSlope(line)
    (x1, y1, x2, y2) = (line[0][0], line[0][1], line[1][0], line[1][1])
    y = y1 + m * (x - x1)
    if ymin < y < ymax and xmin < x < xmax:
        return (x, y)
    return None
    
#Finds the intersection between two line segments
def getIntersect(lA, lB):
    (x1A, y1A, x2A, y2A) = (lA[0][0], lA[0][1], lA[1][0], lA[1][1])
    (x1B, y1B, x2B, y2B) = (lB[0][0], lB[0][1], lB[1][0], lB[1][1])
    if almostEqual(x1A, x2A) and almostEqual(x1B, x2B):
        if almostEqual(x1A, x1B):
            return getMiddleOfLine(lA, lB)
        else:
            return None
    elif almostEqual(x1A, x2A) or almostEqual(x1B, x2B):
        if almostEqual(x1A, x2A):
            return verticalIntersect(lA, lB)
        else:
            return verticalIntersect(lB, lA)
    mA = getSlope(lA)
    mB = getSlope(lB) 

    if almostEqual(mA, mB):
        return None
    x = (y1A - mA * x1A - y1B + mB * x1B) / (mB - mA)
    if almostEqual(x1A, x): return (x1A, y1A)
    elif almostEqual(x2A, x): return (x2A, y2A)
    elif almostEqual(x1B, x): return (x1B, y1B)
    elif almostEqual(x2B, x): return (x2B, y2B)
    if (x - x2A) == 0 or (x - x2B) == 0 or ((x - x1A) / (x - x2A) >= 0 or (x - x1B) / (x - x2B) >= 0):
        return None
    y = y1A + mA * (x - x1A)
    return (x,y)

#Creates a list of edges of a shape
def getEdges(shape):
    edges = []
    for i in range(0, len(shape)):
        edges.append((shape[i - 1], shape[i]))
    return edges


#Uses horizontal scanning lines from the point in question and checks for intersections
#with the edges of the shape. Does not always work when the scanning line strikes the meeting
#point of two edges

#CITATION: See http://www.eecs.umich.edu/courses/eecs380/HANDOUTS/PROJ2/InsidePoly.html 
#solution #1 for the theory that I used for this function
def insideShape(app, shape, point):
    intersects = []
    pX, pY = point[0], point[1]
    line = (point, (-app.width / 2, pY))
    for edge in getEdges(shape):
        intersect = getIntersect(line, edge)
        if intersect != None:
            x, y = intersect
            x, y = round(x, app.rounding), round(y, app.rounding)
            intersects.append((x,y))

    if len(intersects) % 2 == 1:
        return True
    return False

"""
#Note that this function still uses Shapely, just much less so than "shapelyGetMiddleOfOverlap"
#my version of this function is shown above
#Checks if a point is inside a polygon
def insideShape(app, shape, point):
    poly = Polygon(shape)
    point = Point(point)
    return poly.contains(point)
"""

#Generate a set of all the intersection points of two polygons and points completely
#contained within the other polygon
def getAllIntersects(app, shape1, shape2):
    intersects = set()
    for edge1 in getEdges(shape1):
        for edge2 in getEdges(shape2):
            if getIntersect(edge1, edge2) != None:
                x, y = getIntersect(edge1, edge2)
                x, y = round(x, app.rounding), round(y, app.rounding)
                intersects.add((x,y))
    
    for point in shape1:
        if insideShape(app, shape2, point):
            x, y = point
            x, y = round(x, app.rounding), round(y, app.rounding)
            intersects.add((x,y))
    
    for point in shape2:
        if insideShape(app, shape1, point):
            x, y = point
            x, y = round(x, app.rounding), round(y, app.rounding)
            intersects.add((x,y))
    
    return intersects

