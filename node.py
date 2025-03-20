
class Node():
    def __init__(self, ID):
        self.ID = ID
        self.reaches = []
        self.nRch = 0
        
    def addRch(self, rvID, rchID):
        self.reaches.append( (rvID, rchID) )
        self.nRch +=1
class InnerNode(Node):
    def __init__(self, ID):
        super().__init__(ID)

class OutsideNode(Node):
    def __init__(self, ID):
        super().__init__(ID)
        
        
        
