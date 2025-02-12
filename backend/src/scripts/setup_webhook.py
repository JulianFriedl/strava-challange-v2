import requests
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('../../../.env')
load_dotenv(dotenv_path=dotenv_path)

BASE_URL = "https://www.strava.com/api/v3"
CALLBACK_URL = "https://scsport.eu/api/webhook"

CLIENT_ID=
CLIENT_SECRETE=

VERIFY_TOKEN = 'fhgndpahFHDdjdbG837zFH9g98ghH'

def setup_webhook():
    """Set up the Strava webhook subscription."""
    url = f"{BASE_URL}/push_subscriptions"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRETE,
        "callback_url": CALLBACK_URL,
        "verify_token": VERIFY_TOKEN,
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Webhook subscription created successfully!")
        print(response.json())
    except requests.exceptions.HTTPError as e:
        print("HTTPError:", e.response.status_code, e.response.text)
    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRETE:
        print("Error: STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set in the .env file.")
    else:
        setup_webhook()
