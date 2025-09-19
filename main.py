import requests

BASE_URL = "http://127.0.0.1:8000"

def fetch_menu_categories():
    try:
        response = requests.get(f"{BASE_URL}/menu-categories/")
        response.raise_for_status()  # Raises HTTPError for bad responses
        categories = response.json()
        print("Menu Categories:")
        for category in categories:
            print(f"- {category['name']}")  # ✅ Properly indented inside the loop
    except requests.exceptions.HTTPError as http_err:  # ✅ Correct casing: HTTPError
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
    except requests.exceptions.Timeout:
        print("Error: Request timed out.")  # ✅ Corrected typo
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")

if __name__ == "__main__":
    fetch_menu_categories()
