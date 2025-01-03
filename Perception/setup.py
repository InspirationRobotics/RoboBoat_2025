from setuptools import setup, find_packages

setup(name = "Perception_Core", 
      version = "0.1",
      description = "Team Inspiration's RoboBoat Processing and Inference Package",
      author = "Keith Chen",
      packages = find_packages(include=["ML_Model_Core", "Perception_Core"]),
      # NOTE: Install dependencies not currently correct.
      install_requires=['comms_core', 'pyserial', 'scipy', 'filterpy', 'pynmeagps']
)