import os
import logging
import flask
import flask_cors
from datetime import datetime
from pymongo.errors import ConnectionFailure

from repositories.athlete_repo import AthleteRepository
from models.athlete import Athlete
from utils.db_mongo import MongoDB

app = flask.Flask(__name__)
flask_cors.CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:8000", "http://127.0.0.1:8000", "http://stravascape.site"]}})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register blueprints
# app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
# app.register_blueprint(user_blueprint, url_prefix='/api/user')

def initialize_database():
    """Initialize MongoDB connection."""
    try:
        db_instance = MongoDB.get_instance()
        logger.info("Successfully connected to MongoDB: %s", db_instance.name)
        return db_instance
    except ConnectionFailure as e:
        logger.error("Failed to connect to MongoDB: %s", e)
        raise

# Initialize repository
repo = AthleteRepository()

# Test create functionality
def test_create():
    profile = {"medium": "http://example.com/medium.jpg", "full": "http://example.com/full.jpg"}
    tokens = {"access_token": "token123", "refresh_token": "refresh123", "expires_at": datetime.utcnow()}
    athlete = Athlete(
        athlete_id=12345,
        username="johndoe",
        first_name="John",
        last_name="Doe",
        created_at=datetime.utcnow(),
        profile=profile,
        tokens=tokens,
    )
    repo.create_athlete(athlete)
    print("Athlete created")

# Test find functionality
def test_find(athlete_id):
    athlete = repo.find_by_athlete_id(athlete_id)
    if athlete:
        print("Athlete found:", athlete.__dict__)
    else:
        print("Athlete not found")

if __name__ == "__main__":
    try:
        logger.info("Starting backend service...")
        db_instance = initialize_database()
        logger.info("Service initialization completed.")

        print("Starting inline tests...")
        # Run tests
        test_create()
        test_find(12345)

        # Start Flask server
        app.run(host="0.0.0.0", port=8080)
    except Exception as e:
        logger.error("Service failed to start: %s", e)
        exit(1)

