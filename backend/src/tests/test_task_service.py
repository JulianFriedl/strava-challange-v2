import pytest
from unittest.mock import patch, MagicMock
from services.core_services.task_service import TaskService, Task, TaskType


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


def test_shutdown(task_service):
    """
    Test that the TaskService shuts down gracefully.
    """
    with patch("services.core_services.task_service.logger") as mock_logger:
        task_service.shutdown()

        mock_logger.info.assert_any_call("Shutting down ApiRequestService.")
        mock_logger.info.assert_any_call("ApiRequestService shut down complete.")
