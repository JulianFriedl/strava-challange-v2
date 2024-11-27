import logging
import requests
import os

from models.athlete import Athlete
from repositories.athlete_repo import AthleteRepository
from api.exceptions import AuthorizationError, ScopeError, AthleteExistsError

logger = logging.getLogger(__name__)

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRETE")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI")

athlete_repo = AthleteRepository()

def handle_strava_auth():
    """
    Generate Strava OAuth URL.
    """
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": STRAVA_REDIRECT_URI,
        "approval_prompt": "force",
        "scope": "read,activity:read",
    }
    strava_auth_url = f"https://www.strava.com/oauth/authorize?{requests.compat.urlencode(params)}"
    logger.info(f"Generated Strava auth URL: {strava_auth_url}")
    return strava_auth_url

def process_strava_callback(code):
    """
    Exchange code for access token, retrieve athlete data, and save or retrieve the athlete.
    """
    # Exchange authorization code for access token
    token_response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        },
    )

    if token_response.status_code != 200:
        logger.error(f"Token exchange failed: {token_response.text}")
        raise AuthorizationError("Failed to exchange authorization code for token.")

    token_data = token_response.json()

    # Validate the required scope is granted
    access_token = token_data.get("access_token")
    # Verify the required permissions by testing access to activities
    headers = {'Authorization': f'Bearer {access_token}'}
    activities_response = requests.get('https://www.strava.com/api/v3/athlete/activities', headers=headers)

    if activities_response.status_code == 200:
        print("User granted activity access.")
    else:
        raise ScopeError(f"User did not grant the required 'activity:read' scope.")


    athlete_data = token_data["athlete"]

    # Create the Athlete model instance
    athlete = Athlete(
        athlete_id=athlete_data["id"],
        username=athlete_data.get("username", ""),
        first_name=athlete_data.get("firstname", ""),
        last_name=athlete_data.get("lastname", ""),
        created_at=athlete_data.get("created_at", ""),
        profile={
            "medium": athlete_data.get("profile_medium", ""),
            "full": athlete_data.get("profile", ""),
        },
        tokens={
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "expires_at": token_data["expires_at"],
        },
    )

    # Check if the athlete already exists in the database
    existing_athlete = athlete_repo.find_by_athlete_id(athlete.athlete_id)

    if existing_athlete:
        logger.info(f"Athlete {athlete.athlete_id} exists. Logging in.")
        return existing_athlete.to_dict()

    # If not, save the new athlete
    athlete_repo.create_athlete(athlete)
    logger.info(f"New athlete {athlete.athlete_id} registered.")
    return athlete.to_dict()
