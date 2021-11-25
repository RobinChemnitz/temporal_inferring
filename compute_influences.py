import numpy as np


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
