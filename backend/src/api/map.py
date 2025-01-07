from flask import Blueprint, jsonify, request, Response, session
from services.api_services.map_service import get_activities_with_polylines, get_all_athletes, get_all_years
import logging
import orjson
import cProfile
import pstats
import io

ARGS_LIMIT = 7

logger = logging.getLogger(__name__)

map_blueprint = Blueprint('map', __name__)

@map_blueprint.route('/', methods=['GET'])
@map_blueprint.route('', methods=['GET'])
def map():
    """
    Return a list of all the activities that have a polyline and are associated
    with the athlete ID(s) and year(s).
    """

    if not session.get("user_id"):
        logger.info("Not logged in.")
        return jsonify({"error": "unauthenticated"}), 401

    try:
        # Parse and flatten the 'years' parameter
        years_raw = request.args.getlist('years')
        years = [
            int(year.strip())
            for item in years_raw
            for year in item.split(',')
        ]

        # Parse and flatten the 'athletes' parameter
        athlete_ids_raw = request.args.getlist('athletes')
        athlete_ids = [
            int(athlete_id.strip())
            for item in athlete_ids_raw
            for athlete_id in item.split(',')
        ]
    except ValueError as e:
        logger.error(f"Invalid input provided: {e}")
        return jsonify({"error": "Invalid athlete IDs or years"}), 400

    # profiler = cProfile.Profile()
    # profiler.enable()

    response = None
    if len(years) + len(athlete_ids) > ARGS_LIMIT:
        logger.error(f"Too many args: {len(years) + len(athlete_ids)}")
        response = jsonify({"error": "Too many args"}), 400
    else:
        logger.info(f"Map request received, years: {years}, athlete_ids: {athlete_ids}")
        try:
            activities = get_activities_with_polylines(years, athlete_ids)
            response = Response(
            orjson.dumps(activities, option=orjson.OPT_SERIALIZE_DATACLASS | orjson.OPT_SERIALIZE_NUMPY),
            mimetype='application/json'
            ), 200
        except Exception as e:
            logger.error(f"Error calling map service: {e}")
            response = jsonify({"error": "Failed to retrieve map data"}), 500


    # profiler.disable()  # Stop profiling

    # # Save profiling results to a string
    # s = io.StringIO()
    # ps = pstats.Stats(profiler, stream=s).sort_stats(pstats.SortKey.TIME)
    # ps.print_stats()

    # # Log the profiling results (or save them to a file)
    # logger.info("Profiling results:\n" + s.getvalue())

    return response

@map_blueprint.route('/athletes', methods=['GET'])
def athletes():
    """
    Return a list of all the athletes in the database with their metadata.
    """
    logger.info("Athletes request received.")
    if not session.get("user_id"):
        logger.info("Not logged in.")
        return jsonify({"error": "unauthenticated"}), 401

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

    if not session.get("user_id"):
        logger.info("Not logged in.")
        return jsonify({"error": "unauthenticated"}), 401

    try:
        available_years = get_all_years()
        return jsonify(available_years), 200
    except Exception as e:
        logger.error(f"Error fetching years: {e}")
        return jsonify({"error": "Failed to fetch years"}), 500

@map_blueprint.route('/limit', methods=['GET'])
def limit():
    """
    Return Limit for the amount of args to frontend
    """
    logger.info("Limit Request received.")

    if not session.get("user_id"):
        logger.info("Not logged in.")
        return jsonify({"error": "unauthenticated"}), 401

    return jsonify({"limit": ARGS_LIMIT}), 200
