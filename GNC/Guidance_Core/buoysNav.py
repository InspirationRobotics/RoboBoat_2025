from GNC.Nav_Core.info_core import infoCore
from GNC.Guidance_Core.mission_helper import MissionHelper

class BuoyPath:
    def __init__(self):
        self.config     = MissionHelper()
        print("Loading Config file ...")
        self._loadConfig()  


        self.info       = infoCore(modelPath=self.config.model_path,labelMap=self.config.label_map)

        self.redBuoy    = -1.0
        self.greenBuoy  = -1.0
        self.yelloBuoy  = -1.0
        self.obstacle   = -1.0



        pass

    def _loadConfig(self,file_path:str = "GNC/Guidance_Core/Config/barco_polo.json"):
        self.config.parse_config_data(self.config.load_json(path=file_path))

    def run(self):
        """
        DEPRECATED!
        This is the main logic of avoiding buoys
        Our boat only go forward when there's no buoy in the screen
        if on left, turn right, vise versa
        SPECIAL CASE: when encountering yellow buoys or obstacle boat, we compare, compute and find the biggest gap, reset two identifier to control the boat,
        TODO The ability to find biggest gap
        """
        """
        New way of navigation: use a stack, set final location, use computer vision to add more location to stack, read from stack, check distance, remove location from stack
        TODO able to use cv to find midpoint for next location,
        TODO able to find the angle of the object respect to current heading
        DFOV / HFOV / VFOV 100° / 82° / 56°
        angle = (x_rel - 0.5) x HFOV = (x_rel - 0.5) x 82
        """
        
    