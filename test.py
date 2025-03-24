from network import Network
from river1D import Section
import numpy as np
network = Network("rivers.txt", "nodes.txt", "sections.txt", "boundary.txt")

network.simPressimann()
