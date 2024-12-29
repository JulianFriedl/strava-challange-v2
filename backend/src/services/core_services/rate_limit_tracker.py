from datetime import datetime, timedelta
import threading
import time
import logging

logger = logging.getLogger(__name__)

# TODO: currently the rate limit tracker only tracks the read limit, but the
# general limit is higher than the read limit, this might block and api request
# that isn't a get request if the read limit is reached but the general isnt reached.
class RateLimitTracker:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RateLimitTracker, cls).__new__(cls)
            cls._instance.lock = threading.Lock()
            cls._instance.limit_15_min = 200
            cls._instance.limit_daily = 1000
            cls._instance.requests_15_min = 0
            cls._instance.requests_daily = 0
            cls._instance.reset_time_15_min = cls.calculate_next_15_min_reset()
            cls._instance.reset_time_daily = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            logger.info("RateLimitTracker initialized with default limits: 15-min=%d, daily=%d",
                        cls._instance.limit_15_min, cls._instance.limit_daily)
        return cls._instance

    @staticmethod
    def calculate_next_15_min_reset():
        now = datetime.utcnow()
        reset_minute = (now.minute // 15 + 1) * 15
        if reset_minute == 60:
            reset_minute = 0
            now += timedelta(hours=1)
        return now.replace(minute=reset_minute, second=0, microsecond=0)

    def update_limits(self, headers):
        """Update rate limits and usage directly from API response headers."""
        with self.lock:
            self.limit_15_min = int(headers.get("X-ReadRateLimit-Limit", "200").split(",")[0])
            self.limit_daily = int(headers.get("X-ReadRateLimit-Limit", "1000").split(",")[1])
            self.requests_15_min = int(headers.get("X-ReadRateLimit-Usage", "0").split(",")[0])
            self.requests_daily = int(headers.get("X-ReadRateLimit-Usage", "0").split(",")[1])

            logger.info("Rate limits updated: 15-min=%d/%d, daily=%d/%d",
                        self.requests_15_min, self.limit_15_min,
                        self.requests_daily, self.limit_daily)

    def wait_if_needed(self):
        """Pause execution if rate limits are close to being exceeded."""
        with self.lock:
            now = datetime.utcnow()

            # Update reset times dynamically
            if now >= self.reset_time_15_min:
                self.reset_time_15_min = self.calculate_next_15_min_reset()
                self.requests_15_min = 0
                logger.info("15-minute rate limit reset.")

            if now >= self.reset_time_daily:
                self.reset_time_daily = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                self.requests_daily = 0
                logger.info("Daily rate limit reset.")

            # Calculate required sleep times
            sleep_time_15_min = (self.reset_time_15_min - now).total_seconds() if self.requests_15_min >= self.limit_15_min else 0
            sleep_time_daily = (self.reset_time_daily - now).total_seconds() if self.requests_daily >= self.limit_daily else 0

            if sleep_time_15_min > 0 or sleep_time_daily > 0:
                sleep_time = max(sleep_time_15_min, sleep_time_daily)
                logger.warning(f"Rate limit reached. Pausing for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
