from .river import River

Rivers = {}
Rivers_ID = {}
def readRiverInfo(path):
    ID = 1
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split()
            name = line[0]
            length = float(line[1])
            Rivers[ID] = River(name, ID, length)
            Rivers_ID[name] = ID
            ID += 1

def readNodes(path):
    tmpNodes = {}
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split()
            
            num = int(len(line) / 2)
            for i in range(num):
                name = line[i]
                mileage = float(line[i + 1])
                ID = Rivers_ID[name]
                
                tmpNodes[ID].setDefault([])
                tmpNodes[ID].append(mileage)
    
                
            

def readSections(path):
    pass


readRiverInfo('rivers.txt')
