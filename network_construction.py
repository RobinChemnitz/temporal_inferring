import numpy as np
import scipy.sparse
import imageio as imio
import networkx as nx
import settings

# This script transforms a black and white .png file of the road map into a discrete road-network that contains the
# cities. The processed network is saved in the Storage-folder. To automatically generate the network, call
# from_image(filename) which is found at the bottom of this script. Before using this script, the city data should be
# processed.


# Reads a black and white .png image file and interprets black pixels as nodes creates edges to adjacent pixels in the
# 8-pixel neighborhood. Returns the adjacency matrix of the network as a scipy.coo_matrix and the position of the nodes
# in the complex data format as an np.array. The complex position of a node is derived from the location in the image
# and the geographical information in the settings script.
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


# Adds a node to the road network for each city and connects it to the 4 closest road-nodes within a radius of sigma km.
# If there are no road-nodes inthat radius, the city is added without connections. The initial network is given by the
# adjacency matrix A as a coo_marix and the positions of the nodes as an np.array. Returns the new adjacency matrix as a
# coo_matrix. The cities come first in the new matrix, i.e. their index coincides with their position in the city data.
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


# Takes an adjacency matrix A, that was generated by add_cities and determines which cities are not connected to the
# network. Those cities will be deleted from the adjacency matrix as well as from all city data files in the
# Storage-folder. Returns the updated adjacency matrix.
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


# Creates a networkx.Graph from a scipy.sparse matrix (like coo_matrix) and saves it as graph.gml in the Storage-folder.
def create_graph(A):
    graph = nx.from_scipy_sparse_matrix(A)
    nx.write_gml(graph, 'Storage/graph.gml')

    settings.N_NODES = len(graph.nodes)
    settings.N_EDGES = len(graph.edges)


# Given an adjacency matrix as a coo_matrix, computes the edge lengths in km from the geographical positions of the
# nodes which should be stored in Storage/node_pos_geo.npy. Saves the weighted adjacency matrix as a coo_matrix in the
# file distance_network.npz in the Storage-folder.
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


# Automatically generates the road-network from a .png file and embeds the cities into the network. Cities that cannot
# be embedded into the network will be deleted from the Storage files. filename should be the name of the image,
# without the .png ending, that lies in the Data-folder. Generates the files node_pos_geo-npy, graph.gml and
# distance_network.npz. The exact data formats are specified in the README.md.
def from_image(filename):
    A, pixel_pos = image_to_adjacency(filename)
    A = add_cities(A, pixel_pos)
    A = remove_disconnected_cities(A)
    create_graph(A)
    compute_distance_network(A)
