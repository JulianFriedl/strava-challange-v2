import logging

from services.core_services.task_service import TaskService, TaskType, Task
from api.exceptions import ParamError

logger = logging.getLogger(__name__)

def process_activity_event(event):
    """Process incoming activity event."""
    object_type = event.get("object_type")
    aspect_type = event.get("aspect_type")
    object_id = event.get("object_id")
    owner_id = event.get("owner_id")
    updates = event.get("updates", {})

    task_service = TaskService()

    if object_type == "activity":
        if aspect_type == "create":
            task_service.submit_task(
                Task(
                    athlete_id=owner_id,
                    endpoint="activity/create",
                    params={"activity_id": object_id},
                    task_type=TaskType.HANDLE_NEW_ACTIVITY,
                )
            )
        elif aspect_type == "update":
            task_service.submit_task(
                Task(
                    athlete_id=owner_id,
                    endpoint="activity/update",
                    params={
                        "activity_id": object_id,
                        "updates": updates,
                    },
                    task_type=TaskType.HANDLE_UPDATED_ACTIVITY,
                )
            )
        elif aspect_type == "delete":
            task_service.submit_task(
                Task(
                    athlete_id=owner_id,
                    endpoint="activity/delete",
                    params={"activity_id": object_id},
                    task_type=TaskType.HANDLE_DELETED_ACTIVITY,
                )
            )
        else:
            raise ParamError(f"Unknown aspect type for activity: {aspect_type}")
    elif object_type == "athlete":
        task_service.submit_task(
            Task(
                athlete_id=owner_id,
                endpoint="athlete/event",
                params={
                    "event_time": event.get("event_time"),
                    "updates": updates,
                },
                task_type=TaskType.OTHER_EVENT,
            )
        )
    else:
        raise ParamError(f"Unsupported object type: {object_type}")
