from setuptools import setup, find_packages

setup(name = "GNC_Core", 
      version = "0.1",
      description = "Team Inspiration's RoboBoat Guidance, Navigation, and Control Package",
      author = "Keith Chen",
      packages = find_packages(include=["Control_Core", "Guidance_Core", "Nav_Core"]),
      # NOTE: Install dependencies not currently correct.
      install_requires=['comms_core', 'pyserial', 'scipy', 'filterpy', 'pynmeagps']
)