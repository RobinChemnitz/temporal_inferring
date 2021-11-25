import numpy as np
import networkx as nx
import settings


def temporal_activation_probability():
    T = settings.N_TIMEFRAMES

    t_rom = np.load('Storage/romanization_times.npy')
    pi = np.load('Storage/influence_matrix.npy')
    paths = np.load('Storage/shortest_paths.npy', allow_pickle=True)

    graph = nx.read_gml('Storage/graph.gml')
    graph = nx.convert_node_labels_to_integers(graph)
    for c in range(settings.N_CITIES):
        graph.remove_node(c)
    edges = graph.edges

    beta = np.empty(T, dtype=object)
    for t in range(T):
        beta[t] = {}
        for e in edges:
            beta[t][e] = 1

    for c in range(settings.N_CITIES):
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
