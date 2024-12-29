import requests
import logging
from datetime import datetime
from polyline import decode as decode_polyline

from services.core_services.rate_limit_tracker import RateLimitTracker
from models.activity import Activity
from repositories.activity_repo import ActivityRepository
from repositories.athlete_repo import AthleteRepository
from services.core_services.auth_refresh import refresh_token

logger = logging.getLogger(__name__)


def fetch_athlete_activities(athlete_id):
    """
    Fetch all activities for an athlete, respecting Strava API rate limits.
    """
    rate_limit_tracker = RateLimitTracker()
    activity_repo = ActivityRepository()
    athlete_repo = AthleteRepository()

    athlete = athlete_repo.find_by_athlete_id(athlete_id)
    try:
        athlete = refresh_token(athlete)
    except Exception as e:
        logger.error(f"{e}")
        raise Exception("Token refresh failed. Cannot proceed with API request.")

    access_token = athlete.tokens["access_token"]

    activities = []
    page = 1
    PER_PAGE = 200
    end_of_results = False

    while not end_of_results:
        rate_limit_tracker.wait_if_needed()

        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"page": page, "per_page": PER_PAGE}
        response = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers, params=params)

        if response.status_code != 200:
            logger.error("Failed to fetch activities for athlete %d: %s", athlete_id, response.text)
            break

        rate_limit_tracker.update_limits(response.headers)

        data = response.json()
        if not data:
            end_of_results = True
        else:
            activities.extend(data)
            page += 1

        if len(data) < PER_PAGE:
            end_of_results = True

    logger.info("Fetched %d activities for athlete %d.", len(activities), athlete_id)

    for activity_data in activities:
        try:
            activity = Activity.create_activity_from_data(activity_data, athlete_id)

            activity_repo.create_activity(activity)
            logger.debug(f"Inserted activity {activity.activity_id} for athlete {athlete_id}.")
        except Exception as e:
            logger.debug(f"Failed to process activity {activity_data.get('id')}: {e}")

    logger.info("Inserted activities for athlete %d.", athlete_id)
