#This file initializes the airplane with respect to "mode.airplaneSize"

import math
from myClasses import Airplane

#Creates the airplane as an instance of the Airplane class
def createAirplane(mode):
    d1 = (1, 0, 0)
    d2 = (0, 0, 1)

    position = (0, 5, 0)
    airplane = Airplane("mainAirplane", d1, d2, position)

    planeLength = mode.airplaneSize
    wingspan = 6/5 * planeLength
    controlSurfaceThickness = planeLength / 50

    bodyHeight = planeLength / 10
    bodyWidth = planeLength / 10

    yellow = (255, 255, 0)
    red = (255, 0, 0)

    body = {}
    body["name"] = "body"
    body["width"] = bodyWidth
    body["length"] = planeLength
    body["height"] = bodyHeight
    body["d1Offset"], body["d2Offset"], body["d3Offset"] = (0, 0, 0)
    body["color"] = red
    airplane.addPart(body)

    wing = {}
    wing["name"] = "wing"
    wing["width"] = wingspan
    wing["height"] = controlSurfaceThickness
    wing["length"] = 3/10 * planeLength
    wing["d1Offset"] = 1/6 * planeLength
    wing["d2Offset"] = controlSurfaceThickness / 2 + bodyHeight/2
    wing["d3Offset"] = 0 
    wing["color"] = yellow
    airplane.addPart(wing)

    horStab = {}
    horStab["name"] = "horStab"
    horStab["width"] = wingspan * 2/5
    horStab["height"] = controlSurfaceThickness
    horStab["length"] = 2/3 * wing["length"]
    horStab["d1Offset"] = -planeLength/2 + horStab["length"]/2
    horStab["d2Offset"] = controlSurfaceThickness / 2 + bodyHeight/2
    horStab["d3Offset"] = 0 
    horStab["color"] = yellow
    airplane.addPart(horStab)

    vertStab = {}
    vertStab["name"] = "vertStab"
    vertStab["width"] = controlSurfaceThickness
    vertStab["height"] = 1/6 * wingspan
    vertStab["length"] = horStab["length"]
    vertStab["d1Offset"] = -planeLength/2 + vertStab["length"]/2
    vertStab["d2Offset"] = vertStab["height"] / 2 + bodyHeight/2 + controlSurfaceThickness
    vertStab["d3Offset"] = 0 
    vertStab["color"] = yellow
    airplane.addPart(vertStab)

    hitbox = {}
    hitbox["width"] = wingspan
    hitbox["length"] = planeLength
    hitbox["height"] = bodyHeight + controlSurfaceThickness
    hitbox["d1Offset"], hitbox["d2Offset"], hitbox["d3Offset"] = (0, controlSurfaceThickness / 2, 0)
    airplane.createHitbox(hitbox)

    return airplane