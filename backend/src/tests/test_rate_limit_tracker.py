import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from services.core_services.rate_limit_tracker import RateLimitTracker

from api.exceptions import RateLimitExceededException

@pytest.fixture
def rate_limit_tracker():
    """Fixture for RateLimitTracker instance."""
    return RateLimitTracker()


def test_rate_limit_initialization(rate_limit_tracker):
    """Test the initial state of the RateLimitTracker."""
    assert rate_limit_tracker.limit_15_min == 200
    assert rate_limit_tracker.limit_daily == 1000
    assert rate_limit_tracker.requests_15_min == 0
    assert rate_limit_tracker.requests_daily == 0


@patch("services.core_services.rate_limit_tracker.datetime")
def test_wait_if_needed(mock_datetime, rate_limit_tracker):
    now = datetime(2024, 12, 22, 22, 10, 0, 0)
    mock_datetime.utcnow.return_value = now
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    rate_limit_tracker.requests_15_min = rate_limit_tracker.limit_15_min
    rate_limit_tracker.reset_time_15_min = now + timedelta(seconds=5)

    # Expect RateLimitExceededException with a delay of 5 seconds
    with pytest.raises(RateLimitExceededException) as exc_info:
        rate_limit_tracker.wait_if_needed()

    assert exc_info.value.delay == 5, "Expected delay did not match the reset_time_15_min."


def test_update_limits(rate_limit_tracker):
    """Test that update_limits correctly updates from headers."""
    headers = {
        "X-ReadRateLimit-Limit": "100,1000",
        "X-ReadRateLimit-Usage": "50,500"
    }

    rate_limit_tracker.update_limits(headers)

    assert rate_limit_tracker.limit_15_min == 100
    assert rate_limit_tracker.limit_daily == 1000
    assert rate_limit_tracker.requests_15_min == 50
    assert rate_limit_tracker.requests_daily == 500


@patch("services.core_services.rate_limit_tracker.datetime")
def test_combined_logic(mock_datetime, rate_limit_tracker):
    """Test a combined scenario of updating limits and waiting."""
    now = datetime(2024, 12, 22, 22, 10, 0, 0)
    mock_datetime.utcnow.return_value = now
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    # Update limits to simulate headers
    headers = {
        "X-ReadRateLimit-Limit": "100,1000",
        "X-ReadRateLimit-Usage": "100,999"
    }
    rate_limit_tracker.update_limits(headers)

    # Set reset time to force wait
    rate_limit_tracker.reset_time_15_min = now + timedelta(seconds=1)

    # Expect RateLimitExceededException with the calculated delay
    with pytest.raises(RateLimitExceededException) as exc_info:
        rate_limit_tracker.wait_if_needed()

    assert exc_info.value.delay == 1, "Expected delay did not match reset_time_15_min."


@patch("services.core_services.rate_limit_tracker.datetime")
def test_calculate_next_15_min_reset(mock_datetime):
    """Test the calculation of natural 15-minute reset times."""
    now = datetime(2024, 12, 22, 22, 10, 0, 0)
    mock_datetime.utcnow.return_value = now
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    reset_time = RateLimitTracker.calculate_next_15_min_reset()
    assert reset_time.minute == 15
    assert reset_time.second == 0

    # Test for edge case
    mock_datetime.utcnow.return_value = now.replace(minute=55)
    reset_time = RateLimitTracker.calculate_next_15_min_reset()
    assert reset_time.minute == 0
    assert reset_time.hour == 23


@patch("services.core_services.rate_limit_tracker.datetime")
def test_exceeding_limits(mock_datetime, rate_limit_tracker):
    """Test behavior when exceeding both 15-min and daily limits."""
    now = datetime(2024, 12, 22, 22, 10, 0, 0)
    mock_datetime.utcnow.return_value = now
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    rate_limit_tracker.requests_15_min = 200
    rate_limit_tracker.reset_time_15_min = now + timedelta(seconds=10)

    rate_limit_tracker.requests_daily = 1000
    rate_limit_tracker.reset_time_daily = now + timedelta(seconds=20)

    # Expect RateLimitExceededException with the longer of the two delays
    with pytest.raises(RateLimitExceededException) as exc_info:
        rate_limit_tracker.wait_if_needed()

    assert exc_info.value.delay == 20, "Expected delay did not match the longer limit reset time."
