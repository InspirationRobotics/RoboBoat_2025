"""
To aggregate/integrate the various lower-level files (sensor fusion, GPS, IMU),
and create a single list of values to be sent to the Arduino to actuate the motors.
"""

import time
import numpy as np
import threading
import queue
import math
from typing import Tuple, List
from GNC.Nav_Core import gis_funcs
from GNC.Control_Core import sensor_fuse

from API.Motors import t200

class MotorCore():
    def __init__(self, port = "/dev/ttyACM0"):
        self.t200 = t200.T200(port="/dev/ttyACM0")
        # TODO: Put correct heading offset
        self.sensor_fuse = sensor_fuse.SensorFuse(heading_offset=-172)
        self.position_data = {'current_position' : None, 'current_heading' : None, 'current_velocity' : None}

        self.desired_position = (None, None) # lat, lon
        self.desired_heading = None # in degrees
    
    """
    ----------------- RUDIMENTARY FUNCTIONS [PROVEN BASED ON TESTS] -----------------
    """

    """
    As of 2/10/2025, Barco Polo's motor configuration is in the following:
    - Forward port thruster at positive PWM levels will make the boat move counterclockwise.
    - Forward starboard thruster at positive PWM levels will make the boat move clockwise.
    - Aft port thruster at positive PWM levels will make the boat move clockwise.
    - Aft starboard at positive PWM levels will make the boat move clockwise.

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
        # NOTE: We want positive to be right, negative to be right.
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

    def polar_waypoint_navigation(self, distance_theta, heading):
        """
        Navigate to a given point that is a certain number of meters away along a certain heading.
        Will rotate and then move the set distance.

        Args:
            distance_theta (float): Distance to move (in meters)
            heading (float): New absolute heading (degrees)
        """
        desired_lat, desired_lon = gis_funcs.destination_point(
            self.position_data["current_position"][0],
            self.position_data["current_position"][1],
            heading,
            distance_theta
        )

        self.desired_position = (desired_lat, desired_lon)
        self.desired_heading = heading

    def lat_lon_navigation(self, lat, lon):
        """
        Navigate to a new (lat, lon) GPS coordinate. Automatically calculates best heading.

        Args:
            lat (float): Desired GPS latitude coordinate.
            lon (float): Desired GPS longitude coordinate.
        """
        self.desired_position = (lat, lon)
        self.desired_heading = gis_funcs.bearing(
            self.position_data["current_position"][0], self.position_data["current_position"][1], lat, lon
        )

    def cartesian_vector_navigation(self, x, y):
        """
        Move along a certain 2-D vector. Automatically calculates best heading.

        Args:
            x (float): Desired displacement in meters along strafe direction.
            y (float): Desired displacement in meters along surge direction.
        """
        vector_distance = round(math.sqrt(x^2 + y^2), 2)
        vector_theta = round(math.degrees(math.atan2(y/x)), 2)
        self.polar_waypoint_navigation(vector_distance, vector_theta)

    def update_position(self):
        self.position_data = {
            'current_position' : self.sensor_fuse.get_position(),
            'current_heading' : self.sensor_fuse.get_heading(),
            'current_velocity' : self.sensor_fuse.get_velocity()
        }

    # Calculation logic.
    # ---------------------------------------------------------------------

    def solve_wp_bearing(self, curr_pos : Tuple, target_pos : Tuple):
        """
        Returns the absolute bearing in degrees to the target position.
        """
        # Returns the bearing to the target position
        if curr_pos is None:
            return None
        br = gis_funcs.bearing(curr_pos[0], curr_pos[1], target_pos[0], target_pos[1])
        # self.log(f"Current Position: {curr_pos}")
        # self.log(f"Target Position: {target_pos}\n--------")
        return br
    
    def calc_rotation(self, current_heading : float, target_heading : float):
        """
        Takes current heading and target heading as absolute degrees, returns 
        scaled amount of radians needed for desired rotation.
        """
        if current_heading is None or target_heading is None:
            return 0
        min_power = 0.1
        cw = (target_heading - current_heading) % 360
        ccw = (current_heading - target_heading) % 360

        # 1 if clockwise, -1 if counterclockwise
        direction = 1 if cw <= ccw else -1
        distance = min(cw, ccw)

        if distance<7: min_power = 0.15
        if distance<5: min_power = 0.1
        if distance<2: return 0 # 2 degree tolerance

        # self.log(f"Current: {current_heading} Target: {target_heading}")
        # self.log(f"Direction: {'clockwise' if direction==1 else 'counter'}")

        tr = np.radians(direction * distance) * 0.5
        # self.log(f"Target Rotation: {tr}\n--------")
        if(abs(tr)<0.1): tr = direction * min_power

        # self.log(f"Normalized Target Rotation: {tr}\n--------")
        return tr # * distance from center of vehicle
    
    def hold_logic(self, curr_pos, curr_heading, target_pos, target_heading):
        # Returns a vector and rotation to reach the target position and heading
        if curr_pos is None or curr_heading is None:
            return [0, 0], 0
        # vy is forwards
        # vx is lateral
        vy, vx, dist = gis_funcs.vector_to_target(curr_pos, target_pos, curr_heading)
        # Based off the distance, we can scale the target vector (absolute value of components sums to 1). 
        # When more than 3 meters away, we go at the target vector, otherwise we slow down
        scale = min(dist/3, 1)
        target_vector = [vx*scale, vy*scale]
        print(f"[DEBUG MOTOR_CORE] Calculated vector : {target_vector}, vx : {vx}, vy : {vy}, dist: {dist}")
        '''
        TEMPORARY =============================
        Turn vector into only magnitude in forward direction by setting lateral to 0
        And also only going forward if positive
        '''
        target_vector = list(target_vector)
        # self.log(f"Raw Target Vector: {target_vector}")
        target_vector[0] = 0
        target_vector[1] = target_vector[1]*0.75 if target_vector[1] > 0 else 0
        # self.log(f"Normalized Target Vector: {target_vector}\n--------")
        '''
        =======================================
        '''
        target_rotation = self.calc_rotation(curr_heading, target_heading)

        current_position = self.position_data["current_position"]
        print(f"[MOTOR CORE DEBUG] current position : {current_position}, target position : {self.desired_position}")
        print(f"[MOTOR CORE DEBUG] target_vector: {target_vector}, target_rotation: {target_rotation}, distance : {dist}")
        return target_vector, target_rotation, dist
    
    def parse_hold_logic(self, vector, rotation):
        # Pseudocode:
        # If the target rotation or vector is none, initialize as empty list/value
        # Forward thrusters will function as the thrusters to move forward -- if there is a y value > 0, then move forward
        # Back thrusters will be our turning thrusters -- either clockwise or counterclockwise motion.
        
        if vector == None:
            vector = [0, 0]
            print(f"[DEBUG MOTOR CORE] No desired vector.")
        if rotation == None:
            rotation = 0
            print(f"[DEBUG MOTOR CORE] No desired rotation.")

        forward_thruster_value = min(max(-1, vector[1] * 0.5), 1)
        forward_port_value = -(forward_thruster_value)
        forward_starboard_value = -(forward_thruster_value)

        rotational_thruster_value = min(max(rotation, -1), 1)
        aft_port_value = rotational_thruster_value
        aft_starboard_value = rotational_thruster_value
    
        return [forward_port_value, forward_starboard_value, aft_port_value, aft_starboard_value]
    # ---------------------------------------------------------------------------

    def calc_motor_power(self, send_queue, calculate_rate, stop_event):
        while not stop_event.is_set():
            self.update_position()
            motor_values = [0, 0, 0, 0]

            if self.desired_position[0] == None or self.desired_position[1] == None:
                self.desired_position = self.position_data["current_position"]
            if self.desired_heading == None:
                self.desired_heading = self.position_data["current_heading"]

            target_bearing = self.solve_wp_bearing(
                self.position_data["current_position"],
                self.desired_position
            )

            current_heading = self.position_data["current_heading"]
            print(f"[MOTOR CORE DEBUG] current_bearing: {current_heading}, target_bearing: {target_bearing}")
            target_vector, target_rotation, dist = self.hold_logic(
                self.position_data["current_position"],
                self.position_data["current_heading"],
                self.desired_position,
                target_bearing
            )
            motor_values = self.parse_hold_logic(target_vector, target_rotation)

            send_queue.put(motor_values)
            time.sleep(calculate_rate)

    def control_loop(self, value_queue, send_rate, stop_event):
        """
        Takes the values calculated by calc_motor_power(), and sends them to the T200s.
        """
        while not stop_event.is_set():
            try:
                value = value_queue.get(timeout=send_rate)
                forward_port, forward_starboard, aft_port, aft_starboard = value[0], value[1], value[2], value[3]
                self.t200.set_thrusters(forward_port, forward_starboard,aft_port, aft_starboard)
            except queue.Empty:
                continue

    # Calculate motor power thread will send to the control_loop thread. Will have a constant point where we want to go
    # (self.desired_position, heading, etc.), which will be passed into calc_motor_power(). Will deal with specifics for each later.

    def main(self, calculate_rate=0.1, send_rate=0.1, duration=10):
        send_queue = queue.Queue()
        self.stop_event = threading.Event()

        self.control_loop_instance = threading.Thread(target=self.control_loop, args=(send_queue, send_rate, self.stop_event))
        self.control_loop_instance.daemon = True # Ensure this thread exits when main program exits.
        self.control_loop_instance.start()

        self.calc_motor_power_instance = threading.Thread(target=self.calc_motor_power, args=(send_queue, calculate_rate, self.stop_event))
        self.calc_motor_power_instance.daemon = True
        self.calc_motor_power_instance.start()

        if duration == None:
            # Arbitrary number
            duration = 100

        time.sleep(duration)

        self.stop_event.set()

        self.calc_motor_power_instance.join()
        self.control_loop_instance.join()

        self.stop()

    def exit(self):
        self.stop_event.set()

        self.calc_motor_power_instance.join()
        self.control_loop_instance.join()
        print("[MOTOR CORE] Threads joined, motor_core exited.")
    """
    --------------------------------------------------------
    """
    
