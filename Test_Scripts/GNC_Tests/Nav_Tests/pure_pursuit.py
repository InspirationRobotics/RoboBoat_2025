import numpy as np
import cv2
import time

class RobotSimulator:
    def __init__(self, x=0, y=0, theta=0):
        # Robot state
        self.x = x
        self.y = y
        self.theta = theta  # heading in radians
        
        # Velocity state (body frame)
        self.vx = 0  # surge velocity
        self.vy = 0  # sway velocity
        self.omega = 0  # yaw rate
        
        # Physical parameters
        self.mass = 10.0  # kg
        self.inertia = 2.0  # kg*m^2
        
        # Drag coefficients (simulate water resistance)
        self.drag_linear = 2.0  # linear drag
        self.drag_angular = 1.5  # angular drag
        
        # PWM to force conversion factors
        self.surge_factor = 50.0
        self.sway_factor = 50.0
        self.yaw_factor = 20.0
        
        # Control limits
        self.max_pwm = 1.0
        self.min_pwm = -1.0
        
    def apply_pwm(self, surge_pwm, sway_pwm, yaw_pwm):
        """
        Control interface matching actual robot
        PWM values range from -1.0 to 1.0
        """
        # Clamp PWM values
        surge_pwm = np.clip(surge_pwm, self.min_pwm, self.max_pwm)
        sway_pwm = np.clip(sway_pwm, self.min_pwm, self.max_pwm)
        yaw_pwm = np.clip(yaw_pwm, self.min_pwm, self.max_pwm)
        
        # Convert PWM to forces
        force_surge = surge_pwm * self.surge_factor
        force_sway = sway_pwm * self.sway_factor
        torque_yaw = yaw_pwm * self.yaw_factor
        
        return force_surge, force_sway, torque_yaw
    
    def update(self, surge_pwm, sway_pwm, yaw_pwm, dt):
        """Update robot state with physics simulation"""
        # Get forces from PWM
        f_surge, f_sway, torque = self.apply_pwm(surge_pwm, sway_pwm, yaw_pwm)
        
        # Calculate drag forces (opposite to velocity)
        drag_surge = -self.drag_linear * self.vx
        drag_sway = -self.drag_linear * self.vy
        drag_yaw = -self.drag_angular * self.omega
        
        # Total forces
        total_surge = f_surge + drag_surge
        total_sway = f_sway + drag_sway
        total_torque = torque + drag_yaw
        
        # Update velocities (body frame)
        ax = total_surge / self.mass
        ay = total_sway / self.mass
        alpha = total_torque / self.inertia
        
        self.vx += ax * dt
        self.vy += ay * dt
        self.omega += alpha * dt
        
        # Convert body frame velocities to world frame
        vx_world = self.vx * np.cos(self.theta) - self.vy * np.sin(self.theta)
        vy_world = self.vx * np.sin(self.theta) + self.vy * np.cos(self.theta)
        
        # Update position
        self.x += vx_world * dt
        self.y += vy_world * dt
        self.theta += self.omega * dt
        
        # Normalize theta to [-pi, pi]
        self.theta = np.arctan2(np.sin(self.theta), np.cos(self.theta))

class PurePursuitController:
    def __init__(self, lookahead_distance=50.0):
        self.lookahead = lookahead_distance
        self.waypoints = []
        self.current_waypoint_idx = 0
        
    def set_waypoints(self, waypoints):
        """Set waypoints as list of (x, y) tuples"""
        self.waypoints = waypoints
        self.current_waypoint_idx = 0
        
    def get_target_point(self, robot_x, robot_y):
        """Find lookahead point on path"""
        if self.current_waypoint_idx >= len(self.waypoints) - 1:
            return self.waypoints[-1]
        
        # Find the closest point on path ahead
        min_dist = float('inf')
        target = self.waypoints[self.current_waypoint_idx]
        
        for i in range(self.current_waypoint_idx, len(self.waypoints)):
            wx, wy = self.waypoints[i]
            dist = np.sqrt((wx - robot_x)**2 + (wy - robot_y)**2)
            
            # Update current waypoint if we're close enough
            if dist < 20 and i < len(self.waypoints) - 1:
                self.current_waypoint_idx = i + 1
            
            # Find point at lookahead distance
            if dist >= self.lookahead:
                target = (wx, wy)
                break
            
        wx_ss, wy_ss = self.waypoints[-1]
        dist_ss = np.sqrt((wx_ss - robot_x)**2 + (wy_ss - robot_y)**2)
        if dist_ss<50:
            target = self.waypoints[-1]

        return target
    
    def compute_control(self, robot):
        """Compute PWM commands for pure pursuit"""
        if not self.waypoints:
            return 0, 0, 0
        
        # Get target point
        target_x, target_y = self.get_target_point(robot.x, robot.y)
        
        # Calculate error in body frame
        dx = target_x - robot.x
        dy = target_y - robot.y
        
        # Transform to body frame
        dx_body = dx * np.cos(-robot.theta) - dy * np.sin(-robot.theta)
        dy_body = dx * np.sin(-robot.theta) + dy * np.cos(-robot.theta)
        
        # Distance to target
        dist = np.sqrt(dx_body**2 + dy_body**2)
        
        # Desired heading angle in body frame
        desired_angle = np.arctan2(dy_body, dx_body)
        
        # Control laws
        surge_pwm = 0.6 if dist > 10 else 0.3  # Forward speed
        sway_pwm = np.clip(dy_body * 0.01, -0.3, 0.3)  # Lateral correction
        yaw_pwm = np.clip(desired_angle * 0.5, -0.5, 0.5)  # Heading correction
        
        return surge_pwm, sway_pwm, yaw_pwm

def create_curved_path():
    """Generate a smooth, high-resolution curved path using cubic spline interpolation"""
    from scipy.interpolate import CubicSpline
    
    # Define control points for the path
    control_points = [
        (100, 300),   # Start
        (200, 300),   # Straight section
        (280, 280),   # Begin curve
        (320, 240),   # Curve apex
        (380, 220),   # End curve
        (480, 220),   # Straight
        (540, 240),   # Begin S-curve
        (580, 280),   # S-curve middle
        (600, 340),   # S-curve
        (590, 400),   # Final curve
        (560, 450),   # End
    ]
    
    # Extract x and y coordinates
    control_x = np.array([p[0] for p in control_points])
    control_y = np.array([p[1] for p in control_points])
    
    # Create parameter t for interpolation
    t = np.linspace(0, 1, len(control_points))
    
    # Create cubic splines for x and y
    cs_x = CubicSpline(t, control_x, bc_type='natural')
    cs_y = CubicSpline(t, control_y, bc_type='natural')
    
    # Generate high-resolution waypoints (1 point per pixel approximately)
    t_fine = np.linspace(0, 1, 500)
    x_fine = cs_x(t_fine)
    y_fine = cs_y(t_fine)
    
    # Create waypoint list
    waypoints = [(x_fine[i], y_fine[i]) for i in range(len(t_fine))]
    
    return waypoints

def visualize(robot, controller, waypoints):
    """Visualize the simulation using OpenCV"""
    # Create window
    width, height = 800, 600
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Draw waypoints path
    for i in range(len(waypoints) - 1):
        pt1 = (int(waypoints[i][0]), int(waypoints[i][1]))
        pt2 = (int(waypoints[i+1][0]), int(waypoints[i+1][1]))
        cv2.line(img, pt1, pt2, (200, 200, 200), 2)
    
    # Draw waypoints
    for wx, wy in waypoints:
        cv2.circle(img, (int(wx), int(wy)), 3, (150, 150, 150), -1)
    
    # Draw current target
    target = controller.get_target_point(robot.x, robot.y)
    cv2.circle(img, (int(target[0]), int(target[1])), 8, (0, 255, 0), 2)
    
    # Draw lookahead circle
    cv2.circle(img, (int(robot.x), int(robot.y)), 
               int(controller.lookahead), (0, 255, 0), 1)
    
    # Draw robot
    robot_pos = (int(robot.x), int(robot.y))
    cv2.circle(img, robot_pos, 8, (255, 0, 0), -1)
    
    # Draw heading indicator
    heading_len = 20
    end_x = int(robot.x + heading_len * np.cos(robot.theta))
    end_y = int(robot.y + heading_len * np.sin(robot.theta))
    cv2.arrowedLine(img, robot_pos, (end_x, end_y), (0, 0, 255), 2)
    
    # Draw velocity vector
    vel_scale = 5
    vel_x = int(robot.x + robot.vx * vel_scale)
    vel_y = int(robot.y + robot.vy * vel_scale)
    cv2.line(img, robot_pos, (vel_x, vel_y), (255, 128, 0), 1)
    
    # Display info
    info_text = [
        f"Pos: ({robot.x:.1f}, {robot.y:.1f})",
        f"Heading: {np.degrees(robot.theta):.1f} deg",
        f"Vel: ({robot.vx:.2f}, {robot.vy:.2f}) m/s",
        f"Waypoint: {controller.current_waypoint_idx}/{len(waypoints)-1}"
    ]
    
    for i, text in enumerate(info_text):
        cv2.putText(img, text, (10, 30 + i * 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    return img

def main():
    # Initialize
    robot = RobotSimulator(x=100, y=300, theta=0)
    controller = PurePursuitController(lookahead_distance=60.0)
    waypoints = create_curved_path()
    controller.set_waypoints(waypoints)
    
    # Simulation parameters
    dt = 0.05  # 50ms time step
    
    # Trajectory history
    trajectory = []
    
    print("Pure Pursuit Simulation Started")
    print("Press 'q' to quit, 'r' to reset")
    
    while True:
        # Compute control
        surge_pwm, sway_pwm, yaw_pwm = controller.compute_control(robot)
        
        # Update robot state
        robot.update(surge_pwm, sway_pwm, yaw_pwm, dt)
        
        # Record trajectory
        trajectory.append((int(robot.x), int(robot.y)))
        if len(trajectory) > 500:
            trajectory.pop(0)
        
        # Visualize
        img = visualize(robot, controller, waypoints)
        
        # Draw trajectory
        for i in range(len(trajectory) - 1):
            cv2.line(img, trajectory[i], trajectory[i+1], (255, 0, 255), 1)
        
        cv2.imshow("Pure Pursuit Simulation", img)
        
        # Check if reached goal
        goal = waypoints[-1]
        dist_to_goal = np.sqrt((robot.x - goal[0])**2 + (robot.y - goal[1])**2)
        if dist_to_goal < 15:
            cv2.putText(img, "GOAL REACHED!", (300, 300), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Pure Pursuit Simulation", img)
            cv2.waitKey(2000)
            break
        
        # Handle keyboard input
        key = cv2.waitKey(int(dt * 1000)) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            robot = RobotSimulator(x=100, y=300, theta=0)
            controller.current_waypoint_idx = 0
            trajectory = []
    
    cv2.destroyAllWindows()
    print("Simulation ended")

if __name__ == "__main__":
    main()