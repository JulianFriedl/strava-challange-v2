import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from services.core_services.task_service import TaskService, TaskType
from api.webhook import webhook_blueprint


@pytest.fixture(scope="function")
def app():
    """Provide a Flask app instance for testing."""
    app = Flask(__name__)
    app.register_blueprint(webhook_blueprint, url_prefix="/webhook")
    yield app


@pytest.fixture(scope="function")
def client(app):
    """Provide a test client for the Flask app."""
    return app.test_client()


@patch("services.core_services.task_service.TaskService.submit_task")
def test_create_activity_event(mock_submit_task, client):
    """
    Test that the webhook service correctly submits a task for 'create' activity events.
    """
    mock_submit_task.return_value = None

    event_payload = {
        "object_type": "activity",
        "aspect_type": "create",
        "object_id": 123456789,
        "owner_id": 987654321,
        "subscription_id": 120475,
        "event_time": 1516126040,
    }

    response = client.post("/webhook", json=event_payload)
    assert response.status_code == 200

    mock_submit_task.assert_called_once()
    submitted_task = mock_submit_task.call_args[0][0]
    assert submitted_task.athlete_id == 987654321
    assert submitted_task.params["activity_id"] == 123456789
    assert submitted_task.task_type == TaskType.HANDLE_NEW_ACTIVITY


@patch("services.core_services.task_service.TaskService.submit_task")
def test_update_activity_event(mock_submit_task, client):
    """
    Test that the webhook service correctly submits a task for 'update' activity events.
    """
    mock_submit_task.return_value = None

    event_payload = {
        "object_type": "activity",
        "aspect_type": "update",
        "object_id": 123456789,
        "owner_id": 987654321,
        "subscription_id": 120475,
        "event_time": 1516126040,
        "updates": {"title": "Morning Run"},
    }

    response = client.post("/webhook", json=event_payload)
    assert response.status_code == 200

    mock_submit_task.assert_called_once()
    submitted_task = mock_submit_task.call_args[0][0]
    assert submitted_task.athlete_id == 987654321
    assert submitted_task.params["activity_id"] == 123456789
    assert submitted_task.params["updates"] == {"title": "Morning Run"}
    assert submitted_task.task_type == TaskType.HANDLE_UPDATED_ACTIVITY


@patch("services.core_services.task_service.TaskService.submit_task")
def test_delete_activity_event(mock_submit_task, client):
    """
    Test that the webhook service correctly submits a task for 'delete' activity events.
    """
    mock_submit_task.return_value = None

    event_payload = {
        "object_type": "activity",
        "aspect_type": "delete",
        "object_id": 123456789,
        "owner_id": 987654321,
        "subscription_id": 120475,
        "event_time": 1516126040,
    }

    response = client.post("/webhook", json=event_payload)
    assert response.status_code == 200

    mock_submit_task.assert_called_once()
    submitted_task = mock_submit_task.call_args[0][0]
    assert submitted_task.athlete_id == 987654321
    assert submitted_task.params["activity_id"] == 123456789
    assert submitted_task.task_type == TaskType.HANDLE_DELETED_ACTIVITY


@patch("services.core_services.task_service.TaskService.submit_task")
def test_invalid_event(mock_submit_task, client):
    """
    Test that the webhook service does not create tasks for invalid events.
    """
    mock_submit_task.return_value = None

    event_payload = {
        "object_type": "unknown",
        "aspect_type": "create",
        "object_id": 123456789,
        "owner_id": 987654321,
        "subscription_id": 120475,
        "event_time": 1516126040,
    }

    response = client.post("/webhook", json=event_payload)
    assert response.status_code == 400
    mock_submit_task.assert_not_called()
