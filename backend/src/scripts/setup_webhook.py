import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.strava.com/api/v3"
CALLBACK_URL = "http://stravascape.site/api/webhook"

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")

VERIFY_TOKEN = 'fhgndpahFHDdjdbG837zFH9g98ghH'

def setup_webhook():
    """Set up the Strava webhook subscription."""
    url = f"{BASE_URL}/push_subscriptions"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
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
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set in the .env file.")
    else:
        setup_webhook()
