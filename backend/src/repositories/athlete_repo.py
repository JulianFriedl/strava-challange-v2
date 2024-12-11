from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError
from models.athlete import Athlete
from utils.db_mongo import MongoDB

class AthleteRepository:
    def __init__(self):
        self.collection = MongoDB.get_instance().athletes

    def find_by_athlete_id(self, athlete_id: int):
        """
        Find an athlete by athlete_id.
        """
        try:
            data = self.collection.find_one({"athlete_id": athlete_id})
            if data:
                return Athlete.from_mongo(data)
            return None
        except PyMongoError as e:
            raise Exception(f"Failed to find athlete with athlete_id {athlete_id}: {e}")

    def create_athlete(self, athlete: Athlete):
        """
        Insert a new athlete into the database.
        """
        athlete_data = athlete.to_mongo()
        try:
            result = self.collection.insert_one(athlete_data)
            if result.acknowledged:
                return result.inserted_id  # Return the inserted document's ID
            raise Exception("Insert operation not acknowledged by the database.")
        except DuplicateKeyError:
            raise Exception(f"Athlete with athlete_id {athlete.athlete_id} already exists.")
        except PyMongoError as e:
            raise Exception(f"Failed to create athlete: {e}")

    def update_athlete(self, athlete_id: int, update: dict):
        """
        Update an athlete by athlete_id.
        """
        try:
            updated_data = self.collection.find_one_and_update(
                {"athlete_id": athlete_id},
                {"$set": update},
                return_document=ReturnDocument.AFTER
            )
            if updated_data:
                return Athlete.from_mongo(updated_data)
            raise Exception(f"No athlete found with athlete_id {athlete_id} to update.")
        except PyMongoError as e:
            raise Exception(f"Failed to update athlete with athlete_id {athlete_id}: {e}")

    def delete_athlete(self, athlete_id: int):
        """
        Delete an athlete by athlete_id.
        """
        try:
            result = self.collection.delete_one({"athlete_id": athlete_id})
            if result.deleted_count == 0:
                raise Exception(f"No athlete found with athlete_id {athlete_id} to delete.")
            return result.deleted_count
        except PyMongoError as e:
            raise Exception(f"Failed to delete athlete with athlete_id {athlete_id}: {e}")


    def get_all_athletes(self):
        """
        Fetch all athletes from the database.
        """
        try:
            cursor = self.collection.find({})
            return [Athlete.from_mongo(doc) for doc in cursor]
        except Exception as e:
            raise Exception(f"Failed to fetch athletes: {e}")
