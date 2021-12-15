import numpy as np
import algorithm
import settings

# This script performs the sensitivity/stability analysis like proposed in the publication.


# This is a helper function that generates an np.array with N entries according to a bernoulli distribution.
def bernoulli_perturbation(p, N):
    perturbation = np.random.choice([-1, 0], N, p=[p, 1 - p])
    return perturbation


# Perturbs the romanization times of the cities with the bernoulli perturbation and tracks the mean-squared-distance.
# The msd is returned as an np.array of length N_timeframes with dictionaries as entries. The msd of an edge e=(u,v),
# where u and v are in ascending order in time-frame t is given by msd[t][e].
# This code is not optimized and very time-consuming.
def sensitivity(N_simulations=1000, p=0.2):
    T = settings.N_TIMEFRAMES

    t_rom = np.load('Storage/romanization_times.npy')
    alpha = algorithm.temporal_activation_probability(t_rom)

    msd = np.empty(T, dtype=object)
    for t in range(T):
        msd[t] = {}
        for e in alpha[t]:
            msd[t][e] = 0

    print('Sensitivity progress:')
    percent = 0
    for i in range(N_simulations):
        t_rom_tilde = t_rom + bernoulli_perturbation(p, settings.N_CITIES)
        t_rom_tilde = np.where(t_rom_tilde < 0, 0, t_rom_tilde)
        t_rom_tilde = np.array(t_rom_tilde, dtype=int)

        if np.floor(100 * (i + 1) / N_simulations) > percent:
            percent = np.floor(100 * (i + 1) / N_simulations)
            print(str(percent) + '%')

        alpha_tilde = algorithm.temporal_activation_probability(t_rom_tilde)
        for t in range(T):
            for e in alpha_tilde[t]:
                sd = np.square(alpha[t][e] - alpha_tilde[t][e])
                msd[t][e] = msd[t][e] + sd / N_simulations

    return np.array(msd)


# Performs the computation of the acivation probability alpha as if the city with the specified index did not exist.
# Returns the squared-distance to the unperturbed activation probability as a dictionary of the edges. Edges e=(u,v)
# should be sorted such that u and v are in ascending order.
def stability(city):
    T = settings.N_TIMEFRAMES

    alpha = algorithm.temporal_activation_probability()
    alpha_tilde = algorithm.temporal_activation_probability(forget=city)

    sd = np.empty(T, dtype=object)
    for t in range(T):
        sd[t] = {}
        for e in alpha[t]:
            sd[t][e] = np.square(alpha[t][e] - alpha_tilde[t][e])

    return sd
