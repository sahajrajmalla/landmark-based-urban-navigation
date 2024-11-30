import h3
from sklearn.cluster import DBSCAN
import numpy as np
from typing import List, Dict

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
        clustering = DBSCAN(eps=self.eps, min_samples=self.min_samples).fit(coords)
        return clustering.labels_

    def rank_clusters(self, labels: np.ndarray) -> List[tuple]:
        """
        Rank clusters by size, prioritizing larger clusters.
        """
        unique, counts = np.unique(labels, return_counts=True)
        cluster_counts = dict(zip(unique, counts))
        return sorted(cluster_counts.items(), key=lambda x: x[1], reverse=True)

    def handle_noise_points(self, landmarks: List[Dict], labels: np.ndarray) -> List[Dict]:
        """
        Handle noise points identified by DBSCAN (those labeled as -1).
        """
        return [landmarks[i] for i in range(len(labels)) if labels[i] == -1]

    def select_priority_landmark(self, landmarks: List[Dict], labels: np.ndarray) -> Dict:
        """
        Select the priority landmark from the largest cluster based on a predefined or custom priority order.
        """
        sorted_clusters = self.rank_clusters(labels)
        top_cluster_label = sorted_clusters[0][0]  # Largest cluster's label

        if top_cluster_label == -1:
            noise_points = self.handle_noise_points(landmarks, labels)
            if noise_points:
                return noise_points[0]  # Return first noise point as fallback

        top_cluster_landmarks = [landmarks[i] for i in range(len(labels)) if labels[i] == top_cluster_label]
        
        for priority in self.priority_order:
            for landmark in top_cluster_landmarks:
                if landmark['type'] == priority:
                    return landmark

        return top_cluster_landmarks[0]  # Fallback to first landmark in the largest cluster

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
