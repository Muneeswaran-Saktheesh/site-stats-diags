import json
import time
import logging
from collections import deque
from datetime import datetime, timedelta
from statsd import StatsClient
from src.redis_handler import RedisHandler
from src.charging_stations_status import ChargingStationsStatus
from src.site_status import SiteStatus

class ChargingStationsStatusTracker:
    def __init__(self, redis_handler, charging_station_key='cgw/ChargingStationsStatus', site_status_key='cgw/SiteStatus'):
        self.redis_handler = redis_handler
        self.charging_station_key = charging_station_key
        self.site_status_key = site_status_key
        self.previous_charging_station_status = None
        self.previous_site_status = None
        self.previous_time = time.time()

    def get_derivative(self):
        current_time = time.time()
        current_charging_station_status_json = self.redis_handler.get_value(self.charging_station_key)
        logging.debug(f"Current charging station status JSON: {current_charging_station_status_json}")

        try:
            current_charging_station_status = ChargingStationsStatus.from_json(json.loads(current_charging_station_status_json)) if current_charging_station_status_json else None
        except (json.JSONDecodeError, TypeError) as e:
            logging.error(f"Failed to parse current charging station status JSON: {e}")
            current_charging_station_status = None

        current_site_status_json = self.redis_handler.get_value(self.site_status_key)
        logging.debug(f"Current site status JSON: {current_site_status_json}")

        try:
            current_site_status = SiteStatus.from_json(json.loads(current_site_status_json)) if current_site_status_json else None
        except (json.JSONDecodeError, TypeError) as e:
            logging.error(f"Failed to parse current site status JSON: {e}")
            current_site_status = None

        if self.previous_charging_station_status is None or current_charging_station_status is None:
            self.previous_charging_station_status = current_charging_station_status
            self.previous_site_status = current_site_status
            self.previous_time = current_time
            logging.debug("Previous status is None, setting current status as previous and returning None")
            return None

        status_charging_station_diff = self._calculate_status_diff(current_charging_station_status, self.previous_charging_station_status)
        status_site_diff = self._calculate_site_status_diff(current_site_status, self.previous_site_status)

        logging.debug(f"Status differences calculated: {status_charging_station_diff}, {status_site_diff}")

        events = self._detect_events(current_charging_station_status, self.previous_charging_station_status)

        self.previous_charging_station_status = current_charging_station_status
        self.previous_site_status = current_site_status
        self.previous_time = current_time

        return {
            'status_diff': status_charging_station_diff,
            'site_status_diff': status_site_diff,
            'events': events
        }

    def _calculate_status_diff(self, current_status, previous_status):
        if current_status is None or previous_status is None:
            return 0

        current_connector_status = self._get_connector_status(current_status)
        previous_connector_status = self._get_connector_status(previous_status)

        status_diff = []
        for current, previous in zip(current_connector_status, previous_connector_status):
            if current != previous:
                status_diff.append(1)
            else:
                status_diff.append(0)
        logging.debug(f"Status diff: {status_diff}")
        return sum(status_diff)

    def _get_connector_status(self, status):
        if status is None or not status.chargers:
            return []

        return [connector.status for charger in status.chargers for connector in charger.connectors]

    def _calculate_site_status_diff(self, current_status, previous_status):
        if current_status is None or previous_status is None:
            return 0

        current_ev_status = self._get_ev_status(current_status)
        previous_ev_status = self._get_ev_status(previous_status)

        ev_status_diff = []
        for current_ev, previous_ev in zip(current_ev_status, previous_ev_status):
            if current_ev != previous_ev:
                ev_status_diff.append(1)
            else:
                ev_status_diff.append(0)
        logging.debug(f"EV status diff: {ev_status_diff}")
        return sum(ev_status_diff)

    def _get_ev_status(self, status):
        if status is None or not status.evs:
            return []

        return [(ev.charger_id, ev.status) for ev in status.evs]

    def _detect_events(self, current_status, previous_status):
        events = []
        for current_charger, previous_charger in zip(current_status.chargers, previous_status.chargers):
            for current_connector, previous_connector in zip(current_charger.connectors, previous_charger.connectors):
                if current_connector.status != previous_connector.status:
                    event = {
                        'timestamp': datetime.utcnow().isoformat(),
                        'charger_id': current_charger.id,
                        'connector_id': current_connector.id,
                        'status': current_connector.status
                    }
                    logging.debug(f"Event generated: {event}")
                    events.append(event)

                    # Detect critical error pattern
                    if current_connector.status == 'offline' and previous_connector.status == 'suspended_ev':
                        critical_event = {
                            'timestamp': datetime.utcnow().isoformat(),
                            'charger_id': current_charger.id,
                            'connector_id': current_connector.id,
                            'status': 'critical_error_detected'
                        }
                        logging.debug(f"Critical error detected: {critical_event}")
                        events.append(critical_event)
        return events


class SlidingTimeWindow:
    def __init__(self, interval_minutes=5):
        self.interval = timedelta(minutes=interval_minutes)
        self.data = deque()

    def add_log(self, log):
        current_time = datetime.utcnow()
        self.data.append((current_time, log))
        self._remove_old_logs(current_time)
        logging.debug(f"Log added: {log}")

    def _remove_old_logs(self, current_time):
        while self.data and current_time - self.data[0][0] > self.interval:
            logging.debug(f"Removing old log: {self.data[0]}")
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
                logging.debug(f"Critical error pattern detected: {current_log} -> {next_log}")
        logging.debug(f"Total critical error patterns detected: {len(error_patterns)}")
        return error_patterns

    def is_critical_error(self, log1, log2):
        is_critical = (log1['event']['charger_id'] == log2['event']['charger_id'] and
                       log1['event']['connector_id'] == log2['event']['connector_id'] and
                       log1['event']['status'] == 'suspended_ev' and
                       log2['event']['status'] == 'offline')
        logging.debug(f"Comparing logs: {log1['event']} <-> {log2['event']} -> Is Critical: {is_critical}")
        return is_critical


class CustomMetrics:
    def __init__(self, host='localhost', port=8125):
        self.statsd = StatsClient(host, port)
        logging.debug(f"CustomMetrics initialized with host={host} port={8125}")

    def report_critical_error(self, count):
        logging.debug(f"Reporting critical error count: {count}")
        self.statsd.gauge('critical_error_patterns', count)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)  # Change to DEBUG level to see detailed logs
    redis_handler = RedisHandler()
    status_tracker = ChargingStationsStatusTracker(redis_handler)
    time_window = SlidingTimeWindow(interval_minutes=5)
    error_detector = CriticalErrorPatternDetector()
    metrics = CustomMetrics()

    while True:
        derivative = status_tracker.get_derivative()
        logging.debug(f"Main loop derivative: {derivative}")
        if derivative is not None and isinstance(derivative, dict) and 'events' in derivative:
            for event in derivative['events']:
                log = {'timestamp': time.time(), 'event': event}
                logging.debug(f"Log added: {log}")
                time_window.add_log(log)
                error_patterns = error_detector.analyze_logs(time_window.get_logs())
                logging.debug(f"Detected error patterns: {error_patterns}")
                metrics.report_critical_error(len(error_patterns))
                logging.debug(f"Reported {len(error_patterns)} critical error patterns")
                if error_patterns:
                    logging.error(f"Critical error patterns detected: {len(error_patterns)}")
                    # Add alerting mechanism here, e.g., send email or SMS notification

        time.sleep(10)
