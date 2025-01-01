"""
Sandbox file to make it convenient to see how code works/experiment with syntax.
Can be deleted whenever someone feels like cleaning up.
"""

from math import radians, degrees, sin, cos, atan2, asin

curr_lat, curr_lon = map(radians, (37.7749, -122.4194))
bearing = radians(90)
angular_distance = 100000 / 6317000
wp_lat = asin(sin(curr_lat) * cos(angular_distance) + cos(curr_lat) * sin(angular_distance) * cos(bearing))
wp_lon = curr_lon + atan2(sin(bearing) * sin(angular_distance) * cos(curr_lat), cos(angular_distance) - (sin(curr_lat) * sin(wp_lat)))
waypoint = (degrees(wp_lat), degrees(wp_lon))

print(waypoint)
