# RoboBoat_2025 (Barco Polo Software Package v2.0)
Team Inspiration's Codebase for the 2025 RoboBoat Competition. We utilize a single ASV (autonomous surface vessel). See [Hardware Prerequisites](#hardware-prerequisites) for a more detailed specification of our current system.
Before developing ANY code, please read the [format](#format) section thoroughly.

Note that this is a "grand plan" for the software architecture. For this season's competition, it remains to be seen how much will be able to be accomplished.

## Structure
As of the time of writing (1/2/2025), the repository will utilize the following format in order to organize effectively.

```bash
RoboBoat_2025
|-- API
|    | -- Camera
|    |     | -- # Here is all of the low-level camera functionality.
|    | -- GPS
|    |     | -- # Here are all of the low-level GPS functionalities.
|    | -- IMU
|    |     | -- # Here is all of the low-level IMU functionality.
|    | -- Motors
|    |     | -- # Here is all of the low-level motor code.
|    | -- Actuators
|    |     | -- # Currently not developed, projected place to have the low-level control code for the racketball launcher and water cannon.
|    | -- Util
|    |     | -- # Here is all of the low-level functionality used across multiple sensors/devices. This is mainly port/bus handling.
|    
|-- GNC
|    | -- Control_Core
|    |     | -- # All of the code to control the ASV. This is mainly about allowing the ASV to move precisely and accurately.
|    | -- Guidance_Core
|    |     | -- # This is the highest level module of the whole codebase -- here are where the high-level mission algorithms are located.
|    | -- Nav_Core
|    |     | -- # The code to create a map of the course, and calculate paths (and their associated waypoints) through the course.
|
|-- Perception
|    | -- Models
|    |     | -- # Binary files that contain the weights of pre-trained ML models (TensorRT or YOLO)
|    | -- Perception_Core
|    |     | -- # Handles accessing camera streams, running ML models, and returning actionable results.
|    | -- ML_Model_Core
|    |     | -- # Files that handle running ML models and pre-processing camera frames before frames are fed to the model.
|   
|-- Test_Scripts
|   | -- API_Tests
|   |     | -- Camera_Tests
|   |     |     | -- Connectivity Tests
|   |     |     |     | -- # Tests to determine whether a camera can be accessed properly.
|   |     | -- GPS_Tests
|   |     |     | -- GPSLogs
|   |     |     |     | -- # GPS data logging files created by GPS Test files to test GPS API functionality.
|   |     |     | -- Missions
|   |     |     |     | -- # GPS data logging files created by GPS Test files to test GPS API functionality, specifically on mission usage.
|   |     |     | -- # All tests to confirm low-level GPS capabilities.
|   |     | -- IMU_Tests
|   |     |     | -- # All tests to confirm low-level IMU capabilities.
|   |     | -- Motor_Tests
|   |     |     | -- # All tests to confirm low-level motor capabilities.
|   |
|   | -- GNC_Tests
|   |     | -- Control_Tests
|   |     |    | -- # Tests to confirm control code. This will include station keeping, all basic movements, and moving to a given waypoint accurately.
|   |     | -- Nav_Tests
|   |     |     | -- # All tests to confirm navigation capabilities for the ASV. These rely on lower-level functionalities like the GPS and IMU.
|   |     |     | -- Map_Visualization_Dev_Tests
|   |     |     |     | -- # Tests to confirm map visualization capabilities. These are development tests, but can be used to verify once fully developed.
|
|-- Setup
|   | -- # Shell scripts to install all necessary functionalities given the right hardware. 
```

### Usage
The three folders that will be needed for runs are the API, GNC, and Perception folders. These are set up as python packages. To install, please navigate to the given folder and run:
```bash
pip install -e
```
NOTE: This is currently untested and not well-understood. It is probably not necessary for any functionality purpose.

### Miscellaneous Files
- "__pycache__" files should NOT be pushed or pulled from the cloud -- there is a .gitignore file in the root directory that ignores changes to these 
files. Please make sure you do not override this and push __pycache__ files to the cloud.
- There should be "__init__" files located in each folder in our repository. This is because our (python) scripts are run as modules.
- As stated in [Usage](#usage), the API, GNC, and Perception folders are set up as python packages. As such, each of these have a "setup.py" file.

## Hardware Prerequisites

Our current electrical diagram can be found here: https://drive.google.com/file/d/1p00fLm1HOUzSkRoLzEd6WDd1H0qSmS08/view?usp=drive_link

## Running the system

Scripts should be run as modules from the root directory (i.e. inside RoboBoat_2025, but not in any folder within RoboBoat_2025). 
Here is an example to run the test_serial script inside Test_Scripts:
```bash
git pull
python3 -m Test_Scripts.API_Tests.Motor_Tests.test_serial
```
## Format
### Best Practices/Standards for Development
Please conform to the following guidelines when developing code:
1. All code should be tested and verified in all of its functionality before being pushed to the cloud. If this is not feasible, such as when having to push code remotely to enable testing on the ASV, please make note of it, using the "NOTE" keyword in a comment at the top of the file or function.
2. Besides noting the status of functionality if warranted (see [1.](#1.)), it is important that all code is well-documented and readable. Please see [Documentation Guidelines](#documentation-guidelines) for more information.
3. When importing files and classes, make sure the imports are absolute, not relative. This decreases problems to fix when restructuring.

### Documentation Guidelines
The goal is to keep our code well-documented and well-organized. To ensure this, please:
- Add a header at the top of each file detailing what its intended purpose is.
- Add docstrings to each class and function, explaining the purpose of the class/function.
- For functions that take arguments/return specific items, please include in the docstring the arguments expected, along with the type, as well as the type of object returned and what its significance is.
- Add "#" comments throughout the code, especially for long/more convoluted files to explain low-level processes.

## Competition Execution Sequence
This sequence has not been determined yet.