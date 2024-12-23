import logging

from models.activity import Activity, GeoJSONLineString
from repositories.activity_repo import ActivityRepository

logger = logging.getLogger(__name__)


def handle_updated_activity(activity_id: int, updated_fields: dict):
    pass
