from GNC.Nav_Core import map, map_visualizer

"""
Notes on test:
27.359506, -82.453704 (lower left), 27.365954, -82.453677 (upper left), 27.360359, -82.449356 (lower right), 27.363611, -82.449917 (upper right) 
Left side is red buoy, right side is green buoy
"""

test_map = map.Map()
test_preloaded_map = test_map.load_map_config("Test_Scripts/GNC_Tests/Nav_Tests/test_map_config_file.json")

test_map_visualizer = map_visualizer.mapVisualizer(test_preloaded_map, scale = 1.2, 
                                                   path_to_save_image="Test_Scripts/GNC_Tests/Nav_Tests/Map_Visualization_Dev_Tests")
test_map_visualizer.get_map(save = True)