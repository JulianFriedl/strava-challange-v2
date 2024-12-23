import requests
import logging

from services.core_services.rate_limit_tracker import RateLimitTracker
from models.activity import Activity, GeoJSONLineString
from repositories.activity_repo import ActivityRepository
from services.core_services.auth_refresh import refresh_token

logger = logging.getLogger(__name__)


def handle_new_activity(activity_id: int):
    pass
