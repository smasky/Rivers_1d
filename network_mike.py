import re
import numpy as np
from datetime import datetime

from river import River
from river1D import Section, OuterReach, InnerReach
from scipy.linalg import solve, lu

class NetworkMike():
    def __init__(self, branchPath, secPath, boundaryPath, settingPath):
        
        self.nRV = 0 #number of river
        self.t = 1 #time step
        
        self.NAtoID_RV = {} #name to ID of river
        self.RVs = {} #river dictionary
        
        self.readSetting(settingPath) #read setting
        self.readBranch(branchPath) #river node info
        self.readSec(secPath) #section info
        self.readBoundary(boundaryPath) #boundary info
        
        #River init
        self.riverInit()
    
    def readSetting(self, settingPath):
        
        with open(settingPath, "r") as f:
            lines = f.readlines()
            strSetting = " ".join(lines)
        
        #globalZ
        self.initZ = float(re.search("globalZ\s*(\d+(\.\d+)?)", strSetting).group(1))
        #globalQ
        self.initQ = float(re.search("globalQ\s*(\d+(\.\d+)?)", strSetting).group(1))
        #dt
        self.dt = float(re.search("dt\s*(\d+(\.\d+)?)", strSetting).group(1))
        #nt
        self.nt = int(re.search("nt\s*(\d+(\.\d+)?)", strSetting).group(1))
        #dev_sita
        self.dev_sita = float(re.search("dev_sita\s*(\d+(\.\d+)?)", strSetting).group(1))
        #simBegin
        timePattern = r"(simBegin|simEnd)\s*(\d{4})[-/](\d{2})[-/](\d{2}) (\d{1,2}):(\d{2})(?::(\d{2}))?"
        
        timeMatch = re.findall(timePattern, strSetting)
        
        for m in timeMatch:
            label, year, month, day, hour, minute, second = m
            
            second = second if second else "00" 

            if label == "simBegin":
                self.simBegin = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            else:
                self.simEnd = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        
        self.simDuration = (self.simEnd - self.simBegin).total_seconds()/self.dt
        
    def sim_PRSM(self):
                
        for rvID, rv in self.RVs.items():
            
            rv.initSec(self.initQ, self.initZ, self.nt)
            
            for secID, sec in rv.SECs.items():
                mil = sec.mil
                roughness = 0.02 #TODO TEMP
                for rchID, rch in rv.RCHs.items():
                    fdMil = rch.fdNodeInfos[0]
                    bdMil = rch.bdNodeInfos[0]
                    
                    if mil >= fdMil and mil <= bdMil:
                        cSec = Section.createSection(secID, rchID, rvID, mil, roughness, sec.nPoint, sec.xSec, sec.ySec, sec.rSec, self.nt, sec.Q_Series, sec.Z_Series)
                        rch.addSec(cSec)
                    
            for rchID in rv.outRchIDs:
                rch = rv.RCHs[rchID]
                if rch.reverse == True:
                    rch.SECs.reverse()
                
                #temp
                if rch.fdNodeInfos[0] == 0.0:
                    simData = rv.BDs[0][2]
                    T = rv.BDs[0][1]
                else:
                    simData = rv.BDs[1][2]
                    T = rv.BDs[1][1]
                
                rch_ = OuterReach.createOuterReach(rvID, rchID, len(rch.SECs), rch.fdNodeInfos[1], rch.bdNodeInfos[1], 
                                                   rch.SECs, simData, self.dev_sita, self.dt, self.t, rch.reverse, T)
                rv.RCHs_[rchID] = rch_

            for rchID in rv.inRchIDs:
                
                rch = rv.RCHs[rchID]
                
                rch_ = InnerReach.createInnerReach(rvID, rchID, len(rch.SECs), rch.fdNodeInfos[1], rch.bdNodeInfos[1], rch.SECs, self.dev_sita, self.dt, self.t)
                rv.RCHs_[rchID] = rch_            
        
        #Simulation
        t = 1
        record = np.zeros(self.nt)
        
        #hot
        temp =0
        
        while temp < 200:
            temp += 1
            B = np.zeros((self.nInNode, 1))
            A = np.zeros((self.nInNode, self.nInNode))
            
            for rvID, rv in self.RVs.items():
                
                for rchID in rv.outRchIDs:
                    rch = rv.RCHs_[rchID]
                    rch_ = rv.RCHs[rchID]
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
            
            for rvID, rv in self.RVs.items():
                for rchID in rv.outRchIDs:
                    rch = rv.RCHs_[rchID]
                    rch.recompute_QZ(Z[rch.innerNodeID-1, 0])
                
                for rchID in rv.inRchIDs:
                    rch = rv.RCHs_[rchID]
                    rch.recompute_QZ(Z[rch.fdNodeID-1, 0], Z[rch.bdNodeID-1, 0])
        
        while t < self.nt:
            t+=1
            
            B = np.zeros((self.nInNode, 1))
            A = np.zeros((self.nInNode, self.nInNode))
            
            for rvID, rv in self.RVs.items():
                
                for rchID in rv.outRchIDs:
                    rch = rv.RCHs_[rchID]
                    rch_ = rv.RCHs[rchID]
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
            
            for rvID, rv in self.RVs.items():
                for rchID in rv.outRchIDs:
                    rch = rv.RCHs_[rchID]
                    rch.recompute_QZ(Z[rch.innerNodeID-1, 0])
                
                for rchID in rv.inRchIDs:
                    rch = rv.RCHs_[rchID]
                    rch.recompute_QZ(Z[rch.fdNodeID-1, 0], Z[rch.bdNodeID-1, 0])
            
            for rvID, rv in self.RVs.items():
                for rchID, rch in rv.RCHs_.items():
                    rch.update_t()
            
            record[t-1] = Z[0, 0]
        np.savetxt("record.txt", np.array(self.RVs[2].SECs[50].Q_Series))
        
    def readBranch(self, path):
        
        with open(path, 'r') as f:
            lines = f.readlines()
            
            for line in lines:
                line = line.strip().split()
                name = line[0]
                ID_RV = int(line[1])
                length = float(line[3])
                
                self.NAtoID_RV[name] = ID_RV
                self.RVs[ID_RV] = River(name, ID_RV, length)
            
            self.nRV = len(self.NAtoID_RV)
            
            tmpNodes = []
            
            for line in lines:
                
                line = line.strip().split()
                
                ind = line.index("Regular")
                
                num = int((len(line) - 1 - ind)/2)
                
                nodes = []
                for i in range(num):
                    
                    name = line[ind + 1 + 2 * i]
                    ID_RV = self.NAtoID_RV[name]
                    mile = float(line[ind + 2 + 2 * i])
                    nodes.append((ID_RV, mile))
                    
                if len(nodes) > 0:
                    ID_RV = self.NAtoID_RV[line[0]]
                    mil = float(line[3])
                    nodes.append((ID_RV, mil))
                    tmpNodes.append(nodes)
                
        innerNodes = []
        for i in range(len(tmpNodes)):
            merged_with_new = tmpNodes[i]
            for j in range(len(tmpNodes)):
                
                common_elements = set(tmpNodes[i]) & set(tmpNodes[j])
                if len(common_elements) > 0 and i != j:
                    merged_with_new = list(set(tmpNodes[i] + tmpNodes[j]))
                    
            if merged_with_new not in innerNodes:    
                innerNodes.append(merged_with_new)
        
        ID_ND = 0    
        for i in range(len(innerNodes)):
            ID_ND += 1
            for j in range(len(innerNodes[i])):
                ID_RV = innerNodes[i][j][0]
                mile = innerNodes[i][j][1]
                self.RVs[ID_RV].addNode(mile, ID_ND, 0)
        
        self.nInNode = ID_ND

    def readSec(self, path):
        
        with open(path, 'r') as f:
            lines = f.readlines()
            
            i = 0
            while i < len(lines):
                if "COORDINATES" in lines[i]:
                    name = lines[i-2].strip()
                    rvID = self.NAtoID_RV[name]
                    rv = self.RVs[rvID]
                    mil = float(lines[i-1])
                    i += 1
                    continue
                
                if "PROFILE" in lines[i]:
                    line = lines[i].strip().split()
                    num = int(line[1])
                    data = np.zeros((num, 3), dtype = np.float32)
                    for j in range(i+1, i+1+num):
                        line = lines[j].strip().split()
                        data[j-i-1] = [float(line[0]), float(line[1]), 0.02]
                    rv.addSec(mil, data)
                    i += 1+num
                    continue
                    
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
                        
                        timePattern = r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})\s(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(-?\d+(\.\d+)?)"


                        timeMatch = re.match(timePattern, lines[i])
                        year, month, day, hour, minute, second, value, _ = timeMatch.groups()
                        
                        second = second if second else "00"
                        
                        timeValue = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
                        
                        deltaTime = (timeValue - self.simBegin).total_seconds()/self.dt
                        
                        data[j] = [deltaTime, value]
                        
                        i += 1
                    
                    self.RVs[rvID].addBoundary(mil, T, data, self.nt)
                else:
                    i += 1
        
    def riverInit(self):
        
        for _, rv in self.RVs.items():
            
            rv.reachInit()
            
    def extendTimeSeries(self, rv):
        
        nt = self.nt
                
        for _, sec in rv.SECs.items():
            sec.Q_Series = np.ascontiguousarray(np.ones(nt) * self.initQ)
            
            botZ = np.min(sec.ySec)
            sec.Z_Series = np.ascontiguousarray(np.ones(nt) * (botZ+self.initZ)) 