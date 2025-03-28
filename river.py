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
        
        self.RCHs_ = {}  # For C++
        
        self.outRchIDs = []
        self.inRchIDs = []
        
        self.QQ = {}
        self.ZZ = {}
        
        self.nRch = 0
        self.nOutRch = 0
        self.nInRch = 0
        self.nSec = 0
    
    def initSec(self, initQ, initZ, nt):
        
        for ID, sec in self.SECs.items():
            #set initial Q and Z for each section
            sec.Q_Series = np.ascontiguousarray(np.ones(nt) * initQ)
            botZ = np.min(sec.ySec)
            sec.Z_Series = np.ascontiguousarray(np.ones(nt) * (botZ + initZ))
            
            #compute the hydraulic list for each section
            # xSec, ySec = sec.xSec, sec.ySec
            # #TODO Updating: default, the water only flow through the range of left and right highest point
            # minI = np.argmin(ySec)
            # leftHI = np.argmax(ySec[:minI])
            # rightHI = np.argmax(ySec[minI:]) + minI
            
            # effect_ySec = ySec[leftHI:rightHI+1]
            # effect_xSec = xSec[leftHI:rightHI+1]
            
            # i = 0; equalY = []
            # while i < len(effect_ySec):
            #     y = effect_ySec[i]
            #     j = i
            #     while j+1 < len(effect_ySec) and effect_ySec[j+1] == y:
            #         j += 1
            #     if j > i:
            #         equalY.append((i, j, y))
            #     i = j+1
            
        
            # calYSec = np.ascontiguousarray(np.unique(np.concatenate((effect_ySec, 
            #                 [effect_ySec[j] + 1e-6 for i, j, y in equalY])), axis=0))
            # calYSec.sort()

            # areaList = np.ascontiguousarray(np.zeros(len(calYSec)))
            # wpList = np.ascontiguousarray(np.zeros(len(calYSec)))
            # bsList = np.ascontiguousarray(np.zeros(len(calYSec)))
            # for n, y in enumerate(calYSec):
            #     area = 0
            #     wp = 0
            #     bs = 0
            #     for i in range(len(effect_xSec)-1):
            #         x1 = effect_xSec[i]
            #         x2 = effect_xSec[i+1]
            #         y1 = effect_ySec[i]
            #         y2 = effect_ySec[i+1]
                    
            #         if y <= min(y1, y2):
            #             continue
                    
            #         delta1 = y - y1
            #         delta2 = y - y2
            #         delta_x = x2 - x1
                    
            #         if delta1 < 0:
            #             delta1 = 0
            #             delta_x = delta2 / (y1 - y2) * delta_x
            #         elif delta2 < 0:
            #             delta2 = 0
            #             delta_x = -delta1 / (y1 - y2) * delta_x
                    
            #         bs = bs + delta_x
            #         area = area + 0.5 * (delta1 + delta2) * delta_x
            #         wp = wp + np.sqrt(pow(delta1 - delta2, 2) + pow(delta_x, 2))
                
            #     areaList[n] = area
            #     wpList[n] = wp
            #     bsList[n] = bs

            # sec.hydraulicInfo['nY'] = calYSec.size
            # sec.hydraulicInfo['yList'] = calYSec
            # sec.hydraulicInfo['areaList'] = areaList
            # sec.hydraulicInfo['wpList'] = wpList
            # sec.hydraulicInfo['bsList'] = bsList
              
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
    
    