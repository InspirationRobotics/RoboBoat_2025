"""
Interface file to get low-level settings of devices connected to the Jetson
"""

import os
import sys
import platform
import json

def load_json(path):
    """
    Get the JSON file from a specific path and return it.

    Args:
        path (str): Path to JSON file

    Returns:
        data (dict): JSON data converted into python dictionary
    """

    with open(path, "r") as file:
        data = json.load(file)

    return data

# Will have to differentiate when we get to a new ASV
file_dir = os.path.dirname(os.path.abspath(__file__))
settings = load_json(f"{file_dir}/../Config/barco_polo.json")

def findFromId(ids):
    """
    Finding devices based on their port ID.

    Args:
        ids (list): Port to find the device
    """
    print("Starting findFromId")

    # Read script and split output by line
    bash = os.popen("bash ~/RoboBoat_2025/API/usb_link.sh").read()
    bashSplit = bash.split('\n')
    result = []

    # Iterate through passed ids and indices
    for id in enumerate(ids):
        result.append("")
        # Iterate through lines in splitted bash output
        for line in bashSplit:
            # If line in /dev/tty
            if "/dev/tty" in line:
                line = line.split(" - ")
                if id[1] in line[1]:
                    result[id[0]] = line[0]
    
    # Remove empty spots if there aren't matching devices.
    # If there's a result, return the device path
    for i in reversed(result):
        if i == "":
            result.remove(i)
    if len(result) == 0:
        print(bash)
        return ["Device not found, above is a list of all available devices"]
    return result[0]

def dataFromConfig(name):
    """Get USB configuration from device based on name"""
    # See: /Config/barco_polo.json
    # use data for cameras, use usbID for USB cams or other USB connections
    data = None
    usbID = None
    if name == "arduino_port":
        usbID = settings.get("arduino_port")
    else:
        data = settings.get(name)
        if data == None:
            raise Exception("Invalid Name")
    if data != None:
        return data
    if usbID == None:
        print("id not found")
        return None
    return findFromId([usbID])

# TODO: The rest of the file