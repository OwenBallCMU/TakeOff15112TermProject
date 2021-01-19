#This file contains the game modes used in this project

from cmu_112_graphics_modified import *
from extraneous import *
from myClasses import *
from vectors import *
from renderingFunctions import *
from airplaneData import *
from trainingFunctions import *
import math
import random
import time
import pygame
import webbrowser


#Initializes the game. Used by the Freeflight Mode (GameMode) and TrainingMode
def initializeGame(mode):
    sunAngle = mode.app.inputBoxVars["sunAngle"]
    sunDist = 50000
    mode.sunPos = (sunDist * math.cos(sunAngle * math.pi / 180), 
                   sunDist * math.cos(sunAngle * math.pi / 180), 
                   sunDist * math.sin(sunAngle * math.pi / 180))
    mode.observer = [0,0,2]
    mode.viewDirection = [(1, 0, 0), (0, 0, 1), (0, 1, 0)]
    mode.prev = time.time()
    mode.framerate = 30
    mode.clouds = [Cloud() for i in range(mode.app.inputBoxVars["cloudCount"])]
    mode.bushes = [Bush(mode) for i in range(mode.app.inputBoxVars["bushCount"])]
    mode.trees = [Tree(mode) for i in range(mode.app.inputBoxVars["treeCount"])]
    mode.runway = Runway()
    mode.crashed = False
    mode.followPlaneMode = False
    createGround(mode)
    lookAtPlane(mode)
    if mode.app.inputBoxVars["binoculars"]:
        getBinocularWidth(mode)

#Calculates the framerate of the game
def updateFramerate(mode):
    elapsedTime = time.time() - mode.prev
    if elapsedTime != 0:
        actualFramerate = 1 / elapsedTime
    else:
        actualFramerate = mode.framerate
    mode.prev = time.time()
    #Uses a weighted moving average to filter the framerate data and produce
    #a smoother experience
    #Math for exponential moving average based off my 18100 class
    mode.framerate = .75 * mode.framerate + .25 * actualFramerate





#Freeflight Game Mode
class GameMode(Mode):
    #Initialize variables used in this game mode
    def appStarted(mode):
        mode.fov = 90 * math.pi / 180
        mode.rounding = 9
        mode.gravity = 9.81
        #Determines the corners used to generate each of the 6 faces of an object
        mode.faceSetups = [[1, 2, 3, 4], [1, 4, 6, 5], [1, 2, 8, 5], [2, 3, 7, 8], [3, 4, 6, 7], [5, 6, 7, 8]]
        mode.modeActivated()

    #Initializes variables when the mode switches back to GameMode
    def modeActivated(mode):
        initializeGame(mode)
        mode.createButtons()
        mode.app.airplane.reset(mode)
        mode.toolBox = ToolBox(mode)

    #Resizes buttons and graphics when window size changes
    def sizeChanged(mode):
        fixAspectRatio(mode)
        mode.createButtons()
        mode.toolBox = ToolBox(mode)

    #Creeates the buttons at the top of the screen
    def createButtons(mode):
        mode.buttons = []
        width = mode.width / 10
        height = width / 3
        fontSize = int(2/5 * height)
        mode.buttons.append(Button(((0, 0), (width, height)), 
                            "Settings", "white", mode.gotoSettings, fontSize))
        mode.buttons.append(Button(((width, 0), (2 * width, height)), 
                            "Controller", "white", mode.gotoControllerCalibration, fontSize))
        mode.buttons.append(Button(((2 * width, 0), (3 * width, height)), 
                            "Training", "white", mode.gotoTraining, fontSize))
        mode.buttons.append(Button(((3 * width, 0), (4 * width, height)), 
                            "Aircraft", "white", mode.gotoSelection, fontSize))
        mode.buttons.append(Button(((4 * width, 0), (5 * width, height)), 
                            "Help", "white", mode.gotoHelp, fontSize))
        mode.buttons.append(Button(((5 * width, 0), (6 * width, height)), 
                            "Quit", "white", mode.quitApp, fontSize))
    
    #Switches the game mode to SettingsMode
    def gotoSettings(mode, _):
        mode.app.previousMode = mode.app.gameMode
        mode.app.setActiveMode(mode.app.settingsMode)
    
    #Switches the game mode to CalibrationMode
    def gotoControllerCalibration(mode, _):
        mode.app.previousMode = mode.app.gameMode
        mode.app.setActiveMode(mode.app.calibrationMode)

    #Switches the game mode to TrainingMode
    def gotoTraining(mode, _):
        mode.app.setActiveMode(mode.app.trainingMode)

    #Switches the game mode to AirplaneSelectionMode
    def gotoSelection(mode, _):
        mode.app.previousMode = mode.app.gameMode
        mode.app.setActiveMode(mode.app.planeSelectionMode)
    
    #Switches the game mode to HelpMode
    def gotoHelp(mode, _):
        mode.app.previousMode = mode.app.gameMode
        mode.app.setActiveMode(mode.app.helpMode)
    
    #Switches the game mode to QuitConfirmationMode
    def quitApp(mode, _):
        mode.app.previousMode = mode.app.gameMode
        mode.app.setActiveMode(mode.app.quitConfirmationMode)

    #Performs game physics and reads controller inputs
    def timerFired(mode):
        if mode.crashed:
            return
        updateFramerate(mode)
       
        #pump pygame to update controller inputs
        pygame.event.pump()
        mode.app.controllerInputs = getControllerInputs(mode.app)
        mode.app.airplane.performControllerInputs(mode)

        mode.app.airplane.performPhysics(mode)
        Bush.touchingABush(mode.bushes, mode.app.airplane.center, mode)
        Tree.isTreeTouchingPlane(mode.trees, mode)
        
        
        
        #Follow the plane if in followPlaneMode
        if mode.followPlaneMode: 
            if type(mode.app.airplane) == Airplane:
                followPlane(mode)
                lookAtPlane(mode)
            else:
                setFPVCamera(mode)
        else: 
            gotoOrigin(mode)
            lookAtPlane(mode)
        

        

        #Updates binocular width if it is activated
        if mode.app.inputBoxVars["binoculars"] and not mode.followPlaneMode:
            getBinocularWidth(mode)
        mode.toolBox.updateReadouts(mode)

        if distance(mode.app.airplane.center, (0, 0, 0)) >= 1750:
            mode.app.airplane.reset(mode)

    #Updates the game based on user key input
    def keyPressed(mode, event):
        if event.key == "c":
            mode.app.setActiveMode(mode.app.calibrationMode)
        elif event.key == "r":
            mode.app.airplane.reset(mode)
        elif event.key == "Space":
            mode.followPlaneMode = not mode.followPlaneMode

    #Checks for button presses when the mouse is clicked
    def mousePressed(mode, event):
        Button.checkAll(mode, event.x, event.y, mode.buttons)


    def displayWarningMessage(mode, canvas):
        font = f"Arial {int(mode.width/24)}"
        canvas.create_text(mode.width/2, mode.height/4, text = "Too Far! Turn Back Now", fill = "red", font = font)

    #Redraws the scene and all other features
    def redrawAll(mode, canvas):
        drawSky(mode, canvas)
        drawHorizon(mode, canvas)
        drawFloor(mode, canvas)
        if type(mode.app.airplane) == Airplane: mode.runway.draw(mode, canvas)
        drawSun(mode, canvas)
        Cloud.drawAllClouds(mode.clouds, mode, canvas)
        drawShadow(mode, canvas)
        Bush.drawAllShadows(mode.bushes, mode, canvas)
        Tree.drawAllShadows(mode.trees, mode, canvas)
        #Draws bushes that are farther away than the plane
        """
        #Bush.drawAll(mode.bushes, mode, canvas, False)
        #Tree.drawAll(mode.trees, mode, canvas, False)
        """
        inFrontObjects, inBackObjects = getTreesAndBushesInOrder(mode, mode.trees + mode.bushes)

        drawAllTreesAndBushes(inBackObjects, mode, canvas)
        if not mode.crashed:
            if mode.app.inputBoxVars["binoculars"] and not mode.followPlaneMode:
                drawBinocularBackground(mode, canvas)
            if type(mode.app.airplane) == Airplane or not mode.followPlaneMode:
                mode.app.airplane.draw(mode, canvas)

        #Draws bushes that are closer than the plane
        #Bush.drawAll(mode.bushes, mode, canvas, True)
        drawAllTreesAndBushes(inFrontObjects, mode, canvas)
        Button.drawAll(mode.buttons, canvas)
        mode.toolBox.draw(mode, canvas)
        if mode.crashed:
            displayCrashText(mode, canvas)
        if distance(mode.app.airplane.center, (0, 0, 0)) >= 1500:
            mode.displayWarningMessage(canvas)
        
            




#Training Game Mode
class TrainingMode(GameMode):

    #Initialized variables used throughout this game mode
    def appStarted(mode):
        mode.fov = 80 * math.pi / 180
        mode.rounding = 9
        mode.gravity = 9.81
        #Determines the corners used to generate each of the 6 faces of an object
        mode.faceSetups = [[1, 2, 3, 4], [1, 4, 6, 5], [1, 2, 8, 5], [2, 3, 7, 8], [3, 4, 6, 7], [5, 6, 7, 8]]
        mode.trainingSelection = None
        mode.trainingExplanationScreen = True
        mode.timerActive = False
        mode.trainingCompletedTime = time.time() - 10
        #Initialize more game variables and the buttons 
        createTrainingLevels(mode)
        mode.modeActivated()

    #Sets variables and creates buttons when mode is reactivated
    def modeActivated(mode):
        initializeGame(mode)
        mode.createButtons()
        mode.toolBox = ToolBox(mode)

    #Updates variables when screen size changes
    def sizeChanged(mode):
        fixAspectRatio(mode)
        mode.createButtons()
        mode.toolBox = ToolBox(mode)

    #creates the buttons to display on the screen
    def createButtons(mode):
        width = mode.width / 4
        height = mode.height / 12
        yPos = mode.height * 3/4
        mode.beginTrainingButton = Button(((mode.width/2 - width/2, yPos - height/2), (mode.width/2 + width/2, yPos + height/2)),
                                        "Begin Training", "lime", mode.beginTraining)
        width = mode.width / 10
        height = width / 3
        mode.backButton = Button(((0, 0),(width, height)), "Back", "red", mode.backButtonPressed)

        mode.selectionButtons = []
        mode.textBoxes = []
        width = mode.width / 10
        height = width / 3
        fontSize = int(2/5 * height)
        mode.selectionButtons.append(Button(((0, 0), (width, height)), 
                            "Settings", "white", mode.gotoSettings, fontSize))
        mode.selectionButtons.append(Button(((width, 0), (2 * width, height)), 
                            "Controller", "white", mode.gotoControllerCalibration, fontSize))
        mode.selectionButtons.append(Button(((2 * width, 0), (3 * width, height)), 
                            "Free Flight", "white", mode.gotoFreeFlight, fontSize))
        mode.selectionButtons.append(Button(((3 * width, 0), (4 * width, height)), 
                            "Help", "white", mode.gotoHelp, fontSize))
        mode.selectionButtons.append(Button(((4 * width, 0), (5 * width, height)), 
                            "Quit", "white", mode.quitApp, fontSize))
        addTrainingButtons(mode)

    #Switches the game mode to settingsMode
    def gotoSettings(mode, _):
        mode.app.previousMode = mode.app.trainingMode
        mode.app.setActiveMode(mode.app.settingsMode)
    
    #Switches the game mode to calibrationMode
    def gotoControllerCalibration(mode, _):
        mode.app.previousMode = mode.app.trainingMode
        mode.app.setActiveMode(mode.app.calibrationMode)

    #Switches the game mode to gameMode
    def gotoFreeFlight(mode, _):
        mode.app.setActiveMode(mode.app.gameMode)
    
    #Switches the game mode to helpMode
    def gotoHelp(mode, _):
        mode.app.previousMode = mode.app.trainingMode
        mode.app.setActiveMode(mode.app.helpMode)
    
    #Switches the game mode to quitConfirmationMode
    def quitApp(mode, _):
        mode.app.previousMode = mode.app.gameMode
        mode.app.setActiveMode(mode.app.quitConfirmationMode)
       
    #Performs back button action when back button is pressed
    def backButtonPressed(mode, _):
        if mode.trainingSelection != None and mode.trainingExplanationScreen:
            mode.trainingSelection = None
        mode.trainingExplanationScreen = True
        mode.timerActive = False

    #Checks for button presses depending on the active screen
    def mousePressed(mode, event):
        if mode.trainingSelection == None:
            Button.checkAll(mode, event.x, event.y, mode.selectionButtons)
        elif mode.trainingExplanationScreen:
            mode.beginTrainingButton.isPressed(mode, event.x, event.y)
            mode.backButton.isPressed(mode, event.x, event.y)
        else:
            mode.backButton.isPressed(mode, event.x, event.y)

    #Checks for the user trying to reset the level
    def keyPressed(mode, event):
        if mode.trainingSelection != None and not mode.trainingExplanationScreen:
            if event.key == "r":
                mode.app.airplane.reset(mode)
                mode.levelAssignment[mode.trainingSelection][0](mode)

    #Updates game variables
    def timerFired(mode):
        if mode.crashed:
            return

        updateFramerate(mode)

        #Pumps pygame and gets new controller inputs
        pygame.event.pump()
        mode.app.controllerInputs = getControllerInputs(mode.app)
        if mode.trainingSelection != None and not mode.trainingExplanationScreen:
            #Runs if the user is performing a training level
            if mode.app.inputBoxVars["binoculars"] and not mode.followPlaneMode:
                getBinocularWidth(mode)
            mode.executeTrainingMode() 
            mode.toolBox.updateReadouts(mode)

            if mode.followPlaneMode:
                followPlane(mode)
            else:
                gotoOrigin(mode)

    #Begins the training when the "Begin" button is pressed
    def beginTraining(mode, _):
        mode.trainingExplanationScreen = False
        mode.crashed = False
        loaded = mode.trainingSelection
        mode.levelAssignment[loaded][0](mode)

    #Calls the proper training function so the plane performs the proper actions
    def executeTrainingMode(mode):
        loaded = mode.trainingSelection
        mode.levelAssignment[loaded][1](mode)

    #Draws the screen
    def redrawAll(mode, canvas):
        #Training selection screen
        if mode.trainingSelection == None:
            canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "lightblue")
            Button.drawAll(mode.selectionButtons, canvas)
            TextBox.drawAll(mode.textBoxes, canvas)
            if time.time() - mode.trainingCompletedTime < 3:
                height = mode.width/12
                font = f"Arial {int(height/2)}"
                canvas.create_rectangle(0, mode.height/2 - height/2, mode.width, 
                                        mode.height/2 + height/2, fill = "black")
                canvas.create_text(mode.width/2, mode.height/2, 
                                        text = "Training Completed!", 
                                        fill = "orange", font = font)
        #Training explanation Screen
        elif mode.trainingExplanationScreen:
            canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "lightblue")
            font = f"Arial {int(mode.width / 64)}"
            canvas.create_text(mode.width/2, mode.height/2, 
                                        text = mode.trainingText, font = font)
            mode.beginTrainingButton.draw(canvas)
            mode.backButton.draw(canvas)
        #In training level
        else:
            drawSky(mode, canvas)
            drawHorizon(mode, canvas)
            drawFloor(mode, canvas)
            drawSun(mode, canvas)
            Cloud.drawAllClouds(mode.clouds, mode, canvas)
            drawShadow(mode, canvas)
            #Draws the balloons behind the plane if in "ballonTraining"
            if mode.trainingSelection == "balloonTraining":
                Balloon.drawAllShadows(mode.balloons, mode, canvas)
                Balloon.drawAll(mode.balloons, mode, canvas, False)
            if not mode.crashed:
                #Draws the binocular view, the balloons in front of the plane,
                #and/or the timer
                if mode.app.inputBoxVars["binoculars"] and not mode.followPlaneMode:
                    drawBinocularBackground(mode, canvas)
                mode.app.airplane.draw(mode, canvas)
                if mode.trainingSelection == "balloonTraining":
                    Balloon.drawAll(mode.balloons, mode, canvas, True)
                if mode.timerActive:
                    drawTimer(mode, canvas)
            mode.backButton.draw(canvas)
            mode.toolBox.draw(mode, canvas)
            #Displays a target vector for the airTurningTraining mode
            if mode.trainingSelection == "airTurningTraining":
                drawHeadingVector(mode, canvas)
            if mode.crashed:
                displayCrashText(mode, canvas)







#Allows the user to calibrate their controller
class CalibrationMode(Mode):
     
    #Reinitializes buttons and interactive boxes when game mode restarted
    def modeActivated(mode):
        mode.createInputBoxes()
        mode.createSlidersAndButtons()

    #Reinitializes buttons and interactive boxes when window size is changed
    def sizeChanged(mode):
        fixAspectRatio(mode)
        mode.modeActivated(mode)

    #Creates the interactive boxes in the bottom right part of the screen
    def createInputBoxes(mode):
        mode.buttons = []
        mode.textBoxes = []
        mode.inputBoxes= []
        inputVars = ["deadzone", "rollRate", "pitchRate", "yawRate"]
        labels = ["Deadzone Percent:", "Roll Rate:", "Pitch Rate:", "Yaw Rate:"]
        width = mode.width / 8
        height = mode.height / 20
        xVal = mode.width * 7/16
        yVal = mode.height * 3/5
        for i in range(len(inputVars)):
            label = TextBox(((xVal, yVal), (xVal + 3 * width, yVal + height)), labels[i], anchor = W)
            inputBox = InputBox(mode, ((xVal + 2.5 * width, yVal), 
                                       (xVal + 3.5 * width, yVal + height)), 
                                       (200, 200, 200), inputVars[i], 0, 100, 2, int)
            mode.inputBoxes.append(inputBox)
            mode.textBoxes.append(label)
            yVal += 1.5 * height

    #Creates the joystick slider and the channel-specific buttons for each channel
    def createSlidersAndButtons(mode):
        xVal = mode.width / 8
        yVal = mode.height / 16
        height = mode.height / 20
        width = mode.width / 4
        buttonWidth = width / 2
        mode.createButtonLabels(xVal, yVal, width, height, buttonWidth)
        yVal += 1.5 * height
        for channel in mode.app.channels:
            label = TextBox(((xVal, yVal), (xVal + 2 * width, yVal + height)), 
                            channel.name.capitalize(), anchor = W)
            mode.textBoxes.append(label)
        
            sliderX = xVal + .85 * width
            #creates the channel slider
            channel.initializeSlider(sliderX, yVal, width, height)

            #creates the "Reverse" button and channel reassignment button
            buttonX = sliderX + 1.1 * width
            reverseButton = Button(((buttonX, yVal), (buttonX + buttonWidth, yVal + height)), 
                                    "Reverse", "red", channel.reverseChannel)
            mode.buttons.append(reverseButton)
            buttonX = buttonX + 1.1 * buttonWidth
            reassignInput = InputBox(mode, ((buttonX, yVal), 
                                        (buttonX + buttonWidth, yVal + height)), 
                            (100, 100, 235), channel.name + "Index", 0, 
                                    len(mode.app.controllerInputs) - 1, 2, int)
            mode.inputBoxes.append(reassignInput)
            yVal += 1.5 * height

        #Creates the "Reset Calibration" button and the "Back" button
        centerX = mode.width / 2
        resetCalibrationButton = Button(((centerX - width, yVal), 
                                (centerX + width, yVal + height)), 
                                "Reset Calibration", "yellow", ControllerChannel.resetAll)
        mode.buttons.append(resetCalibrationButton)
        width = mode.width / 10
        height = width / 3
        backButton = Button(((0, 0),(width, height)), "Back", "red", mode.backButtonPressed)
        mode.buttons.append(backButton)
        width = height = mode.width / 30
        infoButton = Button(((mode.width - 2 * width, height),
                             (mode.width - width, 2 * height)), "?", "red", mode.launchWebpage)
        mode.buttons.append(infoButton)

    #Creates the labels for the buttons along the top of the screen
    def createButtonLabels(mode, xVal, yVal, width, height, buttonWidth):
        xVal += .85 * width
        joystickLabel = TextBox(((xVal, yVal), (xVal + width, yVal + height)), 
                            "Joystick Position", anchor = CENTER)
        xVal += 1.1 * width
        reverseLabel = TextBox(((xVal, yVal), (xVal + buttonWidth, yVal + height)), 
                            "Reverse", anchor = CENTER)
        xVal += 1.1 * buttonWidth
        reassignLabel = TextBox(((xVal, yVal), (xVal + buttonWidth, yVal + height)), 
                            "Reassign", anchor = CENTER)
        mode.textBoxes.extend([joystickLabel, reverseLabel, reassignLabel])
        
    #Checks for button and inputBox interaction when the mouse is clicked
    def mousePressed(mode, event):
        Button.checkAll(mode, event.x, event.y, mode.buttons)
        InputBox.checkAll(mode, event.x, event.y, mode.inputBoxes)

    #Perform the back button action when pressed
    def backButtonPressed(mode, _):
        mode.app.setActiveMode(mode.app.previousMode)


    #CITATION: Explanation of how to open a browser tab from:
    #https://docs.python.org/3/library/webbrowser.html
    #Launches a helpful website in the user's browswer
    def launchWebpage(mode, _):
        webbrowser.open("https://www.getfpv.com/learn/fpv-essentials/choosing-right-transmitter-mode/", new = 2)

    #Reads channel inputs and calibrates the channels repeatedly
    def timerFired(mode):
        pygame.event.pump()
        mode.app.controllerInputs = getControllerInputs(mode.app)
        mode.reassignChannels()
        ControllerChannel.updateDeadzone(mode.app.inputBoxVars["deadzone"])
        ControllerChannel.calibrateAll(mode.app)

    #Sends any keypresses to the InputBox class
    def keyPressed(mode, event):
        InputBox.keyIsPressed(mode, event.key)  

    #Sets the controller channels to the values inside the inputBoxes
    def reassignChannels(mode):
        for channel in mode.app.channelAssignment.values():
            channel.index = mode.app.inputBoxVars[channel.name + "Index"] 

    #Displays one controller channel input
    def displayRawChannelData(mode, canvas, inputs, i, x, y, font):
        data = inputs[i]
        text = f"Channel {i}: {round(data, 3)}"
        canvas.create_text(x, y, text = text, font = font, anchor = W)

    #Displays all the channels of the input controller
    def displayChannelData(mode, canvas):
        ControllerChannel.drawAllSliders(mode, canvas)
        rawDataY = 17/32 * mode.height
        rawDataX = mode.width / 8
        inputs = mode.app.controllerInputs
        deltaY = .75 * mode.height / 2 / len(inputs)
        fontSize = .9 * deltaY
        font = f"Arial {int(fontSize)}"
        canvas.create_text(rawDataX, rawDataY, text = "Raw Controller Data:", anchor = W, font = font)
        rawDataY += 2 * deltaY
        for i in range(len(inputs)):
            mode.displayRawChannelData(canvas, inputs, i, rawDataX, rawDataY, font)
            rawDataY += deltaY

    #Draws all the buttons, input boxes, and labels
    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = rgbString((200, 255, 200)))
        Button.drawAll(mode.buttons, canvas)
        TextBox.drawAll(mode.textBoxes, canvas)
        mode.displayChannelData(canvas)
        InputBox.drawAll(mode.inputBoxes, canvas)






#Creates the settings game mode
class SettingsMode(Mode):

    #Initializes the input boxes and the back button
    def appStarted(mode):
        #Image downscaled by 25% from:
        #https://www.flaticon.com/free-icon/settings_126472
        mode.settingsIcon = mode.loadImage('media/settingsIcon.png')
        mode.modeActivated()

    #Reinitializes the input boxes and back button when window size is changed
    def sizeChanged(mode):
        fixAspectRatio(mode)
        mode.modeActivated()

    #Reinitializes the input boxes and the back button when mode switches back
    def modeActivated(mode):
        mode.createInputBoxes()
        mode.createBackButton()
        size = roundHalfUp(mode.width / 10)
        mode.settingsIconScaled = mode.settingsIcon.resize((size, size))
        
    #Creates the back button
    def createBackButton(mode):
        width = mode.width / 10
        height = width / 3
        mode.backButton = Button(((0, 0),(width, height)), "Back", "red", mode.backButtonPressed)

    #Create all the input boxes
    def createInputBoxes(mode):
        mode.textBoxes = []
        mode.checkBoxes = []
        mode.inputBoxes = []
        mainLabels = ["Physics", "Graphics", "Data Readouts"]
        columnData = mode.getSettingsData()
        titleText = TextBox(((0, 1/16 * mode.height), 
                             (mode.width, 3/16 * mode.height)), 
                             "Settings", CENTER, "black", "fixedsys")
        mode.textBoxes.append(titleText)
        width = mode.width / 16
        height = width / 3
        xVal = mode.width / 16
        color = (130, 190, 230)
        for i in range(len(mainLabels)):
            yVal = mode.height / 4
            textBox = TextBox(((xVal, yVal), 
                                    (xVal + 3.5 * width, yVal + 1.5 * height)), 
                                     mainLabels[i], CENTER)
            mode.textBoxes.append(textBox)
            column = columnData[i]
            yVal += 2.5 * height
            for inputBoxSetup in column:
                boxType, label, varName = inputBoxSetup[0], inputBoxSetup[1], inputBoxSetup[2]
                textBox = TextBox(((xVal, yVal), (xVal + 3 * width, yVal + height)), label, W)
                mode.textBoxes.append(textBox)
                #Initializes the box differently depending on what type of 
                #box it is
                if boxType == "inputBox":
                    if varName == "sunAngle": minVal = 20
                    else: minVal = 0
                    inputSize = inputBoxSetup[3]
                    inputBox = InputBox(mode, ((xVal + 2.5 * width, yVal), 
                                       (xVal + 3.5 * width, yVal + height)), 
                                        color, varName, minVal, int("9" * inputSize), 
                                                                 inputSize, int)
                    mode.inputBoxes.append(inputBox)
                if boxType == "checkBox":
                    checkBox = CheckBox(mode, (xVal + width * 3, yVal + height / 2), 
                                                            height, color, varName)
                    mode.inputBoxes.append(checkBox)
                yVal += 1.5 * height
            xVal += width * 5

    #Creates a list of all the settings options
    def getSettingsData(mode):

        graphicsData = [
        ["checkBox", "Daytime", "isDaytime"],
        ["inputBox", "Cloud Count", "cloudCount", 2],
        ["inputBox", "Bush Count", "bushCount", 4],
        ["inputBox", "Tree Count", "treeCount", 4],
        ["inputBox", "View Range", "viewRange", 3],
        ["inputBox", "Grass Size", "grassSize", 2],
        ["inputBox", "Sun Angle", "sunAngle", 2],
        ["checkBox", "Use Shapely", "useShapely"],
        ["checkBox", "Full Sorting", "fullSorting"],
        ]

        if type(mode.app.airplane) == Airplane:
            physicsData = [
            ["inputBox", "Drag", "drag", 2],
            ["inputBox", "Motor Power", "throttleStrength", 2],
            ["inputBox", "Stall Speed", "stallSpeed", 2],
            ["inputBox", "Turning Drag", "turningDrag", 2],
            ["inputBox", "Plane Lift", "liftCoeff", 2],
            ]

            graphicsData.extend([
            ["inputBox", "Camera Angle", "cameraAngle", 2],
            ["inputBox", "Camera Dist", "followDistance", 2],
            ])
        else:
            physicsData = [
            ["inputBox", "Drag", "drag", 2],
            ["inputBox", "Motor Power", "throttleStrength", 2],
            ]
            graphicsData.extend([
            ["inputBox", "Camera Uptilt", "uptilt", 2],
            ])

        toolsData = [
        ["checkBox", "Display Data", "displayData"],
        ["checkBox", "Velocity", "velocityReading"],
        ["checkBox", "Altitude", "altitudeReading"],
        ["checkBox", "Attitude", "attitudeReading"],
        ["checkBox", "Distance", "distanceReading"],
        ["checkBox", "Framerate", "framerateReading"],
        ["checkBox", "Binoculars", "binoculars"],
        ]
        return [physicsData, graphicsData, toolsData]

    #Checks for button presses and input box interaction
    def mousePressed(mode, event):
        mode.backButton.isPressed(mode, event.x, event.y)
        InputBox.checkAll(mode, event.x, event.y, mode.inputBoxes)
     
    #Necessary since I commented out the ability for mousePressed() and keyPressed()
    #to call redrawAll() in cmu_112_graphics
    def timerFired(mode):
        pass
    
    #Sends any key presses to the InputBox class 
    def keyPressed(mode, event):
        InputBox.keyIsPressed(mode, event.key)   

    #Performs the back button action when it is pressed
    def backButtonPressed(mode, _):
        mode.app.setActiveMode(mode.app.previousMode)

    def drawSettingsIcons(mode, canvas):
        canvas.create_image(3/4 * mode.width, 1/8 * mode.height, pilImage = mode.settingsIconScaled)
        canvas.create_image(1/4 * mode.width, 1/8 * mode.height, pilImage = mode.settingsIconScaled)
    #Draws all the input boxes, back button, and labels
    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "lightyellow1")
        mode.backButton.draw(canvas)
        TextBox.drawAll(mode.textBoxes, canvas)
        InputBox.drawAll(mode.inputBoxes, canvas)
        mode.drawSettingsIcons(canvas)
        




#Creates the Help game mode
class HelpMode(Mode):
    #Initializes the buttons when the game mode is started
    def appStarted(mode):
        mode.onSelectionScreen = True
        mode.modeActivated()

    #reinitializes the buttons when the window size changes
    def sizeChanged(mode):
        fixAspectRatio(mode)
        mode.modeActivated()

    #creates the buttons and title when the mode is activated
    def modeActivated(mode):
        mode.createButtons()
        mode.createTitle()

    #Creates the title for the Help mode main page
    def createTitle(mode):
        mode.titleText = TextBox(((0, 1/16 * mode.height), 
                                  (mode.width, 3/16 * mode.height)), 
                                  "Help", CENTER, "black", "fixedsys")

    #Creates the buttons for each of the help sections
    def createButtons(mode):
        mode.buttons = []
        mode.createBackButton()
        categories = [
        ["Free Flight", mode.freeFlightText],
        ["Training", mode.trainingText],
        ["Controller Setup", mode.controllerText],
        ["Settings", mode.settingsText]
        ]
        cx, cy = mode.width/2, mode.height/3
        width, height = mode.width/3, mode.height/8
        fontSize = int(height/3)
        for row in categories:
            button = Button(((cx - width/2, cy - height/2), 
                             (cx + width/2, cy + height/2)), row[0], 
                             "cyan", row[1], fontSize)
            mode.buttons.append(button)
            cy += height * 1.25
        cx += mode.width / 4

    #Creates the back button
    def createBackButton(mode):
        width = mode.width / 10
        height = width / 3
        mode.backButton = Button(((0, 0),(width, height)), "Back", "red", mode.backButtonPressed)

    #Performs the back button action in accordance with the current screen the user is on
    def backButtonPressed(mode, _):
        if mode.onSelectionScreen:
            mode.app.setActiveMode(mode.app.previousMode)
        else:
            mode.onSelectionScreen = True

    #Checks for button interaction in accordance with the screen the user is on
    def mousePressed(mode, event):
        mode.backButton.isPressed(mode, event.x, event.y)
        if mode.onSelectionScreen:
            Button.checkAll(mode, event.x, event.y, mode.buttons)

    #Necessary since I commented out the ability for mousePressed() and keyPressed()
    #to call redrawAll() in cmu_112_graphics
    def timerFired(mode):
        pass

    #CITATION:
    #Discovered you can rotate text using "angle =" from
    #https://stackoverflow.com/questions/42601143/is-it-possible-to-rotate-text-displayed-on-a-tkinter-canvas?noredirect=1&lq=1
    def drawQuestionMarks(mode, canvas):
        canvas.create_text(5/32 * mode.width, 1/4 * mode.height, text = "?", angle = 35, font = f"Arial {int(mode.width/6)} bold", fill = "maroon")
        canvas.create_text(27/32 * mode.width, 6/16 * mode.height, text = "?", angle = -42, font = f"Arial {int(mode.width/6)} bold", fill = "maroon")

    #Draws the buttons and text
    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = rgbString((240, 200, 255)))
        mode.backButton.draw(canvas)
        if mode.onSelectionScreen:
            mode.titleText.draw(canvas)
            mode.drawQuestionMarks(canvas)
            Button.drawAll(mode.buttons, canvas)
        else:
            #canvas.create_text(mode.width/8, mode.height/8, anchor = NW, text = mode.text, font = f"Arial {mode.fontsize}")
            canvas.create_text(mode.width/2, mode.height/2, text = mode.text, font = f"Arial {mode.fontsize}")

    #Initialize the text on each screen
    def freeFlightText(mode, _):
        mode.onSelectionScreen = False
        mode.fontsize = int(mode.width/60)
        mode.text = """\
This game mode allows you to fly the plane around an open world

Controls:
-Reset Plane: "r"
-Toggle Camera Mode: Space
-Plane Controls: Use controller

Instructions:
-Fly around the world and practice your skills without fear of crashing 
    a real plane
-Avoid striking the ground too hard or running into bushes
-Use the binocular view in the corner if the plane begins to get very small
-Have fun! You can even fly up to the clouds if you want"""

    def trainingText(mode, _):
        mode.onSelectionScreen = False
        mode.fontsize = int(mode.width/60)
        mode.text = """\
This game mode allows you to practice specific plane flying skills 

Controls:
-Reset Plane: "r"
-Plane Controls: Use controller
-Press the interactive buttons to choose your training
-Exit a training at any time by pressing "Back"

Instructions:
-Choose a skill that you want to practice on the selection screen
-Read the training prompt and click "Begin Training" to practice the skill
-Once you complete a training, you will automatically be sent back to the 
    selection screen"""

    def controllerText(mode, _):
        mode.onSelectionScreen = False
        mode.fontsize = int(mode.width/75)
        mode.text = """\
This mode allows you to customize your controller layout, calibrate your controller, and alter the 
sensitivity of the plane to controller inputs

Calibration: To calibrate your controller, simply hit "Reset Calibration" and then move your 
joysticks in complete circles

Reassigning Channels: Some controllers may not have the proper layout of joysticks. To assign a new 
controller channel to one of the 4 joysticks, move the joystick in the desired direction and view 
which "Raw Data" channel moved. You can then enter this value into the input box in the "Reassign" column

Reversing Channels: To reverse a channel, simply click the reverse button for the corresponding channel

Adjusting Deadzone: Some controllers not designed for RC flying may not perfectly center your 
joysticks when you release them. If you notice this, you can increase your deadzone, which is the 
range in which your joystick input will be set to zero. You can determine the right amount of deadzone 
for your controller by ensuring that your joysticks center themselves within the orange lines on 
the indicators

Pitch, Yaw, and Roll Rates: To alter the sensitivity of the plane to controller inputs, you can 
change these values

-Interact with number input boxes by clicking inside them and typing
    -Backspace, Enter, ".", and numbers are valid key inputs"""
        
    def settingsText(mode, _):
        mode.onSelectionScreen = False
        mode.fontsize = int(mode.width/85)
        mode.text = """\
Physics
-Drag: Changes the drag the plane experiences in the air. 0-99
-Motor Power: Changes how much acceleration the motor produces. 0-99
-Stall Speed: Sets the speed at which the plane begins to stall. 0-99
-Turning Drag: Sets the amount of drag caused by rapid turns. 0-99
-Plane Lift: Changes amount of lift produced by the plane. 0-99

Graphics
-Daytime: Determines if the time of day is day or night
-Cloud Count: Determines the number of clouds in the sky. 0-99
-Bush Count: Sets the number of bushes in the environment. 0-9999
-View Range: Sets the distance in meters that you can see objects at. 0-999
-Sun Angle: Determines the angle of the sun in the sky. 20-90
-Camera Angle: Determines the angle of the following camera above the plane. 0-90
-Camera Dist: Determines the approximate distance the camera follows the plane at. 0-99
-Use Shapely: Enables Shapely to perform the bulk of polygon overlap calculations
              Enable to increase performance

Data Readouts
-Display Data: Determines if any of the 4 below options are display on-screen
-Velocity: Displays the velocity on the screen if enabled
-Altitude: Displays the altitude on the screen if enabled
-Attitude: Displays the angle of the plane above horizontal if enabled
-Distance: Displays the distance of the plane from the origin if enabled
-Framerate: Displays the framerate on the screen if enabled
-Binoculars: Displays a zoomed in view of the airplane if enabled

-Interact with number input boxes by clicking inside them and typing
    -Backspace, Enter, ".", and numbers are valid key inputs"""
    

#Creates the quit confirmation screen
class QuitConfirmationMode(Mode):

    #Initializes variables when the mode is activated
    def modeActivated(mode):
        mode.stage = 1
        mode.quitTime = None
        mode.createButtons()
        mode.createMessage()

    #reinitializes variables when the window size changes
    def sizeChanged(mode):
        fixAspectRatio(mode)
        mode.modeActivated()

    #Creates the "Yes" and "No" buttons
    def createButtons(mode):
        mode.buttons = []
        width = mode.width/8
        height = width/3
        cx, cy = mode.width/2, 9/16 * mode.height
        fontSize = int(height/2)
        yesButton = Button(((cx - 1.25 * width, cy - height/2), 
                            (cx - .25 * width, cy + height/2)), "Yes", 
                            "black", mode.exit, fontSize, "white")
        noButton = Button(((cx + .25 * width, cy - height/2), 
                           (cx + 1.25 * width, cy + height/2)), "No", 
                           "black", mode.resume, fontSize, "white")
        mode.buttons.extend([yesButton, noButton])
    
    #Creates the message to display to the user
    def createMessage(mode):
        mode.messageHeight, mode.messageY = mode.height/8, -mode.width/4
        mode.messageSpeed, mode.maxY = 0, 6/16 * mode.height
        mode.message = TextBox(((0, mode.messageY), 
                                (mode.width, mode.messageY + mode.messageHeight)), 
                                "Are you sure?", CENTER)
    
    #Updates the position of the message on the screen
    def updateMessagePosition(mode):
        mode.messageSpeed += mode.width/2000
        mode.messageY += mode.messageSpeed
        if mode.messageY > mode.maxY:
            mode.messageY = mode.maxY
            mode.messageSpeed *= -.8
        mode.message.y0, mode.message.y1 = mode.messageY, mode.messageY + mode.messageHeight

    #Updates the message text if the user presses "Yes"
    def updateMessageText(mode):
        if mode.stage == 2:
            mode.message.text = "Oh come on, really?"
        if mode.stage == 3:
            mode.message.text = "Last chance."

    #Updates the message text or triggers program termination depending on the value
    #of "mode.stage"
    def exit(mode, _):
        if mode.stage < 3:
            mode.stage += 1
            mode.updateMessageText()
        else:
            mode.quitTime = time.time() + 2

    #Goes back to the previous mode if "No" is pressed
    def resume(mode, _):
        mode.app.setActiveMode(mode.app.previousMode)

    #Checks for button interaction when the mouse is pressed
    def mousePressed(mode, event):
        Button.checkAll(mode, event.x, event.y, mode.buttons)

    #Updates message position and checks if the program should terminate
    def timerFired(mode):
        mode.updateMessagePosition()
        if mode.quitTime != None and time.time() > mode.quitTime:
            mode.app.quit()

    #Draws the button and the message, or draws "Bye" until the program terminates
    def redrawAll(mode, canvas):
        if mode.quitTime == None:
            Button.drawAll(mode.buttons, canvas)
            mode.message.draw(canvas)
        else:
            canvas.create_text(mode.width/2, mode.height/2, text = "Bye :(", 
                               font = f"Arial {int(mode.width/24)}")
    

#Creates the quit confirmation screen
class PlaneSelectionMode(Mode):

    #Initializes variables when the mode is activated
    def modeActivated(mode):
        mode.binocularState = mode.app.inputBoxVars["binoculars"]
        mode.faceSortingState = mode.app.inputBoxVars["fullSorting"]
        mode.timeState = mode.app.inputBoxVars["isDaytime"]
        mode.app.inputBoxVars["binoculars"] = False
        mode.app.inputBoxVars["fullSorting"] = True
        mode.app.inputBoxVars["isDaytime"] = True
        mode.initialize()

    def initialize(mode):
        #CITATION: Runway image is a screenshot from "RealFlight 8"
        #https://www.spektrumrc.com/Products/Default.aspx?ProdID=GPMZ4558
        mode.background = mode.loadImage('media/runway.png')
        mode.scaleBackground()
        mode.planeAngle = 0
        mode.rotationRate = 1
        mode.createButtons()
        mode.observer = (0, 0, 1.5)
        mode.framerate = 30
        mode.prev = time.time()
        mode.fov = 90 * math.pi / 180
        mode.rounding = 9
        #Determines the corners used to generate each of the 6 faces of an object
        mode.faceSetups = [[1, 2, 3, 4], [1, 4, 6, 5], [1, 2, 8, 5], [2, 3, 7, 8], [3, 4, 6, 7], [5, 6, 7, 8]]  
        mode.activateNewPlane()
        mode.viewDirection = [1, 0, 0]
        mode.followPlaneMode = False
        lookAtPlane(mode)

    #Scales the background to fit the current window size
    def scaleBackground(mode):
            scale = mode.width / mode.background.width
            mode.scaledBackground = mode.background.resize((round(mode.background.width * scale), 
                                                            round(mode.background.height * scale)))


    #reinitializes variables when the window size changes
    def sizeChanged(mode):
        fixAspectRatio(mode)
        mode.initialize()

    def createButtons(mode):
        data = [
        ("Top-Mounted Wing", mode.switchToTopMounted),
        ("Bottom-Mounted 1", mode.switchToBottomMounted1),
        ("Bottom-Mounted 2", mode.switchToBottomMounted2),
        ("Biplane", mode.switchToBiplane),
        ("Quadcopter", mode.switchToQuad),
        ]
        mode.buttons = []
        mode.inputBoxes = []
        mode.textBoxes = []
        mode.buttons.append(mode.createBackButton())
        width = mode.width/7
        height = width/3
        cx, cy = mode.width/6, 2/16 * mode.height
        dx = mode.width*2/3 / (len(data) - 1)
        fontSize = int(height/4.5)
        for text, function in data:
            button = Button(((cx - width/2, cy - height/2), (cx + width/2, cy + height/2)), text, "red", function, fontSize)
            mode.buttons.append(button)
            cx += dx

        suffixes = ["Red", "Green", "Blue"]
        width = mode.width/10
        height = width/3
        dx = mode.width/6
        startX = mode.width/2 - dx * 2
        cy = mode.height * 12/16
        color = (190, 190, 190)
        colorLabels = ["Red", "Green", "Blue"]
        for i in range(3):
            cx = startX + dx * (1 + i)
            textBox = TextBox(((cx - width/2, cy - height/2), (cx + width/2, cy + height/2)), colorLabels[i], CENTER)
            mode.textBoxes.append(textBox)


        for prefix in ["body", "wing"]:
            cy += height * 1.5
            for i in range(4):
                x = startX + dx * i
                if i == 0:
                    if prefix == "body":
                        name = "Body Color:"
                    else:
                        name = "Wing Color:"
                    textBox = TextBox(((x - width/2, cy - height/2), (x + width, cy + height/2)), name, E)
                    mode.textBoxes.append(textBox)
                    
                else: 
                    inputBox = InputBox(mode, ((x - width/2, cy - height/2), (x + width/2, cy + height/2)), color, prefix + suffixes[i-1], 0, 255, 3, int)
                    mode.inputBoxes.append(inputBox)

        cx = startX + 4*dx
        cy -= .75 * height
        button = Button(((cx - width/2, cy - height/2), (cx + width/2, cy + height/2)), "Update", (230, 0, 230), mode.update)
        mode.buttons.append(button)
        

    def switchToTopMounted(mode, _):
        mode.app.inputBoxVars["aircraftNumber"] = 1
        mode.activateNewPlane()

    def switchToBottomMounted2(mode, _):
        mode.app.inputBoxVars["aircraftNumber"] = 2
        mode.activateNewPlane()

    def switchToBottomMounted1(mode, _):
        mode.app.inputBoxVars["aircraftNumber"] = 3
        mode.activateNewPlane()

    def switchToBiplane(mode, _):
        mode.app.inputBoxVars["aircraftNumber"] = 4
        mode.activateNewPlane()

    def switchToQuad(mode, _):
        mode.app.inputBoxVars["aircraftNumber"] = 5
        mode.activateNewPlane()

    def activateNewPlane(mode):
        mode.app.airplane = createAirplane(mode)
        mode.app.airplane.center = (4, 0, 0)
        mode.app.airplane.d1 = (math.cos(mode.planeAngle), math.sin(mode.planeAngle), 0)

    def update(mode, _):
        mode.activateNewPlane()

   #Creates the back button
    def createBackButton(mode):
        width = mode.width / 10
        height = width / 3
        return Button(((0, 0),(width, height)), "Back", "red", mode.backButtonPressed)

    #Performs the back button action in accordance with the current screen the user is on
    def backButtonPressed(mode, _):
        mode.app.inputBoxVars["binoculars"] = mode.binocularState
        mode.app.inputBoxVars["fullSorting"] = mode.faceSortingState
        mode.app.inputBoxVars["isDaytime"] = mode.timeState
        mode.app.setActiveMode(mode.app.previousMode)
        

    def keyPressed(mode, event):
        InputBox.keyIsPressed(mode, event.key)  

    #Checks for button interaction when the mouse is pressed
    def mousePressed(mode, event):
        Button.checkAll(mode, event.x, event.y, mode.buttons)
        InputBox.checkAll(mode, event.x, event.y, mode.inputBoxes)

    #Updates message position and checks if the program should terminate
    def timerFired(mode):
        updateFramerate(mode)
        lookAtPlane(mode)
        mode.planeAngle -= mode.rotationRate/mode.framerate
        mode.app.airplane.d1 = (math.cos(mode.planeAngle), math.sin(mode.planeAngle), 0)
        

    #Draws the button and the message, or draws "Bye" until the program terminates
    def redrawAll(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2, pilImage = mode.scaledBackground)
        Button.drawAll(mode.buttons, canvas)
        InputBox.drawAll(mode.inputBoxes, canvas)
        TextBox.drawAll(mode.textBoxes, canvas)
        mode.app.airplane.draw(mode, canvas)
       
    

#Creates the splash screen
class SplashScreenMode(Mode):

    #CITATION: Background image from:
    #https://wallpapercave.com/red-bull-air-race-wallpapers
    #Initializes the background image and scale it to the proper size
    def appStarted(mode):
        mode.background = mode.loadImage('media/background.png')
        mode.scaleBackground()
        mode.createButtonsAndText()

    #Scales the background to fit the current window size
    def scaleBackground(mode):
            scale = mode.width / mode.background.width
            mode.scaledBackground = mode.background.resize((round(mode.background.width * scale), 
                                                            round(mode.background.height * scale)))

    #Updates the buttons, text, and background when the window size changes
    def sizeChanged(mode):
        fixAspectRatio(mode)
        mode.scaleBackground()
        mode.createButtonsAndText()

    #Creates the start button and a message telling the user to plug a controller in
    #Also creates the title and subtitle
    def createButtonsAndText(mode):
        buttonX, buttonY = mode.width/2, 13/16 * mode.height
        buttonWidth, buttonHeight = mode.width/6, mode.height/9
        mode.startButton = Button(((buttonX - buttonWidth/2, buttonY - buttonHeight/2), 
                                   (buttonX + buttonWidth/2, buttonY + buttonHeight/2)),
                                    "Start", "red", mode.startClicked)
        
        textX, textY = mode.width/2, mode.height * 15/16
        textWidth, textHeight = mode.width, mode.height/16
        mode.errorText = TextBox(((textX - textWidth/2, textY - textHeight/2), 
                                  (textX + textWidth/2, textY + textHeight/2)), 
                                  "Please plug in a controller to start!", CENTER, "red")
        mode.displayError = False

        mode.textBoxes = []
        titleX, titleY = mode.width/2, 3/32 * mode.height
        titleWidth, titleHeight = mode.width, mode.height/8
        titleText = TextBox(((titleX - titleWidth/2, titleY - titleHeight/2), 
                                  (titleX + titleWidth/2, titleY + titleHeight/2)), 
                                  "TakeOff!", CENTER, "white", "fixedsys")

        subtitleX, subtitleY = titleX, 3/16 * mode.height
        subtitleWidth, subtitleHeight = mode.width, mode.height/16
        subtitleText = TextBox(((subtitleX - subtitleWidth/2, subtitleY - subtitleHeight/2), 
                                  (subtitleX + subtitleWidth/2, subtitleY + subtitleHeight/2)), 
                                  "an RC Airplane Simulator by Owen Ball", CENTER, "white", "fixedsys")
        mode.textBoxes.extend([titleText, subtitleText])



        #Checks for button interaction when the mouse is pressed
    def mousePressed(mode, event):
        mode.startButton.isPressed(mode, event.x, event.y)


    def startClicked(mode, _):
        #Checks if pygame has detected a controller being plugged in  
        
        if pygame.event.peek(pygame.JOYDEVICEADDED):
            #Connects to the game controller

            #CITATION: Pygame controller initialization from 
            #http://yameb.blogspot.com/2013/01/gamepad-input-in-python.html
            mode.app.gameController = pygame.joystick.Joystick(0)
            mode.app.gameController.init()
            mode.app.controllerInputs = getControllerInputs(mode.app)

            mode.app.airplane = createAirplane(mode)

            mode.app.setActiveMode(mode.app.gameMode)

            #mode.app.setActiveMode(mode.app.trainingMode)
        else:
            #If a controller is not available, prompt the user to get one
            mode.displayError = True

    #Necessary since I commented out the ability for mousePressed() and keyPressed()
    #to call redrawAll() in cmu_112_graphics
    def timerFired(mode):
        pass

    #Draws the background, and then the buttons and text on the screen
    def redrawAll(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2, pilImage = mode.scaledBackground)
        mode.startButton.draw(canvas)
        if mode.displayError:
            mode.errorText.draw(canvas)
        TextBox.drawAll(mode.textBoxes, canvas)
        