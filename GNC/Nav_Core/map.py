"""
Planning:
- Need a map which we can plot points on and calculate waypoints effectively.
- Coordinates will be absolute, not relative to initial starting point.
- Each object plotted needs three things: type of object, latitude, and longitude.
- The map should be a list of objects. It is more to store and visualize the positions of objects than anything else.

This map will be not be complete during a competition run unless we have made it through the full course.
NOTE: We may be able to create two maps -- one that is preconfigured through surveying, and contains all of the mission obstacles/elements, 
and the other being the one that is created as we come across obstacles via computer vision.
"""

class Object:
    def __init__(self, /, object_type : str = None, latitude : float = None, longitude : float = None, confidence : float = None):
        self.object_type = object_type
        self.latitude = latitude
        self.longitude = longitude
        self.confidence = confidence

class Map:
    def __init__(self):
        # List will be in the form of: [Object, Object, etc.]
        self.map = []

    def put_object(self, object : Object):
        self.map.append(object)

    def find_object(self, type : str):
        list = []
        for object in self.map:
            if object.object_type == type:
                list.append(object)
        return list
    
    def change_map(self, new_value: Object):
        self.map.append(new_value)
        print(f"Map updated with: {new_value}")
    
    # def put_object_in_map(self, object : Object):
    #     parsed_object = {object.object_type: ((object.latitude, object.longitude), object.confidence)}
    #     self.map.append(parsed_object)

    # def load_map_config(self, file_path : str | Path):
    #     if not isinstance(file_path, Path):
    #         file_path = Path(file_path)
        
    #     def load_json(path):
    #         with open(path, "r") as file:
    #             data = json.load(file)
    #         return data
        
    #     config = load_json(file_path)

    #     for object_type, individual_instances in config.items():
    #         for index, object_specs in enumerate(individual_instances):
    #             latitude = object_specs["latitude"] 
    #             longitude = object_specs["longitude"] 
    #             confidence = object_specs["confidence"] 
    #             self.put_object_in_map(Object(object_type=object_type, latitude=latitude, longitude=longitude, confidence=confidence))
    #     return self.map