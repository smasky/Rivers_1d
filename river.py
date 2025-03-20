import bisect
from .section import Section
from .reach import Reach
class River():
    
    def __init__(self, name, ID, length):
        
        self.name = name
        self.length = length
        self.ID = ID
        
        self.rchs = []
        self.secs = []
        self.Mis = None
        
        self.nRch = 0
        self.nSec = 0
    
    def addRch(self, fdMi, bdMi, fdNode = None, bdNode = None):
        
        self.nRch += 1
        rch = Reach(self.nRch, fdMi, bdMi, fdNode, bdNode)
        self.rchs.append(rch)
        
    def addSec(self, mil, data):
        
        self.nSec +=1
        sec = Section(self.nSec, mil, data)
        self.secs.append(sec)
    
    def generateMis(self):
        
        self.Mis = [0.0]
        
        for rch in self.reaches:
            self.Mis.append(rch.bdMi)
    
    