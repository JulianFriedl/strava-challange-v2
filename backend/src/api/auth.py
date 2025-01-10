from flask import Blueprint, jsonify, request, redirect, session
import logging
import os
import re

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
    code = request.args.get("code")
    scope = request.args.get("scope")
    logger.info(f"Strava_auth_callback called. Code: {code}, scope: {scope}")
    if not re.match(r"^[a-zA-Z0-9_-]{10,50}$", code):  # TODO test this regex
        return jsonify({"error": "Invalid code"}), 400
    scope_necassary = {"read", "activity:read"}

    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    granted_scope = set(scope.split(","))

    if not scope_necassary.issubset(granted_scope):
        logger.error(f"Authorization error: scope mismatch. Required: {scope_necassary}, Granted: {granted_scope}")
        return jsonify("User did not grant the required 'activity:read' scope."), 403

    try:
        athlete_data = process_strava_callback(code)
        athlete_id = athlete_data.get("athlete_id")
        session["user_id"] = athlete_id
        return redirect(os.getenv("FRONTEND_URL", "http://localhost:5000/"))
    except AuthorizationError as e:
        logger.error(f"Authorization error: {str(e)}")
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_blueprint.route('/status', methods=['GET'])
def auth_status():
    user_id = session.get("user_id")
    if user_id:
        logger.info(f"User {user_id} already logged in.")
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
