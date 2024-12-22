# RoboBoat_2025
Team Inspiration's Codebase for the 2025 RoboBoat Competition. We utilize a single ASV (autonomous surface vessel). See [Hardware Prerequisites](#hardware-prerequisites) for a more detailed specification of our current system.

## Structure
As of right now (12/21/2024), the repository will utilize the following format in order to organize effectively.

```bash
RoboBoat_2025
|-- API
|    | -- GPS
|    |     | -- # Here are all of the low-level GPS functionalities.
|    | -- Motors
|    |     | -- # Here is all of the low-level motor code.
|    | -- Util
|    |     | -- # Here is all of the low-level functionality used across multiple sensors/devices.
|    
|-- Navigation
|   | -- # Will take low-level sensor data and calculate waypoints
|   | -- # This will probably incorporate sensor fusion
|   | -- # Calculation of motor speeds/directions will probably take place here
|
|-- Perception
|    | -- # Accessing camera code will be here
|    | -- # Models will be here too
|    | -- # Model processing files in order to obtain ML model output will be found here as well
|
|-- Mission_Planner
|   | -- # Mission files should be found here
|   | -- # This will include higher-level mission logic, and will weigh perception and navigation data to generate actuation.
|   
|-- Test_Scripts
|   | -- GPS_Tests
|   |     | -- # All tests to confirm low-level GPS capabilities.
|   | -- Motor_Tests
|   |     | -- # All tests to confirm low-level motor capabilities.
|
|-- Setup
|   | -- # Shell scripts to install all necessary functionalities given the right hardware
|
|-- Logs
|   | -- # Logs that give detailed diagnostics of the system (for debug purposes).
```

Note that this is a "grand plan" for the software architecture. For this season's competition, it remains to be seen how much will be able to be accomplished.

## Hardware Prerequisites

We utilize a Jetson Xavier NX, an arduino, and various hardware. Ubuntu version is currently unknown. As the architecture develops, a clearer understanding of 
system specifications will crystallize. 

## Format
The goal is to keep our code well-documented and well-organized. To ensure this, please:
- Add a header at the top of each file detailing what its intended purpose is.
- Add docstrings to each class and function, explaining the purpose of the class/function.
- For functions that take arguments/return specific items, please include in the docstring the arguments expected, along with the type, as well as the type of object returned and what its significance is.
- Add "#" comments throughout the code, especially for long/more convoluted files to explain low-level processes.