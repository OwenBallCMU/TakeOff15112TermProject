#This file initializes the airplane

import math
from myClasses import Airplane, Quad
import random


#Selects which aircraft to load depending on the current aircraft selection
def createAirplane(mode):
    inputNum = mode.app.inputBoxVars["aircraftNumber"]
    if inputNum == 1:
        airplane = createAirplane1(mode)
    elif inputNum == 2:
        airplane = createAirplane2(mode)
    elif inputNum == 3:
        airplane = createAirplane3(mode)
    elif inputNum == 4:
        airplane = createAirplane4(mode)
    elif inputNum == 5:
        airplane = createQuad1(mode)

    return airplane

#Creates a top-mounted wing plane
def createAirplane1(mode):
    d1 = (1, 0, 0)
    d2 = (0, 0, 1)
    position = (-15, 5, 0)
    airplane = Airplane("airplane1", d1, d2, position)

    planeLength = mode.app.airplaneSize
    wingspan = 6/5 * planeLength
    controlSurfaceThickness = planeLength / 50

    bodyHeight = planeLength / 10
    bodyWidth = planeLength / 10

    bodyColor = (mode.app.inputBoxVars["bodyRed"], mode.app.inputBoxVars["bodyGreen"], mode.app.inputBoxVars["bodyBlue"])
    wingColor = (mode.app.inputBoxVars["wingRed"], mode.app.inputBoxVars["wingGreen"], mode.app.inputBoxVars["wingBlue"])

    body = {}
    body["name"] = "body"
    body["width"] = bodyWidth
    body["length"] = planeLength
    body["height"] = bodyHeight
    body["d1Offset"], body["d2Offset"], body["d3Offset"] = (0, 0, 0)
    body["color"] = bodyColor
    airplane.addPart(body)

    wing = {}
    wing["name"] = "wing"
    wing["width"] = wingspan
    wing["height"] = controlSurfaceThickness
    wing["length"] = 3/10 * planeLength
    wing["d1Offset"] = 1/6 * planeLength
    wing["d2Offset"] = controlSurfaceThickness / 2 + bodyHeight/2
    wing["d3Offset"] = 0 
    wing["color"] = wingColor
    airplane.addPart(wing)

    horStab = {}
    horStab["name"] = "horStab"
    horStab["width"] = wingspan * 2/5
    horStab["height"] = controlSurfaceThickness
    horStab["length"] = 2/3 * wing["length"]
    horStab["d1Offset"] = -planeLength/2 + horStab["length"]/2
    horStab["d2Offset"] = controlSurfaceThickness / 2 + bodyHeight/2
    horStab["d3Offset"] = 0 
    horStab["color"] = wingColor
    airplane.addPart(horStab)

    vertStab = {}
    vertStab["name"] = "vertStab"
    vertStab["width"] = controlSurfaceThickness
    vertStab["height"] = 1/6 * wingspan
    vertStab["length"] = horStab["length"]
    vertStab["d1Offset"] = -planeLength/2 + vertStab["length"]/2
    vertStab["d2Offset"] = vertStab["height"] / 2 + bodyHeight/2 + controlSurfaceThickness
    vertStab["d3Offset"] = 0 
    vertStab["color"] = wingColor
    airplane.addPart(vertStab)

    
    prop = {}
    prop["name"] = "prop"
    prop["width"] = planeLength / 3
    prop["height"] = planeLength / 25
    prop["length"] = controlSurfaceThickness
    prop["d1Offset"] = planeLength/2 + controlSurfaceThickness/2
    prop["d2Offset"] = 0
    prop["d3Offset"] = 0
    prop["d1Rotation"] = 45
    prop["color"] = (200, 200, 200)
    airplane.addPart(prop)
    

    hitbox = {}
    hitbox["width"] = wingspan
    hitbox["length"] = planeLength
    hitbox["height"] = bodyHeight + controlSurfaceThickness
    hitbox["d1Offset"], hitbox["d2Offset"], hitbox["d3Offset"] = (0, controlSurfaceThickness / 2, 0)
    airplane.createHitbox(hitbox)

    return airplane


#Creates a plane with a bottom mounted wing with a mid-mounted horizontal stabilizer
def createAirplane2(mode):
    d1 = (1, 0, 0)
    d2 = (0, 0, 1)
    position = (0, 5, 0)
    airplane = Airplane("airplane2", d1, d2, position)

    planeLength = mode.app.airplaneSize
    wingspan = 6/5 * planeLength
    controlSurfaceThickness = planeLength / 50

    bodyHeight = planeLength / 10
    bodyWidth = planeLength / 10

    bodyColor = (mode.app.inputBoxVars["bodyRed"], mode.app.inputBoxVars["bodyGreen"], mode.app.inputBoxVars["bodyBlue"])
    wingColor = (mode.app.inputBoxVars["wingRed"], mode.app.inputBoxVars["wingGreen"], mode.app.inputBoxVars["wingBlue"])

    body = {}
    body["name"] = "body"
    body["width"] = bodyWidth
    body["length"] = planeLength
    body["height"] = bodyHeight
    body["d1Offset"], body["d2Offset"], body["d3Offset"] = (0, 0, 0)
    body["color"] = bodyColor
    airplane.addPart(body)

    wing1 = {}
    wing1["name"] = "wing1"
    wing1["width"] = wingspan/2 - bodyWidth/2
    wing1["height"] = controlSurfaceThickness
    wing1["length"] = 3/10 * planeLength
    wing1["d1Offset"] = 1/6 * planeLength
    wing1["d2Offset"] = controlSurfaceThickness / 2 - bodyHeight/2
    wing1["d3Offset"] = wing1["width"]/2 + bodyWidth/2
    wing1["color"] = wingColor
    airplane.addPart(wing1)

    wing2 = {}
    wing2["name"] = "wing2"
    wing2["width"] = wingspan/2 - bodyWidth/2
    wing2["height"] = controlSurfaceThickness
    wing2["length"] = 3/10 * planeLength
    wing2["d1Offset"] = 1/6 * planeLength
    wing2["d2Offset"] = controlSurfaceThickness / 2 - bodyHeight/2
    wing2["d3Offset"] = -wing2["width"]/2 - bodyWidth/2
    wing2["color"] = wingColor
    airplane.addPart(wing2)

    horStab1 = {}
    horStab1["name"] = "horStab1"
    horStab1["width"] = (wingspan * 2/5) / 2 - bodyWidth/2
    horStab1["height"] = controlSurfaceThickness
    horStab1["length"] = 2/3 * 3/10 * planeLength
    horStab1["d1Offset"] = -planeLength/2 + horStab1["length"]/2
    horStab1["d2Offset"] = 0
    horStab1["d3Offset"] = horStab1["width"]/2 + bodyWidth/2 
    horStab1["color"] = wingColor
    airplane.addPart(horStab1)

    horStab2 = {}
    horStab2["name"] = "horStab2"
    horStab2["width"] = (wingspan * 2/5) / 2 - bodyWidth/2
    horStab2["height"] = controlSurfaceThickness
    horStab2["length"] = 2/3 * 3/10 * planeLength
    horStab2["d1Offset"] = -planeLength/2 + horStab2["length"]/2
    horStab2["d2Offset"] = 0
    horStab2["d3Offset"] = -horStab1["width"]/2 - bodyWidth/2 
    horStab2["color"] = wingColor
    airplane.addPart(horStab2)


    vertStab = {}
    vertStab["name"] = "vertStab"
    vertStab["width"] = controlSurfaceThickness
    vertStab["height"] = 1/6 * wingspan
    vertStab["length"] = horStab1["length"]
    vertStab["d1Offset"] = -planeLength/2 + vertStab["length"]/2
    vertStab["d2Offset"] = vertStab["height"] / 2 + bodyHeight/2
    vertStab["d3Offset"] = 0 
    vertStab["color"] = wingColor
    airplane.addPart(vertStab)

    
    prop = {}
    prop["name"] = "prop"
    prop["width"] = planeLength / 3
    prop["height"] = planeLength / 25
    prop["length"] = controlSurfaceThickness
    prop["d1Offset"] = planeLength/2 + controlSurfaceThickness/2
    prop["d2Offset"] = 0
    prop["d3Offset"] = 0
    prop["d1Rotation"] = 45
    prop["color"] = (200, 200, 200)
    airplane.addPart(prop)
    

    hitbox = {}
    hitbox["width"] = wingspan
    hitbox["length"] = planeLength
    hitbox["height"] = bodyHeight + controlSurfaceThickness
    hitbox["d1Offset"], hitbox["d2Offset"], hitbox["d3Offset"] = (0, controlSurfaceThickness / 2, 0)
    airplane.createHitbox(hitbox)

    return airplane



def createAirplane3(mode):
    d1 = (1, 0, 0)
    d2 = (0, 0, 1)
    position = (0, 5, 0)
    airplane = Airplane("airplane3", d1, d2, position)

    planeLength = mode.app.airplaneSize
    wingspan = 6/5 * planeLength
    controlSurfaceThickness = planeLength / 50

    bodyHeight = planeLength / 10
    bodyWidth = planeLength / 10

    bodyColor = (mode.app.inputBoxVars["bodyRed"], mode.app.inputBoxVars["bodyGreen"], mode.app.inputBoxVars["bodyBlue"])
    wingColor = (mode.app.inputBoxVars["wingRed"], mode.app.inputBoxVars["wingGreen"], mode.app.inputBoxVars["wingBlue"])

    body = {}
    body["name"] = "body"
    body["width"] = bodyWidth
    body["length"] = planeLength
    body["height"] = bodyHeight
    body["d1Offset"], body["d2Offset"], body["d3Offset"] = (0, 0, 0)
    body["color"] = bodyColor
    airplane.addPart(body)

    wing1 = {}
    wing1["name"] = "wing1"
    wing1["width"] = wingspan/2 - bodyWidth/2
    wing1["height"] = controlSurfaceThickness
    wing1["length"] = 3/10 * planeLength
    wing1["d1Offset"] = 1/6 * planeLength
    wing1["d2Offset"] = controlSurfaceThickness / 2 - bodyHeight/2
    wing1["d3Offset"] = wing1["width"]/2 + bodyWidth/2
    wing1["color"] = wingColor
    airplane.addPart(wing1)

    wing2 = {}
    wing2["name"] = "wing2"
    wing2["width"] = wingspan/2 - bodyWidth/2
    wing2["height"] = controlSurfaceThickness
    wing2["length"] = 3/10 * planeLength
    wing2["d1Offset"] = 1/6 * planeLength
    wing2["d2Offset"] = controlSurfaceThickness / 2 - bodyHeight/2
    wing2["d3Offset"] = -wing2["width"]/2 - bodyWidth/2
    wing2["color"] = wingColor
    airplane.addPart(wing2)

    horStab = {}
    horStab["name"] = "horStab"
    horStab["width"] = wingspan * 2/5
    horStab["height"] = controlSurfaceThickness
    horStab["length"] = 2/3 * 3/10 * planeLength
    horStab["d1Offset"] = -planeLength/2 + horStab["length"]/2
    horStab["d2Offset"] = controlSurfaceThickness / 2 + bodyHeight/2
    horStab["d3Offset"] = 0 
    horStab["color"] = wingColor
    airplane.addPart(horStab)

    vertStab = {}
    vertStab["name"] = "vertStab"
    vertStab["width"] = controlSurfaceThickness
    vertStab["height"] = 1/6 * wingspan
    vertStab["length"] = horStab["length"]
    vertStab["d1Offset"] = -planeLength/2 + vertStab["length"]/2
    vertStab["d2Offset"] = vertStab["height"] / 2 + bodyHeight/2 + controlSurfaceThickness
    vertStab["d3Offset"] = 0 
    vertStab["color"] = wingColor
    airplane.addPart(vertStab)

    
    prop = {}
    prop["name"] = "prop"
    prop["width"] = planeLength / 3
    prop["height"] = planeLength / 25
    prop["length"] = controlSurfaceThickness
    prop["d1Offset"] = planeLength/2 + controlSurfaceThickness/2
    prop["d2Offset"] = 0
    prop["d3Offset"] = 0
    prop["d1Rotation"] = 45
    prop["color"] = (200, 200, 200)
    airplane.addPart(prop)
    

    hitbox = {}
    hitbox["width"] = wingspan
    hitbox["length"] = planeLength
    hitbox["height"] = bodyHeight + controlSurfaceThickness
    hitbox["d1Offset"], hitbox["d2Offset"], hitbox["d3Offset"] = (0, controlSurfaceThickness / 2, 0)
    airplane.createHitbox(hitbox)

    return airplane


def createAirplane4(mode):
    airplane = createAirplane3(mode)
    airplane.name = "airplane4"
    
    planeLength = mode.app.airplaneSize
    wingspan = 6/5 * planeLength
    controlSurfaceThickness = planeLength / 50

    bodyHeight = planeLength / 10
    bodyWidth = planeLength / 10

    bodyColor = (mode.app.inputBoxVars["bodyRed"], mode.app.inputBoxVars["bodyGreen"], mode.app.inputBoxVars["bodyBlue"])
    wingColor = (mode.app.inputBoxVars["wingRed"], mode.app.inputBoxVars["wingGreen"], mode.app.inputBoxVars["wingBlue"])

    wing3 = {}
    wing3["name"] = "wing3"
    wing3["width"] = wingspan
    wing3["height"] = controlSurfaceThickness
    wing3["length"] = 3/10 * planeLength
    wing3["d1Offset"] = 1/6 * planeLength
    wing3["d2Offset"] = controlSurfaceThickness / 2 + bodyHeight/2
    wing3["d3Offset"] = 0 
    wing3["color"] = wingColor
    airplane.addPart(wing3)
    
    return airplane




def createQuad1(mode):
    d1 = (1, 0, 0)
    d2 = (0, 0, 1)
    position = (0, 5, 0)
    quad = Quad("quad1", d1, d2, position)

    planeLength = mode.app.airplaneSize / 2
    controlSurfaceThickness = planeLength / 50

    yellow = (255, 255, 0)
    red = (255, 0, 0)
    black = (0, 0, 0)

    body = {}
    body["name"] = "body"
    body["width"] = planeLength * 2**.5
    body["length"] = planeLength / 5
    body["height"] = planeLength / 20
    body["d1Offset"], body["d2Offset"], body["d3Offset"] = (0, 0, 0)
    body["d2Rotation"] = 45
    body["color"] = black
    quad.addPart(body)

    body2 = {}
    body2["name"] = "body2"
    body2["width"] = planeLength * 2**.5
    body2["length"] = planeLength / 5
    body2["height"] = planeLength / 20
    body2["d1Offset"], body2["d2Offset"], body2["d3Offset"] = (0, -planeLength/20, 0)
    body2["d2Rotation"] = -45
    body2["color"] = black
    quad.addPart(body2)


    hitbox = {}
    hitbox["width"] = planeLength
    hitbox["length"] = planeLength
    hitbox["height"] = planeLength / 20
    hitbox["d1Offset"] = hitbox["d2Offset"] = hitbox["d3Offset"] = 0
    quad.createHitbox(hitbox)

    counter = 1
    for offset1 in [-1, 1]:
        for offset2 in [-1, 1]:
            prop = {}
            prop["name"] = f"prop{counter}"
            prop["width"] = planeLength / 3
            prop["height"] = controlSurfaceThickness * 2
            prop["length"] = planeLength / 25
            prop["d1Offset"] = planeLength/2 * offset1
            prop["d2Offset"] = prop["height"] / 2 + body["height"] / 2
            prop["d3Offset"] = planeLength/2 * offset2
            prop["d2Rotation"] = random.randint(0, 360)
            prop["color"] = (200, 200, 200)
            quad.addPart(prop)
            counter += 1
    return quad

