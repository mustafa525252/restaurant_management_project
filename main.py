import requests

BASE_URL = "http://127.0.0.1:8000"

def fetch_menu_categories():
    # Fetch all menu categories from the API endpoint.
    response = requests.get(f"{BASE_URL}/menu-categories/")
    if response.status_code == 200:
        print("Menu Categories:")
        for category in response.json():
            print(f"- {category['name']}")
    else:
        print(f"Failed to fetch categories. Status code:{response.status_code}")
if __name__ == "__main__":
    fetch_menu_categories()