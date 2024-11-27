import pytest
from datetime import datetime
from models.athlete import Athlete
from repositories.athlete_repo import AthleteRepository


@pytest.fixture(scope="module")
def athlete_repo():
    return AthleteRepository()


@pytest.fixture(scope="module")
def sample_athlete():
    profile = {"medium": "http://example.com/medium.jpg", "full": "http://example.com/full.jpg"}
    tokens = {"access_token": "token123", "refresh_token": "refresh123", "expires_at": datetime.utcnow()}
    return Athlete(
        athlete_id=1234123412341234,
        username="johndoe",
        first_name="John",
        last_name="Doe",
        created_at=datetime.utcnow(),
        profile=profile,
        tokens=tokens,
    )


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown(athlete_repo, sample_athlete):
    athlete_repo.create_athlete(sample_athlete)
    yield  # This is where the tests run
    athlete_repo.delete_athlete(sample_athlete.athlete_id)


def test_find_athlete(athlete_repo, sample_athlete):
    athlete = athlete_repo.find_by_athlete_id(sample_athlete.athlete_id)
    assert athlete is not None
    assert athlete.username == "johndoe"


def test_update_athlete(athlete_repo, sample_athlete):
    updated_athlete = athlete_repo.update_athlete(sample_athlete.athlete_id, {"first_name": "Jane"})
    assert updated_athlete is not None
    assert updated_athlete.first_name == "Jane"

