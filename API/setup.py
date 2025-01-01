from setuptools import setup, find_packages

setup(name = "Sensor_API_Core", 
      version = "0.1",
      description = "Team Inspiration's RoboBoat Low-Level Sensor Package",
      author = "Keith Chen, Leonard Wright",
      packages = find_packages(include=["Camera", "GPS", "IMU", "Motors", "Util"]),
      # NOTE: Install dependencies not currently correct.
      install_requires = ['comms_core', 'pyserial', 'scipy', 'filterpy', 'pynmeagps']
)