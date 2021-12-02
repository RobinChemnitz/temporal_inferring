import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as patches
import settings


def evaluate_activation_prob(alpha, sigma=5):
    ms_pos_geo = np.load('Storage/milestone_pos_geo.npy')
    ms_pos = settings.geo_to_complex(ms_pos_geo)

    node_pos_geo = np.load('Storage/node_pos_geo.npy')
    node_pos = settings.geo_to_complex(node_pos_geo)

    graph = nx.read_gml('Storage/graph.gml')
    graph = nx.convert_node_labels_to_integers(graph)
    edges = np.array(graph.edges)

    # use setting.N_MILESTONES and different name for values?
    values = []
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

        values.append(max_alpha)

    values = np.array(values)
    return values


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


def milestone_evolution(values, name, order=None):
    clusters = cluster_milestones()
    N_frames = len(clusters)

    ms_time = np.load('Storage/milestone_times.npy')
    ms_timeframe = np.ceil(ms_time / settings.TIME_RESOLUTION)

    rows = int(np.ceil(N_frames / 4))
    fig, axs = plt.subplots(rows, 4, figsize=(8 / 3 * 4, 3 * rows))

    i = 1
    for frame in range(4 * rows):
        r = int(np.floor(frame / 4.0))
        c = frame % 4

        if rows > 1:
            ax = axs[r, c]
        else:
            ax = axs[c]

        if frame < N_frames:
            if order is None:
                cluster = clusters[frame]
            else:
                cluster = clusters[order[frame]]

            ax.plot(np.linspace(0, 8, 9), values[cluster[0]])

            for m in cluster:
                bar = patches.Rectangle((ms_timeframe[m] - 0.95, 0), 0.9, 2, fc='lightgrey', ec='black', alpha=0.7)
                ax.add_patch(bar)

            index = ''
            if len(cluster) == 1:
                index = str(i)
                i = i + 1
            else:
                index = str(i) + '-' + str(i + len(cluster) - 1)
                i = i + len(cluster)
            ax.set_title('milestone: ' + index)

        ax.set_xlim([0, 9])
        ax.set_ylim([0, 1.1])
        ax.set_xticks([0, 2, 4, 6, 8])

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    plt.savefig('Output/' + name + '.pdf')
