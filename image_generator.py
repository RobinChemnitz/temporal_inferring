import numpy as np
import plots
import settings
import compute_influences
import algorithm
import robustness
import milestone_validation
import networkx as nx
import matplotlib.pyplot as plt

# This script generates the images that are shown in the publication and saves them in the Output-folder. Requires a
# fully initialized Storage-folder. These functions can be used as examples on how to generate new images from the
# results.


# Generates the images of the activation probability alpha over all time-frames with red markers once indicating cities
# and once indicating milestones. Also generates the shift in the activation probabilty hen including the city status
# for the selected time-frames.
def road_activation():
    T = settings.N_TIMEFRAMES
    t_rom = np.load('Storage/romanization_times.npy')
    city_pos_geo = np.load('Storage/city_pos_geo.npy')

    city_markers = []
    for t in range(T):
        city_markers.append(city_pos_geo[np.where(t_rom <= t)[0]])
    city_markers = np.array(city_markers, dtype=object)

    ms_time = np.load('Storage/milestone_times.npy')
    ms_pos_geo = np.load('Storage/milestone_pos_geo.npy')

    ms_time = np.ceil(ms_time / settings.TIME_RESOLUTION)
    ms_markers = []
    for t in range(T):
        ms_markers.append(ms_pos_geo[np.where(ms_time <= t)[0]])
    ms_markers = np.array(ms_markers, dtype=object)

    compute_influences.standard()
    alpha = algorithm.temporal_activation_probability()

    compute_influences.include_status()
    alpha_states = algorithm.temporal_activation_probability()

    diff = np.empty(T, dtype=object)
    for t in range(T):
        diff[t] = {}
        for e in alpha[t]:
            diff[t][e] = alpha_states[t][e] - alpha[t][e]

    plots.visualize_temporal_edge_values(alpha[1:], 'Activation_Probability', markers=city_markers[1:])
    plots.visualize_temporal_edge_values(alpha[1:], 'Temporal_Milestones', markers=ms_markers[1:], ms=80,
                                         mstyle='^')
    plots.visualize_temporal_edge_values(diff[[2, 4, 6]], 'Activation_Shift', ['100 AD', '200 AD', '300 AD'],
                                         colormap='seismic', vmin=-0.2, vmax=0.2)


# Generates the image containing all temporal milestone activations. The order of the milestones can be chosen by hand.
def milestone_activation():
    milestone_validation.eliminate_doubles()
    alpha = algorithm.temporal_activation_probability()
    values = milestone_validation.evaluate_activation_prob(alpha)
    clusters = milestone_validation.cluster_milestones()
    order = np.array([9, 11, 19, 22, 3, 17, 15, 16, 1, 6, 12, 4, 18, 20, 21, 5, 10, 23, 0, 2, 7, 8, 13, 14])
    plots.milestone_evolution(values, clusters, 'Milestone_Evolution', order=order)


# Computes the sensitivity like described in the publication and generates an image showing the mean-squared-distance
# to the unperturbed activation probability in three selected time-frames. If the msd has not been computed yet, this
# is very time-consuming!
def sensitivity():
    try:
        msd = np.load('Storage/sensitivity_msd.npy', allow_pickle=True)
    except FileNotFoundError:
        msd = robustness.sensitivity(1000, 0.2)

    city_pos_geo = np.load('Storage/city_pos_geo.npy')
    t_rom = np.load('Storage/romanization_times.npy')

    city_markers = []
    for t in range(settings.N_TIMEFRAMES):
        city_markers.append(city_pos_geo[np.where(t_rom <= t)[0]])
    city_markers = np.array(city_markers, dtype=object)

    plots.visualize_temporal_edge_values(msd[[2, 4, 6]], 'Sensitivity_MSD', ['100 AD', '200 AD', '300 AD'], vmax=0.3,
                                         markers=city_markers[1:])


# Computes the stability like described in the publication and generates an image showing the squared-distance to the
# unperturbed activation probability in three selected time-frames for two selected cities.
def stability():
    city_pos_geo = np.load('Storage/city_pos_geo.npy')

    selected = [28, 18]

    for city in selected:
        sd = robustness.stability(city)
        city_markers = []
        for t in range(settings.N_TIMEFRAMES):
            city_markers.append([city_pos_geo[city]])
        city_markers = np.array(city_markers, dtype=object)

        plots.visualize_temporal_edge_values(sd[[2, 4, 6]], 'Stability_' + str(city), ['100 AD', '200 AD', '300 AD'],
                                             ms=100, markers=city_markers[[2, 4, 6]])


# Generates an image of the discrete road-network where cities are marked as red nodes.
def draw_network():
    plt.figure(figsize=(14, 10))

    node_color = 'black'
    city_color = 'red'
    node_size = 1
    city_size = 120
    edge_width = 3

    node_pos_geo = np.load('Storage/node_pos_geo.npy')
    graph = nx.read_gml('Storage/graph.gml')
    graph = nx.convert_node_labels_to_integers(graph)

    colors = np.full(settings.N_NODES, node_color)
    colors[:settings.N_CITIES] = city_color
    sizes = np.full(settings.N_NODES, node_size)
    sizes[:settings.N_CITIES] = city_size

    nx.draw_networkx_nodes(graph, node_pos_geo, node_color=colors, node_size=sizes)
    nx.draw_networkx_edges(graph, node_pos_geo, width=edge_width)

    plt.xlim([settings.X_MIN, settings.X_MAX])
    plt.ylim([settings.Y_MIN, settings.Y_MAX])
    plt.tight_layout()
    plt.savefig('Output/Network.pdf')
    plt.close()


# Generates a possible spreading tree and shows its evolution in the selected time-frames. timesframes should be a list
# of the selected time-frames. for nicer images, a high distance factor rho is used for the influence function,
# resulting in a more spatially coherent cascade.
def cascade_images(timeframes):
    frames = len(timeframes)

    D = np.load('Storage/city_distances.npy')
    t_rom = np.load('Storage/romanization_times.npy')
    city_pos_geo = np.load('Storage/city_pos_geo.npy')

    distance_factor = 0.5
    def distance_func(x):
        x = x * distance_factor
        return np.exp(-x)

    f = np.vectorize(distance_func, otypes=[float])
    pi = f(D)
    pi = pi - np.eye(len(pi))

    edges = []
    pos = {}

    fig, axs = plt.subplots(1, frames, figsize=(7 * frames, 5.5))
    current_im = 0

    for t in range(settings.N_TIMEFRAMES):
        parents = np.where(t_rom < t)[0]
        C_t = np.where(t_rom == t)[0]
        graph = nx.Graph()
        graph.add_nodes_from(parents)
        graph.add_nodes_from(C_t)

        for c in C_t:
            pi_sum = np.sum(pi[c][parents])
            pos[c] = city_pos_geo[c]
            rnd = np.random.random()
            cumul = 0
            for p in parents:
                cumul = cumul + pi[p][c] / pi_sum
                if cumul > rnd:
                    edges.append((p, c))
                    break

        graph.add_edges_from(edges)

        if t in timeframes:
            ax = axs[current_im]
            current_im = current_im + 1

            nodes = list(graph.nodes)
            origins = list(np.where(t_rom[nodes] == 0)[0])

            colors = np.full(len(nodes), 'royalblue', dtype=object)
            colors[origins] = 'green'
            sizes = np.full(len(nodes), 110)
            sizes[origins] = 140

            plots.draw_graph(graph, pos, node_color=colors, node_size=sizes, edge_thickness=5.3, arrows=False, ax=ax)
            ax.set_xlabel(str(t * settings.TIME_RESOLUTION) + ' AD', fontsize=24)
            ax.set_xlim([settings.X_MIN, settings.X_MAX])
            ax.set_ylim([35, settings.Y_MAX])



    fig.tight_layout(rect=[0, 0.033, 1, 1])
    plt.savefig('Output/Cascade.pdf')
    plt.close()
