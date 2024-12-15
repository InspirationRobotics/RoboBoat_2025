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
settings = load_json(f"{file_dir}/../config/barco_polo.json")

def findFromID(ids):
    """
    Finding devices based on their port ID.

    Args:
        ids (str): Port to find the device
    """
    pass

# TODO: The rest of the file