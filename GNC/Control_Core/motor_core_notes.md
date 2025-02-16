Problem: We wish to be able to use GPS coordinates in order to accurately localize to a given waypoint.

Assumptions: We have the current position (lat, lon), current heading (absoulte heading in degrees), and target position (lat, lon).

## Steps:
solve_wp_bearing (current_pos, target_pos) -> target_bearing (absoulte heading in degrees).
hold_logic (current_pos, current_heading, target_pos, target_bearing) -> target_vector (vx, vy in meters), target_rotation (scaled amount of rotation needed in radians), target_dist (meters from current position)
calc_motor_power (target_vector, target_rotation) -> motor_power (list of magnitudes between -1 and 1 for all thrusters)

## Function Specifics:
Brief summary of each individual function. The variable names are not exactly the same, but signify what the variable represents.
See motor_core.py for code.

### solve_wp_bearing()
```python
absolute_bearing = bearing(current_lat, current_lon, target_lat, target_lon)
return absolute_bearing
```

### hold_logic()
```python
# vy is forward, vx is lateral
vy, vx, dist = vector_to_target(current_pos, target_pos, current_heading)

# Normalize components of vector so that the parts add to one.
scale = min(dist/3, 1)
target_vector = [vx*scale, vy*scale]

# TEMPORARY [OR MAYBE NOT] -> set the lateral component to 0. Only go forward if the vector is positive.
target_vector[0] = 0
target_vector[1] = target_vector[1] * 0.75 if target_vector[1] > 0 else 0

target_rotation = calc_rotation(current_heading, target_heading)
return target_vector, target_rotation, dist
```

### calc_rotation()
```python
# Mod differences b/w target and current heading, compare which one is smaller to determine direction.
cw = (target_heading - current_heading) % 360
ccw = (current_heading - target_heading) % 360
direction = 1 if cw <= ccw else -1
distance = min(cw, ccw)

target_rotation = radians(direction * distance) * 0.5 # This is a scale, don't know if it is actually necessary
return target_rotation 
```

### calc_motor_power()