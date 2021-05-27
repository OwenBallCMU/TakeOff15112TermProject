#This file stores functions used to perform calulations using vectors

import math

#Finds the distance between two points in 3D space
def distance(point, observer):
    x0, y0, z0 = point
    x1, y1, z1 = observer
    #dist2 = ((x1-x0)**2 + (y1-y0)**2)**.5
    #dist1 = ((x1-x0)**2 + (z1-z0)**2)**.5

    return math.sqrt((x1-x0)**2 + (y1-y0)**2 + (z1-z0)**2)

#Finds the dot product between two vectors
def dotProduct(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

#Finds the cross product between two vectors
def crossProduct(v1, v2):
    x0, y0, z0 = v1
    x1, y1, z1 = v2
    return (y0 * z1 - y1 * z0, x1 * z0 - x0 * z1, x0 * y1 - x1 * y0)

#Finds the magnitude of a vector
def magnitude(v):
    return math.sqrt((v[0])**2 + (v[1])**2 + (v[2])**2)

#Adds a vector that can be scaled to a point to yield a new point
def addVectorToPoint(point, vector, scale):
        x, y, z = (point[0], point[1], point[2])
        rx, ry, rz = (vector[0] * scale, vector[1] * scale, vector[2] * scale)
        return (x + rx, y + ry, z + rz)

#Converts a vector into a unit vector
def makeUnitVector(vector):
    mag = magnitude(vector)
    unitVector = []
    for val in vector:
        unitVector.append(val / mag)
    return unitVector

#CITATION: Math for vector rotation from 
#https://math.stackexchange.com/questions/3130813/rotating-a-vector-perpendicular-to-another
#Rotates a vector about another vector by "amount" degrees
def rotateVector(vector, axis, amount):
    tempVector = crossProduct(vector, axis)
    amount *= math.pi / 180
    return makeUnitVector(vectorSum(vector, math.cos(amount), tempVector, math.sin(amount)))

#Returns the vector that is the sum of two inputted vectors. The vectors can
#be scaled, mostly to enable subtraction
def vectorSum(vector1, scale1, vector2, scale2):
    result = []
    for i in range(len(vector1)):
        result.append(vector1[i] * scale1 + vector2[i] * scale2)
    return result