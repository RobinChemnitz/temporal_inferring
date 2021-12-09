import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.patches as patches
from mpl_toolkits.axes_grid1 import make_axes_locatable
import imageio
import settings


viridis = cm.get_cmap('viridis')
bright_cmap = []
for i in range(256):
    hsv = colors.rgb_to_hsv(viridis(i)[:3])
    hsv[2] = hsv[2] + (1 - hsv[2]) * 0.3
    bright_cmap.append(colors.hsv_to_rgb(hsv))

bright_cmap = colors.ListedColormap(bright_cmap)


def visualize_temporal_edge_values(values, name, labels='AD', vmin=0, vmax=1, colormap='bright', markers=None, mc='red',
                                   ms=40, mstyle='o', fs=24, lw=2.5, one_cbar=True):
    N_frames = len(values)
    if labels == 'AD':
        times = []
        for t in range(N_frames):
            times.append(str((t + 1) * settings.TIME_RESOLUTION) + ' AD')
        labels = times

    rows = 1
    cols = N_frames
    if N_frames % 4 == 0:
        rows = int(N_frames / 4)
        cols = 4

    if colormap == 'bright':
        cmap = bright_cmap
    else:
        cmap = cm.get_cmap(colormap)

    fig, axs = plt.subplots(rows, cols, figsize=(7 * cols, 5.5 * rows))

    graph = nx.read_gml('Storage/graph.gml')
    graph = nx.convert_node_labels_to_integers(graph)
    for c in range(settings.N_CITIES):
        graph.remove_node(c)

    tmp = np.array(graph.edges)
    tmp = list(map(tuple, tmp))
    N_edges = len(tmp)
    edge_list = np.empty(N_edges, dtype=object)
    edge_list[:] = tmp

    edge_values = np.zeros((N_frames, N_edges))
    for f in range(N_frames):
        for i in range(N_edges):
            e = edge_list[i]
            edge_values[f][i] = values[f][e]

    node_pos_geo = np.load('Storage/node_pos_geo.npy')

    for f in range(N_frames):
        r = int(np.floor(f / cols))
        c = f % cols
        if rows == 1:
            if cols == 1:
                ax = axs
            else:
                ax = axs[f]
        else:
            ax = axs[r, c]

        abs_values = np.abs(edge_values[f])
        abs_values = np.where(abs_values > vmax, vmax, abs_values)
        dv = vmax / 10
        for k in range(10):
            args = np.where(np.logical_and(k * dv <= abs_values, abs_values <= (k + 1) * dv))[0]
            edges = edge_list[args]
            nx.draw_networkx_edges(graph, node_pos_geo, edgelist=edges, width=lw + k * lw / 15,
                                   edge_color=edge_values[f][args], edge_vmin=vmin, edge_vmax=vmax, edge_cmap=cmap,
                                   ax=ax)

        nx.draw_networkx_nodes(graph, node_pos_geo, node_size=0, alpha=0, ax=ax)

        if not (markers is None):
            if len(markers[f]) > 0:
                marker_pos_geo = np.array(markers[f]).transpose()
                ax.scatter(marker_pos_geo[0], marker_pos_geo[1], c=mc, s=ms, marker=mstyle)

        ax.set_facecolor('black')
        ax.set_xlabel(labels[f], fontsize=fs)
        ax.set_xlim([settings.X_MIN, settings.X_MAX])
        ax.set_ylim([settings.Y_MIN, settings.Y_MAX])

        if not one_cbar:
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="3.5%", pad=0.05)
            cax.set_yticks([vmin, (vmax + vmin) / 2, vmax])
            cax.tick_params(labelsize=fs)
            smap = cm.ScalarMappable(cmap=cmap)
            smap.set_clim(vmin, vmax)
            plt.colorbar(smap, cax=cax, ticks=[vmin, (vmax + vmin) / 2, vmax])

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    if one_cbar:
        fig.subplots_adjust(right=0.95)
        for r in range(rows):
            if rows == 1:
                if cols == 1:
                    ax = axs
                else:
                    ax = axs[cols - 1]
            else:
                ax = axs[r, cols - 1]

            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.1)
            cax.set_yticks([vmin, (vmax + vmin) / 2, vmax])
            cax.tick_params(labelsize=fs)
            smap = cm.ScalarMappable(cmap=cmap)
            smap.set_clim(vmin, vmax)
            plt.colorbar(smap, cax=cax, ticks=[vmin, (vmax + vmin) / 2, vmax])

    fig.savefig('Output/' + name + '.pdf')
    plt.close(fig)


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


def draw_graph(graph, pos, origins=[], node_color='royalblue', origin_color='limegreen', edge_color='tomato',
               edge_thickness=3.0, node_size=200, arrows=False, ax=None):
    if ax is None:
        fig = plt.figure(figsize=(14, 10))
        ax = plt.gca()

    #need to update this
    map = imageio.imread('Data/Roads_35.png')
    ax.imshow(map, extent=[8, 11.5, 35, 37.5], cmap='binary_r')
    node_list = list(graph.nodes)

    if isinstance(node_color, dict):
        c = []
        for i in node_list:
            c.append(node_color[i])
        node_color = c

    nx.draw_networkx_nodes(graph, pos, nodelist=origins, node_color=origin_color, node_size=node_size * 3, ax=ax)
    nx.draw_networkx_nodes(graph, pos, nodelist=node_list, node_color=node_color, node_size=node_size, ax=ax)
    if arrows:
        arrow_style = patches.ArrowStyle('simple', head_length=.4, head_width=.5, tail_width=.1)
        nx.draw_networkx_edges(graph, pos, width=edge_thickness, edge_color=edge_color, arrowstyle=arrow_style,
                               arrowsize=20, ax=ax)
    else:
        nx.draw_networkx_edges(graph, pos, width=edge_thickness, edge_color=edge_color, ax=ax)


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

            draw_graph(graph, pos, node_color=colors, node_size=sizes, edge_thickness=5.3, arrows=False, ax=ax)
            ax.set_xlabel(str(t * 50) + ' AD', fontsize=24)
            ax.set_xlim([settings.X_MIN, settings.X_MAX])
            ax.set_ylim([settings.Y_MIN, settings.Y_MAX])

    fig.tight_layout(rect=[0, 0.033, 1, 1])
    plt.savefig('Output/Cascade.pdf')
    plt.close()

#test
