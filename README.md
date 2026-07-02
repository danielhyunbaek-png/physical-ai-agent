Architecture:

The Physical AI Agent I'm currently building is a closed loop system that is made to operate a computer exactly how a human does. It uses visual feedback and physical actuations. The system runs on a discrete time loop across a macOS host and two microcontrollers.

Vision:

- Uses a fixed webcam
- Python based pipeline will capture frames at 30 fps. Each frame is deskewed using a precomputed perspective transform to map the MacBook screen to a fixed 1920x1200 pixel grid. 
- Uses OpenCV template matching for UI elements and Tesseract OCR for text extraction. 

Cognition: 

- Runs on the MacBook Pro
- Python FSM that reads perception stream and executes serial commands. 
- Goal: Under 100 ms from screen change to first physical actuation. 

Action:

-Keyboard: Using the Nuphy Air75 v3 keyboard with Blush Nano switches (45g force, 1.4 actuation).
Using the Arduino mega 2560 with 84 12V micro solenoids (10mm stroke, 5N force), housed in a custom 3D printed matrix plate. 11 cascaded 74HC595 shift resistors feeding 11 ULN2803A Darlington arrays. All powered by 12V PSU with a firmware cap of 12 solenoid activations. 

Mouse: 2 axis XY gantry system controlled by Arduino Uno. Powered by NEMA 17 steppers driven by A4988 drivers. Two SG90 hobby servos providing click actuation. 


