import requests
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('../../../.env')
load_dotenv(dotenv_path=dotenv_path)

BASE_URL = "https://www.strava.com/api/v3"
CALLBACK_URL = "http://stravascape.site/api/webhook"

CLIENT_ID=
CLIENT_SECRETE=

VERIFY_TOKEN = 'fhgndpahFHDdjdbG837zFH9g98ghH'

def delete_existing_webhooks():
    url = f"{BASE_URL}/push_subscriptions"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRETE,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        subscriptions = response.json()
        for subscription in subscriptions:
            del_url = f"{BASE_URL}/push_subscriptions/{subscription['id']}"
            del_response = requests.delete(del_url, params=params)
            del_response.raise_for_status()
            print(f"Deleted subscription ID: {subscription['id']}")
    except requests.exceptions.HTTPError as e:
        print("HTTPError:", e.response.status_code, e.response.text)
    except Exception as e:
        print("An error occurred:", str(e))


if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRETE:
        print("Error: STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set in the .env file.")
    else:
        delete_existing_webhooks()
