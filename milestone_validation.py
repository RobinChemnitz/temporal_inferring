import numpy as np
import networkx as nx
import settings

# This script calculates the temporal activation of the milestones based on the activation probability of surrounding
# road-segments. This is used to validate the results of the model.


# Determines the temporal activation of each milestone as the maximum activation probability alpha of a road-segment in
# a radius of sigma km. The activation is returned as a N_milestones x N_timeframes np.array.
def evaluate_activation_prob(alpha, sigma=5):
    ms_pos_geo = np.load('Storage/milestone_pos_geo.npy')
    ms_pos = settings.geo_to_complex(ms_pos_geo)

    node_pos_geo = np.load('Storage/node_pos_geo.npy')
    node_pos = settings.geo_to_complex(node_pos_geo)

    graph = nx.read_gml('Storage/graph.gml')
    graph = nx.convert_node_labels_to_integers(graph)
    edges = np.array(graph.edges)

    activation = []
    for p in ms_pos:
        dist = np.abs(node_pos - np.full(len(node_pos), p))
        close = np.where(dist < sigma)[0]

        max_alpha = np.zeros(settings.N_TIMEFRAMES)
        for node in close:
            adj = np.where(edges == node)[0]
            for seg in edges[adj]:
                a, b = seg
                if a > settings.N_CITIES and b > settings.N_CITIES:
                    for t in range(settings.N_TIMEFRAMES):
                        max_alpha[t] = np.max([alpha[t][(a,b)], max_alpha[t]])

        activation.append(max_alpha)

    activation = np.array(activation)
    return activation


# Checks whether there are milestones in the data that lie closer than sigma km togther and have the same time-stamp.
# Then their are considered to be the same for the milestone validation and the duplicates are deleted from the data in
# the Storage-folder
def eliminate_doubles(sigma = 1):
    M = settings.N_MILESTONES

    ms_pos_geo = np.load('Storage/milestone_pos_geo.npy')
    ms_pos = settings.geo_to_complex(ms_pos_geo)
    ms_time = np.load('Storage/milestone_times.npy')
    ms_disc_t = np.ceil(ms_time / settings.TIME_RESOLUTION)

    eliminated = []

    dist = np.full((M, M), ms_pos) - np.full((M, M), ms_pos).transpose()
    dist = np.abs(dist)
    for m in range(M):
        if m not in eliminated and ms_disc_t[m] > 0:
            close = np.where(dist[m] < sigma)[0]
            for c in close:
                if c != m and ms_disc_t[c] == ms_disc_t[m]:
                    eliminated.append(c)

    valid = []
    for m in range(M):
        if m not in eliminated:
            valid.append(m)
    valid = np.array(valid)

    ms_info = np.load('Storage/milestone_info.npy')

    ms_pos_geo = ms_pos_geo[valid]
    ms_time = ms_time[valid]
    ms_info = ms_info[valid]

    np.save('Storage/milestone_pos_geo.npy', ms_pos_geo)
    np.save('Storage/milestone_times.npy', ms_time)
    np.save('Storage/milestone_info.npy', ms_info)

    settings.N_MILESTONES = len(valid)


# Generates the custers in which the milestones are grouped. Milestones that lie within a radus of sigma km are grouped.
# Returns a list of np.array's that contain the indices of the cluster. If a milestone is not clustered the respective
# entry is an np.array of length 1.
def cluster_milestones(sigma = 1):
    M = settings.N_MILESTONES

    ms_pos_geo = np.load('Storage/milestone_pos_geo.npy')
    ms_pos = settings.geo_to_complex(ms_pos_geo)
    dist = np.abs(np.full((M,M), ms_pos) - np.full((M,M), ms_pos).transpose())

    unprocessed = set(range(M))

    clusters = []

    while unprocessed:
        m = min(unprocessed)
        close = np.where(dist[m] < sigma)[0]
        processed = False

        if np.max(dist[np.ix_(close, close)]) < sigma:
            outside = np.where(dist[m] >= sigma)[0]
            if np.min(dist[np.ix_(close, outside)]) >= sigma:
                clusters.append(close)
                for m_ in close:
                    unprocessed.remove(m_)
                processed = True

        if not processed:
            for m_ in close:
                clusters.append(np.array([m_]))
                unprocessed.remove(m_)

    return clusters

