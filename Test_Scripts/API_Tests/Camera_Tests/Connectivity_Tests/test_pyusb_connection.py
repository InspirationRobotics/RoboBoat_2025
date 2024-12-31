"""
Test script to test functionality of the Pyusb script (ensure it is properly setup).
This test is considered successful when "Device found." is printed on the screen. This should be true as long as there is a camera in a USB port on 
the given computer.
"""

import usb.core
import usb.util

dev = usb.core.find()
if dev is None:
    print("Device not found.")
else:
    print("Device found.")

# If the code doesn't work, try uncommenting this code:

# import os
# os.environ['PYUSB_DEBUG'] = 'debug'
# import usb.core
# usb.core.find()