"""
File that handles all low-level functionality of the camera.
Defines the class Image, which is an object type to hold the information of the image (actual image, as well as dimensions).
Defines the class Camera, which handles all low-level functionality for the cameras on the ASV. This includes handling ML models running on 
camera frames, as well as integration of undistortions and ML model results.
"""

"""
NOTE: This code has not yet been tested. After running tests on the whole camera codebase, the documentation for arguments will have to be 
updated meticulously.
"""
"""
NOTE: This code (and therefore essentially the entire perception core) will not be ready to run until the hardware setup for the cameras is fully known.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Union
from threading import Thread, Lock
from multiprocessing import Process, Value
from Perception.ML_Model_Core.undistort_frame import UndistortedFrame
from Perception.ML_Model_Core.ml_model_api import ML_Model, Results
from API.Camera.find_camera import FindCamera
import time

'''
This is the main camera class that will be used to interact with the camera.
It will handle the camera undistortion and getting the latest frame.
The Camera object is imported into your code and used to get the latest frame.
'''

class Image:
    """
    Image class to store the data of a particular image. Contains two attributes, frame and dimension.

    Args:
        frame (numpy.ndarray): Matrix-stored image from the camera.
    """
    def __init__(self, frame : np.ndarray):
        self.frame = frame
        self.dimensions = (frame.shape[1], frame.shape[0])

class Camera:
    """
    Class to handle low-level functionality of the camera.

    Args:
        camera_id (int, kwarg or positional): Id of the camera to use. Defaults to 0.
        camera_name (str, kwarg or positional): Name of the camera, defaults to "Unknown Camera".
        model (ML_Model, kwarg): ML model to use on camera, defaults to None.
        resolution (Tuple[int, int]): Size of frame of camera, defaults to (1920, 1080).
        fps (int): Frames per second for camera, defaults to 30.
        video_path (str): Path directory to a video file (this is probably for diagnostic purposes), defaults to None.
        camera_type (str): Type of camera (where the camera is located). Defaults to 'port'.
        bus_addr (Tuple[int, int]): Bus address of camera, defaults to None.
    """

    def __init__(self, /, camera_id : int = 0, camera_name : str = "Unknown Camera", *, model : ML_Model = None, 
                 resolution : Tuple[int, int] = (1920, 1080), fps : int = 30, 
                 video_path : str | Path = None, camera_type : str = 'port', 
                 bus_addr : Tuple[int, int] = None):

        self._init_camera_path(camera_id, bus_addr)
        self.video_path = video_path
        self.resolution = resolution
        self.fps = fps
        self.model = model
        self.camera_name = camera_name
        self._load_calibration(camera_type)

        self.stream = False
        self.run_model = False

        self.done_init = False

        self.raw_frame = None
        self.frame = None
        self.results = []
        
        self.camera_lock = Lock()
        self.model_lock = Lock()
        
    def _error(self, message : str):
        """
        Utility function to print out the error message of a specific camera.

        Args:
            message (str): Message to print out to terminal.
        """
        print(f"{self.camera_name} Error: {message}")

    def _info(self, message : str):
        """
        Utility function to notify the user of information pertaining to a specific camera.

        Args:
            message (str): Message to print out to terminal.
        """
        print(f"{self.camera_name} Info: {message}")

    def _init_camera_path(self, camera_id : int, bus_addr : Tuple[int, int]):
        """
        Loads the path for a particular video device, given the camera ID and bus address.
        Puts this camera path in an attribute of the Camera class (Camera.camera_path).

        Args:
            camera_id (int) : Camera ID.
            bus_addr (tuple): Address of the bus, in the format (int, int).
        """

        if bus_addr is not None:
            fc = FindCamera()
            self.camera_path = fc.find_cam(bus_addr[0], bus_addr[1])
            if self.camera_path is None:
                raise ValueError("Error: Camera not found")
        else:
            self.camera_path = f'/dev/video{camera_id}'
    
    def _load_calibration(self, camera_type : str):
        """
        Initializes the distortion and intrinsic matrices for a particular camera, given where the camera is on the ASV.
        Also undistorts the frame based on the matrices loaded. Stores this frame (UndistoredFrame-type object) in an
        attribute of the Camera class (Camera.undistorted_frame).

        Args:
            camera_type (str): Camera to load the calibration for ("port", "starboard", "wide").
        """
        pre_path = Path(__file__).parent.absolute() / "config"
        if not (pre_path / camera_type).exists():
            camera_type = "port"
        dist_calibration_path = pre_path / Path(f'{camera_type}/camera_distortion_matrix.txt')
        int_calibration_path = pre_path / Path(f'{camera_type}/camera_intrinsic_matrix.txt')
        self.undistorted_frame = UndistortedFrame(int_calibration_path, dist_calibration_path, self.resolution)

    def load_model_object(self, model_object : ML_Model):
        """
        Passes a ML model object into an attribute of the Camera class.

        Args:
            model_object (ML_Model): ML model object to be loaded into the camera.
        """
        if not isinstance(model_object, ML_Model):
            self._error("Must be of ML_Model type")
            return
        with self.model_lock:
            self.model = model_object

    def load_model(self, model_path : str | Path, model_type : str = "YOLO", *, half_precision: bool = False):
        """
        Load a ML model into an attribute of the Camera class (Camera.model), given the model path and type.

        Args:
            model_path (str): Path directory to the model.
            model_type (str): Type of model, defaults to 'YOLO'.
            half_precision (kwarg, bool): Whether or not to set model to half precision, defaults to False.
        """

        if not isinstance(model_path, Path):
            model_path = Path(model_path)
        if not model_path.exists():
            pre_path = Path(__file__).parent.absolute() / "Models"
            model_path = pre_path / model_path
            if not model_path.exists():
                self._error("Model path does not exist")
                return
        with self.model_lock:
            self.model = ML_Model(model_path, model_type, half_precision=half_precision)

    def switch_model_object(self, model_object : ML_Model):
        """
        Switch the current ML model to a different ML model.

        Args:
            model_object (ML_model): New ML_Model-type object to laod into the Camera class (Camera.model).
        """
        if not isinstance(model_object, ML_Model):
            self._error("Must be of ML_Model type")
            return
        with self.model_lock:
            self.model = model_object

    def switch_model(self, model_path : str | Path, model_type: str = "YOLO", *, half_precision: bool = False):
        """
        Switches the current model weights to a new set of weights.

        Args:
            model_path (str): Path directory to the file containing the model to switch to.
            model_type (str): Type of model (YOLO or TensorRT).
            half_precision (kwarg, bool): Whether to use half-precision or not. Defaults to False.
        """
        if self.model is None:
            self.load_model(model_path, model_type, half_precision=half_precision)
            return
        if not isinstance(model_path, Path):
                model_path = Path(model_path)
        if not model_path.exists():
            pre_path = Path(__file__).parent.absolute() / "models"
            model_path = pre_path / model_path
            if not model_path.exists():
                self._error("Model path does not exist")
                return
        with self.model_lock:
            self.model.switch_model(model_path, model_type, half_precision=half_precision)

    def start(self):
        """
        Starting the camera stream, and the model to run on the stream, if applicable.
        """
        self.start_stream()
        if self.model:
            self.start_model()

    def stop(self):
        """
        Stopping the camera stream, and the YOLO model, if necessary.
        """
        self.stop_model()
        self.stop_stream()

    def start_model(self):
        """
        Starts the YOLO model by initiating a thread to continually pass in a frame and get back results.
        """
        if not self.stream:
            self._error("Stream not started, cannot start model thread")
            return
        if self.model is None:
            self._error("No model loaded, cannot start model thread")
            return
        if self.run_model:
            self._error("Model thread already running, skipping...")
            return
        self.run_model = True
        self.model_thread = Thread(target=self._model_background_thread)
        self.model_thread.start()
        self._info("Model thread started")

    def stop_model(self):
        """
        Stops YOLO model by ending model thread.
        """
        self.run_model = False
        try:
            self.model_thread.join()
        except:
            return
        self.results = []
        self._info("Model thread stopped")

    def start_stream(self):
        """
        Start the camera stream by initiating a thread to read frames from the camera.
        """
        if self.stream:
            self._error("Stream already started")
            return
        self.warmup()
        self.stream = True
        self.camera_thread = Thread(target=self._camera_background_thread)
        self.camera_thread.start()
        self._info("Stream started")

    def stop_stream(self):
        """
        Stops the camera stream by joining the camera stream thread.
        """
        self.stream = False
        self.done_init = False
        try:
            self.camera_thread.join()
        except:
            return
        self._info("Stream stopped")

    def get_size(self, undistort = True) -> Tuple[int, int]:
        """
        Gets the size of the frame -- if the image has been undistorted, returns the ROI, else just returns the resolution (frame size) of raw image.

        Args:
            undistort (bool): Whether or not to return the undistorted frame size. Defaults to True.
        Returns:
            Tuple: The (width, height) in pixels of the frame. Width is x, height is y.
        """
        if undistort:
            return self.undistorted_frame.get_roi_dimensions()
        return self.resolution
    
    def warmup(self, frame : np.ndarray = None) -> np.ndarray:
        """
        Warms up both the undistort function and the ML model. Takes a frame, undistorts it, and then runs the model 
        on the undistorted frame.

        Args:
            frame (numpy.ndarray): Temporary frame to warm up the undistort functionality, ML model. Defualts to None.
        """
        temp_frame = self._warmup_undistort(frame)
        if self.model is not None:
            self.model.predict(temp_frame)

    # NOTE: Not sure what the point of warming up is -- my guess is that the cameras and all of their functionalities (threads, etc.) should be 
    # fully up and running before any actual missions start, so no potentially important data is lost.

    def _warmup_undistort(self, frame : np.ndarray = None) -> np.ndarray:
        """
        Warm up the undistort function by sending it a frame. If no frame is passed in, then it automatically creates a garbage frame
        (frame with randomly chosen pixels). 

        Args:
            frame (numpy.ndarray): Frame to undistort. Defaults to None.
        Returns:
            warmup_frame (numpy.ndarray): Undistorted frame.
        """
        if frame is None:
            # Make a frame with random values
            warmup_frame = np.random.randint(0, 255, (self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        else:
            warmup_frame = frame
        warmup_frame = self.undistorted_frame.undistort(warmup_frame, with_cuda=True)
        self._info("Undistortion warmed up...")
        return warmup_frame

    def get_latest_frame(self, *, undistort = True, with_cuda = True) -> Union[Image, None]:
        """
        Returns the most recent frame from the camera. Checks if there is a raw frame (Camera.raw_frame) -> if there is, it returns that then resets the raw frame.
        If not, then checks for a processed frame and returns that (Camera.frame). If there is neither, returns None.


        Args:
            undistort (kwarg, bool): Whether or not to undistort the image before returning, defaults to True.
            with_cuda (kwarg, bool): Whether or not to use CUDA functionality, defaults to True.
        Returns:
            Image: Either None or an Image-type object that contains the latest (raw or processed (undistorted)) frame.
        """
        with self.camera_lock:
            if not self.done_init:
                return None
            # If there is a raw frame use that and then reset it. 
            # Otherwise check if there is a processed frame and use that. If not return None.
            if self.raw_frame is not None:
                frame = self.raw_frame
                self.raw_frame = None
            elif self.frame is not None:
                return Image(self.frame)
            else:
                return None
        if undistort:
            frame = self.undistorted_frame.undistort(frame, with_cuda = with_cuda)
        self.frame = frame
        return Image(frame)
    
    def get_latest_model_results(self) -> List:
        """
        Returns the Camera.results attribute (list-type), which are the results from the ML model after running on the most recent frame.
        """
        with self.model_lock:
            return self.results
        
    def draw_model_results(self, frame, results : List[Results] = None, confidence=0.5):
        """
        Draw the results from the ML model on the frame.

        Args:
            frame: Frame to draw on.
            results (list): Results from ML model, defaults to None.
            confidence (float): Confidence threshold for drawing items, defaults to 0.5.

        Returns:
            frame (numpy.ndarray): Modified frame.
        """
        if results is None:
            results = self.get_latest_model_results()
        for result in results:
            names = result.names
            for box in result.boxes:
                conf = box.conf.item()
                # Only draw box around object if the confidence of detection is above the confidence threshold.
                if conf < confidence:
                    continue
                x1, y1, x2, y2 = box.xyxy.cpu().numpy().flatten()
                cls_id = box.cls.item()
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, f"{names[cls_id]}: {conf:.2f}", (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame
    
    def _model_background_thread(self):
        """
        Callback function to run on a camera stream.
        Passes in the raw camera frame for the model, and gets back the results.
        Stores the model's predictions (results) in an attribute of the Camera class.
        """
        while self.run_model:
            with self.camera_lock:
                frame = self.frame
            if self.stream:
                with self.model_lock:
                    if self.model is not None:
                        self.results = self.model.predict(frame)
            time.sleep(1/(self.fps))

    def _camera_background_thread(self):
        """
        Callback function for streaming on the camera.
        Captures the stream using either OpenCV or GStreamer.
        Reads the video object, puts it in self.raw_frame (attribute of Camera Class).
        Handles cleaning up the streaming pipeline if there is no data to collect.
        """

        if self.video_path == None:
            capture_flag = f'v4l2src device={self.camera_path} ! image/jpeg, width={self.resolution[0]}, height={self.resolution[1]}, framerate={self.fps}/1 ! jpegdec ! videoconvert ! video/x-raw, format=BGR ! appsink'
            try:
                self.cap = cv2.VideoCapture(capture_flag)
            except:
                self._error("Failed to open camera using GStreamer; Defaulting to OpenCV")
                self.cap = cv2.VideoCapture(self.camera_path)
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        else:
            self.cap = cv2.VideoCapture(self.video_path)
        self.done_init = True
        while self.stream:
            with self.camera_lock:
                ret, self.raw_frame = self.cap.read()
                if not ret:
                    self._error("Failed to capture image")
                    self.stream = False
                    break
            time.sleep(1/(self.fps))

        self.cap.release()
        return