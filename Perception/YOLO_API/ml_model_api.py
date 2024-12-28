"""
File that defines the class ML_Model, which handles the running of a YOLO model or TensorRT model (only for NVIDIA GPUs) on a camera stream.
"""

import cv2
import time
import numpy as np
from typing import List
from pathlib import Path
from threading import Thread, Lock
from ultralytics import YOLO
from ultralytics.engine.results import Results

# NOTE: Unsure whether the TensorRT methods have been tested yet.

class ML_Model:
    """
    Class that handels the loading and running of ML models on frames (either TensorRT or YOLO).

    Args:
        model_path (str): Path directory to the model.
        model_type (str): Type of model, defaults to 'YOLO'.
        half_precision (kwarg, bool): Whether or not to set model to half precision, defaults to False.
    """

    def __init__(self, model_path: str | Path, model_type: str = "YOLO", *, half_precision: bool = False):
        self._set_params(model_path, model_type, half_precision=half_precision)

    """
    Half-precision means that the model uses FP16 (16-bit floating point numbers) rather than FP32 (32-bit) to store numbers.
    This makes models much less computationally expensive, but also runs the risk of numerical instability due to rounding issues.
    """

    def switch_model(self, model_path: str | Path, model_type: str = "YOLO", *, half_precision: bool = False):
        """
        Switches current instance of ML_Model to a different model (different weights to use). Resets the model and then uploads the new weights.

        Args:
            model_path (str): Model weights to upload (.engine or .pt).
            model_type (str): Model type (TensorRT or YOLO).
            half_precision (kwarg, bool): Whether or not to store model with half precision. Defaults to False.
        """

        self._reset_params()
        self._set_params(model_path, model_type, half_precision=half_precision)
        print(f'Model switched successfully to: {model_type} \n \
              With weights: {model_path}')

    def _set_params(self, model_path: str | Path, model_type: str, *, half_precision):
        """
        Sets the parameters of the ML model by finding the name of the model (either 'YOLO' or 'tensorrt') and the path 
        to the model's parameters. It then stores these as attributes of the ML_Model class (ML_Model.model_path, ML_Model_type, 
        ML_model.half_precision).

        Args:
            model_path (str): Path directory to the .pt file (YOLO) or .engine file (tensorrt).
            model_type (str): Type of model to run.
            half_precision (kwarg, bool): Whether or not to run the model at half precision (saves memory footprint/allows for larger training size).
        """

        if not isinstance(model_path, Path):
            model_path = Path(model_path)
        self.model_path = model_path
        self.model_type = model_type.lower()
        self.half_precision = half_precision
        self.model = None
        self._async_init_model()

    def _async_init_model(self):
        """
        Asynchronously initializes ML model.
        What this really means is that when this function is called, it starts and then stops a thread whose target is _init_model().
        This enables the initialization of the ML model independent of when the ML model needs to start predicting/returning results.
        """
        init_thread = Thread(target=self._init_model)
        init_thread.start()
        init_thread.join()

    def _init_model(self):
        """
        Initializes the ML model, by making an instance of the YOLO class. If the file is for the TensorRT model, it will 
        nonetheless run the model by creating an instance of the YOLO class.
        Configures the ML model's task (detect), along with other settings.
        """

        if self.model_type == "yolo":
            if self.model_path.suffix != ".pt":
                raise ValueError("Model path must be a .pt file for YOLO models")
            self.model = YOLO(self.model_path, task="detect", verbose=False)
        elif self.model_type == "tensorrt":
            if self.model_path.suffix != ".engine":
                raise ValueError("Model path must be a .engine file for TensorRT models. Please use \
                                    the create_tensorrt_model() to generate a TensorRT model from the .pt file.")
            self.model = YOLO(self.model_path, task="detect", verbose=False)
        else:
            raise ValueError("Invalid model type. Please choose between YOLO and TensorRT")
        print(f"Model initialized successfully: {self.model_type}")

    def _reset_params(self):
        """
        Deletes the model, and stores None in the attribute in which the YOLO model was saved (ML_Model.model). 
        """
        del self.model
        self.model = None

    def predict(self, frame: np.ndarray) -> list[Results]:
        """
        Passes in a frame to the ML model and gets back the results.

        Args:
            frame (np.ndarray): Raw frame to run inference on.

        Returns:
            results (list[Results]): A list of the results (a custom class created by YOLO) returned by the model.
        """
        if self.model is None or frame is None:
            return []
        results: list[Results] = self.model(frame, half=self.half_precision)
        return results

    def create_tensorrt_model(self, model_path: str | Path = None):
        """
        Creates a TensorRT model from a YOLO model (.pt) file, given the model path.

        Args:
            model_path (str): Path directory to the .pt file to transform.
        """
        if model_path == None:
            model_path = self.model_path
        print("Creating TensorRT model...please be patient")
        model = YOLO(model_path)
        model.export(format="engine", half=self.half_precision)
        print("Model created successfully")

if __name__ == "__main__":
    model = ML_Model("models/yolov8n.pt")
    model.create_tensorrt_model(half_precision=True)