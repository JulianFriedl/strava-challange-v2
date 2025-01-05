import pytest
from unittest.mock import patch
from services.core_services.task_service import TaskService, Task, TaskType
from services.core_services.rate_limit_tracker import RateLimitTracker
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


@patch.object(TaskService, "handle_final_failure")
@patch("services.core_services.task_service.fetch_athlete_activities")
def test_retry_logic_calls_final_failure(mock_fetch_activities, mock_handle_final_failure, task_service):
    """
    Test that handle_final_failure is invoked when retries are exhausted.
    """
    mock_fetch_activities.side_effect = Exception("Temporary error")

    retry_task = Task(
        athlete_id=12345,
        endpoint="https://api.strava.com/api/v3/athlete/activities",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
    )

    task_service.submit_task(retry_task)
    task_service.executor.shutdown(wait=True)

    assert mock_handle_final_failure.call_count == 1

    retry_state = mock_handle_final_failure.call_args[0][0]
    assert retry_task in retry_state.args


@patch("services.core_services.task_service.fetch_athlete_activities")
def test_immediate_and_delayed_task_execution(mock_fetch_activities, task_service):
    """
    Test that immediate and delayed tasks are processed in the correct order.
    """
    mock_fetch_activities.return_value = None

    immediate_task = Task(
        athlete_id=12345,
        endpoint="https://api.strava.com/api/v3/athlete/activities",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
        execute_after=datetime.now(),
    )

    future_time = datetime.now() + timedelta(seconds=1)
    delayed_task = Task(
        athlete_id=67890,
        endpoint="https://api.strava.com/api/v3/athlete/activities",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
        execute_after=future_time,
    )

    task_service.submit_task(immediate_task)
    task_service.submit_task(delayed_task)

    # Immediate task should execute right away
    time.sleep(0.1)
    mock_fetch_activities.assert_any_call(athlete_id=12345)

    # Delayed task should not be executed yet
    assert not any(call.kwargs.get("athlete_id") == 67890 for call in mock_fetch_activities.mock_calls)

    # Wait for the delayed task to execute
    time.sleep(1.1)
    mock_fetch_activities.assert_any_call(athlete_id=67890)
    assert mock_fetch_activities.call_count == 2

@patch("services.core_services.task_service.fetch_athlete_activities")
def test_large_number_of_tasks(mock_fetch_activities, task_service):
    """
    Test TaskService with a large number of tasks to ensure correct handling and execution timing.
    """
    mock_fetch_activities.return_value = None
    now = datetime.now()

    num_tasks = 20
    tasks = [
        Task(
            athlete_id=1000 + i,
            endpoint=f"https://api.strava.com/api/v3/athlete/activities/{i}",
            params={},
            task_type=TaskType.FETCH_ACTIVITIES,
            execute_after=now + timedelta(seconds=i * 0.1),
        )
        for i in range(num_tasks)
    ]

    for task in tasks:
        task_service.submit_task(task)

    time.sleep(num_tasks * 0.1 + 1)  # Add buffer time

    assert mock_fetch_activities.call_count == num_tasks

    # Ensure tasks were executed in the correct order
    processed_athletes = [call.kwargs["athlete_id"] for call in mock_fetch_activities.mock_calls]
    expected_athletes = [task.athlete_id for task in tasks]
    assert processed_athletes == expected_athletes, "Tasks were not executed in the correct order"

@patch("services.core_services.task_service.fetch_athlete_activities")
def test_threading_timer_delayed_execution(mock_fetch_activities, task_service):
    """
    Test that threading.Timer delays execution until after the specified execute_after time.
    """
    mock_fetch_activities.return_value = None
    now = datetime.now()

    execute_after = now + timedelta(seconds=1)
    delayed_task = Task(
        athlete_id=12345,
        endpoint="https://api.strava.com/api/v3/athlete/activities",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
        execute_after=execute_after,
    )

    task_service.submit_task(delayed_task)

    # Ensure task is not executed immediately
    time.sleep(0.5)
    assert mock_fetch_activities.call_count == 0, "Task executed before execute_after time"

    # Wait for the task to execute
    time.sleep(0.6)
    assert mock_fetch_activities.call_count == 1, "Task did not execute after execute_after time"
    mock_fetch_activities.assert_called_once_with(athlete_id=12345)


@patch("services.core_services.task_service.fetch_athlete_activities")
def test_overlapping_tasks_execution(mock_fetch_activities, task_service):
    """
    Test that multiple tasks with overlapping execution times are executed in the correct order.
    """
    mock_fetch_activities.return_value = None
    now = datetime.now()

    task1 = Task(
        athlete_id=12345,
        endpoint="https://api.strava.com/api/v3/athlete/activities/1",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
        execute_after=now + timedelta(seconds=1),  # Executes after 1 second
    )

    task2 = Task(
        athlete_id=67890,
        endpoint="https://api.strava.com/api/v3/athlete/activities/2",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
        execute_after=now + timedelta(seconds=2),  # Executes after 2 seconds
    )

    task3 = Task(
        athlete_id=54321,
        endpoint="https://api.strava.com/api/v3/athlete/activities/3",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
        execute_after=now + timedelta(seconds=1.5),  # Executes after 1.5 seconds
    )

    task_service.submit_task(task1)
    task_service.submit_task(task2)
    task_service.submit_task(task3)

    # Wait and verify task execution order
    time.sleep(1.1)  # Slightly longer than task1's delay
    assert mock_fetch_activities.call_count == 1, "Task1 should have executed"
    mock_fetch_activities.assert_any_call(athlete_id=12345)

    time.sleep(0.5)  # Wait for task3 to execute
    assert mock_fetch_activities.call_count == 2, "Task3 should have executed"
    mock_fetch_activities.assert_any_call(athlete_id=54321)

    time.sleep(0.5)  # Wait for task2 to execute
    assert mock_fetch_activities.call_count == 3, "Task2 should have executed"
    mock_fetch_activities.assert_any_call(athlete_id=67890)

    # Ensure all tasks executed in the correct order
    calls = [call.kwargs["athlete_id"] for call in mock_fetch_activities.mock_calls]
    expected_order = [12345, 54321, 67890]
    assert calls == expected_order, f"Expected order {expected_order}, but got {calls}"


@patch("services.core_services.task_service.fetch_athlete_activities")
def test_rate_limit_handling(mock_fetch_activities, task_service):
    """
    Test that tasks are requeued when rate limits are exceeded.
    """
    tracker = RateLimitTracker()

    def mock_fetch(athlete_id):
        RateLimitTracker().wait_if_needed()

    mock_fetch_activities.side_effect = mock_fetch

    now = datetime.now()
    headers = {
        "X-ReadRateLimit-Limit": "100,1000",
        "X-ReadRateLimit-Usage": "100,999"
    }
    tracker.update_limits(headers)
    tracker.reset_time_15_min = now + timedelta(seconds=1)

    # Create a task
    task = Task(
        athlete_id=12345,
        endpoint="https://api.strava.com/api/v3/athlete/activities",
        params={},
        task_type=TaskType.FETCH_ACTIVITIES,
        execute_after=datetime.now(),
    )

    # Submit the task
    task_service.submit_task(task)

    time.sleep(0.1)
    assert mock_fetch_activities.call_count == 1, "Task was executed too fast"
    time.sleep(1)
    assert mock_fetch_activities.call_count == 2, "Task was not executed after rate limit delay"


def test_shutdown(task_service):
    """
    Test that the TaskService shuts down gracefully.
    """
    with patch("services.core_services.task_service.logger") as mock_logger:
        task_service.shutdown()

        mock_logger.info.assert_any_call("Shutting down ApiRequestService.")
        mock_logger.info.assert_any_call("ApiRequestService shut down complete.")
