# temporal_inferring
This repository contains the code associated to the paper 'Romanization of ancient Tunisia: Inferring temporal activation of the Roman road network' by [AUTHORS]. It contains the algorithm to compute the activation probability of road-segments from a given input database, the verification of the results using a milestone database and a the sensitivity/stability analysis of the method.

### On the position datatype

## File structure
### Input
The input of the program belongs into the 'Data' folder in the form of three files: 'city_database.xls', 'milestone_database.xls' and 'roads_coarse.png'. We have included another image file 'roads_35.png', which is not necessary for the algorithm and is only used for image generation.

###### city_database.xls
This is an .xls Excel-file which contains the necessary data of the cities that should be used in for the algorithm. The exact column structure is required to be readable by the code. The file consists of 14 columns which are the following

| site_key | modern name | latin name | X      |       Y | Status BC | Status 0-50 | ... | Status 350-400 |
| ---------|-------------|------------|--------|---------|-----------|-------------| --- | ---------------|
| string   |  string     |  string    |decimal | decimal | string    | string       | ... |  string        |

The first three columns are only information about the cities to identify them more easily but have no effect on the algorithm. The X/Y-values denote the geographical position (longitude/latitude) of the cities and are required to be decimal numbers of the form 12.3456789. The 9 status columns need to contain the strings 'civita', 'municipium' or 'colonia'. Abbreaviations like 'civ', 'mun', 'col' are not accepted. If multiple status are given, e.g. 'civita/colonia', only the higher status is considered. Additional information/annotations in the status fields do not lead to an error, but are simply ignored.

###### milestone_database.xls
This is an .xls Excel-file which contains the necessary data of the milestones that should be used to validate the results. The exact column structure is required to be readable by the code. The file consists of 6 columns which are the following

| ms_key | site_key | start date | end date | X       | Y      |
| ------ |----------|------------|----------|---------|--------|
| string |  string  |  integer   | integer  | decimal | decimal|    

The first two columns are only information about the milestones to identify them more easily but have no effect in the validation. The start and end date indicate the time period in which the placement of the milestone can be dated. These dates need to be written as an integer for the year without AD/BC. Years BC can be deoted by negative integers. The date that is used b the algorithm for validation is the mid-point between start and end date. The X/Y-values denote the geographical position (longitude/latitude) of the milestones and are required to be decimal numbers of the form 12.3456789.

###### roads_coarse.png
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
An `N_MILESTONES` float array that contains the date that is associated to each milestone. This is the mid-point between the start and end date that were provided in the milestone database. To associate this date `ms_time` to a discrete time-frame use `np.ceil(ms_time / settings.TIME_RESOLUTION)`. Note hat this only works properly for positive dates.

#### node_pos_geo.npy
An `N_NODESx2` float matrix that contains the geographical position of each node in the road-network. The first column contain the longitude and the second column the latitude of the nodes. These geographical positions can be transformed to a more usable format by `storage.geo_to_complex()`. The first `N_CITIES` columns are of the city-nodes and therefore identical to `city_pos_geo.npy`.

#### romanization_times.npy
An `N_MILESTONES` integer array that contains the timeframe in which each of the cities gets romanized.

#### shortest_paths.npy
An 'N_CITIESxN_CITIES' array that contains python lists. For a pair of cities c1, c2, the list contains all edges that lie in *a* shortest path from c1 to c2. An edge is encoded as a python list of two elements which are the node-indices of its endpoints. These shortest paths are computed in `dijkstra.compute_all_shortest_paths`. To load this file it is necessary to set `allow_pickle=True`, i.e. to use `np.load('Storage/shortest_paths.npy', allow_pickle=True)`.




