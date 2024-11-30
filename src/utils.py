import pandas as pd
import numpy as np
from typing import List, Dict

from tqdm import tqdm
from math import radians, cos, sin, sqrt, atan2, degrees


def load_landmarks(file_path: str) -> List[Dict]:
    """
    Load landmarks data from a CSV file and convert to dictionary format.
    """
    landmarks = pd.read_csv(file_path)
    return landmarks.to_dict('records')

def load_buildings(file_path: str) -> pd.DataFrame:
    """
    Load building data and ensure latitude and longitude are of float type.
    """
    buildings = pd.read_csv(file_path)
    buildings['latitude'] = buildings['latitude'].astype(float)
    buildings['longitude'] = buildings['longitude'].astype(float)
    return buildings

def preprocess_landmark_tag(landmark_tag: List[Dict]) -> pd.DataFrame:
    """
    Process and format the landmark_tag into a DataFrame.
    """
    # Replace None values with NaN-filled dictionaries
    landmark_tag = [
        i or {"name": np.nan, "lat": np.nan, "lon": np.nan, "type": np.nan}
        for i in landmark_tag
    ]
    
    # Create DataFrame and handle string manipulation
    landmark_tag_df = pd.DataFrame(landmark_tag).add_prefix("landmark_")
    landmark_tag_df["landmark_tags_name"] = landmark_tag_df["landmark_tags_name"].str.split().str.join('_')

    return landmark_tag_df


def haversine_distance(coord1, coord2, round_to=0):
    """
    Calculate the Haversine distance between two coordinates (lat/lon).
    Returns distance in meters.
    """
    R = 6371000  # Radius of Earth in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    
    a = sin(dphi/2)**2 + cos(phi1) * cos(phi2) * sin(dlambda/2)**2
    distance = 2 * R * atan2(sqrt(a), sqrt(1 - a))
    
    return round(distance, round_to) if round_to else int(distance)


def calculate_initial_compass_bearing(pointA, pointB):
    """
    Calculate the compass bearing from pointA to pointB.
    Returns the bearing in degrees (0 = North, 90 = East, 180 = South, 270 = West).
    """
    lat1 = radians(pointA[0])
    lat2 = radians(pointB[0])
    dLon = radians(pointB[1] - pointA[1])
    
    x = sin(dLon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
    
    initial_bearing = atan2(x, y)
    initial_bearing = degrees(initial_bearing)
    
    compass_bearing = (initial_bearing + 360) % 360  # Normalize to 0-360
    return compass_bearing


def preprocess_landmarks(ktm_buildings):
    """
    Preprocess the ktm_buildings DataFrame by removing rows where 'landmark_tags_name' is null.
    """
    ktm_buildings = ktm_buildings[ktm_buildings.landmark_tags_name.notnull()]
    return ktm_buildings
