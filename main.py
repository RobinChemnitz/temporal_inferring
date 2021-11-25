import numpy as np

import data_reader
import network_construction
import dijkstra
import compute_influences
import algorithm
import plots
import milestone_validation
import settings


def process_data():
    data_reader.read_city_database()
    data_reader.read_milestone_database()

    network_construction.from_image('roads_coarse')

    dijkstra.compute_all_shortest_paths()

    compute_influences.standard()


def generate_images():
    alpha = algorithm.temporal_activation_probability()

    t_rom = np.load('Storage/romanization_times.npy')
    city_pos_geo = np.load('Storage/city_pos_geo.npy')

    city_markers = []
    for t in range(settings.N_TIMEFRAMES):
        city_markers.append(city_pos_geo[np.where(t_rom <= t)[0]])
    city_markers = np.array(city_markers, dtype=object)

    ms_time = np.load('Storage/milestone_times.npy')
    ms_pos_geo = np.load('Storage/milestone_pos_geo.npy')

    ms_time = np.ceil(ms_time / settings.TIME_RESOLUTION)
    ms_markers = []
    for t in range(settings.N_TIMEFRAMES):
        ms_markers.append(ms_pos_geo[np.where(ms_time <= t)[0]])
    ms_markers = np.array(ms_markers, dtype=object)

    plots.visualize_temporal_edge_values(alpha[1:], 'Activation_Probability_MS.pdf', markers=ms_markers[1:], ms=80,
                                         mstyle='^')
    plots.visualize_temporal_edge_values(alpha[[2, 4, 6]], 'Activation_Probability.pdf',
                                         labels=['100 AD', '200 AD', '300 AD'], markers=city_markers[[2,4,6]])


process_data()
settings.init_from_storage()
#generate_images()

alpha = algorithm.temporal_activation_probability()
values = milestone_validation.evaluate_activation_prob(alpha)
milestone_validation.milestone_evolution(values, list(range(29)), 'Milestone_Activation')

