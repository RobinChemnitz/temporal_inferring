import data_reader
import network_construction
import dijkstra
import compute_influences
import algorithm
import image_generator
import settings


# Reads the files from the 'Data'-folder and saves the processed data in the 'Storage'-folder. If the data has already
# been processed it suffices to call settings.init_from_storage. The input data needs to consist of the files
# city_database.xls, milestone_database.xls and roads_coarse.png. The exact data formats are specified in the README.md.
def process_data():
    data_reader.read_city_database()
    data_reader.read_milestone_database()

    network_construction.from_image('roads_coarse')

    dijkstra.compute_all_shortest_paths()


# If the data hasn't been processed, call process_data(). Otherwise call settings.init_from_storage()

process_data()
settings.init_from_storage()


# Example of how to compute the activation probability alpha from the data in the Storage-folder.

compute_influences.standard()
alpha = algorithm.temporal_activation_probability()


# Generate the images used in the publication.

image_generator.road_activation()
image_generator.milestone_activation()
image_generator.sensitivity()
image_generator.stability()
image_generator.draw_network()
image_generator.cascade_images([1,2,3])
