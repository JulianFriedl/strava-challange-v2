import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging


logger = logging.getLogger(__name__)

class MongoDB:
    _instance = None

    @staticmethod
    def get_instance():
        if MongoDB._instance is None:
            # Construct MongoDB URI from environment variables
            username = os.getenv("MONGO_INITDB_ROOT_USERNAME", "rootuser")
            password = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "rootpass")
            port = os.getenv("MONGO_PORT", "27017")
            db_name = os.getenv("MONGO_INITDB_NAME", "StravaChallangeV2Db")

            # MongoDB URI for Docker setup
            mongo_uri = f"mongodb://{username}:{password}@mongo:{port}"
            logging.info(f"Connecting to MongoDB at {mongo_uri}")

            # Uncomment this line for local MongoDB testing
            # mongo_uri = f"mongodb://{username}:{password}@localhost:{port}/{db_name}"

            try:
                client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000, maxPoolSize=100, minPoolSize=10)
                # Test connection
                client.server_info()  # Will raise an exception if unable to connect
                MongoDB._instance = client[db_name]
                logging.info(f"Connected to database: {MongoDB._instance.name}")
            except ConnectionFailure as e:
                logging.error(f"Failed to connect to MongoDB")
                logging.debug(f"{e}")
                raise

        return MongoDB._instance
