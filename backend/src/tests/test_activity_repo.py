import pytest
from datetime import datetime
from models.activity import Activity, GeoJSONLineString
from repositories.activity_repo import ActivityRepository


@pytest.fixture(scope="module")
def activity_repo():
    return ActivityRepository()


@pytest.fixture(scope="module")
def sample_activities():
    polyline = GeoJSONLineString(type="LineString", coordinates=[[-122.5, 37.7], [-122.6, 37.8]])
    return [
        Activity(
            activity_id=12345,
            athlete_id=67890,
            name="Morning Ride",
            type="Ride",
            start_date=datetime.utcnow(),
            moving_time=3600.0,
            distance=25000.0,
            total_elevation_gain=500.0,
            polyline=polyline,
            kudos=25,
            suffer_score=80,
            url="http://example.com/activity/12345",
            year=2024,
        ),
        Activity(
            activity_id=67890,
            athlete_id=67890,
            name="Evening Ride",
            type="Ride",
            start_date=datetime.utcnow(),
            moving_time=3600.0,
            distance=30000.0,
            total_elevation_gain=700.0,
            polyline=polyline,
            kudos=30,
            suffer_score=90,
            url="http://example.com/activity/67890",
            year=2024,
        ),
        Activity(
            activity_id=54321,
            athlete_id=12345,
            name="Afternoon Swim",
            type="Swim",
            start_date=datetime.utcnow(),
            moving_time=2700.0,
            distance=2000.0,
            total_elevation_gain=0.0,
            polyline=polyline,
            kudos=5,
            suffer_score=10,
            url="http://example.com/activity/54321",
            year=2024,
        ),
    ]


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown(activity_repo, sample_activities):
    """
    Setup: Add multiple activities before tests.
    Teardown: Remove all added activities after tests.
    """
    for activity in sample_activities:
        activity_repo.create_activity(activity)
    yield  # This is where the tests run
    for activity in sample_activities:
        activity_repo.delete_activity(activity.activity_id)

def test_find_activity_by_id(activity_repo, sample_activities):
    activity = activity_repo.find_activity_by_id(sample_activities[0].activity_id)
    assert activity is not None
    assert activity.name == sample_activities[0].name


def test_update_activity(activity_repo, sample_activities):
    updated_activity = activity_repo.update_activity(sample_activities[0].activity_id, {"name": "Evening Ride"})
    assert updated_activity is not None
    assert updated_activity.name == "Evening Ride"


def test_list_activities_by_athlete_and_year(activity_repo, sample_activities):
    activities = activity_repo.list_activities_by_athlete_and_year(sample_activities[0].athlete_id, sample_activities[0].year)
    assert len(activities) > 0
    assert activities[0].year == sample_activities[0].year

def test_find_activities_by_athlete_and_type(activity_repo):
    activities = activity_repo.find_activities_by_athlete_and_type(67890, "Ride")
    assert len(activities) == 2
    assert all(activity.type == "Ride" for activity in activities)
    assert activities[0].athlete_id == 67890
    assert activities[1].athlete_id == 67890

    activities = activity_repo.find_activities_by_athlete_and_type(12345, "Swim")
    assert len(activities) == 1
    assert activities[0].type == "Swim"
    assert activities[0].athlete_id == 12345

    activities = activity_repo.find_activities_by_athlete_and_type(12345, "Ride")
    assert len(activities) == 0
