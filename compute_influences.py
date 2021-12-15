import numpy as np
import settings

# This script contains implementations of the influence functions that were proposed in the publication. Requires the
# shortest path distances between to be computed in advance and saved in the Storage-folder


# Computes the influences as proposed in the publication with a distance factor of rho=0.08. Saves the influences as a
# N-cities x N_cities matrix such that pi[p][c] is the influence of p on c.
def standard():
    city_distances = np.load('Storage/city_distances.npy')

    rho = 0.08
    def func(x):
        x = x * rho
        return np.exp(-x)

    f = np.vectorize(func, otypes=[float])
    pi = f(city_distances)
    pi = pi - np.eye(len(pi))

    np.save('Storage/influence_matrix.npy', pi)


# Computes the influences as proposed in the publication with a distance factor of rho=0.08. Additionally, the city
# status is included to increase the influence of ciies with a higher status. Saves the influences as a
# N-cities x N_cities matrix such that pi[p][c] is the influence of p on c.
def include_status():
    city_distances = np.load('Storage/city_distances.npy')
    city_states = np.load('Storage/city_states.npy')
    t_rom = np.load('Storage/romanization_times.npy')

    rho = 0.08
    def func(x):
        x = x * rho
        return np.exp(-x)

    f = np.vectorize(func, otypes=[float])
    pi = f(city_distances)
    pi = pi - np.eye(len(pi))

    def status_factor(status):
        if status == 'civ':
            return 1
        if status == 'mun':
            return 2
        if status == 'col':
            return 2.5

    for c in range(settings.N_CITIES):
        P_c = np.where(t_rom < t_rom[c])[0]
        for p in P_c:
            pi[p][c] = status_factor(city_states[p][t_rom[c]]) * pi[p][c]

    np.save('Storage/influence_matrix.npy', pi)
