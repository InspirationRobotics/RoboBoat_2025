from GNC.Nav_Core import map, map_visualizer

test_map = map.Map()
test_preloaded_map = test_map.load_map_config("Test_Scripts/GNC_Tests/Nav_Tests/test_map_config_file.json")

test_map_visualizer = map_visualizer.mapVisualizer(test_preloaded_map)
# object_specifics = test_map_visualizer.loaded_map

lat_min = 10000
lat_max = 0
lon_min = 10000
lon_max = 0

for index, object in enumerate(test_map_visualizer.loaded_map):
    for tuple in object.values():
        coordinates = tuple[0]
        latitude = coordinates[0]
        longitude = coordinates[1]

        if latitude > lat_max:
            lat_max = latitude
        elif latitude < lat_min:
            lat_min = latitude
        if longitude > lon_max:
            lon_max = longitude
        elif longitude < lon_min:
            lon_min = longitude

print(f"[TEST] Lat_min = {lat_min}, Lat_max : {lat_max}, Lon_min : {lon_min}, Lon_max : {lon_max}")
        