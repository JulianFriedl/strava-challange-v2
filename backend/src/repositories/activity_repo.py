from pymongo import ReturnDocument
from pymongo.errors import PyMongoError
from utils.db_mongo import MongoDB
from models.activity import Activity


class ActivityRepository:
    def __init__(self):
        self.collection = MongoDB.get_instance().activities

    def create_activity(self, activity: Activity):
        """
        Insert a new Activity into the database.
        """
        try:
            activity_data = activity.to_mongo()
            self.collection.insert_one(activity_data)
        except PyMongoError as e:
            raise Exception(f"Failed to create activity: {e}")

    def find_activity_by_id(self, activity_id: int):
        """
        Find an Activity by its ActivityID.
        """
        try:
            data = self.collection.find_one({"activity_id": activity_id})
            return Activity.from_mongo(data) if data else None
        except PyMongoError as e:
            raise Exception(f"Failed to find activity: {e}")

    def update_activity(self, activity_id: int, update: dict):
        """
        Update an Activity by its ActivityID.
        """
        try:
            updated_data = self.collection.find_one_and_update(
                {"activity_id": activity_id},
                {"$set": update},
                return_document=ReturnDocument.AFTER,
            )
            if not updated_data:
                raise Exception(f"No activity found with ActivityID {activity_id}")
            return Activity.from_mongo(updated_data)
        except PyMongoError as e:
            raise Exception(f"Failed to update activity: {e}")

    def delete_activity(self, activity_id: int):
        """
        Delete an Activity by its ActivityID.
        """
        try:
            result = self.collection.delete_one({"activity_id": activity_id})
            if result.deleted_count == 0:
                raise Exception(f"No activity found with ActivityID {activity_id}")
        except PyMongoError as e:
            raise Exception(f"Failed to delete activity: {e}")

    def list_activities_by_athlete_and_year(self, athlete_id: int, year: int):
        """
        List all activities for a given AthleteID and Year.
        """
        try:
            filter_criteria = {"athlete_id": athlete_id, "year": year}
            cursor = self.collection.find(filter_criteria)

            activities = [Activity.from_mongo(doc) for doc in cursor]
            return activities
        except PyMongoError as e:
            raise Exception(f"Failed to list activities: {e}")

    #TODO: For the challange it would probably be good to also filter by Year, maybe change the index for the collection too to include the Year
    def find_activities_by_athlete_and_type(self, athlete_id: int, activity_type: str):
        """
        Find all Activities by AthleteID and Type.
        """
        try:
            query = {"athlete_id": athlete_id, "type": activity_type}
            cursor = self.collection.find(query)
            activities = [Activity.from_mongo(doc) for doc in cursor]
            return activities
        except PyMongoError as e:
            raise Exception(f"Failed to find activities for athlete_id={athlete_id} and type={activity_type}: {e}")
