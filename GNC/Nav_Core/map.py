"""
Planning:
- Need a map which we can plot points on and calculate waypoints effectively.
- Coordinates will be absolute, not relative to initial starting point.
- Each object plotted needs three things: type of object, latitude, and longitude.
- The map should be a list of objects. It is more to store and visualize the positions of objects than anything else.
"""

class Object:
    def __init__(self, /, object_type : str = "None", latitude : float = None, longitude : float = None):
        self.object_type = object_type
        self.latitude = latitude
        self.longitude = longitude

class Map:
    def __init__(self):
        pass