# Import the crawl_buildings_data function from the appropriate module
from src.crawl.get_buildings import crawl_buildings_data
from src.crawl.get_landmarks import crawl_landmarks_data
from src.preprocess import crawl_and_process_landmarks_data
import pandas as pd
from tqdm import tqdm
from src.select_landmarks import LandmarkPriority
from src.utils import load_landmarks, load_buildings, preprocess_landmark_tag, preprocess_landmarks
import osmnx as ox
from src.route_optimizer import RouteOptimizer

from tqdm import tqdm

def main():
    # Call the function to crawl building data and save to CSV
    crawl_buildings_data()
    crawl_landmarks_data()
    crawl_and_process_landmarks_data()
    

    # Load and preprocess data
    landmarks_dict = load_landmarks('./data/cleaned_landmarks.csv')
    ktm_buildings = load_buildings('./data/kathmandu_buildings.csv').head(10)

    # Initialize LandmarkPriority object
    landmark_priority = LandmarkPriority()

    # Initialize list to store the priority landmarks
    landmark_tag = []

    # Use tqdm for progress visualization
    for lat, lon in tqdm(zip(ktm_buildings['latitude'], ktm_buildings['longitude']), total=len(ktm_buildings)):
        priority_landmark = landmark_priority.get_priority_landmark_for_hex(lat, lon, landmarks_dict)
        
        if priority_landmark:
            landmark_tag.append(priority_landmark)
        else:
            landmark_tag.append(None)

    # Preprocess the landmark tag data into DataFrame
    landmark_tag_df = preprocess_landmark_tag(landmark_tag)

    # Concatenate the original buildings data with the landmark tag data
    ktm_buildings = pd.concat([ktm_buildings, landmark_tag_df], axis=1)

    # Save the final result
    ktm_buildings.to_csv('./data/ktm_buildings_with_landmarks.csv', index=False, encoding='utf-8')
    
    
    # Load the Kathmandu walkable graph
    G = ox.graph_from_place('Kathmandu, Nepal', network_type='walk')

    # Load and preprocess data
    cleaned_ktm_buildings =  pd.read_csv('./data/ktm_buildings_with_landmarks.csv')
    cleaned_ktm_buildings = preprocess_landmarks(cleaned_ktm_buildings)

    # Initialize an empty list to store hashes
    hashes = []

    # Iterate over the rows of the ktm_buildings dataframe and generate the hash
    for index, row in tqdm(cleaned_ktm_buildings.iterrows(), total=len(cleaned_ktm_buildings), desc="Generating Hashes"):
        try:
            # Extract landmark and destination locations
            landmark_location = [row.landmark_lat, row.landmark_lon]
            destination_location = (row.latitude, row.longitude)
            
            # Initialize the RouteOptimizer and generate the shortest path
            optimizer = RouteOptimizer(G, landmark_location, destination_location)
            path = optimizer.get_shortest_path()

            # Generate the hash string for the route
            hash_string = optimizer.generate_hash(row.landmark_tags_name, path)
            hashes.append(hash_string)

            # Print progress for debugging purposes
            print(f"Index: {index} :: Building at ({row.latitude}, {row.longitude}) has hash: {hash_string}")
        except Exception as e:
            print(f"Error at index {index}: {e}")
            hashes.append(None)  # In case of error, append None or handle accordingly

    # Add the generated hashes to the ktm_buildings DataFrame
    cleaned_ktm_buildings["route_hashes"] = hashes

    # Save the DataFrame to CSV format
    cleaned_ktm_buildings.to_csv('./data/ktm_buildings_with_hashes.csv', index=False)

    # Save the DataFrame to JSON format
    cleaned_ktm_buildings.to_json('./data/ktm_buildings_with_hashes.json', orient='records', lines=True)

    print("Data has been successfully saved to 'ktm_buildings_with_hashes.csv' and 'ktm_buildings_with_hashes.json'.")
        

# This ensures that the script is run only when executed directly, not when imported
if __name__ == "__main__":
    main()
