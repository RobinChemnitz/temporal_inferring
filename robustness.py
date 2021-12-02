import numpy as np
import algorithm
import settings


def bernoulli_perturbation(p, N):
    perturbation = np.random.choice([-1, 0], N, p=[p, 1 - p])
    return perturbation


# Optimize this. this is terrible
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
