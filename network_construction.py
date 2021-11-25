import numpy as np
import scipy.sparse
import imageio as imio
import networkx as nx
import settings


def image_to_adjacency(filename):
    im = imio.imread('Data/' + filename + '.png')
    y_pixel, x_pixel = im.shape

    X_RES = (settings.X_MAX - settings.X_MIN) / x_pixel
    Y_RES = (settings.Y_MAX - settings.Y_MIN) / y_pixel

    coord_to_idx = {}
    idx_to_coord = {}
    pixel_pos = []

    idx = 0
    for i in range(y_pixel):
        for j in range(x_pixel):
            if im[i][j] == 0:
                idx_to_coord[idx] = (i, j)
                coord_to_idx[(i, j)] = idx
                pixel_pos.append([settings.X_MIN + X_RES * (j + 0.5), settings.Y_MAX - Y_RES * (i + 0.5)])
                idx = idx + 1
    pixel_pos = np.array(pixel_pos)
    pixel_pos = settings.geo_to_complex(pixel_pos)

    settings.N_PIXELS = len(pixel_pos)
    N = settings.N_PIXELS

    row = []
    col = []

    for i in range(N):
        (k, l) = idx_to_coord[i]
        if (k, l - 1) in coord_to_idx.keys():
            j = coord_to_idx[(k, l - 1)]
            row.append(i)
            col.append(j)
            row.append(j)
            col.append(i)
        if (k - 1, l - 1) in coord_to_idx.keys():
            j = coord_to_idx[(k - 1, l - 1)]
            row.append(i)
            col.append(j)
            row.append(j)
            col.append(i)
        if (k - 1, l) in coord_to_idx.keys():
            j = coord_to_idx[(k - 1, l)]
            row.append(i)
            col.append(j)
            row.append(j)
            col.append(i)
        if (k - 1, l + 1) in coord_to_idx.keys():
            j = coord_to_idx[(k - 1, l + 1)]
            row.append(i)
            col.append(j)
            row.append(j)
            col.append(i)

    entries = np.ones(len(row))
    A = scipy.sparse.coo_matrix((entries, (row, col)))

    return A, pixel_pos


def add_cities(A, pixel_pos, sigma=8):
    city_pos_geo = np.load('Storage/city_pos_geo.npy')
    city_pos = settings.geo_to_complex(city_pos_geo)

    C = settings.N_CITIES

    row = A.row + C
    col = A.col + C

    add_row = []
    add_col = []

    for c in range(C):
        dist = np.abs(pixel_pos - city_pos[c])
        close_nodes = np.where(dist < sigma)[0]
        if len(close_nodes) > 4:
            close_nodes = np.argsort(dist)[:4]
        for n in close_nodes:
            add_row.append(c)
            add_col.append(C + n)
            add_row.append(C + n)
            add_col.append(c)

    row = np.concatenate([add_row, row])
    col = np.concatenate([add_col, col])

    entries = np.ones(len(row))
    A = scipy.sparse.coo_matrix((entries, (row, col)))

    node_pos = np.concatenate([city_pos, pixel_pos])
    node_pos_geo = settings.complex_to_geo(node_pos)
    np.save('Storage/node_pos_geo.npy', node_pos_geo)

    return A


def remove_disconnected_cities(A):
    C = settings.N_CITIES

    A_csr = A.tocsr()
    degree = A_csr.sum(axis=1)

    connected = np.where(degree[:C] > 0)[0]

    if len(connected) < C:
        city_info = np.load('Storage/city_info.npy')
        city_states = np.load('Storage/city_states.npy')
        romanization_times = np.load('Storage/romanization_times.npy')
        city_pos_geo = np.load('Storage/city_pos_geo.npy')
        node_pos_geo = np.load('Storage/node_pos_geo.npy')

        city_info = city_info[connected]
        city_states = city_states[connected]
        romanization_times = romanization_times[connected]
        city_pos_geo = city_pos_geo[connected]
        node_pos_geo = np.concatenate([node_pos_geo[connected], node_pos_geo[C:]])

        np.save('Storage/city_info.npy', city_info)
        np.save('Storage/city_states.npy', city_states)
        np.save('Storage/romanization_times.npy', romanization_times)
        np.save('Storage/city_pos_geo.npy', city_pos_geo)
        np.save('Storage/node_pos_geo.npy', node_pos_geo)

        pixels = np.array(list(range(C, len(A))))
        valid_nodes = np.concatenate([connected, pixels])

        row_valid = np.in1d(A.row, valid_nodes)
        col_valid = np.in1d(A.col, valid_nodes)
        valid_entries = np.logical_and(row_valid, col_valid)

        new_row = A.row[valid_entries]
        new_col = A.col[valid_entries]
        entries = np.ones(len(new_row))

        A = scipy.sparse.coo_matrix((entries, (new_row, new_col)))

        settings.N_CITIES = len(connected)

        return A

    else:
        return A


def create_graph(A):
    graph = nx.from_scipy_sparse_matrix(A)
    nx.write_gml(graph, 'Storage/graph.gml')

    settings.N_NODES = len(graph.nodes)
    settings.N_EDGES = len(graph.edges)


def compute_distance_network(A):
    node_pos_geo = np.load('Storage/node_pos_geo.npy')
    node_pos = settings.geo_to_complex(node_pos_geo)

    N = settings.N_NODES

    row = A.row
    col = A.col

    distances = []

    for i in range(len(row)):
        dist = np.abs(node_pos[row[i]] - node_pos[col[i]])
        distances.append(dist)

    distance_network = scipy.sparse.coo_matrix((distances, (row, col)))
    scipy.sparse.save_npz('Storage/distance_network.npz', distance_network)


def from_image(filename):
    A, pixel_pos = image_to_adjacency(filename)
    A = add_cities(A, pixel_pos)
    A = remove_disconnected_cities(A)
    create_graph(A)
    compute_distance_network(A)


# M = len(ms_pos)
#
# epsilon = 1
# doubles = []
# eliminated = []
#
# dist = np.full((M, M), ms_pos) - np.full((M, M), ms_pos).transpose()
# dist = np.abs(dist)
# for m in range(M):
#     if m not in eliminated and ms_disc_t[m] > 0:
#         dubs = []
#         close = np.where(dist[m] < epsilon)[0]
#         for c in close:
#             if c != m and ms_disc_t[c] == ms_disc_t[m]:
#                 dubs.append(c)
#                 eliminated.append(c)
#         if dubs:
#             dubs.append(m)
#             eliminated.append(m)
#             doubles.append(dubs)
#
# for dubs in doubles:
#     for m in range(len(dubs) - 1):
#         ms_time[dubs[m]] = 0
#         ms_disc_t[dubs[m]] = 0
#
# valid = []
#
# sigma = 5
# for m in range(M):
#     dist = np.abs(pixel_pos - ms_pos[m])
#     if np.min(dist) < sigma and ms_time[m] > 0:
#         kick_out = [[8.1, 35.4], [8.6, 35.08], [10.8, 34.95]]
#         kick_out = geo_to_complex(np.array(kick_out))
#         if min(np.abs(kick_out - ms_pos[m])) > 15:
#             valid.append(m)


# plt.figure(figsize=(14, 10))
#
# node_color = 'black'
# city_color = 'red'
# node_size = 1
# city_size = 80
# edge_width = 3
#
# pos = complex_to_geo(graph_pos)
#
# colors = np.full(len(pos), node_color)
# colors[:M] = city_color
# sizes = np.full(len(pos), node_size)
# sizes[:M] = city_size
#
# nx.draw_networkx_nodes(graph, pos, node_color=colors, node_size=sizes)
# nx.draw_networkx_edges(graph, pos, width=edge_width)
