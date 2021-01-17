#This file contains the code that initializes app-wide variables and the game modes

from cmu_112_graphics_modified import *
from myClasses import *
from gameModes import *
import pygame



#Initializes the game controller channels
#Defaults to my Spektrum Dx6i but can be changed in controller calibration
def createChannels(app):
    app.channels = []
    throttle = ControllerChannel(app.inputBoxVars["throttleIndex"], "throttle")
    app.channels.append(throttle)
    yaw = ControllerChannel(app.inputBoxVars["yawIndex"], "yaw")
    yaw.isReversed = True
    app.channels.append(yaw)
    pitch = ControllerChannel(app.inputBoxVars["pitchIndex"], "pitch")
    app.channels.append(pitch)
    roll = ControllerChannel(app.inputBoxVars["rollIndex"], "roll")
    roll.isReversed = True
    app.channels.append(roll)
    app.channelAssignment = {}
    for channel in app.channels:
        app.channelAssignment[channel.name] = channel


#Creates the ModalApp and adds the main game modes to app
class TakeOff(ModalApp):
    def appStarted(app):
        #Initializes variables shared between modes
        app.initializeInputVariables()
        app.airplaneSize = 1

        #Creates the game modes
        app.gameMode = GameMode()
        app.calibrationMode = CalibrationMode()
        app.splashScreenMode = SplashScreenMode()
        app.trainingMode = TrainingMode()
        app.settingsMode = SettingsMode()
        app.helpMode = HelpMode()
        app.quitConfirmationMode = QuitConfirmationMode()

        #Begins Pygame
        pygame.init()

        #Creates the controller channels
        createChannels(app)

        #Sets the settings used by the game modes
        app.timerDelay = 1
        app.aspectRatio = 16/9
    
        #Launches the splashScreen mode
        app.previousMode = app.splashScreenMode
        app.setActiveMode(app.splashScreenMode)
       
     
    #Initializes the variables that the user can interact with
    def initializeInputVariables(app):
        app.inputBoxVars = {}
        app.inputBoxVars["deadzone"] = 1
        app.inputBoxVars["rollRate"] = 50
        app.inputBoxVars["pitchRate"] = 50
        app.inputBoxVars["yawRate"] = 50
        app.inputBoxVars["drag"] = 50
        app.inputBoxVars["throttleStrength"] = 30
        app.inputBoxVars["stallSpeed"] = 12
        app.inputBoxVars["turningDrag"] = 50
        app.inputBoxVars["liftCoeff"] = 50

        app.inputBoxVars["isDaytime"] = True
        app.inputBoxVars["cloudCount"] = 10
        app.inputBoxVars["bushCount"] = 150
        app.inputBoxVars["treeCount"] = 500
        app.inputBoxVars["viewRange"] = 155
        app.inputBoxVars["grassSize"] = 30
        app.inputBoxVars["sunAngle"] = 45
        app.inputBoxVars["cameraAngle"] = 15
        app.inputBoxVars["followDistance"] = 5
        app.inputBoxVars["uptilt"] = 30
        app.inputBoxVars["useShapely"] = True
        app.inputBoxVars["fullSorting"] = False

        app.inputBoxVars["throttleIndex"] = 1
        app.inputBoxVars["yawIndex"] = 0
        app.inputBoxVars["pitchIndex"] = 3
        app.inputBoxVars["rollIndex"] = 2

        app.inputBoxVars["displayData"] = True
        app.inputBoxVars["altitudeReading"] = True
        app.inputBoxVars["attitudeReading"] = True
        app.inputBoxVars["velocityReading"] = True
        app.inputBoxVars["distanceReading"] = True
        app.inputBoxVars["framerateReading"] = True
        app.inputBoxVars["binoculars"] = True

        app.inputBoxVars["aircraftNumber"] = 4


#Runs the game
TakeOff(width=1200, height=675)


