from flask import Blueprint, jsonify, request, redirect, session
import logging
import os

from services.api_services.leaderboard_service import get_all_athlete_activities
from api.exceptions import AuthorizationError, ScopeError


logger = logging.getLogger(__name__)
leaderboard_blueprint = Blueprint('leaderboard', __name__)

@leaderboard_blueprint.route('/', methods=['GET'])
def leaderboard():
    """
    Generate and return the total leaderboard as well as all sub-leaderboards.
    """
    logger.info("Leaderboard request received.")
    try:
        athlete_activities = get_all_athlete_activities()
        return jsonify({"leaderboard": athlete_activities}), 200
    except Exception as e:
        logger.error(f"Error generating leaderboard: {e}")
        return jsonify({"error": "Failed to generate leaderboard"}), 500