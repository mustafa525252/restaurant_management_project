import requests

BASE_URL = "http://127.0.0.1:8000"

def fetch_menu_categories():
    try:
        response = requests.get(f"{BASE_URL}/menu-categories/")
        response.raise_for_status()
        categories = response.json()
        print("Menu Categories:")
        for category in categories:
            print(f"- {category['name']}")
    except requests.exceptions.HttpError as http_err:
        print(f"HTTP error occured:{http_err}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
    except request.exceptions.Timeout:
        print("Error: Request time out.")
    except request.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
        
if __name__ == "__main__":
    fetch_menu_categories()