import numpy as np
import data_reader
import network_construction
import dijkstra
import compute_influences
import algorithm
import plots
import milestone_validation
import robustness
import settings


def process_data():
    data_reader.read_city_database()
    data_reader.read_milestone_database()

    network_construction.from_image('roads_coarse')

    dijkstra.compute_all_shortest_paths()


def generate_images():
    T = settings.N_TIMEFRAMES

    compute_influences.standard()
    alpha = algorithm.temporal_activation_probability()
    compute_influences.include_status()
    alpha_states = algorithm.temporal_activation_probability()

    t_rom = np.load('Storage/romanization_times.npy')
    city_pos_geo = np.load('Storage/city_pos_geo.npy')

    city_markers = []
    for t in range(T):
        city_markers.append(city_pos_geo[np.where(t_rom <= t)[0]])
    city_markers = np.array(city_markers, dtype=object)

    plots.visualize_temporal_edge_values(alpha[1:], 'Activation_Probability', markers=city_markers[1:])

    ms_time = np.load('Storage/milestone_times.npy')
    ms_pos_geo = np.load('Storage/milestone_pos_geo.npy')

    ms_time = np.ceil(ms_time / settings.TIME_RESOLUTION)
    ms_markers = []
    for t in range(T):
        ms_markers.append(ms_pos_geo[np.where(ms_time <= t)[0]])
    ms_markers = np.array(ms_markers, dtype=object)

    plots.visualize_temporal_edge_values(alpha[1:], 'Temporal_Milestones', markers=ms_markers[1:], ms=80,
                                         mstyle='^')

    diff = np.empty(T, dtype=object)
    for t in range(T):
        diff[t] = {}
        for e in alpha[t]:
            diff[t][e] = alpha_states[t][e] - alpha[t][e]

    plots.visualize_temporal_edge_values(diff[[2, 4, 6]], 'Activation_Shift', ['100 AD', '200 AD', '300 AD'],
                                         colormap='seismic', vmin=-0.2, vmax=0.2)

    plots.draw_network()
    plots.cascade_images([1, 2, 3])

    alpha = algorithm.temporal_activation_probability()
    values = milestone_validation.evaluate_activation_prob(alpha)
    order = np.array([9, 11, 19, 22, 3, 17, 15, 16, 1, 6, 12, 4, 18, 20, 21, 5, 10, 23, 0, 2, 7, 8, 13, 14])
    milestone_validation.milestone_evolution(values, 'Milestone_Evolution', order=order)


# process_data()
settings.init_from_storage()
# generate_images()

# msd = robustness.sensitivity(1000, 0.2)
msd = np.load('Storage/sensitivity_msd.npy', allow_pickle=True)
city_pos_geo = np.load('Storage/city_pos_geo.npy')
t_rom = np.load('Storage/romanization_times.npy')
city_markers = []
for t in range(settings.N_TIMEFRAMES):
    city_markers.append(city_pos_geo[np.where(t_rom <= t)[0]])
city_markers = np.array(city_markers, dtype=object)
plots.visualize_temporal_edge_values(msd[[2,4,6]], 'Sensitivity_MSD', ['100 AD', '200 AD', '300 AD'], vmax=0.3,
                                     markers=city_markers[1:])


# sum = np.zeros(settings.N_CITIES)
# for city in range(settings.N_CITIES):
#     sd = robustness.stability(city)
#     for t in range(settings.N_TIMEFRAMES):
#         for e in sd[t]:
#             sum[city] = sum[city] + sd[t][e]

selected = [28, 18]

for city in selected:
    sd = robustness.stability(city)
    city_markers = []
    for t in range(settings.N_TIMEFRAMES):
        city_markers.append([city_pos_geo[city]])
    city_markers = np.array(city_markers, dtype=object)

    plots.visualize_temporal_edge_values(sd[[2,4,6]], 'Stability_' + str(city), ['100 AD', '200 AD', '300 AD'],
                                         ms=100, markers=city_markers[[2,4,6]])
