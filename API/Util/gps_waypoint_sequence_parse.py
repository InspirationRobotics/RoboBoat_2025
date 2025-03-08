import math


def apply_offset(lat, lon, dx, dy):
    """
    Apply a Cartesian offset (dx, dy) in meters to a latitude/longitude point.
    Args:
        dx (int, float) : Positive moves the point east, negative moves the point west.
        dy (int, float) : Positive moves the point north, negative moves the point south.
    """
    R = 6378137  # Earth's radius in meters
    dlat = (dy / R) * (180 / math.pi)
    dlon = (dx / (R * math.cos(math.radians(lat)))) * (180 / math.pi)
    return lat + dlat, lon + dlon

def process_waypoints(file_path, dx, dy):
    """Read waypoints from a file, apply an offset, and overwrite the file."""
    with open(file_path, 'r') as file:
        waypoints = [line.strip().split(', ') for line in file]
    
    new_waypoints = [apply_offset(float(lat), float(lon), dx, dy) for lat, lon in waypoints]
    
    with open(file_path, 'w') as file:
        for lat, lon in new_waypoints:
            file.write(f"{lat}, {lon}\n")

# Example usage
file_path = "GNC/Guidance_Core/Config/waypoints.txt"  # Replace with actual file path
dx, dy = 20, 0 # Offset in meters
process_waypoints(file_path, dx, dy)