import numpy as np

class Section():
    def __init__(self, ID, mil, pointData):
        self.ID = ID
        self.mil = mil
        self.Q_Series = 0
        self.Z_Series = 0
        self.Q = 0
        self.Z = 0
        self.nPoint = pointData.shape[0]
        self.xSec = np.ascontiguousarray(pointData[:, 0], dtype=np.float64)
        self.ySec = np.ascontiguousarray(pointData[:, 1], dtype=np.float64)
        self.rSec = np.ascontiguousarray(pointData[:, 2], dtype=np.float64)