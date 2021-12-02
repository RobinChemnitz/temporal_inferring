import numpy as np
import settings


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
