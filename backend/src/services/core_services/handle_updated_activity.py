import logging
from models.activity import Activity
from repositories.activity_repo import ActivityRepository

logger = logging.getLogger(__name__)

def handle_updated_activity(activity_id: int, updated_fields: dict):
    """
    Handle the update of an activity by applying the changes specified in updated_fields
    to the existing activity in the database.
    """
    activity_repo = ActivityRepository()

    try:
        updated_activity = activity_repo.update_activity(activity_id, updated_fields)
        logger.info(f"Successfully updated activity {activity_id} with fields: {updated_fields}")
        return updated_activity

    except Exception as e:
        raise Exception(f"Error updating activity {activity_id}") from e
