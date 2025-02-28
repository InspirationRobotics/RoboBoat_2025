"""Just my idea, making all possible obstacle and target in one class but with different setup"""

class target:
    def __init__(self):
        self.lat        = None  # of center
        self.lon        = None
        self.radius     = None
        self.width      = None
        self.height     = None

        self.obstacle:bool = None
        self.target:bool   = None

    