"""
File that defines UndistortedFrame, a class that handles the undistortion of camera frames on the ASV's cameras.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple

class UndistortedFrame:
    """
    Class that contains functions to undistort camera frames.

    Args:
        intrinsics (str): Path in the form of a string, that leads to a .txt file containing the intrinsic matrix for the camera.
        distortion (str): Path in the form of a string, that leads to a .txt file containing the distortion matrix for the camera.
        size (tuple): Resolution/size of the camera frame, defaults to (1920, 1080).
    """
    def __init__(self, intrinsics : Path | str | np.ndarray, distortion : Path | str | np.ndarray, size : Tuple[int, int] = (1920, 1080)):
    
        if isinstance(intrinsics, (Path, str)):
            intrinsics = np.loadtxt(intrinsics)
        if isinstance(distortion, (Path, str)):
            distortion = np.loadtxt(distortion)

        self.intrinsics = intrinsics
        self.dist = distortion
        self.size = size

        # Find the optimal image based on intrinsic + distortion matrices.
        # Calculate ROI (Region of Interest) to ensure there is no invalid pixel information after distortion.
        # Calculation of ROI (in this case) preserves the number of pixels (since the argument is 1 rather than 0 -- 0 emphasizes optimal undistortion.)
        self.new_camera_matrix, self.roi = cv2.getOptimalNewCameraMatrix(intrinsics, distortion, size, 1, size)

        # Finds remapping matrices for x and y pixel values to undistort the image -- allows for one lookup function for all pixels rather
        # than separate calculations for all pixels.
        self.mapx, self.mapy = cv2.initUndistortRectifyMap(intrinsics, distortion, None, self.new_camera_matrix, size, 5)

    def undistort_only(self, frame, *, cuda = False):
        """
        Undistorts the image without cropping the image based on the dimensions of the ROI.
        Either returns the image via normal OpenCV remap or via OpenCV CUDA remap.

        Args:
            frame (numpy.ndarray): Frame to undistort.
            cuda (kwarg, bool): Whether or not to utilize CUDA (only works with NVIDIA GPUs).

        Returns:
            numpy.ndarray: Undistorted image.
        """
        if cuda:
            cuMapX = cv2.cuda.GpuMat(self.mapx)
            cuMapY = cv2.cuda.GpuMat(self.mapy)
            cuFrame = cv2.cuda.GpuMat(frame)
            undistorted_img = cv2.cuda.remap(cuFrame, cuMapX, cuMapY, cv2.INTER_LINEAR)
            return undistorted_img.download()
        return cv2.remap(frame, self.mapx, self.mapy, cv2.INTER_LINEAR)

    def crop_roi(self, frame):
        """
        Crop the passed in frame to only the ROI (Region of Interest).

        Args:
            frame (numpy.ndarray): Frame to crop

        Returns:
            numpy.ndarray: Cropped frame (frame w/ new dimensions based on ROI specs)
        """
        x, y, w, h = self.roi
        return frame[y:y+h, x:x+w]
    
    def get_roi_dimensions(self):
        """
        Gets the dimensions of the ROI (w, h).

        Returns:
            tuple: (width, height) of ROI
        """
        x, y, w, h = self.roi
        return ((x+w)-x, (y+h)-y)

    def undistort(self, frame, *, with_cuda = False):
        """
        Undistort the image, and crop the image to the dimensions of the ROI (region of interest).

        Args:
            frame (numpy.ndarray): Frame to undistort.
            with_cuda (kwarg, bool): Whether or not to use CUDA (only works on NVIDA GPUs).
        """
        undistorted_img = self.undistort_only(frame, cuda = with_cuda)
        return self.crop_roi(undistorted_img)