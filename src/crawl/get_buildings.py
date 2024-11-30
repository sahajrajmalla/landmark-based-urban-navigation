import logging
from pathlib import Path
import osmnx as ox
from shapely.geometry import MultiPolygon
import pandas as pd
from typing import Optional


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_building_data(place_name: str) -> Optional[pd.DataFrame]:
    """
    Fetch building data from OpenStreetMap for a given place.
    
    Args:
        place_name (str): The name of the place to fetch data for (e.g., "Kathmandu, Nepal").
    
    Returns:
        pd.DataFrame | None: A DataFrame with building data or None if an error occurs.
    """
    try:
        logger.info(f"Fetching building data for {place_name}...")
        building_data = ox.features_from_place(place_name, tags={'building': True})
        logger.info(f"Successfully fetched {len(building_data)} building entries.")
        return building_data
    except Exception as e:
        logger.error(f"Error fetching building data: {e}")
        return None


def process_building_data(building_data: pd.DataFrame) -> pd.DataFrame:
    """
    Process building data by converting geometries and calculating centroids.
    
    Args:
        building_data (pd.DataFrame): The raw building data DataFrame.
    
    Returns:
        pd.DataFrame: The processed DataFrame with centroid and latitude/longitude columns.
    """
    # Convert Polygon geometries to MultiPolygon where necessary
    building_data['geometry'] = building_data['geometry'].apply(
        lambda x: MultiPolygon([x]) if x.geom_type == 'Polygon' else x
    )

    # Calculate centroid of each building (considering projection for accuracy)
    building_data['centroid'] = building_data['geometry'].centroid

    # Extract latitude and longitude
    building_data['latitude'] = building_data['centroid'].apply(lambda point: point.y if point else None)
    building_data['longitude'] = building_data['centroid'].apply(lambda point: point.x if point else None)
    selected_cols = [
        "amenity",
        "building",
        "name",
        "geometry",
        'centroid',
        'latitude',
        'longitude'
                    ]
    select_cols_building_data= building_data[selected_cols]
    select_cols_building_data.reset_index(inplace=True)
    return select_cols_building_data


def save_building_data(building_data: pd.DataFrame, output_dir: Path) -> None:
    """
    Save the processed building data to CSV files.
    
    Args:
        building_data (pd.DataFrame): The processed building data.
        output_dir (Path): The directory where the CSV files will be saved.
    """
    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save the data to CSV
    building_data.to_csv(output_dir / "kathmandu_buildings.csv", index=False)
    logger.info(f"Data saved to {output_dir / 'kathmandu_buildings.csv'}")


def save_landmarks(building_data: pd.DataFrame, output_dir: Path) -> None:
    """
    Save the data for potential landmarks (buildings with names) to a CSV file.
    
    Args:
        building_data (pd.DataFrame): The processed building data.
        output_dir (Path): The directory where the CSV file will be saved.
    """
    landmarks_data = building_data[building_data['name'].notnull()]
    landmarks_data.to_csv(output_dir / "potential_landmarks.csv", index=False)
    logger.info(f"Landmarks data saved to {output_dir / 'potential_landmarks.csv'}")


def crawl_buildings_data() -> None:
    """
    Main function to crawl building data, process it, and save it to files.
    """
    place_name = "Kathmandu, Nepal"
    output_dir = Path(__file__).resolve().parent / "../../data"

    # Step 1: Fetch the data
    building_data = fetch_building_data(place_name)
    if building_data is None:
        logger.error("Failed to fetch building data. Exiting.")
        return

    # Step 2: Process the data
    building_data = process_building_data(building_data)

    # Step 3: Save the processed data
    save_building_data(building_data, output_dir)
    save_landmarks(building_data, output_dir)


