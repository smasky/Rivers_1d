from config import DT

class Reach():
    
    def __init__(self, ID, fdNodeInfos, bdNodeInfos):
        
        self.ID = ID
        self.fdNodeInfos = fdNodeInfos
        self.bdNodeInfos = bdNodeInfos
        
        self.SECs = []
    
    def addSec(self, sec):
        self.SECs.append(sec)

class OutsideReach(Reach):
    
    def __init__(self, ID, fdNodeInfos, bdNodeInfos):
        
        super().__init__(ID, fdNodeInfos, bdNodeInfos)
        
        if bdNodeInfos[1] == bdNodeInfos[2]:
            self.reverse = True
        else:
            self.reverse = False
        
class InnerReach(Reach): 
    
    def __init__(self, ID, fdNodeInfos, bdNodeInfos):
        
        super().__init__(ID, fdNodeInfos, bdNodeInfos)
        
    