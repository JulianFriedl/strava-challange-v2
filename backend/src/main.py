import os
import logging
from flask import Flask, session
from flask_session import Session
from flask_compress import Compress
import flask_cors
from pymongo.errors import ConnectionFailure
import atexit
from datetime import timedelta

from repositories.athlete_repo import AthleteRepository
from utils.db_mongo import MongoDB
from scripts.seed_data import seed_athletes, seed_activities
from services.core_services.task_service import TaskService
from api.auth import auth_blueprint
from api.map import map_blueprint
from api.webhook import webhook_blueprint
from config.log_config import setup_logging

app = Flask(__name__)

flask_cors.CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:3000", "http://127.0.0.1:3000", "http://stravascape.site"]}})

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'fallback-key-for-dev')

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(weeks=2)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"

# Secure Cookie Settings
# app.config['SESSION_COOKIE_SECURE'] = True         # Use HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True       # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'      # Mitigate CSRF, might need to be disapled in prod
Session(app)

compress = Compress()
compress.init_app(app)

setup_logging()
logger = logging.getLogger(__name__)

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
app.register_blueprint(map_blueprint, url_prefix='/api/map')
app.register_blueprint(webhook_blueprint, url_prefix='/api/webhook')


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
        logger.info("Database is empty, Seeding data...")
        seed_athletes("./data/athletes.json")
        seed_activities("./data/activities.json")
        seed_activities("./data/activities2.json")
        logger.info("Database seeding completed.")
    else:
        logger.info("Database already contains data. Skipping seeding.")


@atexit.register
def shutdown_worker():
    logger.info("Shutting down ApiRequestService at application exit.")
    TaskService.shutdown()


if __name__ == "__main__":
    try:
        logger.info("Starting backend service...")
        db_instance = initialize_database()
        # seed_database_if_empty()
        TaskService(max_workers=3)
        # Check if running in development mode
        if os.getenv("FLASK_ENV", "development") == "development":
            logger.info("Running Flask development server...")
            app.run(host="0.0.0.0", port=8080)
        else:
            logger.info("Running in production mode.")
    except Exception as e:
        logger.error("Service failed to start: %s", e)
        exit(1)

