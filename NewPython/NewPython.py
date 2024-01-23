import sys
import pandas as pd
import requests
import matplotlib.pyplot as plt
import time
import os

# Function to geocode address using TomTom Geocoding API
def geocode_address_tomtom(address, api_key):
    base_url = "https://api.tomtom.com/search/2/geocode/{}.json".format(address)
    params = {
        "key": api_key,
        "limit": 1  # Assuming we only want the top result
    }
    
    print(f"Geocoding address: {address}")  # Print the address being queried

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        result = response.json()
        # Parsing the response according to TomTom's API structure for geocoding
        if result.get('results'):
            lat = result['results'][0]['position']['lat']
            lon = result['results'][0]['position']['lon']
            return lat, lon
        else:
            print(f"No results for address: {address}")
            return None
    else:
        print(f"Error for address: {address} - {response.text}")
        return None


def convert_to_cartesian(lat, lon):
    # Dummy function for converting to Cartesian coordinates
    # Replace with actual conversion logic
    return float(lat), float(lon)

def plot_data(data):
    # Function to create a scatter plot
    x_coords, y_coords = zip(*data['Cartesian'])
    categories = data['Category']
    plt.figure(figsize=(10, 6))
    for category in set(categories):
        idx = [i for i, x in enumerate(categories) if x == category]
        plt.scatter([x_coords[i] for i in idx], [y_coords[i] for i in idx], label=f'Category {category}')
    plt.title('Scatter Plot of Cartesian Coordinates with Category Color Coding')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.grid(True)
    plt.savefig('C:\\Users\\usr\\Desktop\\NewPython\\scatter_plot.jpg')  # Saves the plot as a PNG file
    plt.show()
    print(os.getcwd())

# Read data from files

excel_file_path = 'C:\\Users\\usr\\Desktop\\NewPython\\data_addressess.xlsx'
addresses_data = pd.read_excel(excel_file_path, sheet_name='data_addresses')
print(addresses_data.columns)
data_with_category = pd.read_excel(excel_file_path , sheet_name="data_addresses")

if 'Category' not in addresses_data.columns:
    raise ValueError("The 'Category' column is missing in the Excel sheet.")


# Geocode addresses with request limit
api_key ='6aN0y7NqoPw90dwhMemNB11dhKrGwSKt'
request_limit = 50
request_count = 0

limit_message_printed = False

def safe_geocode(address):
    
    global request_count , limit_message_printed
    if request_count < request_limit:
        time.sleep(2)  # TomTom also has a rate limit, adjust as needed
        coords = geocode_address_tomtom(address, api_key)  # Use the new TomTom function
        request_count += 1
        if coords:  # Check if coordinates are not None
            print(f"Coordinates for '{address}': {coords}")
        else:
            print(f"Coordinates for '{address}' not found.")
        return coords
    else:
        if not limit_message_printed:
            print("Request limit reached.")
            limit_message_printed = True
        return None


addresses_data['Coordinates'] = addresses_data['Address'].apply(safe_geocode)

# Convert to Cartesian coordinates
addresses_data['Cartesian'] = addresses_data['Coordinates'].apply(
    lambda coords: convert_to_cartesian(*coords) if coords else (None, None)
)

# Merge with category data
combined_data = addresses_data.merge(data_with_category, on='Address', how='inner')
print(combined_data.columns)

# Plot data
plot_data(addresses_data) 