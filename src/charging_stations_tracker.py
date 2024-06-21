import json
import time
import logging
from src.charging_stations_status import ChargingStationsStatus
from collections import deque
from datetime import datetime, timedelta
from statsd import StatsClient
from src.redis_handler import RedisHandler


class ChargingStationsStatusTracker:
    def __init__(self, redis_handler, key='cgw/ChargingStationsStatus'):
        self.redis_handler = redis_handler
        self.key = key
        self.previous_status = None
        self.previous_time = time.time()

    def get_derivative(self):
        current_time = time.time()
        current_status_json = self.redis_handler.get_value(self.key)
        current_status = ChargingStationsStatus.from_json(
            json.loads(current_status_json)) if current_status_json else None

        if self.previous_status is None or current_status is None:
            self.previous_status = current_status
            self.previous_time = current_time
            return None

        time_diff = current_time - self.previous_time
        # Define a method to calculate the difference between current and previous status
        status_diff = self._calculate_status_diff(current_status, self.previous_status)

        self.previous_status = current_status
        self.previous_time = current_time

        if time_diff == 0:
            return None
        return status_diff / time_diff

    def _calculate_status_diff(self, current_status, previous_status):
        # This function should compare the current and previous status and return the difference
        # Placeholder implementation
        return len(current_status.chargers) - len(previous_status.chargers)


class SlidingTimeWindow:
    def __init__(self, interval_minutes=5):
        self.interval = timedelta(minutes=interval_minutes)
        self.data = deque()

    def add_log(self, log):
        current_time = datetime.now()
        self.data.append((current_time, log))
        self._remove_old_logs(current_time)

    def _remove_old_logs(self, current_time):
        while self.data and current_time - self.data[0][0] > self.interval:
            self.data.popleft()

    def get_logs(self):
        return [log for timestamp, log in self.data]


class CriticalErrorPatternDetector:
    def __init__(self):
        self.patterns = []

    def analyze_logs(self, logs):
        error_patterns = []
        for i in range(len(logs) - 1):
            current_log = logs[i]
            next_log = logs[i + 1]
            if self.is_critical_error(current_log, next_log):
                error_patterns.append((current_log, next_log))
        self.patterns = error_patterns
        print(f"Detected error patterns: {self.patterns}")  # Debug information
        return error_patterns

    def is_critical_error(self, log1, log2):
        # Check if the logs are for the same charger and connector and have specific statuses
        return (log1['event']['charger_id'] == log2['event']['charger_id'] and
                log1['event']['connector_id'] == log2['event']['connector_id'] and
                log1['event']['status'] == 'suspended_ev' and
                log2['event']['status'] == 'finishing')


class CustomMetrics:
    def __init__(self, host='localhost', port=8125):
        self.statsd = StatsClient(host, port)

    def report_critical_error(self, count):
        self.statsd.gauge('critical_error_patterns', count)


def monitor_system():
    redis_handler = RedisHandler()
    status_tracker = ChargingStationsStatusTracker(redis_handler)
    time_window = SlidingTimeWindow(interval_minutes=5)
    error_detector = CriticalErrorPatternDetector()
    metrics = CustomMetrics()

    while True:
        derivative = status_tracker.get_derivative()
        if derivative is not None and isinstance(derivative, dict) and 'event' in derivative:
            # Ensure derivative is in the expected format before constructing log
            log = {'timestamp': time.time(), 'event': derivative['event']}
            time_window.add_log(log)
            error_patterns = error_detector.analyze_logs(time_window.get_logs())
            metrics.report_critical_error(len(error_patterns))
            if error_patterns:
                logging.error(f"Critical error patterns detected: {len(error_patterns)}")
                # Add alerting mechanism here, e.g., send email or SMS notification

        time.sleep(10)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor_system()
