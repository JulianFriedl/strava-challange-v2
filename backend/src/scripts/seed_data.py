import json
from datetime import datetime
import sys
import os
from polyline import decode as decode_polyline

# Add the src directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from pymongo.errors import DuplicateKeyError
from repositories.athlete_repo import AthleteRepository
from repositories.activity_repo import ActivityRepository
from models.athlete import Athlete
from models.activity import Activity, GeoJSONLineString

def seed_athletes(data_file):
    athlete_repo = AthleteRepository()

    with open(data_file, 'r') as file:
        athletes = json.load(file)

    for entry in athletes:
        strava_athlete = entry["strava_data"]["athlete"]
        athlete = Athlete(
            athlete_id=strava_athlete["id"],
            username=strava_athlete["username"],
            first_name=strava_athlete["firstname"],
            last_name=strava_athlete["lastname"],
            created_at=datetime.fromisoformat(strava_athlete["created_at"].replace("Z", "+00:00")),
            profile={"medium": strava_athlete["profile_medium"], "full": strava_athlete["profile"]},
            tokens={
                "access_token": entry["strava_data"]["access_token"],
                "refresh_token": entry["strava_data"]["refresh_token"],
                "expires_at": datetime.utcfromtimestamp(entry["strava_data"]["expires_at"]),
            },
        )

        try:
            athlete_repo.create_athlete(athlete)
            print(f"Inserted athlete: {athlete.username}")
        except Exception as e:
            print(f"Duplicate athlete: {athlete.username}, skipping...")


def seed_activities(data_file: str):
    activity_repo = ActivityRepository()

    with open(data_file, "r") as file:
        activities_data = json.load(file)

    for athlete_id, athlete_data in activities_data["athletes"].items():
        for route in athlete_data["routes"]:
            # Process the polyline (decode if present)
            polyline = route.get("map", {}).get("summary_polyline")
            coordinates = decode_polyline(polyline) if polyline else []

            activity = Activity(
                activity_id=route["activity_id"],
                athlete_id=athlete_data["user_id"],
                name=route["name"],
                type=route["type"],
                start_date=datetime.fromisoformat(route["start_date"]),
                moving_time=route["moving_time"],
                distance=route["distance"],
                total_elevation_gain=route["total_elevation_gain"],
                polyline=GeoJSONLineString(
                    type="LineString",
                    coordinates=coordinates,
                ) if coordinates else None,
                kudos=route["kudos"],
                suffer_score=route["suffer_score"],
                url=route["url"],
                year=datetime.fromisoformat(route["start_date"]).year,
            )

            try:
                activity_repo.create_activity(activity)
                # print(f"Inserted activity: {activity.name} for athlete ID {athlete_id}")
            except Exception as e:
                print(f"Error inserting activity {activity.activity_id}: {e}")

