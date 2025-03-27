from network import Network
from network_mike import NetworkMike
from river1D import Section
import numpy as np
import time
# network = Network("rivers.txt", "nodes.txt", "sections.txt", "boundary.txt", "setting.txt")

# network.simPressimann()
riverPath = "C:/Users/49210/Desktop/set1/set1/river_data.txt"
secPath = "C:/Users/49210/Desktop/set1/set1/sectionall.txt"
boundaryPath = "C:/Users/49210/Desktop/set1/set1/bd.txt"
settingPath = "C:/Users/49210/Desktop/set1/set1/setting.txt"
network = NetworkMike(riverPath, secPath, boundaryPath, settingPath)

network.simPressimann()