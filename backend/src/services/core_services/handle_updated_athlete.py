import logging

from repositories.athlete_repo import AthleteRepository

logger = logging.getLogger(__name__)

def handle_updated_athlete(athlete_id: int, updated_fields: dict):
    """
    Handle updates to an athlete's profile, preferences, or account status.
    """
    athlete_repo = AthleteRepository()

    try:
        # valid_fields = {"name", "profile_picture", "location", "privacy_settings", "status"}
        # filtered_fields = {key: value for key, value in updated_fields.items() if key in valid_fields}

        # if not filtered_fields:
        #     logger.warning(f"No valid fields to update for athlete {athlete_id}. Skipping update.")
        #     return None

        athlete_repo.update_athlete(athlete_id, updated_fields)
        logger.info(f"Successfully updated athlete {athlete_id} with fields: {updated_fields}")

        #TODO: Handle these cases
        if "privacy_settings" in updated_fields:
            logger.info(f"Privacy settings updated for athlete {athlete_id}.")

        if "status" in updated_fields and updated_fields["status"] == "deactivated":
            logger.info(f"Athlete {athlete_id} deactivated.")

    except Exception as e:
        raise Exception(f"Error updating athlete {athlete_id}") from e
