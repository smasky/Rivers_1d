import numpy as np
from section import Section
from reach import Reach, OutsideReach, InnerReach
class River():
    
    def __init__(self, name, ID, length):
        
        self.name = name
        self.length = length
        self.ID = ID
        
        self.MILtoSEC_ID = {}
        
        self.nodeInfos = []
        
        self.SECs = {}
        self.RCHs = {}
        self.BDs = {}
        self.RCHs_ = {}
        
        self.outRchIDs = []
        self.inRchIDs = []
        
        self.QQ = {}
        self.ZZ = {}
        
        self.nRch = 0
        self.nOutRch = 0
        self.nInRch = 0
        self.nSec = 0
    
    def addNode(self, mil, nodeID, T):
        
        self.nodeInfos.append( (mil, nodeID, T) )
        
    def addRch(self, fdMi, bdMi, fdNode = None, bdNode = None):
        
        self.nRch += 1
        self.nInRch += 1
        
        rch = Reach(self.nRch, fdMi, bdMi, fdNode, bdNode)
        self.rchs.append(rch)
        
    def addSec(self, mil, data):
        
        self.nSec +=1 #ID
        self.MILtoSEC_ID[mil] = self.nSec #ID
        
        sec = Section(self.nSec, mil, data)
        self.SECs[self.nSec] = sec
        
        self.QQ[mil] = sec.Q
        self.ZZ[mil] = sec.Z
    
    def addBoundary(self, mil, T, OBdata, nt):
        
        timeSer = np.arange(0, nt, 1)
        simData = np.zeros((nt, 1))
        
        insertValue = np.interp(timeSer, OBdata[:, 0], OBdata[:, 1])
        simData[:, 0] = insertValue
        
        simData = np.ascontiguousarray(simData)
        
        if mil == self.length:
            self.BDs[1] = (self.ID, T, simData, OBdata)
        else:
            self.BDs[0] = (self.ID, T, simData, OBdata)
                        
    def reachInit(self):
        
        self.nodeInfos.sort()
        
        ID_RCH = 0
        
        if self.nodeInfos[0][0] > 0.0:
            self.nOutRch += 1
            self.nodeInfos.insert( 0, (0.0, 0, 1) )
            
        if self.nodeInfos[-1][0] < self.length:
            self.nOutRch += 1
            self.nodeInfos.append( (self.length, 1, 1) )
        
        for i in range(len(self.nodeInfos)-1):
            
            ID_RCH += 1
            
            if( self.nodeInfos[i][-1] or self.nodeInfos[i+1][-1] ):
                
                if self.nodeInfos[i+1][1] == self.nodeInfos[i+1][2]:
                    boundInfos = self.BDs[1]
                else:
                    boundInfos = self.BDs[0]
                    
                reach = OutsideReach(ID_RCH, self.nodeInfos[i], self.nodeInfos[i+1], boundInfos)
                
                self.outRchIDs.append(ID_RCH)
            else:
                reach = InnerReach(ID_RCH, self.nodeInfos[i], self.nodeInfos[i+1])
                self.inRchIDs.append(ID_RCH)
                
            self.RCHs[ID_RCH] = reach
            
        self.nRch = ID_RCH
        
    def getRch(self, rchID):
        return self.rchs[rchID - 1]
    
    def generateMis(self):
        
        self.Mis = [0.0]
        
        for rch in self.reaches:
            self.Mis.append(rch.bdMi)
    
    