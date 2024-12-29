import logging

from models.activity import Activity, GeoJSONLineString
from repositories.activity_repo import ActivityRepository

logger = logging.getLogger(__name__)


def handle_deleted_activity(activity_id: int):
    """
    Handle the deletion of an activity by removing it from the database
    and performing any necessary cleanup.
    """
    activity_repo = ActivityRepository()

    try:
        activity = activity_repo.find_activity_by_id(activity_id)
        if not activity:
            logger.warning(f"Activity with ID {activity_id} not found. Nothing to delete.")
            return

        activity_repo.delete_activity(activity_id)
        logger.info(f"Successfully deleted activity {activity_id}.")

        # Handle cascading cleanup if we need it in the future
        # Example: Update statistics, remove references in other collections, etc.
        logger.debug(f"Performing post-deletion cleanup for activity {activity_id}.")
        perform_post_deletion_cleanup(activity)

    except Exception as e:
        raise Exception(f"Error deleting activity {activity_id}") from e


def perform_post_deletion_cleanup(activity: Activity):
    """
    Perform any necessary cleanup after deleting an activity.
    """
    logger.info(f"Post-deletion cleanup for activity {activity.activity_id} completed.")
