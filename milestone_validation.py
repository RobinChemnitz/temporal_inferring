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


def milestone_evolution(values, idx, name):
    N_frames = len(values)

    ms_time = np.load('Storage/milestone_times.npy')
    ms_timeframe = np.ceil(ms_time / settings.TIME_RESOLUTION)

    rows = int(np.ceil(N_frames / 4))
    fig, axs = plt.subplots(rows, 4, figsize=(8 / 3 * 4, 3 * rows))

    for frame in range(4 * rows):
        r = int(np.floor(frame / 4.0))
        c = frame % 4

        if rows > 1:
            ax = axs[r, c]
        else:
            ax = axs[c]

        if frame < N_frames:
            ax.plot(np.linspace(0, 8, 9), values[frame])
            bar = patches.Rectangle((ms_timeframe[frame] - 0.95, 0), 0.9, 2, fc='lightgrey', ec='black', alpha=0.7)
            ax.add_patch(bar)
            ax.set_title('milestone:' + str(idx[frame]))
        ax.set_xlim([0, 9])
        ax.set_ylim([0, 1.1])
        ax.set_xticks([0, 2, 4, 6, 8])

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    plt.savefig('Output/' + name + '.pdf')
