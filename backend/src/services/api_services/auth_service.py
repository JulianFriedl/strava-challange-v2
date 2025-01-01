import logging
import requests
import os

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
        "approval_prompt": "force",
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
    except requests.exceptions.RequestException as e:
        logger.error(f"Token exchange failed: {e}")
        raise AuthorizationError("Failed to exchange authorization code for token.")
    except ValueError:
        logger.error("Invalid token response format.")
        raise AuthorizationError("Invalid token response format.")

    access_token = token_data["access_token"]
    athlete_data = token_data["athlete"]

    # Test access to the activities endpoint
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        activities_response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities", headers=headers, timeout=10
        )
        if activities_response.status_code != 200:
            logger.error(f"Activities endpoint access failed: {activities_response.text}")
            raise ScopeError("User did not grant the required 'activity:read' scope.")
        logger.info("User granted activity access.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Activities endpoint test failed: {e}")
        raise ScopeError("Failed to verify activity access.")


    logger.debug(f"Activity response headers: {activities_response.headers}")
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
