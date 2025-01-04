import logging
from repositories.athlete_repo import AthleteRepository
from repositories.activity_repo import ActivityRepository

logger = logging.getLogger(__name__)


def get_activities_with_polylines(years, athlete_ids):
    """
    Fetch all activities that have a polyline and match the provided athlete IDs and years.
    """
    logger.debug(f"Fetching activities for years {years} and athlete_ids {athlete_ids}.")
    activity_repo = ActivityRepository()
    activities = activity_repo.list_activities_with_polylines(athlete_ids, years)
    return activities


def get_all_athletes():
    """
    Fetch all athletes from the database.
    """
    logger.debug("Fetching all athletes.")
    athlete_repo = AthleteRepository()
    athletes = athlete_repo.get_all_athletes()
    return [athlete.to_dict() for athlete in athletes]


def get_all_years():
    """
    Fetch all unique years that have associated activities.
    """
    logger.debug("Fetching all years with activities.")
    activity_repo = ActivityRepository()
    years = activity_repo.get_unique_years()
    return years
