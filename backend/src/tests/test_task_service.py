import pytest
from freezegun import freeze_time
from unittest.mock import patch, MagicMock
from services.core_services.task_service import TaskService, Task, TaskType
from datetime import datetime, timedelta
import time

@pytest.fixture(scope="function")
def task_service():
    """Provide a fresh TaskService instance for each test."""
    with patch.object(TaskService, "_instance", None):  # Reset singleton
        service = TaskService(max_workers=2)
        yield service
        service.shutdown()


@patch("services.core_services.task_service.fetch_athlete_activities")
def test_submit_task(mock_fetch_activities, task_service):
    """
    Test that a task can be submitted and processed by TaskService.
    """
    mock_fetch_activities.return_value = None
    dummy_task = Task(
        athlete_id=12345,
        endpoint="https://api.strava.com/api/v3/athlete/activities",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
    )

    task_service.submit_task(dummy_task)
    task_service.executor.shutdown(wait=True)
    mock_fetch_activities.assert_called_once_with(athlete_id=12345)


@patch("services.core_services.task_service.fetch_athlete_activities")
def test_retry_logic(mock_fetch_activities, task_service):
    """
    Test that retry logic works when process_task fails.
    """
    mock_fetch_activities.side_effect = [Exception("Temporary error"), Exception("Temporary error"), None]

    retry_task = Task(
        athlete_id=12345,
        endpoint="https://api.strava.com/api/v3/athlete/activities",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
    )

    task_service.submit_task(retry_task)
    task_service.executor.shutdown(wait=True)
    assert mock_fetch_activities.call_count == 3

@patch("services.core_services.task_service.fetch_athlete_activities")
def test_delayed_task_execution_with_mock_time(mock_fetch_activities, task_service):
    """
    Test that a task with an `execute_after` time is delayed correctly without actual waiting.
    """
    mock_fetch_activities.return_value = None

    future_time = datetime.now() + timedelta(seconds=2)
    delayed_task = Task(
        athlete_id=12345,
        endpoint="https://api.strava.com/api/v3/athlete/activities",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
        execute_after=future_time,
    )

    with freeze_time(datetime.now()) as frozen_time:
        task_service.submit_task(delayed_task)
        # Initially, the task should not be executed
        mock_fetch_activities.assert_not_called()

        # Move time forward by 2 seconds
        frozen_time.tick(timedelta(seconds=2))
        task_service.process_queue()  # Trigger task processing manually
        mock_fetch_activities.assert_called_once_with(athlete_id=12345)


@patch("services.core_services.task_service.fetch_athlete_activities")
def test_immediate_and_delayed_task_execution_with_mock_time(mock_fetch_activities, task_service):
    """
    Test that immediate and delayed tasks are processed in the correct order using mocked time.
    """
    mock_fetch_activities.return_value = None

    # Immediate task
    immediate_task = Task(
        athlete_id=12345,
        endpoint="https://api.strava.com/api/v3/athlete/activities",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
    )

    # Delayed task
    future_time = datetime.now() + timedelta(seconds=2)
    delayed_task = Task(
        athlete_id=67890,
        endpoint="https://api.strava.com/api/v3/athlete/activities",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
        execute_after=future_time,
    )

    with freeze_time(datetime.now()) as frozen_time:
        task_service.submit_task(immediate_task)
        task_service.submit_task(delayed_task)

        # Trigger task processing for immediate task
        task_service.process_queue()
        mock_fetch_activities.assert_any_call(athlete_id=12345)

        # Assert delayed task has not been called yet
        assert not any(call.kwargs.get("athlete_id") == 67890 for call in mock_fetch_activities.mock_calls)

        # Move time forward by 2 seconds and process the delayed task
        frozen_time.tick(timedelta(seconds=2))
        task_service.process_queue()
        mock_fetch_activities.assert_any_call(athlete_id=67890)
        assert mock_fetch_activities.call_count == 2

def test_shutdown(task_service):
    """
    Test that the TaskService shuts down gracefully.
    """
    with patch("services.core_services.task_service.logger") as mock_logger:
        task_service.shutdown()

        mock_logger.info.assert_any_call("Shutting down ApiRequestService.")
        mock_logger.info.assert_any_call("ApiRequestService shut down complete.")
