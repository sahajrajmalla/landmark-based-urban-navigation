import requests
import json
import logging
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "http://overpass-api.de/api/interpreter"
BBOX_SOUTHWEST = (27.5748, 85.2066)
BBOX_NORTHEAST = (27.8663, 85.5540)
LANDMARKS_DIR = Path("./data/landmarks")

# Dictionary of categories and their associated amenities
AMENITIES: Dict[str, List[str]] = {
    "Education": ["school", "university", "college", "library"],
    "Healthcare": ["hospital", "clinic", "doctors", "pharmacy"],
    "Transportation": ["bus_stop", "train_station", "airport", "parking"],
    "Food_and_Drink": ["restaurant", "cafe", "fast_food", "bar"],
    "Shopping": ["supermarket", "mall", "convenience", "clothes"],
    "Leisure_and_Entertainment": ["park", "playground", "cinema", "sports_centre"],
    "Accommodation": ["hotel", "motel", "guest_house"],
    "Financial_and_Professional": ["bank", "atm", "lawyer", "business"],
    "Public_Services": ["post_office", "police", "fire_station", "government"],
    "Worship": ["church", "mosque", "synagogue", "temple"],
    "Health_and_Beauty": ["gym", "spa", "beauty", "tattoo"],
    "Community": ["community_centre", "social_facility", "shelter"],
    "Sports_and_Recreation": ["stadium", "sports_hall", "swimming_pool", "tennis_court"],
    "Tourism": ["museum", "monument", "zoo", "theme_park", "viewpoint"],
    "Infrastructure": ["telecom_tower", "bridge", "power_station"],
    "Emergency_Services": ["ambulance_station", "emergency_phone"],
    "Cultural_and_Historical": ["castle", "archaeological_site"],
    "Natural_Features": ["tree", "forest", "waterfall"],
    "Industrial_and_Commercial": ["factory", "warehouse"],
    "Water_and_Hydrology": ["reservoir", "river"],
    "Agriculture": ["farm", "orchard"],
    "Residential": ["apartment", "house"],
    "Parking_and_Charging": ["car_parking", "charging_station"],
    "Waste_Management": ["waste_basket", "recycling"],
    "Dining": ["pub", "bakery", "ice_cream"]
}


def create_landmarks_directory() -> None:
    """
    Ensure the 'landmarks' directory exists.
    """
    if not LANDMARKS_DIR.exists():
        LANDMARKS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created 'landmarks' directory at {LANDMARKS_DIR}")


def construct_bbox() -> str:
    """
    Construct the bounding box string for Kathmandu using the southwest and northeast corners.
    
    Returns:
        str: Bounding box in the format "lat_southwest,lon_southwest,lat_northeast,lon_northeast".
    """
    bbox = f"{BBOX_SOUTHWEST[0]},{BBOX_SOUTHWEST[1]},{BBOX_NORTHEAST[0]},{BBOX_NORTHEAST[1]}"
    return bbox


def fetch_landmark_data(amenity: str, bbox: str) -> dict:
    """
    Fetch landmark data for a given amenity and bounding box using the Overpass API.
    
    Args:
        amenity (str): The amenity to query (e.g., "restaurant").
        bbox (str): The bounding box for the query.
    
    Returns:
        dict: JSON response from the API containing the queried data.
    """
    query = f"""
    [out:json][timeout:60];
    (
    node["amenity"="{amenity}"]({bbox});
    way["amenity"="{amenity}"]({bbox});
    relation["amenity"="{amenity}"]({bbox});
    );
    out body;
    >;
    out skel qt;
    """

    try:
        response = requests.get(BASE_URL, params={"data": query})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for amenity {amenity}: {e}")
        return {}


def save_landmark_data(category: str, amenity: str, data: dict) -> None:
    """
    Save the landmark data to a JSON file.
    
    Args:
        category (str): The category of the amenity (e.g., "Food_and_Drink").
        amenity (str): The amenity name (e.g., "restaurant").
        data (dict): The data to save (usually fetched from the Overpass API).
    """
    file_path = LANDMARKS_DIR / f"{category}_{amenity}.json"
    
    if data:
        try:
            with open(file_path, "w") as outfile:
                json.dump(data, outfile, indent=4)
            logger.info(f"Saved data for {category}: {amenity} to {file_path}")
        except IOError as e:
            logger.error(f"Error saving data for {category}: {amenity}: {e}")


def crawl_landmarks_data() -> None:
    """
    Crawl landmarks data for all categories and amenities and save to JSON files.
    """
    logger.info("Starting landmark data crawl...")

    # Step 1: Create the 'landmarks' directory if it doesn't exist
    create_landmarks_directory()

    # Step 2: Construct the bounding box for Kathmandu
    bbox = construct_bbox()

    # Step 3: Iterate over all amenities and categories
    for category, amenity_list in AMENITIES.items():
        for amenity in amenity_list:
            logger.info(f"Fetching data for {category}: {amenity}...")
            data = fetch_landmark_data(amenity, bbox)
            if data:
                save_landmark_data(category, amenity, data)
            else:
                logger.warning(f"No data found for {category}: {amenity}")

    logger.info("Landmark data crawl completed.")
