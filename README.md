# Landmark-Based Addressing for Enhanced Urban Navigation


## landmark-based-urban-navigation

---

## Overview

This repository provides a Python-based solution for optimizing routes and prioritizing landmarks for urban navigation, specifically focusing on Kathmandu. The system uses OpenStreetMap (OSM) data and custom algorithms to:

1. **Optimize routes** between landmarks and buildings based on shortest travel times.
2. **Prioritize landmarks** near buildings, using a clustering method (DBSCAN) to categorize and rank landmarks by size and type.

This solution integrates several key functionalities, including:
- Landmark selection and clustering based on proximity.
- Route optimization based on travel time.
- Generation of hash-based route directions for navigation.

The output consists of a CSV and JSON file with each building’s corresponding priority landmark, optimized route, and travel hash.

## Contents

- `route_optimizer.py`: Contains the logic for route optimization, including finding nearest nodes, computing shortest paths, and generating route hashes.
- `select_landmarks.py`: Contains the logic for selecting and ranking landmarks based on their proximity to buildings using clustering techniques.
- `utils.py`: Utility functions for data preprocessing, distance calculation, and bearing calculation.
- `main.py`: The main script that integrates all the functionalities, processes data, and saves the results to CSV and JSON files.
- `requirements.txt`: The list of required dependencies for the project.

## Key Components

### 1. **Route Optimization** (Implemented in `route_optimizer.py`):
The route optimization process involves:
- **Graph Construction**: A walkable graph of Kathmandu is constructed using the `osmnx` library to fetch data from OpenStreetMap.
- **Shortest Path Calculation**: Using NetworkX, the shortest path between a landmark and a building is calculated based on travel time, considering edge speeds and travel times derived from OSM data.
- **Route Hash Generation**: A route hash is generated based on the directions (cardinal bearings) and distances along the path.

### 2. **Landmark Prioritization** (Implemented in `select_landmarks.py`):
The landmark prioritization process involves:
- **Clustering**: DBSCAN is used to cluster landmarks based on their geographical proximity. H3 hexagons are employed to categorize landmarks into geographical areas.
- **Ranking**: Clusters are ranked by size, and landmarks are prioritized according to a predefined order (e.g., temple, tourist spot, bus stop).
- **Noise Handling**: Landmarks that do not fit well into any cluster (outliers) are handled separately and included in the final prioritization.

### 3. **Utility Functions** (Implemented in `utils.py`):
- **Haversine Distance**: Calculates the geographical distance between two points (latitude, longitude) using the Haversine formula.
- **Initial Compass Bearing**: Calculates the initial compass bearing from one geographic point to another.
- **Data Loading and Preprocessing**: Functions to load CSV files containing building and landmark data, preprocess them, and handle missing or incorrect entries.

### 4. **Main Script** (Implemented in `main.py`):
- **Data Crawling and Preprocessing**: Calls functions to crawl building and landmark data, preprocess the data, and clean up any inconsistencies.
- **Route and Landmark Integration**: Iterates through buildings and landmarks, prioritizes the closest landmark for each building, and calculates the optimized route.
- **Result Saving**: Saves the final results (including route hashes) into a CSV and JSON format for further analysis or application development.

### 5. **Requirements File** (`requirements.txt`):
This file lists the dependencies needed to run the project. These libraries and tools include data manipulation, geospatial analysis, machine learning, and visualization packages.

## Setup Instructions

To set up the project environment and run the system, follow these steps:

### 1. **Setting Up Python Environment**
Make sure you have Python 3.8+ installed. It is recommended to create a virtual environment for this project to avoid conflicts with other Python projects.

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv route_optimizer_env
   ```

2. Activate the virtual environment:
   - For Windows:
     ```bash
     .\route_optimizer_env\Scripts\activate
     ```
   - For macOS/Linux:
     ```bash
     source route_optimizer_env/bin/activate
     ```

### 2. **Install Dependencies**
With the virtual environment activated, install the necessary dependencies listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 3. **Running the Main Script**
After the dependencies are installed, you can run the main script, `main.py`, to execute the route optimization and landmark prioritization:

```bash
python main.py
```

The script will:
- Crawl the building and landmark data.
- Process and clean the data.
- Prioritize landmarks for each building.
- Optimize routes and generate route hashes.
- Save the results in both CSV and JSON formats.

### 4. **Output Files**
After running the script, the following output files will be created:
- `ktm_buildings_with_landmarks.csv`: Contains the building data along with the associated prioritized landmark.
- `ktm_buildings_with_hashes.csv`: Contains the building data with route hashes, representing the optimized path from a landmark to the building.
- `ktm_buildings_with_hashes.json`: A JSON representation of the same data for use in web applications or APIs.

### 5. **Data Files**
Ensure that you have the necessary input data files, such as `cleaned_landmarks.csv` and `kathmandu_buildings.csv`, placed in the `./data/` directory.

## File Descriptions

- `route_optimizer.py`: Contains the class `RouteOptimizer` for performing route optimization using shortest path algorithms and generating route hashes.
- `select_landmarks.py`: Contains the class `LandmarkPriority` for clustering landmarks and selecting the most relevant ones based on proximity and priority.
- `utils.py`: Utility functions for data handling, distance calculations, and preprocessing.
- `main.py`: Main script that orchestrates data crawling, processing, and integration of route optimization and landmark prioritization.
- `requirements.txt`: Dependency file listing all required libraries.

## Dependencies

Below is a list of Python libraries required for this project:

- `osmnx`: For downloading and processing OpenStreetMap (OSM) data to build a walkable graph.
- `networkx`: For performing graph-based operations like finding the shortest path.
- `numpy`: For numerical operations and data manipulation.
- `pandas`: For handling CSV files and data frames.
- `scikit-learn`: For DBSCAN clustering of landmarks.
- `h3`: For working with H3 hexagons and spatial indexing.
- `geopandas`: For geospatial data manipulation.
- `shapely`: For geometric operations.
- `tqdm`: For displaying progress bars during execution.
- `joblib`: For parallel processing (if applicable).

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.

## References

- OpenStreetMap: https://www.openstreetmap.org
- OSMnx: https://osmnx.readthedocs.io/en/stable/
- DBSCAN Clustering: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html

## Conclusion

This system provides a robust framework for urban navigation by integrating geospatial analysis with route optimization and landmark prioritization. It can be extended for use in other cities or to include additional features like multi-modal transport analysis.