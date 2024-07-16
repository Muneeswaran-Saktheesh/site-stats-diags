import json
import time
import logging
from datetime import datetime
from src.charging_stations_status import ChargingStationsStatus
from src.charging_stations_tracker import ChargingStationsStatusTracker, SlidingTimeWindow, \
    CriticalErrorPatternDetector, CustomMetrics
from src.redis_handler import RedisHandler
from src.terminal_screen import TerminalScreen

class Command:
    def __init__(self, cmds, terminal_screen: TerminalScreen):
        self.cmds = cmds
        self.terminal_screen = terminal_screen
        self.redis_handler = RedisHandler()
        self.key_charging_stations = 'cgw/ChargingStationsStatus'
        self.time_window = SlidingTimeWindow(interval_minutes=5)
        self.error_detector = CriticalErrorPatternDetector()
        self.metrics = CustomMetrics()
        self.status_tracker = ChargingStationsStatusTracker(self.redis_handler)

    def execute(self) -> None:
        while True:
            try:
                derivative = self.status_tracker.get_derivative()
                logging.debug(f"Derivative: {derivative}")

                if derivative is not None and 'event' in derivative:
                    event = derivative['event']
                    log = {
                        'timestamp': datetime.now().isoformat(),
                        'event': event.to_json()  # Assuming 'event' is a ChargingStationsStatus object
                    }
                    self.time_window.add_log(log)

                    error_patterns = self.error_detector.analyze_logs(self.time_window.get_logs())
                    self.metrics.report_critical_error(len(error_patterns))
                    if error_patterns:
                        logging.error(f"Critical error patterns detected: {len(error_patterns)}")
                        # Add alerting mechanism here, e.g., send email or SMS notification

                    # Display the current status on the terminal screen
                    self.terminal_screen.display(self.get_current_status_display())

                time.sleep(10)

            except Exception as e:
                logging.error(f"Error during monitoring: {e}")
                break  # Exit the loop on error

    def get_current_status_display(self) -> str:
        try:
            charging_stations_status_json = self.redis_handler.get_value(self.key_charging_stations)
            if charging_stations_status_json is not None:
                charging_stations_status_dict = json.loads(charging_stations_status_json)
                charging_stations_status = ChargingStationsStatus.from_json(charging_stations_status_dict)
                return charging_stations_status.display()
        except Exception as e:
            logging.error(f"Error retrieving current status: {e}")
        return "No data available."

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cmds = None  # Define commands if needed
    terminal_screen = TerminalScreen()  # Assuming TerminalScreen is properly defined
    command = Command(cmds, terminal_screen)
    command.execute()

