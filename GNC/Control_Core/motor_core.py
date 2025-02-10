"""
To aggregate/integrate the various lower-level files (sensor fusion, GPS, IMU),
and create a single list of values to be sent to the Arduino to actuate the motors.
"""

import serial
import time

from API.Motors import t200

class MotorCore():
    def __init__(self, port = "/dev/ttyACM0"):
        self.t200 = t200.T200(port="/dev/ttyACM0")
    

    """
    ----------------- RUDIMENTARY FUNCTIONS [PROVEN BASED ON TESTS] -----------------
    """

    """
    As of 2/10/2025, Barco Polo's motor configuration is in the following:
    - Stern port thruster at positive PWM levels will make the boat move clockwise.
    - Stern starboard thruster at positive PWM levels will make the boat move counterclockwise.
    - Aft port thruster at positive PWM levels will make the boat move counterclockwise.
    - Aft starboard at positive PWM levels will make the boat move counterclockwise.

    When PWMs are greater than 1500 for Blue Robotics thrusters, the thrusters spin clockwise.
    Thrusters with a clockwise prop have a forward thrust vector when spinning clockwise.
    Thrusters with a counter clockwise prop have a backward thrust vector when spinning clockwise.
    """
    
    def surge(self, magnitude):
        """Configures for forward (positive magnitude) or backward (negative magnitude) movement"""
        self.t200.set_thrusters(-magnitude, -magnitude, magnitude, -magnitude)

    def stay(self):
        """Sets all motors to no power."""
        self.t200.set_thrusters(0,0,0,0)

    def stop(self):
        """Stop motors."""
        self.t200.stop_thrusters()

    def slide(self, magnitude):
        """Sliding (strafing) in horizontal direction without rotating, positive is left, negative is right."""
        self.t200.set_thrusters(magnitude,-magnitude,magnitude,magnitude)

    def rotate(self, magnitude):
        """Yaw/rotation, positive magnitude is clockwise, negative is counterclockwise."""
        self.t200.set_thrusters(-magnitude,magnitude,magnitude,magnitude)

    """
    --------------------------------------------------------
    """

    """
    ----------------- FUNCTIONS WITH GPS WAYPOINT NAVIGATION/Kalman Filter/Control Loop [NEEDS TESTING] -----------------
    """

    # The goal is to be able to navigate to a given point, when given either a point in polar or vector form.
    # Polar can either be (meters, heading/theta)
    # Vector form can be new (lat, lon) to move to, (meters (x/lateral), meters(y/forward or backward)) to change position by.

    def polar_waypoint_navigation(self, distance_theta, heading):
        """
        Navigate to a given point that is a certain number of meters away along a certain heading.
        Will rotate and then move the set distance.

        Args:
            distance_theta (float): Distance to move (in meters)
            heading (float): New absolute heading (radians)
        """
        pass

    def lat_lon_navigation(self, lat, lon):
        """
        Navigate to a new (lat, lon) GPS coordinate. Automatically calculates best heading.

        Args:
            lat (float): Desired GPS latitude coordinate.
            lon (float): Desired GPS longitude coordinate.
        """
        pass

    def cartesian_vector_navigation(self, x, y):
        """
        Move along a certain 2-D vector. Automatically calculates best heading.

        Args:
            x (float): Desired displacement in meters along strafe direction.
            y (float): Desired displacement in meters along surge direction.
        """
        pass

    """
    --------------------------------------------------------
    """
    