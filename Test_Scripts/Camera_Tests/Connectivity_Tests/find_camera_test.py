"""
Diagnostic test to determine what the __find_cams method does in the FineCamera class.
This is more personal learning than anything else.

This test is considered successful when the results is a list of tuples with three positions in each tuple.
"""
# NOTE: This test is to be done as soon as the cameras are mounted to the ASV.

from API.Camera import find_camera

fC = find_camera.FindCamera()
