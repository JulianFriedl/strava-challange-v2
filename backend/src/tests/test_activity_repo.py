import pytest
from datetime import datetime
from models.activity import Activity, GeoJSONLineString
from repositories.activity_repo import ActivityRepository


@pytest.fixture(scope="module")
def activity_repo():
    return ActivityRepository()


@pytest.fixture(scope="module")
def sample_activities():
    polyline = GeoJSONLineString(type="LineString", coordinates=[[37.7, -122.5], [37.8, -122.6]])
    return [
        Activity(
            activity_id=1,
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
            activity_id=2,
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
            activity_id=3,
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
    try:
        for activity in sample_activities:
            activity_repo.create_activity(activity)
    finally:
        yield  # This is where the tests run
        for activity in sample_activities:
            try:
                activity_repo.delete_activity(activity.activity_id)
            except Exception as e:
                print(f"Error during cleanup for activity {activity.activity_id}: {e}")

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

def test_create_activity_with_no_polyline(activity_repo):
    activity_id = 4
    try:
        activity = Activity(
            activity_id=activity_id,
            athlete_id=67890,
            name="Walk",
            type="Walk",
            start_date=datetime.utcnow(),
            moving_time=1800.0,
            distance=2000.0,
            total_elevation_gain=50.0,
            polyline=None,  # No polyline
            kudos=10,
            suffer_score=15,
            url="http://example.com/activity/99999",
            year=2024,
        )
        activity_repo.create_activity(activity)
        created_activity = activity_repo.find_activity_by_id(activity_id)
        assert created_activity is not None
        assert created_activity.polyline is None
    finally:
        activity_repo.delete_activity(activity_id)


def test_create_activity_with_invalid_polyline(activity_repo):
    activity_id = 5
    try:
        polyline = GeoJSONLineString(type="LineString", coordinates=[[37.7]])  # Invalid polyline
        activity = Activity(
            activity_id=activity_id,
            athlete_id=67890,
            name="Jog",
            type="Run",
            start_date=datetime.utcnow(),
            moving_time=1200.0,
            distance=1500.0,
            total_elevation_gain=20.0,
            polyline=polyline,
            kudos=5,
            suffer_score=8,
            url="http://example.com/activity/88888",
            year=2024,
        )
        activity_repo.create_activity(activity)
        created_activity = activity_repo.find_activity_by_id(activity_id)
        assert created_activity is not None
        assert created_activity.polyline is None  # Invalid polyline should result in None
    finally:
        activity_repo.delete_activity(activity_id)
