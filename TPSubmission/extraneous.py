#This file stores helper functions used by various other files that do not 
#specifically relate to any part of the code

import decimal

#CITATION: rgbString function adapted from course notes at
#https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors

#rgbString but takes in a tuple instead
def rgbString(color):
        # Don't worry about the :02x part, but for the curious,
        # it says to use hex (base 16) with two digits.
        r, g, b = color
        return f'#{r:02x}{g:02x}{b:02x}'

def rgbScale(color, scale):
    r = min(roundHalfUp(color[0] * scale), 255)
    g = min(roundHalfUp(color[1] * scale), 255)
    b = min(roundHalfUp(color[2] * scale), 255)
    return (r, g, b)
    
#CITATION: roundHalfUp function taken from course notes at
#https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    # You do not need to understand how this function works.
    import decimal
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#CITATION: almostEqual function taken from course notes at
#https://www.cs.cmu.edu/~112/notes/notes-data-and-operations.html#FloatingPointApprox
def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

#Preserves the aspect ratio of the window when the user changes it
def fixAspectRatio(mode):
    width = mode.app.width
    height = int(width / mode.app.aspectRatio)
    mode.app.setSize(width, height)
