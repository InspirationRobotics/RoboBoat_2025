"""
File that contains classes to load and parse data about video devices connected to a host computer (in this case the Jetson).
"""

import usb.core
import usb.util
import subprocess

# NOTE: Have absolutely no idea what this does.
class find_class(object):
    def __init__(self, class_):
        self._class = class_
    def __call__(self, device):
        if device.bDeviceClass == self._class:
            return True
        for cfg in device:
            intf = usb.util.find_descriptor(cfg, bInterfaceClass=self._class)
            if intf is not None:
                return True
        return False

class FindCamera:
    """
    Class to find all of the video devices connected to the Jetson.
    Upon instantiation it loads all of the devices with their associated information into a list.
    This list is an attribute of the class called "matches", and contains a list of tuples, with each tuple detailing a specific device.
    Format of tuples: (device bus, device address, v4ctl information).
    """

    def __init__(self):
        self.matches = [] # A list of devices, with each tuple having all of the information to do with a unique device.
        self.__find_cams()
        pass

    def __find_cams(self):
        """
        Finds all of the USB video devices plugged into the Jetson.
        Then gets all of the v412-ctl data for each of the devices.
        Appends each device with its various information to self.matches, an attribute of the FindCamera class.
        """

        # Find all USB devices with video interface class (14)
        devices = usb.core.find(find_all=True, custom_match=find_class(14))

        # Get the v4l2-ctl data
        v4ctl = subprocess.check_output("v4l2-ctl --list-devices", shell=True).decode("utf-8")
        v4ctl = v4ctl.split("\n")

        for device in devices:
            try:
                output = subprocess.check_output(f'lsusb -tvv | grep /dev/bus/usb/{device.bus:03}/{device.address:03}', shell=True).decode("utf-8")
                id = output.split("\n")[0].strip().split(" ")[0].split("1-", 1)[-1]
                for i in range(len(v4ctl)):
                    if id in v4ctl[i]:
                        self.matches.append((device.bus, device.address, v4ctl[i+1].strip()))
                        break
            except:
                pass
    
    def find_cam(self, bus : int, address : int) -> str:
        """
        Finds the v4l2ctl information for a specific video device given the bus and address information.

        Args:
            bus (int): Bus of the device.
            address (int): Address of the device.

        Returns:
            str: v4l2ctl information for the designated device.
        """

        for match in self.matches:
            if match[0] == bus and match[1] == address:
                return match[2]
        return None

    @staticmethod
    def _find_cam(bus : int, address : int) -> str:
        """
        Essentially does what the FindCamera class is supposed to do. It is a static method, so internalizes what is defined as 
        multiple functions in the class.

        Finds the video USB devices, appends the result to a list along with parsed v4l2ctl information for each device.
        That list is then parsed by the bus and address of the specific device that is passed into the function, and returns the v4l2ctl data 
        for that specific device.

        NOTE: Not exactly sure what the bus and address are supposed to look like. As such, the argument documentation will need to be updated (made more specific)

        Args:
            bus (int): Bus of the device.
            address (int): Address of the device.

        Returns:
            str: v4l2ctl information for the designated device.
        """

        # Find all USB devices with video interface class (14)
        devices = usb.core.find(find_all=True, custom_match=find_class(14))

        # Get the v4l2ctl data
        v4ctl = subprocess.check_output("v4l2-ctl --list-devices", shell=True).decode("utf-8")
        v4ctl = v4ctl.split("\n")

        matches = []

        for device in devices:
            try:
                output = subprocess.check_output(f'lsusb -tvv | grep /dev/bus/usb/{device.bus:03}/{device.address:03}', shell=True).decode("utf-8")
                id = output.split("\n")[0].strip().split(" ")[0].split("1-", 1)[-1]
                for i in range(len(v4ctl)):
                    if id in v4ctl[i]:
                        matches.append((device.bus, device.address ,v4ctl[i+1].strip()))
                        break
            except:
                pass
        
        for match in matches:
            if match[0] == bus and match[1] == address:
                return match[2]
        return None