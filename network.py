import re
import numpy as np

from river import River
from river1D import Section, OuterReach, InnerReach
from scipy.linalg import solve, lu
class Network():
    def __init__(self, riverPath, nodePath, sectionPath, boundaryPath):
        
        self.nRV = 0
        self.nInND = 0 
        
        self.NAtoID_RV = {}
        self.RVs = {}
        
        self.t = 1
        self.nt = 2000
        self.dt = 1.0
        self.dev_sita = 0.75
        self.Q_init = 5.0
        self.Z_init = 2.0
        
        self.readRiverInfo(riverPath)
        self.readNodeInfo(nodePath)
        self.readSecInfo(sectionPath)
        self.readBoundary(boundaryPath)
        
        self.riverInit()
    
    def simPressimann(self):
        
        a =  np.ascontiguousarray(np.ones(self.nt))*10
        
        b =  np.ascontiguousarray(np.ones(self.nt))
        
        for rvID, rv in self.RVs.items():
            
            self.extendTimeSeries(rv)
            
            for secID, sec in rv.SECs.items():
                mil = sec.mil
                for rchID, rch in rv.RCHs.items():
                    fdMil = rch.fdNodeInfos[0]
                    bdMil = rch.bdNodeInfos[0]
                    
                    if mil >= fdMil and mil <= bdMil:
                        cSec = Section.createSection(secID, rchID, rvID, mil, sec.nPoint, sec.xSec, sec.ySec, sec.rSec, self.nt, sec.Q_Series, sec.Z_Series)
                        rch.addSec(cSec)
                    
            for rchID in rv.outRchIDs:
                rch = rv.RCHs[rchID]
                if rch.reverse == True:
                    rch.SECs.reverse()
                
                #temp
                if rch.fdNodeInfos[0] == 0.0:
                    c = a
                    T = rv.BDs[0].T
                else:
                    c = b
                    T = rv.BDs[1].T
                
                rch_ = OuterReach.createOuterReach(rvID, rchID, len(rch.SECs), rch.fdNodeInfos[1], rch.bdNodeInfos[1], 
                                                   rch.SECs, c, self.dev_sita, self.dt, self.t, rch.reverse, T)
                rv.RCHs_[rchID] = rch_

            for rchID in rv.inRchIDs:
                
                rch = rv.RCHs[rchID]
                
                rch_ = InnerReach.createInnerReach(rvID, rchID, len(rch.SECs), rch.fdNodeInfos[1], rch.bdNodeInfos[1], rch.SECs, self.dev_sita, self.dt, self.t)
                rv.RCHs_[rchID] = rch_            
        
        B = np.zeros((self.nInNode, 1))
        A = np.zeros((self.nInNode, self.nInNode))
        for rvID, rv in self.RVs.items():
            
            for rchID in rv.outRchIDs:
                rch = rv.RCHs_[rchID]
                rch.compute_outer_coefficients()
                nodeID, coe_z, const_z = rch.get_node_coe()
                B[nodeID-1, 0] += const_z
                A[nodeID-1, nodeID-1] += coe_z
            
            for rchID in rv.inRchIDs:
                rch = rv.RCHs_[rchID]
                rch.compute_inner_coefficients()
                fdID, bdID, alpha, beta, zeta = rch.get_fd_coe()
                bdID, fdID, sita, eta, gama = rch.get_bd_coe()
                
                B[fdID-1, 0] += alpha
                A[fdID-1, fdID-1] += beta
                A[fdID-1, bdID-1] += zeta
                
                B[bdID-1, 0] += sita
                A[bdID-1, bdID-1] += eta
                A[bdID-1, fdID-1] += gama
        p, l, u = lu(A)
        y = solve(p.dot(l), B)
        Z = solve(u, y)
        print(Z)
    def readRiverInfo(self, path):
        
        ID_RV = 0
        
        with open(path, 'r') as f:
            
            lines = f.readlines()
            
            for line in lines:
                
                ID_RV += 1
                line = line.strip().split()
                name = line[0]
                length = float(line[1])
                
                self.NAtoID_RV[name] = ID_RV
                self.RVs[ID_RV] = River(name, ID_RV, length)

            self.nRV = ID_RV
            
    def readNodeInfo(self, path):
        
        ID_ND = 0
        
        with open(path, 'r') as f:
            
            lines = f.readlines()
            
            for line in lines:
                if line != '':
                    line = line.strip().split()
                    num = int(len(line) / 2)
                    
                    ID_ND += 1
                    
                    # Add nodes to rivers
                    for i in range(num):
                        name = line[2 * i]
                        mileage = float(line[2 * i + 1])
                        ID = self.NAtoID_RV[name]
                        self.RVs[ID].addNode(mileage, ID_ND, 0)
                        
        self.nInNode = ID_ND
    
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
                    name = match.group(1); rvID = self.NAtoID_RV[name]
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
    
    def readBoundary(self, path):
        
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
                    name = match.group(1); rvID = self.NAtoID_RV[name]
                    i += 1
                    mil = float(re.match("Mileage\s*(\d+(\.\d+)?)", lines[i]).group(1))
                    i += 1
                    num = int(re.match("Num\s*(\d+)", lines[i]).group(1))
                    i += 1
                    T = int(re.match("Type\s*(\d+(\.\d+)?)", lines[i]).group(1))
                    i += 1
                    
                    data = np.zeros((num, 2), dtype = np.float32)
                    
                    for j in range(num):
                        
                        line = lines[i].strip().split()
                        
                        data[j] = line
                        
                        i += 1
                    
                    self.RVs[rvID].addBoundary(mil, T, data)
                else:
                    i += 1
        
    def riverInit(self):
        
        for _, rv in self.RVs.items():
            
            rv.reachInit()
    
    def extendTimeSeries(self, rv):
        
        nt = self.nt
        
        for _, sec in rv.SECs.items():
            sec.Q_Series = np.ascontiguousarray(np.ones(nt) * self.Q_init)
            sec.Z_Series = np.ascontiguousarray(np.ones(nt) * self.Z_init)
        
        # for I, bd in rv.BDs.items():
        #     T = bd.T
        #     if T == 1:
        #         data = np.ones(nt)
        #         if I == 0:
        #             rv.SECs[1].Z_Series = data
        #         else:
        #             rv.SECs[rv.nSec].Z_Series = data
        #     else:
        #         data = np.ones(nt) * 10
        #         if I == 0:
        #             rv.SECs[1].Q_Series = data
        #         else:
        #             rv.SECs[rv.nSec].Q_Series = data
            
            
        
            
                
                
        
        
        
        
        
