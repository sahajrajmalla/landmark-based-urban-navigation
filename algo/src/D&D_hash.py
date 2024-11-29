import pandas as pd

banepa_buildings = pd.read_csv("./banepa_buildings.csv")
banepa_buildings


import h3
from sklearn.cluster import DBSCAN
import numpy as np

class LandmarkPriority:

    def __init__(self, hex_resolution=7):
        self.hex_resolution = hex_resolution

    def get_hexagons(self, lat, lon):
        h3_index = h3.geo_to_h3(lat, lon, self.hex_resolution)
        return h3.k_ring(h3_index, 1)

    def cluster_landmarks(self, landmarks):
        coords = np.array([(landmark['lat'], landmark['lon']) for landmark in landmarks])
        # coords = landmarks_df[['lat', 'lon']].values  # Extract only lat and lon columns as a numpy array
        clustering = DBSCAN(eps=0.005, min_samples=5).fit(coords)
        labels = clustering.labels_
        return labels

    def rank_clusters(self, labels):
        unique, counts = np.unique(labels, return_counts=True)
        cluster_counts = dict(zip(unique, counts))
        # Sort clusters by size
        sorted_clusters = sorted(cluster_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_clusters

    def select_priority_landmark(self, landmarks, labels):
        sorted_clusters = self.rank_clusters(labels)
        top_cluster_label = sorted_clusters[0][0]
        top_cluster_landmarks = [landmarks[i] for i in range(len(labels)) if labels[i] == top_cluster_label]

        # Prioritization logic
        priority_order = ["temple", "tourist_spot", "bus_stop", "government_building", "market", "school"]
        for priority in priority_order:
            for landmark in top_cluster_landmarks:
                if landmark['type'] == priority:
                    return landmark

        # In case no landmark matches the prioritization logic
        return top_cluster_landmarks[0]

    def get_priority_landmark_for_hex(self, lat, lon, landmarks):
        hexagons = self.get_hexagons(lat, lon)
        landmarks_in_hex = [landmark for landmark in landmarks if h3.geo_to_h3(landmark['lat'], landmark['lon'], self.hex_resolution) in hexagons]
        if not landmarks_in_hex:
            return None
        labels = self.cluster_landmarks(landmarks_in_hex)
        priority_landmark = self.select_priority_landmark(landmarks_in_hex, labels)
        return priority_landmark
    
    
    
import pandas as pd

landmarks = pd.read_csv('landmarks_clean.csv')
landmarks = landmarks[["tags_name", "lat", "lon", "tags_amenity"]]
landmarks.columns = ["name", "lat", "lon", "type"]

landmarks_dict = landmarks.to_dict('records')




banepa_buildings.latitude = banepa_buildings.latitude.astype(float)
banepa_buildings.longitude = banepa_buildings.longitude.astype(float)
landmark_tag = []

# visualize with tqdm

for lat, lon in zip(banepa_buildings.latitude, banepa_buildings.longitude):
    landmark_priority = LandmarkPriority()
    priority_landmark = landmark_priority.get_priority_landmark_for_hex(lat, lon, landmarks_dict)
    landmark_tag.append(priority_landmark)
    print(priority_landmark)
    
    
import pandas as pd
import numpy as np

landmark_tag = [i if i else {"name": np.nan, "lat": np.nan, "lon": np.nan, "type": np.nan} for i in landmark_tag]
landmark_tag_df = pd.DataFrame(landmark_tag)
landmark_tag_df.columns = ["landmark_" + i for i in landmark_tag_df.columns]

# Handle NaN values in the lambda function
landmark_tag_df["landmark_name"] = landmark_tag_df["landmark_name"].apply(
    lambda x: "_".join(i.strip() for i in x.split(" ")) if pd.notna(x) else x
)

banepa_buildings = pd.concat([banepa_buildings, landmark_tag_df], axis=1)


import pandas as pd
import geopandas as gpd
import networkx as nx
import math
from math import radians, cos, sin, asin, sqrt, atan2
import osmnx as ox
                
G = ox.graph_from_place('Banepa, Nepal', network_type='drive')

def find_nearest_node(G, point):
    return min(G.nodes, key=lambda x: math.dist((G.nodes[x]['y'], G.nodes[x]['x']), point))

class RouteOptimizer:

    def __init__(self, G, landmark_location, destination_location):
        self.G = G
        self.landmark_location = find_nearest_node(G, landmark_location)
        self.destination_location = find_nearest_node(G, destination_location)
        
    def get_shortest_path(self):
        # impute missing edge speed and add travel times
        self.G = ox.add_edge_speeds(self.G)
        self.G = ox.add_edge_travel_times(self.G)

        # calculate shortest path minimizing travel time
        orig = self.landmark_location
        dest = self.destination_location
        self.path = nx.shortest_path(self.G, orig, dest, 'travel_time')
        return self.path
    
    
    def calculate_initial_compass_bearing(self, pointA, pointB):
        lat1 = math.radians(pointA[0])
        lat2 = math.radians(pointB[0])
        diffLong = math.radians(pointB[1] - pointA[1])
        x = math.sin(diffLong) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))
        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        return compass_bearing


def haversine_distance(coord1, coord2, round_to=0):
    R = 6371000  # radius of Earth in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1, phi2 = radians(lat1), radians(lat2) 
    dphi       = radians(lat2 - lat1)
    dlambda    = radians(lon2 - lon1)
    
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    distance = 2 * R * atan2(sqrt(a), sqrt(1 - a))
    
    if round_to == 0:
        return int(distance)
    
    return round(float(distance), round_to)


# Hash Generation Function
def generate_hash(landmark_name, path, optimizer):
    directions = []
    prev_dir = None
    sum_length = 0

    for i in range(len(path) - 1):
        # Retrieve the coordinates of the nodes from the graph
        pointA = (optimizer.G.nodes[path[i]]['y'], optimizer.G.nodes[path[i]]['x'])
        pointB = (optimizer.G.nodes[path[i + 1]]['y'], optimizer.G.nodes[path[i + 1]]['x'])
        
        bearing = optimizer.calculate_initial_compass_bearing(pointA, pointB)
   
        if i == len(path) - 2:
            print("Last point")
            length = haversine_distance(pointA, pointB, round_to=2)
        else:
            length = haversine_distance(pointA, pointB)
        
        if (bearing >= 0 and bearing < 45) or (bearing >= 315 and bearing < 360):
            dir = "N"
        elif bearing >= 45 and bearing < 135:
            dir = "E"
        elif bearing >= 135 and bearing < 225:
            dir = "S"
        else:
            dir = "W"

        if prev_dir == dir:
            sum_length += length
        else:
            if prev_dir is not None:
                directions.append(f"{prev_dir}_{sum_length}")
            sum_length = length
            prev_dir = dir

    # Add the last direction and length
    if prev_dir is not None:
        directions.append(f"{prev_dir}_{sum_length}")
        
    # make the last direction round to 2 decimal places
    try:
        directions[-1] = f"{directions[-1].split('_')[0]}_{float(directions[-1].split('_')[1]):.2f}"
    except:
        pass

    hash_string = f"{landmark_name}|{'|'.join(directions)}"
    return hash_string
    
# delete rows in banepa_buildings where landmark_name is null
banepa_buildings = banepa_buildings[banepa_buildings.landmark_name.notnull()]

# iterate over the rows of the banepe_buildings dataframe and generate the hash
hashes = []
for index, row in banepa_buildings.iterrows():
    landmark_location = [row.landmark_lat, row.landmark_lon]
    destination_location = (row.latitude, row.longitude)
    optimizer = RouteOptimizer(G, landmark_location, destination_location)
    path = optimizer.get_shortest_path()
    hash_string = generate_hash(row.landmark_name, path, optimizer)
    hashes.append(hash_string)
    print(f"Index: {index} :: Building at ({row.latitude}, {row.longitude}) has hash: {hash_string}")
    
    
banepa_buildings["hashes"] = hashes


json_data = banepa_buildings[["name", "latitude", "longitude", "landmark_name", "landmark_lat", "landmark_lon", "hashes"]]
# write into json file in multiple lines
json_data.to_json("banepa_buildings_with_hashes.json", orient="records")