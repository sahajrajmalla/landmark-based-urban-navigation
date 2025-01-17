import osmnx as ox
import networkx as nx
from src.utils import haversine_distance, calculate_initial_compass_bearing


# Function to calculate heuristic for A* algorithm
def heuristic(u, v, G):
    """Custom heuristic function for A* algorithm that calculates great-circle distance."""
    try:
        u_lat, u_lon = G.nodes[u]['y'], G.nodes[u]['x']
        v_lat, v_lon = G.nodes[v]['y'], G.nodes[v]['x']
        return ox.distance.great_circle_vec(u_lat, u_lon, v_lat, v_lon)
    except KeyError as e:
        raise ValueError(f"Missing node attributes for {u} or {v}: {e}")

class RouteOptimizer:
    def __init__(self, G, landmark_location, destination_location):
        """
        Initialize the route optimizer with the graph and locations.
        """
        self.G = G
        self.landmark_location = self.find_nearest_node(landmark_location)
        self.destination_location = self.find_nearest_node(destination_location)
        
    def find_nearest_node(self, point):
        """
        Find the nearest node in the graph to the given point (latitude, longitude).
        """
        lat, lon = point
        return ox.distance.nearest_nodes(self.G, X=lon, Y=lat)

    def get_shortest_path(self):
        """
        Get the shortest path based on travel time using A*.
        """
        # Add speed and travel time to edges
        self.G = ox.add_edge_speeds(self.G)  # Adds edge speeds based on OSM data
        self.G = ox.add_edge_travel_times(self.G)  # Calculate travel times

        # Compute shortest path based on travel time using A*
        orig = self.landmark_location
        dest = self.destination_location
        self.path = nx.astar_path(self.G, orig, dest, heuristic=lambda u, v: heuristic(u, v, self.G), weight='travel_time')
        return self.path

    def generate_hash(self, landmark_name, path):
        """
        Generate a hash string based on directions along the path.
        The directions are based on compass bearings and segment lengths.
        """
        directions = []
        prev_dir = None
        sum_length = 0

        for i in range(len(path) - 1):
            # Get coordinates of the current and next nodes
            pointA = (self.G.nodes[path[i]]['y'], self.G.nodes[path[i]]['x'])
            pointB = (self.G.nodes[path[i + 1]]['y'], self.G.nodes[path[i + 1]]['x'])
            
            # Calculate compass bearing
            bearing = calculate_initial_compass_bearing(pointA, pointB)

            # Determine cardinal direction based on bearing
            if (bearing >= 0 and bearing < 45) or (bearing >= 315 and bearing < 360):
                dir = "N"
            elif bearing >= 45 and bearing < 135:
                dir = "E"
            elif bearing >= 135 and bearing < 225:
                dir = "S"
            else:
                dir = "W"

            # Calculate the distance between points
            length = haversine_distance(pointA, pointB, round_to=2) if i == len(path) - 2 else haversine_distance(pointA, pointB)

            # Aggregate distances for the same direction
            if prev_dir == dir:
                sum_length += length
            else:
                if prev_dir is not None:
                    directions.append(f"{prev_dir}_{sum_length:.2f}")
                sum_length = length
                prev_dir = dir

        # Add the final direction and distance
        if prev_dir is not None:
            directions.append(f"{prev_dir}_{sum_length:.2f}")

        # Generate the hash string
        hash_string = f"{landmark_name}|{'|'.join(directions)}"
        return hash_string
