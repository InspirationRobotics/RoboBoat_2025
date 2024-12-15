import json
import os
import sys

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

# path = r"C:\Users\netwo\OneDrive\Team Inspiration\RoboBoat 2025\RoboBoat_2025\API\barco_polo.json"

# with open(path, "r") as file:
#     data = json.load(file)

# print(type(data))

file_dir = os.path.dirname(os.path.abspath(__file__))
settings = load_json(f"{file_dir}/../config/barco_polo.json")
print(settings)