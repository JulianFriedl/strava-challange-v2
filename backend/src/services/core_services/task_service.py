from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import queue
from dataclasses import dataclass
import logging
from enum import Enum

from services.core_services.fetch_athlete_activities import fetch_athlete_activities

logger = logging.getLogger(__name__)


class TaskType(Enum):
    FETCH_ACTIVITIES = "fetch_activities"


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
        before=lambda retry_state: logger.warning(
            f"Attempt {retry_state.attempt_number} for function {retry_state.fn}"
        ),
        after=lambda retry_state: logger.error(
            f"Failed after attempt {retry_state.attempt_number}: {retry_state.outcome.exception()}"
        ),
    )
    def process_task(self, task: Task):
        logger.info("Processing task - %s", task)
        try:
            if task.task_type == TaskType.FETCH_ACTIVITIES:
                fetch_athlete_activities(
                    athlete_id=task.athlete_id,
                )
                logger.info(f"Finished processing FETCH_ACTIVITIES task for athlete {task.athlete_id}.")
            else:
                logger.warning(f"Unhandled task type: {task.task_type}")
        except Exception as e:
            logger.error("Error processing task: %s", str(e))
            raise

    def shutdown(self):
        logger.info("Shutting down ApiRequestService.")
        self.executor.shutdown(wait=True)
        logger.info("ApiRequestService shut down complete.")
