import logging

from repositories.athlete_repo import AthleteRepository
from repositories.activity_repo import ActivityRepository

logger = logging.getLogger(__name__)

def handle_updated_athlete(athlete_id: int, updated_fields: dict):
    """
    Handle updates to an athlete, specifically handling the case where access is revoked.
    """
    athlete_repo = AthleteRepository()
    activity_repo = ActivityRepository()

    try:
        if updated_fields.get("authorized") == "false":
            athlete_deleted = athlete_repo.delete_athlete(athlete_id)
            if not athlete_deleted:
                logger.warning(f"Athlete {athlete_id} not found. No deletion performed.")

            activity_repo.delete_activities_by_athlete_id(athlete_id)

            logger.info(f"Successfully handled deauthorization for athlete {athlete_id}.")
        else:
            logger.warning(f"Unexpected update fields for athlete {athlete_id}: {updated_fields}")

    except Exception as e:
        raise Exception(f"Failed to handle updated athlete {athlete_id}. {e}") from e
