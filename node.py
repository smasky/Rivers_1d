
class Node():
    def __init__(self, ID):
        self.ID = ID
        self.reaches = []
        self.nRch = 0
        self.neighborID = []
        
    def addRch(self, rvID, rchID, direction):
        '''
        rvID: river ID
        rchID: reach ID
        direction: 0 for upstream, 1 for downstream
        '''
        self.reaches.append( (rvID, rchID, direction) )
        self.nRch +=1
class InnerNode(Node):
    def __init__(self, ID):
        super().__init__(ID)

class OutsideNode(Node):
    def __init__(self, ID):
        super().__init__(ID)
        
        
        
