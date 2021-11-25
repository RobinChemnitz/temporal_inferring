import numpy as np
import networkx as nx

global N_TIMEFRAMES
global N_CITIES
global N_PIXELS
global N_NODES
global N_EDGES

X_FACTOR = 89.67  # computed on a latitude of 36.25 which is in the middle of our data field
Y_FACTOR = 111.2
X_MIN = 8
X_MAX = 11.5
Y_MIN = 34.9
Y_MAX = 37.5
TIME_RESOLUTION = 50


def geo_to_complex(geo):
    geo = geo.transpose()
    comp = geo[0] * X_FACTOR + geo[1] * Y_FACTOR * 1.0j
    return comp


def complex_to_geo(comp):
    geo = [comp.real / X_FACTOR, comp.imag / Y_FACTOR]
    return np.array(geo).transpose()


def init_from_storage():
    global N_TIMEFRAMES
    global N_CITIES
    global N_PIXELS
    global N_NODES
    global N_EDGES

    city_states = np.load('Storage/city_states.npy')
    N_CITIES, N_TIMEFRAMES = np.shape(city_states)

    graph = nx.read_gml('Storage/graph.gml')
    N_NODES = len(graph.nodes)
    N_EDGES = len(graph.edges)
    N_PIXELS = N_NODES - N_CITIES
