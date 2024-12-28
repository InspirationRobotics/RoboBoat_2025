# import usb.core
# import usb.util

# dev = usb.core.find()
# if dev is None:
#     print("Device not found.")
# else:
#     print("Device found.")

import os
os.environ['PYUSB_DEBUG'] = 'debug'
import usb.core
usb.core.find()