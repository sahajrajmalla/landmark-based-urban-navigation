# Import the crawl_buildings_data function from the appropriate module
from src.crawl.buildings import crawl_buildings_data

def main():
    # Call the function to crawl building data and save to CSV
    crawl_buildings_data()

# This ensures that the script is run only when executed directly, not when imported
if __name__ == "__main__":
    main()
