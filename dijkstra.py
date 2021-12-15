import numpy as np
import scipy.sparse
import settings

# This script contains the implementation of a Dijkstra-algorithm


# Loads the network that is represented by the Storage/distance_network.npz coo_matrix and computes for each pair of
# cities the shortest paths in the network between them. The paths are saved as a N_cities x N_cities np.array whose
# entries are lists containing the edges of the shortest paths. An edge is a tuple of the two node indices in ascending
# order. If there are multiple shortest paths, all of them are added to the list. Also saves the lengths of the the
# shortest path between any teo cities as a N_cities x N_cities np.array named city_distances.npy.
def compute_all_shortest_paths():
    A = scipy.sparse.load_npz('Storage/distance_network.npz')
    row = A.row
    col = A.col
    dist = A.data

    A = A.tocsr()

    N = settings.N_NODES
    C = settings.N_CITIES

    city_distances = np.zeros((C, C))
    paths = np.empty((C, C), dtype=object)

    neighbors = {}
    for k in range(len(row)):
        i = row[k]
        if i not in neighbors:
            neighbors[i] = {}
        neighbors[i][col[k]] = dist[k]

    for origin in range(C):
        dist_from_origin = np.full(N, np.inf)
        dist_from_origin[origin] = 0

        unvisited = set(range(N))

        while unvisited:
            current = min(unvisited, key=lambda v: dist_from_origin[v])
            if dist_from_origin[current] == np.inf:
                break
            if current >= C or current == origin:
                for n in neighbors[current]:
                    if dist_from_origin[n] > dist_from_origin[current] + A[current, n]:
                        dist_from_origin[n] = dist_from_origin[current] + A[current, n]
            unvisited.remove(current)

        city_distances[origin] = dist_from_origin[:C]

        for target in range(C):
            front = set()
            front.add(target)
            edges = []
            while front:
                new_front = set()
                for f in front:
                    for p in neighbors[f]:
                        if p > C and dist_from_origin[p] + A[p, f] == dist_from_origin[f]:
                            if f != target:
                                if p < f:
                                    edges.append([p, f])
                                else:
                                    edges.append([f, p])
                            new_front.add(p)

                front = new_front

            paths[origin, target] = edges

    np.save('Storage/city_distances.npy', city_distances)
    np.save('Storage/shortest_paths.npy', paths, allow_pickle=True)
