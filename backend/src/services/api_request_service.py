from concurrent.futures import ThreadPoolExecutor
import queue
from dataclasses import dataclass
import logging
from enum import Enum
import time

logger = logging.getLogger(__name__)

class TaskType(Enum):
    FETCH_ACTIVITIES = "fetch_activities"
    DUMMY_TASK = "dummy_task"

@dataclass
class Task:
    endpoint: str
    params: dict
    callback: callable
    task_type: TaskType

class ApiRequestService:
    _instance = None  # Singleton instance

    def __new__(cls, max_workers=5):
        if cls._instance is None:
            cls._instance = super(ApiRequestService, cls).__new__(cls)
            cls._instance.executor = ThreadPoolExecutor(max_workers=max_workers)
            cls._instance.task_queue = queue.Queue()
            logger.info("ApiRequestService initialized with %d workers.", max_workers)
        return cls._instance

    def submit_task(self, task: Task):
        logger.info(
            "Submitting task - Endpoint: %s, Params: %s, Callback: %s, Task Type: %s",
            task.endpoint,
            task.params,
            task.callback.__name__,
            task.task_type.value
        )

        try:
            if not isinstance(task.task_type, TaskType):
                raise ValueError(f"Invalid task type: {task.task_type}")
            if not callable(task.callback):
                raise ValueError("Callback must be callable.")

            self.executor.submit(self.process_task, task)
            logger.info("Task submitted successfully.")
        except Exception as e:
            logger.error("Failed to submit task: %s", str(e))

    def process_task(self, task: Task):
        logger.info("Processing task - %s", task)
        time.sleep(3)
        try:
            response = {"dummy_response": "success"}
            task.callback(response)
            logger.info("Task processed successfully.")
        except Exception as e:
            logger.error("Error processing task: %s", str(e))

    def shutdown(self):
        logger.info("Shutting down ApiRequestService.")
        self.executor.shutdown(wait=True)
        logger.info("ApiRequestService shut down complete.")

# Dummy Callback Function for Testing
def dummy_callback(response):
    logger.info("Dummy callback executed with response: %s", response)
