from datetime import datetime, timedelta
import requests
import logging
from repositories.athlete_repo import AthleteRepository
from models.athlete import Athlete
import os

logger = logging.getLogger(__name__)

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRETE = os.getenv('STRAVA_CLIENT_SECRETE')


def refresh_token(athlete: Athlete):
    """
    Refresh the access token for an athlete if expired.
    Raises:
        Exception: If the refresh token request fails or the update operation fails.
    Return:
        Athlete
    """
    athlete_id = athlete.athlete_id
    expires_at = athlete.tokens.get("expires_at", 0)
    refresh_token = athlete.tokens.get("refresh_token", "")

    current_time = datetime.utcnow()
    if current_time < datetime.utcfromtimestamp(expires_at) - timedelta(minutes=30):
        logger.info(f"Token for athlete {athlete_id} is still valid.")
        return athlete

    logger.info(f"Refreshing token for athlete {athlete_id}...")

    data = {
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRETE,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post('https://www.strava.com/oauth/token', data=data)
    if response.status_code == 200:
        data = response.json()
        new_tokens = {
            "access_token": data['access_token'],
            "refresh_token": data['refresh_token'],
            "expires_at": data['expires_at'],
        }

        athlete_repo = AthleteRepository()
        try:
            new_athlete = athlete_repo.update_athlete(athlete_id, {"tokens": new_tokens})
            logger.info(f"Token refreshed successfully for athlete {athlete_id}.")
            return new_athlete
        except Exception as e:
            raise Exception(f"Failed to update athlete {athlete_id}: {e}")
    else:
        raise Exception(f"Failed to refresh token for athlete {athlete_id}. Status code: {response.status_code}")
