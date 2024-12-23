from flask import Blueprint, jsonify, request, Response
from services.api_services.map_service import get_activities_with_polylines, get_all_athletes, get_all_years
import logging
import orjson
import cProfile
import pstats
import io

logger = logging.getLogger(__name__)

map_blueprint = Blueprint('map', __name__)

@map_blueprint.route('/', methods=['GET'])
def map():
    """
    Return a list of all the activities that have a polyline and are associated
    with the athlete ID(s) and year(s).
    """
    # profiler = cProfile.Profile()
    # profiler.enable()
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

        logger.info(f"Map request received, years: {years}, athlete_ids: {athlete_ids}")
        response = None
        try:
            activities = get_activities_with_polylines(years, athlete_ids)

            response = Response(
            orjson.dumps(activities, option=orjson.OPT_SERIALIZE_DATACLASS | orjson.OPT_SERIALIZE_NUMPY),
            mimetype='application/json'
            ), 200
        except Exception as e:
            logger.error(f"Error calling map service: {e}")
            response = jsonify({"error": "Failed to retrieve map data"}), 500

    except ValueError as e:
        logger.error(f"Invalid input provided: {e}")
        response = jsonify({"error": "Invalid athlete IDs or years"}), 400

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
