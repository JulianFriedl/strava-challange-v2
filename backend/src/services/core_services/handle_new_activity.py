import requests
import logging
from datetime import datetime

from services.core_services.rate_limit_tracker import RateLimitTracker
from models.activity import Activity
from repositories.activity_repo import ActivityRepository
from repositories.athlete_repo import AthleteRepository
from services.core_services.auth_refresh import refresh_token

logger = logging.getLogger(__name__)

STRAVA_API_URL = "https://www.strava.com/api/v3/activities"


def handle_new_activity(activity_id: int, athlete_id: int):
    """
    Handle the creation of a new activity event by fetching data from Strava API,
    refreshing tokens if necessary, and storing the activity in the database.
    """
    rate_limit_tracker = RateLimitTracker()
    activity_repo = ActivityRepository()
    athlete_repo = AthleteRepository()

    athlete = athlete_repo.find_by_athlete_id(athlete_id)
    try:
        athlete = refresh_token(athlete)
    except Exception as e:
        raise Exception("Token refresh failed. Cannot proceed with API request.") from e

    access_token = athlete.tokens["access_token"]

    activity_url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        rate_limit_tracker.wait_if_needed()
        response = requests.get(activity_url, headers=headers)
        rate_limit_tracker.update_limits(response.headers)

        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch activity {activity_id} for athlete {athlete_id}. "
                f"Status code: {response.status_code}, Response: {response.text}"
            )

        activity_data = response.json()
        logger.info(f"Fetched activity data for activity {activity_id}.")
    except Exception as e:
        raise Exception(f"Error fetching activity {activity_id}") from e

    try:
        activity = Activity.create_activity_from_data(activity_data, athlete_id)
        activity_repo.create_activity(activity)

        logger.debug(f"Inserted activity {activity.activity_id} for athlete {athlete_id}.")
    except Exception as e:
        raise Exception(f"Failed to process activity {activity_data.get('id')}") from e
