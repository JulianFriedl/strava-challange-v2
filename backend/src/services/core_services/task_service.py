from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import queue
from dataclasses import dataclass
import logging
from enum import Enum
from datetime import datetime, timedelta
import threading
import heapq

from api.exceptions import RateLimitExceededException

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
    execute_after: datetime = None


# TODO: Revisit TaskService singleton implementation.
# Currently using a single Gunicorn process with multiple threads to ensure shared state.
# Consider implementing a centralized task queue (e.g., Redis, RabbitMQ), or implement it
# as a seperate Microservice for scalability and true singleton behavior across processes.
class TaskService:
    _instance = None  # Singleton instance

    def __new__(cls, max_workers=3):
        if cls._instance is None:
            cls._instance = super(TaskService, cls).__new__(cls)
            cls._instance.executor = ThreadPoolExecutor(max_workers=max_workers)
            cls._instance.task_queue = []
            cls._instance.queue_lock = threading.Lock()  # Protect task_queue
            cls._instance.active_timer = None  # Track the active timer for scheduling
            logger.info("ApiRequestService initialized with %d workers.", max_workers)
        return cls._instance

    def submit_task(self, task: Task):
        execute_after = task.execute_after or datetime.now()

        logger.info(
            "Submitting task - Athlete_id: %s Endpoint: %s, Params: %s, Task Type: %s, Execute After: %s",
            task.athlete_id,
            task.endpoint,
            task.params,
            task.task_type.value,
            execute_after,
        )

        with self.queue_lock:
            execute_after = task.execute_after or datetime.now()
            # heapq sorts the task_queue by its execute_after
            # it sorts based on the first element of the tuple
            heapq.heappush(self.task_queue, (execute_after, task))
        self.executor.submit(self.process_queue)
        logger.info("Task submitted successfully.")

    # TODO: simplify design pattern. Currently:
    # Requeue the task and sleep until the next execution time
    # This design leverages a mix of a loop (to process all ready tasks)
    # and a timer (to wait for future tasks without busy-waiting).
    # It's somewhat complex because we combine immediate execution
    # and delayed scheduling in the same flow.
    def process_queue(self):
        while True:
            with self.queue_lock:
                if not self.task_queue:
                    return

                execute_after, task = heapq.heappop(self.task_queue)
                now = datetime.now()

                if execute_after > now:
                    # Requeue the task and sleep until the next execution time
                    heapq.heappush(self.task_queue, (execute_after, task))
                    delay = (execute_after - now).total_seconds()
                    logger.info(
                        "Task requeued - Athlete_id: %s, Task Type: %s, Execute After: %s, Delay: %.2f seconds",
                        task.athlete_id,
                        task.task_type.value,
                        execute_after,
                        delay,
                    )
                    threading.Timer(delay, self.process_queue).start()
                    return  # return since there are no tasks that can be exec before execute_after

            # Process the task outside the lock
            self.process_task(task)

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
        except RateLimitExceededException as e:
            logger.warning(f"Requeuing task due to rate limit: Athlete_id={task.athlete_id}, Delay={e.delay:.2f} seconds")
            # Requeue the task with the delay as the new execute_after time
            task.execute_after = datetime.now() + timedelta(seconds=e.delay)
            self.submit_task(task)
        except Exception as e:
            logger.error("Error processing task: %s", str(e))
            raise

    def shutdown(self):
        logger.info("Shutting down ApiRequestService.")
        self.executor.shutdown(wait=True)
        logger.info("ApiRequestService shut down complete.")
