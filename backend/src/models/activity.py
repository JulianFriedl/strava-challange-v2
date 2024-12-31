from datetime import datetime
from utils.datetime_utils import parse_datetime
from polyline import decode as decode_polyline
import logging


logger = logging.getLogger(__name__)

class GeoJSONLineString:
    def __init__(self, type: str, coordinates: list[list[float]]):
        self.type = type
        self.coordinates = coordinates

    @classmethod
    def from_mongo(cls, data):
        """Convert MongoDB GeoJSON data to GeoJSONLineString instance (swap longitude and latitude)."""
        return cls(
            type=data["type"],
            coordinates=[[coord[1], coord[0]] for coord in data["coordinates"]],
        )

    def to_mongo(self):
        """Convert GeoJSONLineString instance to a MongoDB-compatible dictionary (swap latitude and longitude)."""
        return {
            "type": self.type,
            "coordinates": [[coord[1], coord[0]] for coord in self.coordinates],
        }


class Activity:
    def __init__(
        self,
        activity_id: int,
        athlete_id: int,
        name: str,
        type: str,
        start_date: datetime,
        moving_time: float,
        distance: float,
        total_elevation_gain: float,
        kudos: int,
        suffer_score: int,
        url: str,
        year: int,
        elapsed_time: float = None,
        commute: bool = None,
        average_speed: float = None,
        max_speed: float = None,
        has_heartrate: bool = None,
        max_watts: float = None,
        description: str = None,
        calories: float = None,
        polyline: GeoJSONLineString = None,
    ):
        self.activity_id = activity_id
        self.athlete_id = athlete_id
        self.name = name
        self.type = type
        self.start_date = parse_datetime(start_date)
        self.moving_time = moving_time
        self.distance = distance
        self.total_elevation_gain = total_elevation_gain
        self.polyline = polyline
        self.kudos = kudos
        self.suffer_score = suffer_score
        self.url = url
        self.year = year
        self.elapsed_time = elapsed_time
        self.commute = commute
        self.average_speed = average_speed
        self.max_speed = max_speed
        self.has_heartrate = has_heartrate
        self.max_watts = max_watts
        self.description = description
        self.calories = calories

    @classmethod
    def from_mongo(cls, data):
        """Convert MongoDB document to Route instance."""
        polyline_data = data.get("summary_polyline")
        polyline = GeoJSONLineString.from_mongo(polyline_data) if polyline_data else None
        return cls(
            activity_id=data["activity_id"],
            athlete_id=data["athlete_id"],
            name=data["name"],
            type=data["type"],
            start_date=data["start_date"],
            moving_time=data["moving_time"],
            distance=data["distance"],
            total_elevation_gain=data["total_elevation_gain"],
            polyline=polyline,
            kudos=data["kudos"],
            suffer_score=data["suffer_score"],
            url=data["url"],
            year=data["year"],
            elapsed_time=data.get("elapsed_time"),
            commute=data.get("commute"),
            average_speed=data.get("average_speed"),
            max_speed=data.get("max_speed"),
            has_heartrate=data.get("has_heartrate"),
            max_watts=data.get("max_watts"),
            description=data.get("description"),
            calories=data.get("calories"),
        )

    def to_mongo(self):
        """Convert Route instance to a MongoDB-compatible dictionary."""
        return {
            "activity_id": self.activity_id,
            "athlete_id": self.athlete_id,
            "name": self.name,
            "type": self.type,
            "start_date": self.start_date,
            "moving_time": self.moving_time,
            "distance": self.distance,
            "total_elevation_gain": self.total_elevation_gain,
            "summary_polyline": self.polyline.to_mongo() if self.polyline else None,
            "kudos": self.kudos,
            "suffer_score": self.suffer_score,
            "url": self.url,
            "year": self.year,
            "elapsed_time": self.elapsed_time,
            "commute": self.commute,
            "average_speed": self.average_speed,
            "max_speed": self.max_speed,
            "has_heartrate": self.has_heartrate,
            "max_watts": self.max_watts,
            "description": self.description,
            "calories": self.calories,
        }

    @staticmethod
    def create_activity_from_data(activity_data: dict, athlete_id: int):
        """
        Create an Activity object from Strava activity data.
        """
        activity_id = activity_data.get("id")
        if not activity_id:
            logger.warning("Activity ID missing. Skipping activity.")
            raise Exception("No activity Id found.")

        summary_polyline = activity_data.get("map", {}).get("summary_polyline")
        decoded_coordinates = None
        if summary_polyline:
            try:
                decoded_coordinates = decode_polyline(summary_polyline)
            except Exception as e:
                logger.warning(f"Failed to decode polyline for activity {activity_id}: {e}")

        start_date = activity_data.get("start_date_local", "1900-01-01T00:00:00Z")

        activity = Activity(
            activity_id=activity_id,
            athlete_id=athlete_id,
            name=activity_data.get("name", ""),
            type=activity_data.get("sport_type", "Unknown"),
            start_date=start_date,
            moving_time=activity_data.get("moving_time", 0) / 60,
            distance=activity_data.get("distance", 0) / 1000,
            total_elevation_gain=activity_data.get("total_elevation_gain", 0),
            kudos=activity_data.get("kudos_count", 0),
            suffer_score=activity_data.get("suffer_score", 0),
            url=f"https://www.strava.com/activities/{activity_id}",
            year=datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ").year,
            elapsed_time=activity_data.get("elapsed_time", 0),
            commute=activity_data.get("commute", False),
            average_speed=activity_data.get("average_speed", 0),
            max_speed=activity_data.get("max_speed", 0),
            has_heartrate=activity_data.get("has_heartrate", False),
            max_watts=activity_data.get("max_watts", 0),
            description=activity_data.get("description", ""),
            calories=activity_data.get("calories", 0),
            polyline=GeoJSONLineString(
                type="LineString",
                coordinates=decoded_coordinates
            ) if decoded_coordinates else None,

        )
        return activity
