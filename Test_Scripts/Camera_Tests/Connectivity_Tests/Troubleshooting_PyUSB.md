# Purpose
Part of the camera API includes using the PYUSB package. You can find the documentation at this link: https://github.com/pyusb/pyusb
However, there was some difficulty in installing the package. This file documents possible problems that may be encountered, and the 
ways to mitigate these problems.

## Textbook Way to Install
To install the PyUSB library, it is first necessary to install the libusb library.
Run the following code to install (this is for a Debian/Ubuntu based system).

```Debian/Ubuntu
sudo apt update
sudo apt install libusb-1.0-0-dev
```

Then, you can install the PyUSB library:

```bash
pip install pyusb
# Verifying that installation worked properly:
python -m pip show pyusb
```

If this does not work, look at [Cannot Install PyUSB](#cannot-install-pyusb-module) for a possible solution.

## Description of Possible Problems and their Solutions with Respect to PyUSB Module Functionality

If PyUSB raises an error (specifically usb.core.find()), you can use the following diagnostic test to get more detailed debug logs:

```python
import os
os.environ['PYUSB_DEBUG'] = 'debug'
import usb.core
usb.core.find()
```

Sample output:
```terminal
2024-12-28 17:18:03,423 ERROR:usb.libloader:'Libusb 1' could not be found
2024-12-28 17:18:03,425 ERROR:usb.backend.libusb1:Error loading libusb 1.0 backend
2024-12-28 17:18:03,425 ERROR:usb.libloader:'OpenUSB library' could not be found
2024-12-28 17:18:03,425 ERROR:usb.backend.openusb:Error loading OpenUSB backend
2024-12-28 17:18:03,425 ERROR:usb.libloader:'Libusb 0' could not be found
2024-12-28 17:18:03,425 ERROR:usb.backend.libusb0:Error loading libusb 0.1 backend
```

### "No Backend"
If the following error occurs (in some sort of shape or form),
```terminal
usb.core.NoBackendError: No backend available
```
it most likely means that you did not install libusb. If installing libusb does not work, the following link is most likely your best bet: https://github.com/pyusb/pyusb/blob/master/docs/faq.rst

### Cannot Install PyUSB Module
If you get the following error, that probably means that you are using some sort of Debian-based platform such as RaspberryPiOS:
```terminal
Error: externally-managed-environment × 
This environment is externally managed 
╰─> To install Python packages system-wide, try apt install python3-xyz, where xyz is the package you are trying to install. 
If you wish to install a non-Debian-packaged Python package, create a virtual environment using python3 -m venv path/to/venv. 
Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make sure you have python3-full installed. 
For more information visit http://rptl.io/venv
```

It is possible to set up a virtual environment and install PyUSB on that environment.
First navigate to a directory where you would like to put the files which will be necessary to keep on your personal hard drive to keep using it.
DO NOT run the following commands in the RoboBoat_2025 directory:
```bash (Linux/MacOS)
python3 -m venv myenv
source myenv/bin/activate
```
Alternatively, for Windows,
```bash (Windows)
myenv\Scripts\activate
```

There should be a "myenv" next to your directory/username in terminal at this point:
```terminal
# Generic format:
(myenv) [username]:~/Documents $
```
After this, run 
```bash
pip install pyusb
# Optionally,
python -m pip show pyusb
```
At this point, any python code that is executed in this virtual environment will have these installed packages. After done with the session, remember to deactivate the environment:
```bash
deactivate
```

If you wish to reenter the environment, you can navigate to the same directory as you had done originally to avoid populating a different directory with the same files, but the steps will have to be followed the same way.