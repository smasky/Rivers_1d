class Section():
    def __init__(self, ID, mil, data):
        self.ID = ID
        self.mil = mil
        self.nPoint = data.shape[0]
        self.data = data