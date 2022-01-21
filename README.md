# temporal_inferring
This repository contains the code associated to the paper 'Romanization of ancient Tunisia: Inferring temporal activation of the Roman road network' by [AUTHORS]. It contains the algorithm to compute the activation probability of road-segments from a given input database, the verification of the results using a milestone database and the sensitivity/stability analysis of the method.

## Program structure

#### main.py
This is the intended entry point of the program. From here one can load data-sets, execute the algorithm and generate output images. It is important to initialize the settings before any computation, see `settings.py`.

#### settings.py
The main purpose of this module is to store global variables of the program like thenumber of cities, milestones etc. This information needs to be initialized before any computation. This is either done automatically by processing the data using `data_ready.py` and `network_construction.py` or by calling `setting.init_from_storage()` if the processed data is already in the Storage folder. Additionally, `storage.py` contains the functions to convert geographical coordinates to the complex datatype, see section *On the position datatype*.

#### data.reader.py
This is the first module that needs to be called when a new city-/milestone-database (see section **Input**) is provided. The processed data will be saved into the Storage folder and the information on the cities/milestones in `settings.py` is updated. This module does not handle the input of the road-map, which is handled by `network_construction.py` instead. 

#### network_construction.py
This module reads the coarse image of the road map and generates a network from it that contains the cities. Hence, the city-database must already be processed in the Storage folder. 

#### dijkstra.py
This module only conists of an implementation of Dijkstra's algorithm, which is used in the network construction. We implemented a modified version of the algorithm tha computes *all* shortest paths if there are multiple.

#### compute_influences.py
This module contains thecomputation of the influence functions that were proposed in the paper. When called, these functions compute all influences in a matrix which is saved into the Storage folder as `influence_matrix.npy`, see the **Storage** section below.

#### algorithm.py
This module only contains one function which is the main algorithm of the program, which computes the activation probability of each road-segment for each point in time. When executing the algorithm, the Storage folder must be fully initialized, including `influence_matrix.npy` which is computed by `compute_influences.py`.

#### milestone_validation.py
This module contains the computation of the activation probability of each of the milestones. This requires the Storage folder to be fully initialized and takes the activation probability of the road-segments as an input. This activation probability can be computed using `algorithm.py`. If desired, duplicates in the milestone data can be eliminated before executing `evaluate_activation_prob` by calling `eliminate_doubles()`. An example of the full use of `milestone_validation.py` can be seen in `image_generator.milestone_activation()`.

#### robustness.py
This module computes the sensitiity and stability of the method. This requires the Storage folder to be fully initialized, including `influence_matrix.npy`. Since the sensitivity uses a Monte Carlo method of at least 1000 iterations, this computation can be very time-consuming.

#### image_generator.py
This module is directing the creation of the output images which are shown in the puplication. Each of these functions can be seen as an example of how the respecive features of the program can be used. Minor tweaks in the parameters of the image generation can be done here. The actual code that builds the images is out-sourced to `plots.py`.

#### plots.py
This module contains the code that builds up the images which can be seen in the publication. To generate the images, use the functions `image_generator.py` instead. If major changes in the images are desired, these changes can be made in `plots.py`.

## File structure

### On the position datatype
The locations of cities, milestones, network nodes are usually provided in the form of geographical coordinates, i.e. longitude and latitude. We call this type of position the *geographical position* and store it as a list or numpy array of length 2. However, geographical coordinates are not particularly easy to handle, e.g. when computing distances. Therfore, we convert gepgraphical coordinates into complex numbers where the real part encodes the longitude and the imaginary part encodes the latitude. The conversion of longitude-/latitude-units to kilometers is dependent on the position on the globe. However, the region that we consider is small enough that these differences become 
negligible. We apply a conversion of 1 longitude-unit = 89.67 km and 1 latitude-unit = 111.2 km. Converting one data-type into the other can be done using `settings.py`. Generally, position data should always be converted to geographical coordinates before using them in an output. 

### Input
The input of the program belongs into the 'Data' folder in the form of three files: 'city_database.xls', 'milestone_database.xls' and 'roads_coarse.png'. We have included another image file 'roads_35.png', which is not necessary for the algorithm and is only used for image generation.

#### city_database.xls
This is an .xls Excel-file which contains the necessary data of the cities that should be used in for the algorithm. The exact column structure is required to be readable by the code. The file consists of 14 columns which are the following

| site_key | modern name | latin name | X      |       Y | Status BC | Status 0-50 | ... | Status 350-400 |
| ---------|-------------|------------|--------|---------|-----------|-------------| --- | ---------------|
| string   |  string     |  string    |decimal | decimal | string    | string      | ... |  string        |

The first three columns are only information about the cities to identify them more easily but have no effect on the algorithm. The X/Y-values denote the geographical position (longitude/latitude) of the cities and are required to be decimal numbers of the form 12.3456789. The 9 status columns need to contain the strings 'civita', 'municipium' or 'colonia'. Abbreaviations like 'civ', 'mun', 'col' are not accepted. If multiple status are given, e.g. 'civita/colonia', only the higher status is considered. Additional information/annotations in the status fields do not lead to an error, but are simply ignored.

#### milestone_database.xls
This is an .xls Excel-file which contains the necessary data of the milestones that should be used to validate the results. The exact column structure is required to be readable by the code. The file consists of 6 columns which are the following

| ms_key | site_key | start date | end date | X       | Y      |
| ------ |----------|------------|----------|---------|--------|
| string |  string  |  integer   | integer  | decimal | decimal|    

The first two columns are only information about the milestones to identify them more easily but have no effect in the validation. The start and end date indicate the time period in which the placement of the milestone can be dated. These dates need to be written as an integer for the year without AD/BC. Years BC can be deoted by negative integers. The date that is used b the algorithm for validation is the mid-point between start and end date. The X/Y-values denote the geographical position (longitude/latitude) of the milestones and are required to be decimal numbers of the form 12.3456789.

#### roads_coarse.png
This image file is the blueprint for the road-network that is considered in the algorithm. It is important that the pixel colors are purely binary, i.e. white or black. Each black pixel of the image represents one node of the network, so the resolution of the image should not be too high. Ideally, the resolution is chosen such that each road only has a width of one pixel.

### Storage
Since the same data is often used for multiple executions of the code, the processed data is stored in the 'Storage' folder. Most of the files are numpy matrices .npy that can be loaded using `np.load('Storage/filename.npy')`. Here, we list all the files that get stored in this folder and how to use them in alphabetical order. 

#### city_distances.npy
An `N_CITIESxN_CITIES` float matrix that contains the distance between any two cities inside the road-network (*not* their geographical distance), measured in kilometers. This is the distance that is used for the calculaion of the influence.

#### city_info.npy
An `N_CITIESx3` string matrix that contains the information of the cities. The three columns contain the site_key, modern name, latin name. This information is used to identify a city based on its index in the program. 

#### city_pos_geo.npy
An `N_CITIESx2` float matrix that contains the geographical position of each city. The first column contain the longitude and the second column the latitude of the city. These geographical positions can be transformed to a more usable format by `storage.geo_to_complex()`.

#### city_states.npy
An `N_CITIESxN_TIMEFRAMES` (so in our case `N_CITIESx9`) matrix whose values are strings of maximum length 3. These strings indicate what status a city has in each of the timeframes. The 3-letter abbreviations used are 'civ', 'mun' and 'col'. If the city was not romanized in a timeframe, i.e. does not have a status yet, its entry is ''.

#### distance_network.npz
An `scipy.sparse.coo_matrix` of float values. This is the weighted adjacency matrix of the road-network, hence is of the size `N_NODESxN_NODES`. The entries indicate the length of the edges which are measure in kilometers. To load the matrix use `scipy.sparse.load_npz('Storage/distance_network.npz')`. The first `N_CITIES` indices are of the city-nodes.

#### influence_matrix.npy
An `N_CITIESxN_CITIES` float matrix the influence between the cities that were computed by `compute_influences.py`. The entry the in row p and column c is the influence of p on c.

#### milestone_info.npy
An `N_MILESTONESx2` string matrix that contains the information of the milestones. The two columns contain the ms_key and the site_ke. This information is used to identify a milestone based on its index in the program. 

#### milestone_pos_geo.npy
An `N_MILESTONESx2` float matrix that contains the geographical position of each milestone. The first column contains the longitude and the second column the latitude of the milestone. These geographical positions can be transformed to a more usable format by `storage.geo_to_complex()`.

#### milestone_times.npy
An `N_MILESTONES` float array that contains the date that is associated to each milestone. This is the mid-point between the start and end date that were provided in the milestone database. To associate this date `ms_time` to a discrete time-frame use `np.ceil(ms_time / settings.TIME_RESOLUTION)`. Note that this only works properly for positive dates.

#### node_pos_geo.npy
An `N_NODESx2` float matrix that contains the geographical position of each node in the road-network. The first column contain the longitude and the second column the latitude of the nodes. These geographical positions can be transformed to a more usable format by `storage.geo_to_complex()`. The first `N_CITIES` columns are of the city-nodes and therefore identical to `city_pos_geo.npy`.

#### romanization_times.npy
An `N_MILESTONES` integer array that contains the timeframe in which each of the cities gets romanized.

#### shortest_paths.npy
An 'N_CITIESxN_CITIES' array that contains python lists. For a pair of cities c1, c2, the list contains all edges that lie in *a* shortest path from c1 to c2. An edge is encoded as a python list of two elements which are the node-indices of its endpoints. These shortest paths are computed in `dijkstra.compute_all_shortest_paths`. To load this file it is necessary to set `allow_pickle=True`, i.e. to use `np.load('Storage/shortest_paths.npy', allow_pickle=True)`.




