"""
Test function calculations.

Results outputted in terminal should be:

midpoint: (35.93161735278957, -120.2823877144226)
calculate heading: 136.50291057349023°
waypoint from vector: (37.76933666901586, -121.27195953730251)
latitude distance: 410436.7913282438
longitude distance: 372864.0499035577 m
haversine: 554381.152335549086 m
extend vector: (30.200670280916178, -114.42489263022979)
"""

# Assuming mapHelper is defined here or imported.
def test_map_helper():
    from GNC.Nav_Core import nav_util_calculations
    mh = nav_util_calculations.mapHelper()
    
    # Test calculate_midpoint
    point1 = (37.7749, -122.4194)  # San Francisco
    point2 = (34.0522, -118.2437)  # Los Angeles
    midpoint = mh.calculate_midpoint(point1, point2)
    print(f"Midpoint between {point1} and {point2}: {midpoint}")
    
    # Test calculate_heading_to_waypoint
    heading = mh.calculate_heading_to_waypoint(point1, point2)
    print(f"Heading from {point1} to {point2}: {heading:.2f}°")
    
    # Test calculate_waypoint_from_vector
    bearing = 90  # East
    magnitude = 100000  # 100 km
    waypoint = mh.calculate_waypoint_from_vector(point1, bearing, magnitude)
    print(f"Waypoint from {point1} at bearing {bearing}° and distance {magnitude}m: {waypoint}")
    
    # Test calculate_latitude_distance
    lat1, lat2 = 37.7749, 34.0522
    lat_distance = mh.calculate_latitude_distance(lat1, lat2)
    print(f"Latitude distance between {lat1}° and {lat2}°: {lat_distance:.2f} meters")
    
    # Test calculate_longitude_distance
    lon1, lon2 = -122.4194, -118.2437
    avg_lat = (lat1 + lat2) / 2
    lon_distance = mh.calculate_longitude_distance(lon1, lon2, avg_lat)
    print(f"Longitude distance between {lon1}° and {lon2}° at average latitude {avg_lat}°: {lon_distance:.2f} meters")
    
    # Test haversine
    haversine_distance = mh.haversine(point1, point2)
    print(f"Haversine distance between {point1} and {point2}: {haversine_distance:.2f} meters")
    
    # Test extend_vector
    vector_tail = (37.7749, -122.4194)
    vector_head = (34.0522, -118.2437)
    scale = 2  # Extend by twice the distance
    extended_point = mh.extend_vector(vector_tail, vector_head, scale)
    print(f"Extended vector from {vector_tail} to {vector_head} scaled by {scale}: {extended_point}")

# Run the tests
if __name__ == "__main__":
    test_map_helper()