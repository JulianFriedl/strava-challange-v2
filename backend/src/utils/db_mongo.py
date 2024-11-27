import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

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
            print(f"Connecting to MongoDB at {mongo_uri}")

            # Uncomment this line for local MongoDB testing
            # mongo_uri = f"mongodb://{username}:{password}@localhost:{port}/{db_name}"

            try:
                client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)  # 5-second timeout
                # Test connection
                client.server_info()  # Will raise an exception if unable to connect
                MongoDB._instance = client[db_name]
                print(f"Connected to database: {MongoDB._instance.name}")
            except ConnectionFailure as e:
                print(f"Failed to connect to MongoDB: {e}")
                raise # TODO:for dev, handle error correctly for prod

        return MongoDB._instance
