# Setup Scripts for RoboBoat 2025 Documentation
Contained in this folder are all of the scripts to install dependencies that are needed to run the code in this repository.
This is an ideal situation -- there may be dependencies that need to be installed that have been overlooked/have not been implemented here.
NOTE: Scripts are meant for use on Ubuntu versions later 20.04 and later.

## Usage
For each file you wish to execute, navigate to the parent folder of the file, then, replacing the "fine_name" with the file you wish to execute, run:
```bash
sudo chmod +x [file_name].sh
sudo ./[file_name].sh
```

## List of files
- python3
- pip
- OpenCV
- Smopy
- YOLO/Ultralytics
- Filterpy (for sensor fusion)
- PyUSB
