import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import imageio
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.patches as patches
from mpl_toolkits.axes_grid1 import make_axes_locatable
import settings

# This script conatins helper functions that plot the results of the method.


# This generates the colormap bright_cmap that is used in the publication.
viridis = cm.get_cmap('viridis')
bright_cmap = []
for i in range(256):
    hsv = colors.rgb_to_hsv(viridis(i)[:3])
    hsv[2] = hsv[2] + (1 - hsv[2]) * 0.3
    bright_cmap.append(colors.hsv_to_rgb(hsv))
bright_cmap = colors.ListedColormap(bright_cmap)


# Generates and saves an image that displays the indicated edge values as they develop in time. The values should be
# given as an np.array of the length of the timeframes. Each entry is a dictionary that contains the value of each edge
# e=(u,v), where u and v are in ascending order.
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
            edges = list(edge_list[args])
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


# Generates the image containing all temporal milestone activations. values is a N_milestones x N_timeframes np.array
# with the temporal activation of each milestone. cluster is the grouping that is computed by milestone_validation. If
# an order is specified the milestones are sorted in that way. An order is an N_milstones np.array containing the
# ordering, see image_generator.milestone_activation() for an example.
def milestone_evolution(values, clusters, name, order=None):
    N_frames = len(clusters)

    ms_time = np.load('Storage/milestone_times.npy')
    ms_disc_t = np.ceil(ms_time / settings.TIME_RESOLUTION)

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
                bar = patches.Rectangle((ms_disc_t[m] - 0.95, 0), 0.9, 2, fc='lightgrey', ec='black', alpha=0.7)
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


# Draws a graph onto a high-resolution image of the road map. Works similar to networkx.draw_networkx.
def draw_graph(graph, pos, origins=[], node_color='royalblue', origin_color='limegreen', edge_color='tomato',
               edge_thickness=3.0, node_size=200, arrows=False, ax=None):
    if ax is None:
        fig = plt.figure(figsize=(14, 10))
        ax = plt.gca()

    map = imageio.imread('Data/roads_35.png')
    ax.imshow(map, extent=[settings.X_MIN, settings.X_MAX, 35, settings.Y_MAX], cmap='binary_r')
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

