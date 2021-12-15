import numpy as np
import networkx as nx

# This script stores general information about the currently loaded data. If the data is already processed and in the
# Storage-folder, init_from_storage needs to be called upon initialization.


global N_TIMEFRAMES
global N_CITIES
global N_PIXELS
global N_NODES
global N_EDGES
global N_MILESTONES

# The area that the model considers. This should be the boundaries of the road map that is used.
X_MIN = 8
X_MAX = 11.5
Y_MIN = 34.9
Y_MAX = 37.5

# These factors indicate how far one degree in geographical coordinates is when measured in km. The X_factor is computed
# on a latitude of 36.25 which is in the middle of our data field
X_FACTOR = 89.67
Y_FACTOR = 111.2

# The length of one time-frame in years
TIME_RESOLUTION = 50


# These two functions transform geographical coordinates to complex coordinates and vice versa. Geo-coordiantes are
# given as an N x 2 array such that geo[i] is a 2d-array with x and y coordinate. The complex data format stores the
# x-coordinate as the real-part and the y-coordinate in the imaginary part. Additionally, the coordinates are multiplied
# with the x_ and y_factor such that the absolute distance between two complex coordinates is the distance in km between
# them.

def geo_to_complex(geo):
    geo = geo.transpose()
    comp = geo[0] * X_FACTOR + geo[1] * Y_FACTOR * 1.0j
    return comp


def complex_to_geo(comp):
    geo = [comp.real / X_FACTOR, comp.imag / Y_FACTOR]
    return np.array(geo).transpose()


# Initializes all values based on the files in the Storage-folder. This needs to be called in the beginning when running
# the code while the procssed data is already saved in the Storage-folder.
def init_from_storage():
    global N_TIMEFRAMES
    global N_CITIES
    global N_PIXELS
    global N_NODES
    global N_EDGES
    global N_MILESTONES

    city_states = np.load('Storage/city_states.npy')
    N_CITIES, N_TIMEFRAMES = np.shape(city_states)

    graph = nx.read_gml('Storage/graph.gml')
    N_NODES = len(graph.nodes)
    N_EDGES = len(graph.edges)
    N_PIXELS = N_NODES - N_CITIES

    ms_info = np.load('Storage/milestone_info.npy')
    N_MILESTONES = len(ms_info)
