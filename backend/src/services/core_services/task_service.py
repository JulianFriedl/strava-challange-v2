from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import queue
from dataclasses import dataclass
import logging
from enum import Enum

from services.core_services.fetch_athlete_activities import fetch_athlete_activities
from services.core_services.handle_updated_activity import handle_updated_activity
from services.core_services.handle_updated_athlete import handle_updated_athlete
from services.core_services.handle_deleted_activiy import handle_deleted_activity
from services.core_services.handle_new_activity import handle_new_activity

logger = logging.getLogger(__name__)


class TaskType(Enum):
    FETCH_ACTIVITIES = "fetch_activities"
    HANDLE_NEW_ACTIVITY = "handle_new_activity"
    HANDLE_UPDATED_ACTIVITY = "handle_updated_activity"
    HANDLE_DELETED_ACTIVITY = "handle_deleted_activity"
    HANDLE_UPDATED_ATHLETE = "handle_updated_athlete"


@dataclass
class Task:
    athlete_id: int
    endpoint: str
    params: dict
    task_type: TaskType


class TaskService:
    _instance = None  # Singleton instance

    def __new__(cls, max_workers=5):
        if cls._instance is None:
            cls._instance = super(TaskService, cls).__new__(cls)
            cls._instance.executor = ThreadPoolExecutor(max_workers=max_workers)
            cls._instance.task_queue = queue.Queue()
            logger.info("ApiRequestService initialized with %d workers.", max_workers)
        return cls._instance

    def submit_task(self, task: Task):
        logger.info(
            "Submitting task - Athlete_id: %s Endpoint: %s, Params: %s, Task Type: %s",
            task.athlete_id,
            task.endpoint,
            task.params,
            task.task_type.value
        )

        if not isinstance(task.task_type, TaskType):
            logger.error(f"Invalid task type: {task.task_type}")
            return

        self.executor.submit(self.process_task, task)
        logger.info("Task submitted successfully.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        before=lambda retry_state: logger.info(
            f"Attempt {retry_state.attempt_number} for function {retry_state.fn}"
        ),
        after=lambda retry_state: logger.error(
            f"Failed after attempt {retry_state.attempt_number}: {retry_state.outcome.exception()}"
        ),
    )
    #TODO: handle the case where all workers are blocked because of RatelimitTracker
    # and a non rate limited tasks execution gets blocked because the other workers
    # are waiting on the RatelimitTracker.
    # possible requeue task execution instead of sleeping in RatelimitTracker, and
    # then check in process task if the ratelimit has been reset yet before re-executing
    def process_task(self, task: Task):
        logger.info("Processing task - %s", task)
        try:
            if task.task_type == TaskType.FETCH_ACTIVITIES:
                fetch_athlete_activities(athlete_id=task.athlete_id)
                logger.info(f"Finished processing FETCH_ACTIVITIES task for athlete {task.athlete_id}.")

            elif task.task_type == TaskType.HANDLE_NEW_ACTIVITY:
                activity_id = task.params.get("activity_id")
                if not activity_id:
                    logger.error("Missing 'activity_id' in params for HANDLE_NEW_ACTIVITY.")
                    return
                handle_new_activity(activity_id, task.athlete_id)
                logger.info(f"Handled new activity: {task.params}")

            elif task.task_type == TaskType.HANDLE_UPDATED_ACTIVITY:
                activity_id = task.params.get("activity_id")
                updates = task.params.get("updates")
                if not activity_id or updates is None:
                    logger.error("Missing 'activity_id' or 'updates' in params for HANDLE_UPDATED_ACTIVITY.")
                    return
                handle_updated_activity(activity_id, updates)
                logger.info(f"Handled updated activity: {task.params}")

            elif task.task_type == TaskType.HANDLE_DELETED_ACTIVITY:
                activity_id = task.params.get("activity_id")
                if not activity_id:
                    logger.error("Missing 'activity_id' in params for HANDLE_DELETED_ACTIVITY.")
                    return
                handle_deleted_activity(activity_id)
                logger.info(f"Handled deleted activity: {task.params}")

            elif task.task_type == TaskType.HANDLE_UPDATED_ATHLETE:
                updates = task.params.get("updates")
                if updates is None:
                    logger.error("Missing 'updates' in params for HANDLE_UPDATED_ATHLETE.")
                    return
                handle_updated_athlete(task.athlete_id, updates)
                logger.info(f"Handled updated athlete: {task.params}")

            else:
                logger.warning(f"Unhandled task type: {task.task_type}")
        except Exception as e:
            logger.error("Error processing task: %s", str(e))
            raise

    def shutdown(self):
        logger.info("Shutting down ApiRequestService.")
        self.executor.shutdown(wait=True)
        logger.info("ApiRequestService shut down complete.")
