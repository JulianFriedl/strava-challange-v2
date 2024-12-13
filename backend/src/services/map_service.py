import logging
from repositories.athlete_repo import AthleteRepository
from repositories.activity_repo import ActivityRepository

logger = logging.getLogger(__name__)

athlete_repo = AthleteRepository()
activity_repo = ActivityRepository()

def get_activities_with_polylines(years, athlete_ids):
    """
    Fetch all activities that have a polyline and match the provided athlete IDs and years.
    """
    logger.info(f"Fetching activities for years {years} and athlete_ids {athlete_ids}.")
    activities = activity_repo.list_activities_with_polylines(athlete_ids, years)
    return activities


def get_all_athletes():
    """
    Fetch all athletes from the database.
    """
    logger.info("Fetching all athletes.")
    athletes = athlete_repo.get_all_athletes()
    return [athlete.to_dict() for athlete in athletes]


def get_all_years():
    """
    Fetch all unique years that have associated activities.
    """
    logger.info("Fetching all years with activities.")
    years = activity_repo.get_unique_years()
    return years
