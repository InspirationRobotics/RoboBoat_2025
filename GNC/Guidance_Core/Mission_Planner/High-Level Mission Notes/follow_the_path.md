# Mission Logic for Mapping Migration Patterns (Follow the Path)

Reference link: https://robonation.gitbook.io/roboboat-resources/section-3-autonomy-challenge/3.2-task-descriptions#id-3.2.2-task-2-mapping-migration-patterns-follow-the-path

## Configuration Setup
- GPS Coordinates of point slightly before entrance to the Path (5 meters before along heading of the path)
- General absolute heading pointing in between the first two buoys (degrees would be preferable)
- Whether the Red buoys or Green buoys are located on the right or left sides, respectively.

## Mission Logic
### Assumptions
- We are localized in the general direction of the buoys, with the correct general heading and at the start of the path.

### Logic
1. Find two closest buoys. These buoys should be one green and one red.
2. Calculate the waypoint that passes in between each buoy. Start moving forward, but yaw according to step 3.
3. Based on config file of whether the red/green buoys are on the right/left, yaw to force the correct-colored buoy into the correct side of the screen (left goes on left, right goes on right, etc.). If there are multiple cameras, then same thing, except force the image into the port/starboard camera, respectively.
4. 

