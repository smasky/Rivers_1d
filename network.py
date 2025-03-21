import re
import numpy as np

from river import River
from reach import Reach
from node import InnerNode, OutsideNode

class Network():
    def __init__(self, riverPath, nodePath, sectionPath):
        self.NA_ID_RV = {}
        self.RV_ND = {}
        self.ID_ND = 1
        self.ID_RV = 1
        self.NDs = {}
        self.RVs ={}
        
        self.readRiverInfo(riverPath)
        self.readNodeInfo(nodePath)
        
        self.generateRchAndNode()
        self.readSecInfo(sectionPath)
        a = 1
    
    def readRiverInfo(self, path):
        
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().split()
                name = line[0]
                length = float(line[1])
                self.NA_ID_RV[name] = self.ID_RV
                self.RV_ND.setdefault(self.ID_RV, [])
                
                self.RVs[self.ID_RV] = River(name, self.ID_RV, length)
                
                self.ID_RV += 1

    def readNodeInfo(self, path):
        
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line != '':
                    line = line.strip().split()
                    num = int(len(line) / 2)
                    
                    for i in range(num):
                        name = line[2 * i]
                        mileage = float(line[2 * i + 1])
                        ID = self.NA_ID_RV[name]
                        
                        self.RV_ND[ID].append((mileage, self.ID_ND, 1))
                        
                        self.ID_ND += 1
    
    def readSecInfo(self, path):
        
        with open(path, 'r') as f:
            lines = f.readlines()

            totalL = len(lines)
            i=0
            while True:
                
                if i >= totalL:
                    break
                
                line = lines[i]
                match = re.match("Name\s*(\w+)", line)
                
                if match:
                    name = match.group(1); rvID = self.NA_ID_RV[name]
                    i += 1
                    mil = float(re.match("Mileage\s*(\d+(\.\d+)?)", lines[i]).group(1))
                    i += 1
                    rough = float(re.match("Roughness\s*(\d+(\.\d+)?)", lines[i]).group(1))
                    i += 1
                    num = int(re.match("Num\s*(\d+)", lines[i]).group(1))
                    i += 1
                    
                    data = np.zeros((num, 3), dtype = np.float32)
                    
                    for j in range(num):
                        
                        line = lines[i].strip().split()
                        if len(line) == 2:
                            x, y = line
                            r = rough
                        else:
                            x, y, r = line
                        
                        data[j] = [x, y, r]
                    
                        i += 1
                    
                    self.RVs[rvID].addSec(mil, data)

                else:
                    i += 1
                        
    def generateRchAndNode(self):
    
        for rvID, infos in self.RV_ND.items():
            
            ID_RCH = 1
            
            length = self.RVs[rvID].length
            
            infos.sort()
            
            if infos[0][0] >= 0.0:
                self.ID_ND += 1
                infos.insert(0, (0.0, self.ID_ND, 0))
            
            if infos[-1][0] <= length:
                self.ID_ND += 1
                infos.append((length, self.ID_ND, 0))

            for i in range( len(infos) -1 ):
                
                fdMi = infos[i][0]
                bdMi = infos[i+1][0]
                
                if infos[i][1] in self.NDs:
                    fdNode = self.NDs[infos[i][1]]
                else:
                    fdNode = InnerNode(infos[i][1]) if infos[i][2] else OutsideNode(infos[i][1])
                    self.NDs[infos[i][1]] = fdNode
                    
                if infos[i+1][1] in self.NDs:
                    bdNode = self.NDs[infos[i+1][1]]
                else:
                    bdNode = InnerNode(infos[i+1][1]) if infos[i+1][2] else OutsideNode(infos[i+1][1])
                    self.NDs[infos[i+1][1]] = bdNode
                    
                self.RVs[rvID].addRch(fdMi, bdMi, fdNode, bdNode)
                fdNode.addRch(rvID, ID_RCH)
                bdNode.addRch(rvID, ID_RCH)