#This file stores the data needed by each training level, such as the functions
#timerFired calls to perform the training


from myClasses import *
from renderingFunctions import *
import time
from vectors import *
import extraneous

#Initializes the names of each training mode, their respective function names,
#and the color of their button
def createTrainingLevels(mode):
    easyColor = (0, 255, 0)
    mediumColor = (255, 255, 0)
    hardColor = (255, 0, 0)
    mode.levelAssignment = {
    "rollTraining": [startRollTraining, rollTraining, "Learn to Roll", easyColor],
    "pitchTraining": [startPitchTraining, pitchTraining, "Learn to Pitch", easyColor],
    "yawTraining": [startYawTraining, yawTraining, "Learn to Yaw", easyColor],
    "throttleTraining": [startThrottleTraining, throttleTraining, "Using the Throttle", easyColor],
    "turningTraining": [startTurningTraining, turningTraining, "Turning", easyColor],
    "takeOffTraining": [startTakeOffTraining, takeOffTraining, "Taking Off", mediumColor],
    "landingTraining": [startLandingTraining, landingTraining, "Landing", mediumColor],
    "airTurningTraining": [startAirTurningTraining, airTurningTraining, "Air Turning", mediumColor],
    "prolongedTraining": [startProlongedTraining, prolongedTraining, "Prolonged Flight", mediumColor],
    "landing2Training": [startLanding2Training, landing2Training, "Landing 2", mediumColor],
    "lowFlyingTraining": [startLowFlyingTraining, lowFlyingTraining, "Flying Low", hardColor],
    "invertedTraining": [startInvertedTraining, invertedTraining, "Inverted Flight", hardColor],
    "knifeTraining": [startKnifeTraining, knifeTraining, "Knife-Edging", hardColor],
    "verticalTraining": [startVerticalTraining, verticalTraining, "Vertical Flight", hardColor],
    "balloonTraining": [startBalloonTraining, balloonTraining, "Balloon Popping", hardColor],
    }

#Adds the training buttons to a list of buttons. Also creates the title and labels
def addTrainingButtons(mode):
    titleText = TextBox(((0, 2/16 * mode.height), (mode.width, 4/16 * mode.height)), "Training", CENTER, "black", "fixedsys")
    mode.textBoxes.append(titleText)
    cx = mode.width / 4
    width = mode.width / 5
    height = mode.height / 12 
    fontSize = int(1/3 * height)

    for col in getColumnData(mode):
        cy = mode.height / 3
        textBox = TextBox(((cx - width/2, cy - height/2), (cx + width/2, cy + height/2)), col[0], CENTER)
        mode.textBoxes.append(textBox)
        cy += height * 1.5
        for row in col[1:]:
            button = Button(((cx - width/2, cy - height/2), (cx + width/2, cy + height/2)), row[0], row[1], row[2], fontSize)
            mode.selectionButtons.append(button)
            cy += height * 1.25
        cx += mode.width / 4

#Generates a list of the data needed to create buttons
#Done in this manner to very easily add, remove, or alter training levels
def getColumnData(mode):
    easy = ["Easy",
    [mode.levelAssignment["rollTraining"][2], mode.levelAssignment["rollTraining"][3], mode.levelAssignment["rollTraining"][0]],
    [mode.levelAssignment["pitchTraining"][2], mode.levelAssignment["pitchTraining"][3], mode.levelAssignment["pitchTraining"][0]],
    [mode.levelAssignment["yawTraining"][2], mode.levelAssignment["yawTraining"][3], mode.levelAssignment["yawTraining"][0]],
    [mode.levelAssignment["throttleTraining"][2], mode.levelAssignment["throttleTraining"][3], mode.levelAssignment["throttleTraining"][0]],
    [mode.levelAssignment["turningTraining"][2], mode.levelAssignment["turningTraining"][3], mode.levelAssignment["turningTraining"][0]],
    ]
    medium = ["Medium",
    [mode.levelAssignment["takeOffTraining"][2], mode.levelAssignment["takeOffTraining"][3], mode.levelAssignment["takeOffTraining"][0]],
    [mode.levelAssignment["landingTraining"][2], mode.levelAssignment["landingTraining"][3], mode.levelAssignment["landingTraining"][0]],
    [mode.levelAssignment["airTurningTraining"][2], mode.levelAssignment["airTurningTraining"][3], mode.levelAssignment["airTurningTraining"][0]],
    [mode.levelAssignment["prolongedTraining"][2], mode.levelAssignment["prolongedTraining"][3], mode.levelAssignment["prolongedTraining"][0]],
    [mode.levelAssignment["landing2Training"][2], mode.levelAssignment["landing2Training"][3], mode.levelAssignment["landing2Training"][0]],
    ]
    hard = ["Hard",
    [mode.levelAssignment["lowFlyingTraining"][2], mode.levelAssignment["lowFlyingTraining"][3], mode.levelAssignment["lowFlyingTraining"][0]],
    [mode.levelAssignment["invertedTraining"][2], mode.levelAssignment["invertedTraining"][3], mode.levelAssignment["invertedTraining"][0]],
    [mode.levelAssignment["knifeTraining"][2], mode.levelAssignment["knifeTraining"][3], mode.levelAssignment["knifeTraining"][0]],
    [mode.levelAssignment["verticalTraining"][2], mode.levelAssignment["verticalTraining"][3], mode.levelAssignment["verticalTraining"][0]],
    [mode.levelAssignment["balloonTraining"][2], mode.levelAssignment["balloonTraining"][3], mode.levelAssignment["balloonTraining"][0]],
    ]
    return [easy, medium, hard]

#Recolors the training button once the training has been completed
def recolorButton(mode, name):
    for button in mode.selectionButtons:
        if button.text == mode.levelAssignment[name][2] and 255 in button.color:
            newColor = rgbScale(button.color, 1/2)
            button.color = newColor
            mode.levelAssignment[name][3] = newColor

#Returns the user to the training selection screen when a training is completed
def trainingCompleted(mode):
    mode.trainingCompletedTime = time.time()
    recolorButton(mode, mode.trainingSelection)
    mode.trainingSelection = None
    mode.trainingExplanationScreen = True
    mode.timerActive = False


#Sets the inputted controller channels to 0 so the user cannot user them
def disableChannels(mode, channels):
    if not isinstance(channels, list):
        channels = [channels]
    for channel in channels:
        mode.app.controllerInputs[mode.app.channelAssignment[channel].index] = 0




##################################
#Training Levels
##################################

#StartTraining functions are called by selecting the training via button or clicking to
#begin the training

#Training functions are called in timerFired and perform the unique functions
#needed by a training level


def startRollTraining(mode):
    mode.trainingSelection = "rollTraining"
    mode.followPlaneMode = False
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.center = (5, 5, 1)
    mode.trainingText = """\
\tRolling your plane means to rotate it wing-tip over wing-tip. To perform this, 
move your roll stick in either direction to roll the plane. This causes the ailerons on the 
wings to move, which results in the plane turning

\tTo complete this training, roll your plane upside-down.
Note that you have no control over the plane other than in the roll-axis
    """

def rollTraining(mode):
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.velocity = 20
    disableChannels(mode, ["pitch", "yaw", "throttle"])
    mode.airplane.performControllerInputs(mode)
    lookAtPlane(mode)
    if dotProduct(mode.airplane.d2, (0, 0, 1)) < -.95:
        trainingCompleted(mode)
        


def startPitchTraining(mode):
    mode.trainingSelection = "pitchTraining"
    mode.followPlaneMode = False
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.center = (5, 5, 1)
    mode.trainingText = """\
\tPitching your plane means to rotate it nose (front) over tail (back). To perform this, 
move your pitch stick in either direction to pitch the plane up or down. This causes the 
elevator on the tail to move, which results in the plane pitching up or down. On a typical
plane, pulling down on the pitch stick pitches the plane upwards.

\tTo complete this training, pitch the plane up until it is facing the sky.
Note that you have no control over the plane other than in the pitch-axis"""

def pitchTraining(mode):
    mode.airplane.velocity = 20
    disableChannels(mode, ["roll", "yaw", "throttle"])
    mode.airplane.performControllerInputs(mode)
    lookAtPlane(mode)
    if dotProduct(mode.airplane.d1, (0, 0, 1)) > .95:
        trainingCompleted(mode)


def startYawTraining(mode):
    mode.trainingSelection = "yawTraining"
    mode.followPlaneMode = False
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.center = (5, 5, 1)
    mode.trainingText = """\
\tYawing your plane means to spin it around an axis perpendicular to the wing surface. 
To perform this, move your yaw stick in either direction to yaw the plane left or right. This 
causes the rudder on the tail to move, which results in the plane yawing. Yawing can also be 
used to steer while on the ground

\tTo complete this training, yaw the plane up until it is facing backwards.
Note that you have no control over the plane other than in the yaw-axis"""

def yawTraining(mode):
    mode.airplane.velocity = 20
    disableChannels(mode, ["pitch", "roll", "throttle"])
    mode.airplane.performControllerInputs(mode)
    lookAtPlane(mode)
    if dotProduct(mode.airplane.d1, (-1, 0, 0)) > .95:
        trainingCompleted(mode)


def startThrottleTraining(mode):
    mode.trainingSelection = "throttleTraining"
    mode.followPlaneMode = False
    mode.airplane.d2 = (-.5 ** .5, 0, .5 ** .5)
    mode.airplane.d1 = (.5 ** .5, 0, .5 ** .5)
    mode.trainingText = """\
\tThe throttle controls how fast your plane will travel through the air To increase 
the throttle, push up on the throttle stick, and to lower it, pull down This causes 
the motor on the plane to speed up or slow down, which results in the plane either 
going slower or faster.

\tTo complete this training, raise your throttle all the way
Note that you have no control over the plane other than the throttle"""

def throttleTraining(mode):
    mode.airplane.velocity = 20
    mode.airplane.center = (5, 5, 1)
    disableChannels(mode, ["roll", "yaw", "pitch"])
    throttle = mode.app.channelAssignment["throttle"].getValue(mode.app) * 5
    mode.airplane.center = addVectorToPoint(mode.airplane.center, mode.airplane.d1, throttle)
    lookAtPlane(mode)
    if throttle >= 4.5:
        trainingCompleted(mode)



def startTurningTraining(mode):
    mode.trainingSelection = "turningTraining"
    mode.followPlaneMode = False
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.center = (5, 5, 1)
    mode.rollActive = True
    mode.trainingText = """\
\tA common technique of turning a plane is known as "bank and yank." This type of turn is 
performed by first rolling your plane to one side and then "yanking" back on the pitch stick 
to perform a bank turn. Once the plane has been turned, you can roll the plane back to being level

\tTo complete this training, first roll the plane to one side, and then pull back on the pitch stick
Note that you have no control over yaw or the throttle"""

def turningTraining(mode):
    mode.airplane.velocity = 20
    if mode.rollActive:
        disableChannels(mode, "pitch")
    else:
        disableChannels(mode, "roll")
    disableChannels(mode, ["yaw", "throttle"])
    mode.airplane.performControllerInputs(mode)
    lookAtPlane(mode)
    if abs(dotProduct(mode.airplane.d2, (0, -1, 0))) > .95:
        mode.rollActive = False
    if abs(mode.airplane.d1[1]) > .9:
        trainingCompleted(mode)


def startTakeOffTraining(mode):
    mode.trainingSelection = "takeOffTraining"
    mode.followPlaneMode = False
    mode.airplane.center = (-35, 5, 0)
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.velocity = 0
    mode.trainingText = """\
\tTo take off a plane, you need to increase the plane's speed in order to generate lift.
This is done by raising the throttle all the way. As the plane gains speed, gently pull 
down on the pitch stick to pitch the plane upwards. Once the plane starts coming off the 
ground, reduce how hard you are pulling back on the pitch stick to prevent the plane from 
going straight up

\tTo complete this training, take the plane off and raise it to an altitude of 15 meters
Note that in this training you have no roll or yaw control"""

def takeOffTraining(mode):
    disableChannels(mode, ["roll", "yaw"])
    mode.airplane.performControllerInputs(mode)
    mode.airplane.performPhysics(mode)
    lookAtPlane(mode)
    if mode.airplane.center[2] > 15:
        trainingCompleted(mode)

def startLandingTraining(mode):
    mode.trainingSelection = "landingTraining"
    mode.followPlaneMode = False
    mode.airplane.center = (-60, 5, 20)
    mode.airplane.d2 = (1/2, 0, 3**.5/2)
    mode.airplane.d1 = (3**.5 / 2, 0, -1/2)
    mode.airplane.velocity = 15
    mode.timeCompleted = None
    mode.trainingText = """\
\tTo land a plane, first lower the throttle. This allows the plane to slow down. Then,
use the pitch stick to make the plane nearly horizontal, with just a slight downwards angle. 
If the plane begins to force its nose down on its own, increase your throttle slightly and 
pull back on the pitch stick to keep it from nose-diving.

\tTo complete this training, land the plane on the ground gently
Note that you have no roll or yaw control in this training"""
def landingTraining(mode):
    disableChannels(mode, ["roll", "yaw"])
    mode.airplane.performControllerInputs(mode)
    mode.airplane.performPhysics(mode)
    lookAtPlane(mode)
    if mode.timeCompleted == None and mode.airplane.justTouchedGround and not mode.crashed:
        mode.timeCompleted = time.time()
    if mode.timeCompleted != None and time.time() - mode.timeCompleted > 2:
        trainingCompleted(mode)

def startAirTurningTraining(mode):
    mode.trainingSelection = "airTurningTraining"
    mode.followPlaneMode = False
    mode.airplane.center = (-40, 20, 15)
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.velocity = 15
    mode.trainingText = """\
\tTo turn the plane in the air, first roll the plane to one side, then pull back on
the pitch stick until the plane has turned the desired amount. You can then roll the 
plane back to being level.

\tTo complete the following training, turn the plane until it is pointing in the same 
direction as the blue line. Make sure to level the plane off when you finish your turn
Note that you have no yaw control in this training"""

def airTurningTraining(mode):
    disableChannels(mode, "yaw")
    mode.airplane.performControllerInputs(mode)
    mode.airplane.performPhysics(mode)
    lookAtPlane(mode)
    if dotProduct(mode.airplane.d1, (-1, 0, 0)) > .9 and dotProduct(mode.airplane.d2, (0, 0, 1)) > .9:
        trainingCompleted(mode)

def drawHeadingVector(mode, canvas):
    goalVector = (-1, 0, 0)
    planePos = getXandY(mode, mode.airplane.center)
    vectorTipPos = getXandY(mode, addVectorToPoint(mode.airplane.center, goalVector, 5))
    if vectorTipPos[0] != None:
        canvas.create_line(planePos, vectorTipPos, fill = "blue", width = 3)


def startLanding2Training(mode):
    mode.trainingSelection = "landing2Training"
    mode.followPlaneMode = False
    mode.airplane.center = (-30, 10, 10)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.pitch(-70)
    mode.airplane.roll(-40)
    mode.airplane.yaw(15)
    mode.airplane.velocity = 15
    mode.timeCompleted = None
    mode.trainingText = """\
\tIn this landing exercise, you have full control of the plane. Use your roll stick to
first level off the plane and then use your pitch and throttle to gently land the plane
Be careful to not stall the plane by lowering its airspeed too much

To complete this training, successfully land the plane"""
def landing2Training(mode):
    mode.airplane.performControllerInputs(mode)
    mode.airplane.performPhysics(mode)
    lookAtPlane(mode)
    if mode.timeCompleted == None and mode.airplane.justTouchedGround and not mode.crashed:
        mode.timeCompleted = time.time()
    if mode.timeCompleted != None and time.time() - mode.timeCompleted > 2:
        trainingCompleted(mode)


def startProlongedTraining(mode):
    mode.trainingSelection = "prolongedTraining"
    mode.followPlaneMode = False
    mode.airplane.center = (-20, 10, 0)
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.velocity = 0
    mode.timerActive = True
    mode.timerEnd = time.time() + 20
    mode.trainingText = """\
\tIn this training, your goal is to keep the plane in the air for an extended period 
of time. This can be done by simply taking the plane off and using pitch control to keep
the plane off the ground. For an added challenge, you can try to turn the plane while in
the air to keep it near you

\tTo complete the following training, keep the plane in the air for 20 seconds.
The timer is displayed at the top of the screen"""

def prolongedTraining(mode):
    mode.airplane.performControllerInputs(mode)
    mode.airplane.performPhysics(mode)
    lookAtPlane(mode)
    if mode.airplane.justTouchedGround:
        mode.timerEnd = time.time() + 20
    if time.time() > mode.timerEnd:
        trainingCompleted(mode)

def startInvertedTraining(mode):
    mode.trainingSelection = "invertedTraining"
    mode.followPlaneMode = False
    mode.airplane.center = (-20, 10, 0)
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.velocity = 0
    mode.timerActive = True
    mode.timerEnd = time.time() + 10
    mode.trainingText = """\
\tInverted flying means to fly the plane with the top of the plane facing the ground.
To begin flying inverted, use your roll stick to roll the plane upside-down. Once you have 
rolled the plane upside-down, your pitch and yaw controls become inverted. To keep the 
plane from crashing, you will need to push up slightly on the pitch stick instead of pulling 
down. Note that roll controls do not get reverse.

To complete this training, take off the plane and fly it inverted for 10 seconds"""

def invertedTraining(mode):
    mode.airplane.performControllerInputs(mode)
    mode.airplane.performPhysics(mode)
    lookAtPlane(mode)
    if dotProduct(mode.airplane.d2, (0, 0, 1)) > 0:
        mode.timerEnd = time.time() + 10
    if time.time() > mode.timerEnd:
        trainingCompleted(mode)

def startKnifeTraining(mode):
    mode.trainingSelection = "knifeTraining"
    mode.followPlaneMode = False
    mode.airplane.center = (-20, 10, 0)
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.velocity = 0
    mode.timerActive = True
    mode.timerEnd = time.time() + 10
    mode.trainingText = """\
\tKnife-edging is when you fly the plane with direction of the wingspan perpendicular
to the ground. To begin knife-edging, roll the plane 90 degrees to one side. To control
the altitude of the plane while knife-edging, you should use the yaw stick. To turn while
knife-edging, you can use the pitch stick.

\tTo complete this training, fly the plane in the knife-edge position for 10 seconds while
also keeping the plane within 10 meters of the ground"""

def knifeTraining(mode):
    mode.airplane.performControllerInputs(mode)
    mode.airplane.performPhysics(mode)
    lookAtPlane(mode)
    if magnitude(crossProduct(mode.airplane.d2, (0, 0, 1))) < .75 or mode.airplane.center[2] > 10:
        mode.timerEnd = time.time() + 10
    if time.time() > mode.timerEnd:
        trainingCompleted(mode)

def startLowFlyingTraining(mode):
    mode.trainingSelection = "lowFlyingTraining"
    mode.followPlaneMode = False
    mode.airplane.center = (-20, 10, 0)
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.velocity = 0
    mode.timerActive = True
    mode.timerEnd = time.time() + 15
    mode.trainingText = """\
This training is designed to test your control of the airplane.

\tTo complete this training, fly the plane within 5 meters of the ground for 15 seconds. 
For an added challenge, try to keep the plane close to you by performing bank-and-yank turns.

Note that it may be beneficial to not raise your throttle all the way for this training"""

def lowFlyingTraining(mode):
    mode.airplane.performControllerInputs(mode)
    mode.airplane.performPhysics(mode)
    lookAtPlane(mode)
    if mode.airplane.center[2] > 5 or mode.airplane.justTouchedGround:
        mode.timerEnd = time.time() + 15
    if time.time() > mode.timerEnd:
        trainingCompleted(mode)

def startVerticalTraining(mode):
    mode.trainingSelection = "verticalTraining"
    mode.followPlaneMode = False
    mode.airplane.center = (-20, 10, 0)
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.velocity = 0
    mode.timerActive = True
    mode.timerEnd = time.time() + 10
    mode.trainingText = """\
\tSome RC airplanes have enough power to climb completely vertically. In order to do this, 
first take the plane off and gain some speed. Then, pull back on the pitch stick until the plane 
is facing straight up. Use your pitch, yaw, and roll controls to counteract the plane trying to 
point its nose downwards. 

\tTo complete this training, take off the plane and then keep it facing straight up for 10 seconds. 
If this is too difficult, you can practice by increasing the throttle strength in settings"""

def verticalTraining(mode):
    mode.airplane.performControllerInputs(mode)
    mode.airplane.performPhysics(mode)
    lookAtPlane(mode)
    if dotProduct(mode.airplane.d1, (0, 0, 1)) < .8:
        mode.timerEnd = time.time() + 10
    if time.time() > mode.timerEnd:
        trainingCompleted(mode)

def startBalloonTraining(mode):
    mode.trainingSelection = "balloonTraining"
    mode.followPlaneMode = True
    mode.airplane.center = (-20, 10, 0)
    mode.airplane.d2 = (0, 0, 1)
    mode.airplane.d1 = (1, 0, 0)
    mode.airplane.velocity = 0
    mode.balloons = [Balloon(mode) for i in range(20)]
    mode.trainingText = """\
\tIn this training, your goal is to pop all the balloons by flying the plane into them.
Some of the balloons are close to the ground, so be careful. All of the balloons spawn 
close together, so from any one balloon you should be able to see the rest. If not, you 
can increase your view distance in settings

To complete this training, pop all 20 balloons without crashing"""

def balloonTraining(mode):
    mode.airplane.performControllerInputs(mode)
    mode.airplane.performPhysics(mode)
    Balloon.popBalloons(mode, mode.balloons)
    lookAtPlane(mode)
    if len(mode.balloons) == 0:
        trainingCompleted(mode)
