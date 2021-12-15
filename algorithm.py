import numpy as np
import networkx as nx
import settings

# This script contains the implementation of the road-segment activation probability calculation. Requires a fully
# initialized Storage-folder.


# Returns the temporal activation probability alpha of each road-segment as an np.array of dictionaries. alpha has
# N_timeframes entries each of which is a dictionary containing the activation probabilities of the respective
# frame. Given an edge e=(u,v), where u and v are in ascending order, and a time-frame t, the activation probability is
# given by alpha[t][e].
# With the parameter t_rom one can overwrite the times of romanization of the cities. This is used for the sensitvity
# analysis. If forget is set of an city index, i.e. integer < N_cities, then the algorithm is performed as if the city
# did not exist. This is used in the stability analysis.
def temporal_activation_probability(t_rom=None, forget=None):
    T = settings.N_TIMEFRAMES

    graph = nx.read_gml('Storage/graph.gml')
    graph = nx.convert_node_labels_to_integers(graph)
    for c in range(settings.N_CITIES):
        graph.remove_node(c)
    edges = graph.edges

    if t_rom is None:
        t_rom = np.load('Storage/romanization_times.npy')
    pi = np.load('Storage/influence_matrix.npy')
    paths = np.load('Storage/shortest_paths.npy', allow_pickle=True)

    N_cities = settings.N_CITIES
    if forget is not None:
        N_cities = N_cities - 1
        args = list(range(settings.N_CITIES))
        args.remove(forget)
        t_rom = t_rom[args]
        pi = pi[args].transpose()
        pi = pi[args].transpose()
        paths = paths[args].transpose()
        paths = paths[args].transpose()

    beta = np.empty(T, dtype=object)
    for t in range(T):
        beta[t] = {}
        for e in edges:
            beta[t][e] = 1

    for c in range(N_cities):
        P_c = np.where(t_rom < t_rom[c])[0]
        pi_sum = np.sum(pi.transpose()[c][P_c])

        phi_c = {}

        for p in P_c:
            theta_pc = pi[p][c] / pi_sum
            path = list(map(tuple, paths[p][c]))
            for e in path:
                if e not in phi_c:
                    phi_c[e] = 0
                phi_c[e] = phi_c[e] + theta_pc

        for e in phi_c:
            for t in range(t_rom[c], T):
                beta[t][e] = beta[t][e] * (1 - phi_c[e])

    alpha = np.empty(T, dtype=object)
    for t in range(T):
        alpha[t] = {}
        for e in edges:
            alpha[t][e] = 1 - beta[t][e]

    return alpha
