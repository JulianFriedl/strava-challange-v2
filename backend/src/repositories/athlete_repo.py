from pymongo import ReturnDocument
from models.athlete import Athlete
from utils.db_mongo import MongoDB

class AthleteRepository:
    def __init__(self):
        self.collection = MongoDB.get_instance().athletes

    def find_by_athlete_id(self, athlete_id: int):
        """
        Find an athlete by athlete_id.
        """
        data = self.collection.find_one({"athlete_id": athlete_id})
        return Athlete.from_mongo(data) if data else None

    def create_athlete(self, athlete: Athlete):
        """
        Insert a new athlete into the collection.
        """
        athlete_dict = athlete.to_mongo()
        self.collection.insert_one(athlete_dict)

    def update_athlete(self, athlete_id: int, update: dict):
        """
        Update an athlete by athlete_id.
        """
        return self.collection.find_one_and_update(
            {"athlete_id": athlete_id},
            {"$set": update},
            return_document=ReturnDocument.AFTER
        )

    def delete_athlete(self, athlete_id: int):
        """
        Delete an athlete by athlete_id.
        """
        result = self.collection.delete_one({"athlete_id": athlete_id})
        return result.deleted_count
