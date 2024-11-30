import json
import pandas as pd
from pathlib import Path
from typing import List

# Constants
LANDMARKS_DIR = Path("./data/landmarks")
OUTPUT_FILE = Path("./data/cleaned_landmarks.csv")
REQUIRED_COLUMNS = ["type", "id", "lat", "lon", "tags_name", "tags_amenity"]

# Initialize logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json_files_from_directory(directory: Path) -> List[dict]:
    """
    Load all JSON files from a specified directory.

    Args:
        directory (Path): Directory to load files from.

    Returns:
        List[dict]: List of JSON objects loaded from files.
    """
    json_data = []

    if not directory.exists() or not any(directory.iterdir()):
        raise FileNotFoundError(f"The directory {directory} is missing or empty.")

    for filename in directory.iterdir():
        if filename.suffix == '.json':
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if 'elements' in content:
                        json_data.append(content)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing {filename}: {e}")
                continue

    return json_data

def process_landmark_data(json_data: List[dict]) -> pd.DataFrame:
    """
    Process JSON data into a cleaned DataFrame.

    Args:
        json_data (List[dict]): List of JSON objects to process.

    Returns:
        pd.DataFrame: Cleaned DataFrame containing the landmark data.
    """
    # Flatten the JSON and normalize
    dfs = []
    for data in json_data:
        df = pd.json_normalize(data['elements'], sep='_')
        if not df.empty:
            dfs.append(df)

    if not dfs:
        raise ValueError("No valid data frames to process.")

    # Concatenate all data frames
    final_df = pd.concat(dfs, ignore_index=True)

    # Drop rows with missing lat, lon, or name
    final_df.dropna(subset=['lat', 'lon', 'tags_name'], inplace=True)

    # Remove duplicate rows
    final_df.drop_duplicates(subset=['tags_name', 'lat', 'lon'], inplace=True)

    # Reset index after cleaning
    final_df.reset_index(drop=True, inplace=True)

    # Select required columns, if they exist
    final_df_select_col = [col for col in REQUIRED_COLUMNS if col in final_df.columns]
    df_selected = final_df[final_df_select_col]

    return df_selected

def save_landmark_data(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save the cleaned DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame containing the cleaned data.
        output_path (Path): Path where to save the CSV file.
    """
    try:
        df.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Data saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving data to {output_path}: {e}")

def crawl_and_process_landmarks_data() -> None:
    """
    Main function to crawl and process landmarks data.
    It loads, processes, and saves the cleaned data.
    """
    logger.info("Starting the landmark data crawl and processing...")

    # Load the JSON files from the 'landmarks' directory
    json_data = load_json_files_from_directory(LANDMARKS_DIR)

    # Process the JSON data into a cleaned DataFrame
    cleaned_df = process_landmark_data(json_data)

    # Save the cleaned DataFrame to a CSV file
    save_landmark_data(cleaned_df, OUTPUT_FILE)

    logger.info("Landmark data processing completed.")
