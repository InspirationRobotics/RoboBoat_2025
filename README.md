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

### Miscellaneous Files
- There are "__pycache__" folders littered throughout the code base. These are not actual files, but instead files compiled by the python editor in order to be run by the computer. It is easier to upload these with our scripts than to try and clean them out; doing so generally results in convoluted merge conflicts.

- There should be "__init__" files located in each folder in our repositoy. This is because our (python) scripts are run as modules.


Note that this is a "grand plan" for the software architecture. For this season's competition, it remains to be seen how much will be able to be accomplished.

## Hardware Prerequisites

Our current electrical diagram can be found here: https://drive.google.com/file/d/1p00fLm1HOUzSkRoLzEd6WDd1H0qSmS08/view?usp=drive_link

## Running the system

Scripts should be run as modules from the root directory (i.e. inside RoboBoat_2025, but not in any folder within RoboBoat_2025). 
Here is an example to run the test_serial script inside Test_Scripts:

```bash
git pull
python3 -m Test_Scripts.test_serial
```

## Format
The goal is to keep our code well-documented and well-organized. To ensure this, please:
- Add a header at the top of each file detailing what its intended purpose is.
- Add docstrings to each class and function, explaining the purpose of the class/function.
- For functions that take arguments/return specific items, please include in the docstring the arguments expected, along with the type, as well as the type of object returned and what its significance is.
- Add "#" comments throughout the code, especially for long/more convoluted files to explain low-level processes.