from network import Network
from network_mike import NetworkMike
from river1D import Section
import numpy as np
# network = Network("rivers.txt", "nodes.txt", "sections.txt", "boundary.txt", "setting.txt")

# network.simPressimann()
riverPath = "C:/Users/smasky/Desktop/set1/set1/river_data.txt"
secPath = "C:/Users/smasky/Desktop/set1/set1/sectionall.txt"
boundaryPath = "C:/Users/smasky/Desktop/set1/set1/bd.txt"
settingPath = "C:/Users/smasky/Desktop/set1/set1/setting.txt"
network = NetworkMike(riverPath, secPath, boundaryPath, settingPath)
network.simPressimann()
