from flask import Blueprint, jsonify, request
from services.map_service import get_activities_with_polylines, get_all_athletes, get_all_years
import logging

logger = logging.getLogger(__name__)
map_blueprint = Blueprint('map', __name__)

@map_blueprint.route('/', methods=['GET'])
def map():
    """
    Return a list of all the activities that have a polyline and are associated
    with the athlete ID(s) and year(s).
    """
    years = request.args.getlist('years')  # Get 'years' as a list
    athlete_ids_raw = request.args.getlist('athletes')  # Get 'athletes' as a list

    # Flatten and parse athlete IDs
    athlete_ids = []
    try:
        for item in athlete_ids_raw:
            # Split the item by commas to handle multiple IDs in one item
            ids = item.split(',')
            athlete_ids.extend(int(aid.strip()) for aid in ids)
        logger.info(f"Map request received, years: {years}, athlete_ids: {athlete_ids}")
    except ValueError as e:
        logger.error(f"Invalid athlete IDs provided: {athlete_ids_raw}")
        return jsonify({"error": "Invalid athlete IDs"}), 400
    try:
        activities = get_activities_with_polylines(years, athlete_ids)
        return jsonify(activities), 200
    except Exception as e:
        logger.error(f"Error fetching activities: {e}")
        return jsonify({"error": "Failed to fetch activities"}), 500

@map_blueprint.route('/athletes', methods=['GET'])
def athletes():
    """
    Return a list of all the athletes in the database with their metadata.
    """
    logger.info("Athletes request received.")

    try:
        all_athletes = get_all_athletes()
        return jsonify(all_athletes), 200
    except Exception as e:
        logger.error(f"Error fetching athletes: {e}")
        return jsonify({"error": "Failed to fetch athletes"}), 500

@map_blueprint.route('/years', methods=['GET'])
def years():
    """
    Return all available years in the activities.
    """
    logger.info("Years request received.")

    try:
        available_years = get_all_years()
        return jsonify(available_years), 200
    except Exception as e:
        logger.error(f"Error fetching years: {e}")
        return jsonify({"error": "Failed to fetch years"}), 500
