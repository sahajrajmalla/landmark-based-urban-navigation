import osmnx as ox
import networkx as nx
import pandas as pd
from tqdm import tqdm
from joblib import Parallel, delayed
import h3
from sklearn.cluster import DBSCAN
import numpy as np
from typing import List, Dict
import logging
import gc

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="networkx.utils.backends")

def setup_logging():
    logging.basicConfig(
        filename="output.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

# Landmark Priority Class
class LandmarkPriority:
    def __init__(self, hex_resolution=7, eps=0.005, min_samples=5, priority_order=None):
        self.hex_resolution = hex_resolution
        self.eps = eps
        self.min_samples = min_samples
        self.priority_order = priority_order if priority_order else [
            "temple", "tourist_spot", "bus_stop", "government_building", "market", "school"
        ]

    def get_hexagons(self, lat: float, lon: float) -> List[str]:
        """
        Generate the H3 hexagons (including neighbors) for a given latitude and longitude.
        """
        h3_index = h3.geo_to_h3(lat, lon, self.hex_resolution)
        return h3.k_ring(h3_index, 1)

    def cluster_landmarks(self, landmarks: List[Dict]) -> np.ndarray:
        """
        Perform DBSCAN clustering on landmarks based on latitude and longitude.
        """
        coords = np.array([(landmark['lat'], landmark['lon']) for landmark in landmarks])
        if len(coords) == 0:
            return np.array([])
        clustering = DBSCAN(eps=self.eps, min_samples=self.min_samples).fit(coords)
        return clustering.labels_

    def rank_clusters(self, labels: np.ndarray) -> List[tuple]:
        """
        Rank clusters by size, prioritizing larger clusters.
        """
        if len(labels) == 0:
            return []
        unique, counts = np.unique(labels, return_counts=True)
        cluster_counts = dict(zip(unique, counts))
        return sorted(cluster_counts.items(), key=lambda x: x[1], reverse=True)

    def select_priority_landmark(self, landmarks: List[Dict], labels: np.ndarray) -> Dict:
        """
        Select the priority landmark from the largest cluster based on a predefined or custom priority order.
        """
        if len(labels) == 0:
            return None

        sorted_clusters = self.rank_clusters(labels)
        if not sorted_clusters:
            return None

        top_cluster_label = sorted_clusters[0][0]  # Largest cluster's label

        top_cluster_landmarks = [landmarks[i] for i in range(len(labels)) if labels[i] == top_cluster_label]

        for priority in self.priority_order:
            for landmark in top_cluster_landmarks:
                if landmark['type'] == priority:
                    return landmark

        return top_cluster_landmarks[0] if top_cluster_landmarks else None

    def get_priority_landmark_for_hex(self, lat: float, lon: float, landmarks: List[Dict]) -> Dict:
        """
        Identify the priority landmark for a given latitude and longitude by clustering landmarks in hexagons.
        """
        hexagons = self.get_hexagons(lat, lon)
        landmarks_in_hex = [landmark for landmark in landmarks if h3.geo_to_h3(landmark['lat'], landmark['lon'], self.hex_resolution) in hexagons]

        if not landmarks_in_hex:
            return None

        labels = self.cluster_landmarks(landmarks_in_hex)
        return self.select_priority_landmark(landmarks_in_hex, labels)

# Function to calculate heuristic for A* algorithm
def heuristic(u, v, G):
    """Custom heuristic function for A* algorithm that calculates great-circle distance."""
    u_lat, u_lon = G.nodes[u]['y'], G.nodes[u]['x']
    v_lat, v_lon = G.nodes[v]['y'], G.nodes[v]['x']
    return ox.distance.great_circle_vec(u_lat, u_lon, v_lat, v_lon)

# Function to process scenarios for landmark-based routing
def process_landmark_scenario(building, landmarks, G, landmark_selector):
    """Process a single routing scenario for landmark-based systems."""
    building_coords = (building['latitude'], building['longitude'])
    priority_landmark = landmark_selector.get_priority_landmark_for_hex(
        building['latitude'], building['longitude'], landmarks
    )

    if not priority_landmark:
        return {'Path Length': None, 'Travel Time': None, 'Status': 'Failed'}

    building_node = ox.distance.nearest_nodes(G, building_coords[1], building_coords[0])
    landmark_node = ox.distance.nearest_nodes(G, priority_landmark['lon'], priority_landmark['lat'])

    if not nx.has_path(G, building_node, landmark_node):
        return {'Path Length': None, 'Travel Time': None, 'Status': 'Failed'}

    path = nx.astar_path(G, building_node, landmark_node, heuristic=lambda u, v: heuristic(u, v, G), weight='travel_time')
    path_length = len(path)
    travel_time = sum(
        G.get_edge_data(path[i], path[i+1])[0].get('travel_time', 0)
        for i in range(len(path)-1)
    )

    return {'Path Length': path_length, 'Travel Time': travel_time, 'Status': 'Success'}

def process_traditional_scenario(building, landmark, G):
    """Process a single routing scenario for traditional systems."""
    building_coords = (building['latitude'], building['longitude'])
    landmark_coords = (landmark['lat'], landmark['lon'])

    building_node = ox.distance.nearest_nodes(G, building_coords[1], building_coords[0])
    landmark_node = ox.distance.nearest_nodes(G, landmark_coords[1], landmark_coords[0])

    if not nx.has_path(G, building_node, landmark_node):
        return {'Path Length': None, 'Travel Time': None, 'Status': 'Failed'}

    path = nx.dijkstra_path(G, building_node, landmark_node, weight='travel_time')
    path_length = len(path)
    travel_time = sum(
        G.get_edge_data(path[i], path[i+1])[0].get('travel_time', 0)
        for i in range(len(path)-1)
    )

    return {'Path Length': path_length, 'Travel Time': travel_time, 'Status': 'Success'}

def simulate_routing(buildings_df, landmarks_df, G, algorithm='A*', num_scenarios=1000, landmark_selector=None, chunk_size=10000):
    """Simulate routing scenarios and calculate metrics in chunks."""
    total_results_file = f'{algorithm}_results.csv'
    with open(total_results_file, 'w') as output_file:
        # Write headers
        output_file.write("Path Length,Travel Time,Status\n")

        # Process in chunks
        for chunk_start in tqdm(range(0, num_scenarios, chunk_size), desc="Processing Chunks"):
            chunk_end = min(chunk_start + chunk_size, num_scenarios)
            building_sample = buildings_df.iloc[chunk_start:chunk_end]
            landmark_sample = landmarks_df.sample(min(len(building_sample), len(landmarks_df)))

            if algorithm == 'Landmark':
                args = [
                    (building, landmark_sample.to_dict('records'), G, landmark_selector)
                    for building in building_sample.to_dict('records')
                ]
            else:
                args = [
                    (building, landmark_sample.iloc[0].to_dict(), G)
                    for building in building_sample.to_dict('records')
                ]

            results = Parallel(n_jobs=48, backend="loky", batch_size=10)(
                delayed(process_landmark_scenario if algorithm == 'Landmark' else process_traditional_scenario)(*arg)
                for arg in args
            )

            # Write results
            for result in results:
                output_file.write(f"{result['Path Length']},{result['Travel Time']},{result['Status']}\n")

            # Clean up memory
            del building_sample
            del landmark_sample
            del results
            gc.collect()

            logging.info(f"Processed chunk {chunk_start} to {chunk_end}.")


def calculate_metrics(landmark_file, traditional_file, output_file):
    """Calculate comparison metrics from the saved results."""
    logging.info("Calculating metrics from the saved results.")
    landmark_results = pd.read_csv(landmark_file)
    traditional_results = pd.read_csv(traditional_file)

    comparison_df = pd.DataFrame({
        'Metric': ['Average Path Length', 'Average Travel Time', 'Success Rate'],
        'Landmark-Based': [
            landmark_results['Path Length'].mean(),
            landmark_results['Travel Time'].mean(),
            (landmark_results['Status'] == 'Success').mean()
        ],
        'Traditional': [
            traditional_results['Path Length'].mean(),
            traditional_results['Travel Time'].mean(),
            (traditional_results['Status'] == 'Success').mean()
        ]
    })

    comparison_df.to_csv(output_file, index=False)
    logging.info(f"Comparison metrics saved to {output_file}.")

def main():
    setup_logging()
    logging.info("Starting the routing simulation program.")

    # Load road network and datasets
    logging.info("Loading road network and datasets.")
    G = ox.graph_from_place("Kathmandu, Nepal", network_type="drive")
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    buildings = pd.read_csv('./data/kathmandu_buildings.csv')
    landmarks = pd.read_csv('./data/cleaned_landmarks.csv')

    # Initialize LandmarkPriority
    landmark_selector = LandmarkPriority()

    # Define the number of scenarios and chunk size
    num_scenarios = len(buildings)
    chunk_size = 10000

    # logging.info("Running landmark-based routing simulations.")
    # simulate_routing(buildings, landmarks, G, algorithm='Landmark', num_scenarios=num_scenarios, landmark_selector=landmark_selector, chunk_size=chunk_size)

    logging.info("Running traditional routing simulations.")
    simulate_routing(buildings, landmarks, G, algorithm='Traditional', num_scenarios=num_scenarios, landmark_selector=landmark_selector, chunk_size=chunk_size)

    logging.info("Calculating and saving comparison metrics.")
    calculate_metrics('Landmark_results.csv', 'Traditional_results.csv', 'comparison_metrics.csv')

    logging.info("Program completed successfully.")

if __name__ == "__main__":
    main()
