from flask import Blueprint, jsonify, request
from services.auth_service import handle_strava_auth, process_strava_callback
from api.exceptions import AuthorizationError, ScopeError, AthleteExistsError
import logging

logger = logging.getLogger(__name__)
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/strava_auth_url', methods=['GET'])
def strava_auth_url():
    """
    Generate and return the Strava OAuth URL.
    """
    try:
        auth_url = handle_strava_auth()
        return jsonify({"auth_url": auth_url}), 200
    except Exception as e:
        logger.error(f"Error generating Strava auth URL: {e}")
        return jsonify({"error": "Failed to generate auth URL"}), 500


@auth_blueprint.route("/strava_auth_callback", methods=["GET"])
def strava_auth_callback():
    """
    Handle the Strava authorization callback.
    """
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    try:
        athlete_data = process_strava_callback(code)
        return jsonify(athlete_data), 200
    except AuthorizationError as e:
        logger.error(f"Authorization error: {str(e)}")
        return jsonify({"error": str(e)}), e.status_code
    except ScopeError as e:
        logger.error(f"Scope error: {str(e)}")
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
