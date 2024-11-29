import requests
import json

# Bounding box coordinates
bbox = "27.6010367,85.4602795,27.6943733,85.5640106"

# Dictionary of categories and their associated amenities
amenities = {
    "Education": ["school", "university", "college", "library"],
    # "Healthcare": ["hospital", "clinic", "doctors", "pharmacy"],
    # "Transportation": ["bus_stop", "train_station", "airport", "parking"],
    # "Food_and_Drink": ["restaurant", "cafe", "fast_food", "bar"],
    # "Shopping": ["supermarket", "mall", "convenience", "clothes"],
    # "Leisure_and_Entertainment": ["park", "playground", "cinema", "sports_centre"],
    # "Accommodation": ["hotel", "motel", "guest_house"],
    # "Financial_and_Professional": ["bank", "atm", "lawyer", "business"],
    # "Public_Services": ["post_office", "police", "fire_station", "government"],
    # "Worship": ["church", "mosque", "synagogue", "temple"],
    # "Health_and_Beauty": ["gym", "spa", "beauty", "tattoo"],
    # "Community": ["community_centre", "social_facility", "shelter"]
}

base_url = "http://overpass-api.de/api/interpreter"

for category, amenity_list in amenities.items():
    for amenity in amenity_list:
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

        response = requests.get(base_url, params={"data": query})
        data = response.json()

        # Saving the data to a file
        with open(f"{category}_{amenity}.json", "w") as outfile:
            json.dump(data, outfile)

        print(f"Saved data for {category}: {amenity} in {category}_{amenity}.json")
