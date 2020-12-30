Project Name: TakeOff: RC Airplane Simulator




Project Description:
	The goal of this RC airplane simulator is to help users learn to fly RC aircraft. In the RC hobby, simulators are essential 
tools, as they can help teach someone how to fly an aircraft before they fly it in real life and can either damage the aircraft or 
endanger others. I hope to have the user be able to plug in a controller, calibrate it, and then be able to fly the plane around 
an open world. There will also be a collection of activities that a user can use to practice specific skills to help them learn the 
basics of flying RC airplanes.




Running the project:

Python 3.8.5 was used to create this project. Python can be installed from:
https://www.python.org/downloads/

The "mainvX" Python file must be in the same folder as the "media" folder and "cmu_112_graphics_modified," as well as in the same folder as all
the other python files. This organization of files should be set up by default. To execute the program, you have to open the "mainvX" file and run the code in this file

Also make sure to use the cmu_112_graphics_modified.py file I provided instead of cmu_112_graphics.py. This modified version has lines 475, 483, 497, 510 and 556 commented out. 
This keeps keyPressed and mouse movements from calling redrawAll(), since in my case, timerFired() will constantly trigger redrawAll anyways.

*Ensure that pygame 2.X is installed as well as Shapely. More info at bottom of this file*



Using the code

Controller Setup:
There is no keyboard support, only controller support. To use a controller, plug it in and click "start"
Regular game controllers can be used, or radio transmitters can be used with a proper USB adaptor for your transmitter.

-To calibrate a controller, open the "Controller" menu, hit "reset" and move all joysticks in a complete circle at the full 
	extent of their motion.
-To reassign channels, identify the proper channel by looking at the "Raw Data" output and then click the blue box under "reassign"
next to the channel that you want to reassign. Use backspace to delete the previous entry and then type the new channel. Click
off the box or press enter to save the new assignment.



Using the Main Game Mode:
-While on the field, you can use your controller to take off the aircraft and fly it around the world. 
-The settings menu, which is accessed by using the mouse to press the settings button, allows the user to customize the features in the
main game mode

Keyboard shortcuts in main game mode:
-"r": resets the aircraft
-"Space": toggles between a stationary camera and a camera following the plane



Training Mode:
-The buttons can be used to navigate to the desired training. Once a training is completed, the user is put back on the training selection screen.



Settings Mode

Physics:
	-Settings are self-explanatory
	-min values of 0 and max values of 99

Graphics
	-Daytime: Sets time to day if checked, otherwise nighttime
	-Cloud Count: sets the number of clouds 0-99      Reduce to increase performance
	-Bush Count: sets the number of bushes 0-9999     Reduce to increase performance
	-View Range: sets the maximum distance objects (except clouds) can be seen at  0-999      Reduce to improve performance
	-Sun Angle: Sets the angle of the sun in the sky. 20-90, below 30 not recommended
	-Camera Angle: Sets the angle at which the following-mode camera views the plane. Higher angle means more vertical
	-Camera Dist: Sets the approximate distance the camera follows the plane at 0-99
	-Use Shapely: toggle between using Shapely and not using Shapely     Enable to increase performance
		-Disclaimer: Not using Shapely will result in periodic crashes, especially on take-off
Data Readouts:
	-Display Data: Toggles if any of the features other than "Binoculars" are displayed
	-Altitude: Displays the current altitude of the plane when enabled
	-Velocity: Displays the curennt velocity of the plane when enabled
	-Attitude: Displays the current attitude (angle above the horizontal) when enabled
	-Distance: Displays the current distance from the plane to the origin when enabled
	-Framerate: Displays the current framerate when enabled
	-Binoculars: Shows a zoomed in view of the plane in the corner when enabled. Small performance reduction




Notes:
Graphics Offsets used
	-When offsetting text, buttons, etc., I often used multiples of 1/4, 1/8, 1/16, 1/32, and 1/64, which is why these numbers appear
	throughout the code. This greatly helped with lining different things up with each other

The question mark box on the controller screen opens an internet tab, at least in Windows
If you don't want the program to do this, just don't click the button




External Libraries Needed:
-Pygame Version 2.X: https://pypi.org/project/pygame/
-Shapely: https://pypi.org/project/Shapely/
-Webbrowser: https://docs.python.org/3/library/webbrowser.html (Should be installed already)


