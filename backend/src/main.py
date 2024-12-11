import os
import logging
import flask
import flask_cors
from datetime import datetime
from pymongo.errors import ConnectionFailure

from repositories.athlete_repo import AthleteRepository
from repositories.activity_repo import ActivityRepository
from models.activity import Activity, GeoJSONLineString
from models.athlete import Athlete
from utils.db_mongo import MongoDB
from scripts.seed_data import seed_athletes, seed_activities

from api.auth import auth_blueprint
from api.map import map_blueprint

app = flask.Flask(__name__)
flask_cors.CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:8000", "http://127.0.0.1:8000", "http://stravascape.site"]}})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register blueprints
# app.register_blueprint(user_blueprint, url_prefix='/api/user')

app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
app.register_blueprint(map_blueprint, url_prefix='/api/map')

def initialize_database():
    try:
        db_instance = MongoDB.get_instance()
        logger.info("Successfully connected to MongoDB: %s", db_instance.name)
        return db_instance
    except ConnectionFailure as e:
        logger.error("Failed to connect to MongoDB: %s", e)
        raise

def seed_database_if_empty():
    """
    Check if the database is empty and seed it if necessary.
    """
    athlete_repo = AthleteRepository()

    # Check for existing data
    if not athlete_repo.get_all_athletes():
        logger.info(f"Database is empty, Seeding data...")
        seed_athletes("./data/athletes.json")
        seed_activities("./data/activities.json")
        logger.info("Database seeding completed.")
    else:
        logger.info("Database already contains data. Skipping seeding.")

if __name__ == "__main__":
    try:
        logger.info("Starting backend service...")
        db_instance = initialize_database()
        logger.info("Service initialization completed.")

        seed_database_if_empty() # seed db for dev

        # Start Flask server
        app.run(host="0.0.0.0", port=8080)
    except Exception as e:
        logger.error("Service failed to start: %s", e)
        exit(1)

