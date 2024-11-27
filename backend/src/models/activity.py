from datetime import datetime
from utils.datetime_utils import parse_datetime

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
        }
