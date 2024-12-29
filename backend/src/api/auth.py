from flask import Blueprint, jsonify, request, redirect, session
import logging
import os

from services.api_services.auth_service import handle_strava_auth, process_strava_callback
from api.exceptions import AuthorizationError, ScopeError


logger = logging.getLogger(__name__)
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/strava_auth_url', methods=['GET'])
def strava_auth_url():
    """
    Generate and return the Strava OAuth URL.
    """
    logger.info("Strava_auth_url request received.")
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
    logger.info("Strava_auth_callback called.")
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    try:
        athlete_data = process_strava_callback(code)
        athlete_id = athlete_data.get("athlete_id")
        session["user_id"] = athlete_id
        return redirect(os.getenv("FRONTEND_URL", "http://localhost:5000/"))
    except AuthorizationError as e:
        logger.error(f"Authorization error: {str(e)}")
        return jsonify({"error": str(e)}), e.status_code
    except ScopeError as e:
        logger.error(f"Scope error: {str(e)}")
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_blueprint.route('/status', methods=['GET'])
def auth_status():
    user_id = session.get("user_id")
    if user_id:
        return jsonify({"logged_in": True, "user_id": user_id})
    return jsonify({"logged_in": False}), 401


@auth_blueprint.route('/logout', methods=['POST'])
def auth_logout():
    if "user_id" in session:
        logger.info(f"User {session.get('user_id')} logged out.")
        session.clear()

    response = jsonify({"message": "Logout successful"})
    response.set_cookie('session', '', expires=0)
    return response, 200
