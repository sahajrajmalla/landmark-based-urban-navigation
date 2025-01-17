import logging
from pathlib import Path
import osmnx as ox
from shapely.geometry import MultiPolygon
import pandas as pd
from typing import Optional


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
EPSG_CODE = "EPSG:4326"


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
    try:
        logger.info("Preprocessing building data...")

        # Convert geometries to MultiPolygon if needed
        building_data["geometry"] = building_data["geometry"].apply(
            lambda x: MultiPolygon([x]) if x.geom_type == "Polygon" else x
        )

        # Calculate centroids
        building_data["centroid"] = building_data["geometry"].centroid

        # Extract latitude and longitude
        building_data["latitude"] = building_data["centroid"].y
        building_data["longitude"] = building_data["centroid"].x

        # Reproject data to EPSG:4326
        building_data = building_data.to_crs(EPSG_CODE)

        # Select relevant columns
        selected_cols = ["amenity", "building", "name", "geometry", "latitude", "longitude"]
        building_data = building_data[selected_cols]

        # Drop rows with missing values
        # building_data.dropna(inplace=True)
        building_data.dropna(subset=["latitude", "longitude"], inplace=True)

        # Remove duplicates
        building_data.drop_duplicates(subset=["latitude", "longitude"], inplace=True)

        logger.info("Preprocessing completed.")
        return building_data
    except Exception as e:
        logger.error(f"Error in preprocessing building data: {e}")
        return None


def validate_data(building_data):
    """
    Validate the integrity and quality of the processed data.

    Args:
        building_data (GeoDataFrame): Processed building data.

    Returns:
        bool: True if validation passes, False otherwise.
    """
    try:
        logger.info("Validating data...")

        # Check for missing values
        if building_data.isnull().sum().any():
            logger.warning("Data contains missing values.")

        # Check for duplicate entries
        if building_data.duplicated(subset=["latitude", "longitude"]).any():
            logger.warning("Data contains duplicate entries.")

        # Ensure geometries are valid
        invalid_geometries = building_data[~building_data["geometry"].is_valid]
        if not invalid_geometries.empty:
            logger.warning(f"Found {len(invalid_geometries)} invalid geometries.")

        logger.info("Validation completed.")
        return True
    except Exception as e:
        logger.error(f"Error in data validation: {e}")
        return False


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
    
    # Step 3: Validate the data
    validate_data(building_data)

    # Step 3: Save the processed data
    save_building_data(building_data, output_dir)
    save_landmarks(building_data, output_dir)


