import logging
import requests
import os
import time

from models.athlete import Athlete
from repositories.athlete_repo import AthleteRepository
from api.exceptions import AuthorizationError, ScopeError
from services.core_services.task_service import TaskService, Task, TaskType

logger = logging.getLogger(__name__)

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRETE")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI")



def handle_strava_auth():
    """
    Generate Strava OAuth URL.
    """
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": STRAVA_REDIRECT_URI,
        "approval_prompt": "auto",
        "scope": "read,activity:read",
    }
    strava_auth_url = f"https://www.strava.com/oauth/authorize?{requests.compat.urlencode(params)}"
    logger.debug(f"Generated Strava auth URL: {strava_auth_url}")
    return strava_auth_url


def process_strava_callback(code):
    """
    Exchange code for access token, retrieve athlete data, and save or retrieve the athlete.
    """
    logger.debug(f"Processing Strava callback for code: {code}")

    athlete_repo = AthleteRepository()
    # Exchange authorization code for access token
    for attempt in range(3):
        try:
            token_response = requests.post(
                "https://www.strava.com/oauth/token",
                data={
                    "client_id": STRAVA_CLIENT_ID,
                    "client_secret": STRAVA_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )
            token_response.raise_for_status()
            token_data = token_response.json()
            break  # Exit loop on success
        except requests.exceptions.RequestException as e:
            logger.error(f"Token exchange failed on attempt {attempt + 1}: {e}")
            logger.error(f"Env variables: CLIENT_ID={STRAVA_CLIENT_ID}, CLIENT_SECRET={STRAVA_CLIENT_SECRET}, REDIRECT_URI={STRAVA_REDIRECT_URI}")
            logger.error(f"Token exchange request: {token_response.request.body}")
            logger.error(f"Token exchange response: {token_response.status_code}, {token_response.text}")
            if attempt < 2:
                time.sleep(1)  # Backoff
            else:
                raise AuthorizationError("Failed to exchange authorization code for token.")

    logger.info(f"Token exchange suceeded after {attempt + 1} tries.")
    access_token = token_data["access_token"]
    athlete_data = token_data["athlete"]

    # Construct Athlete instance
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
            "access_token": access_token,
            "refresh_token": token_data["refresh_token"],
            "expires_at": token_data["expires_at"],
        },
    )

    # Store or update athlete in database
    existing_athlete = athlete_repo.find_by_athlete_id(athlete.athlete_id)
    if existing_athlete:
        logger.info(f"Athlete {athlete.athlete_id} exists. Logging in.")
        athlete_repo.update_athlete(athlete.athlete_id, athlete.to_mongo())
    else:
        athlete_repo.create_athlete(athlete)
        logger.info(f"New athlete {athlete.athlete_id} registered.")

        # Submit task to fetch activities
        task = Task(
            athlete_id=athlete.athlete_id,
            endpoint="https://api.strava.com/api/v3/activities",
            params={},
            task_type=TaskType.FETCH_ACTIVITIES,
        )
        api_request_service = TaskService()
        api_request_service.submit_task(task)
        logger.info(f"Task submitted for athlete {athlete.athlete_id} to fetch activities.")

    return athlete.to_dict()
