import json
import time
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

        # Email settings
        self.smtp_server = 'smtp.example.com'
        self.smtp_port = 587
        self.sender_email = 'alert@example.com'
        self.sender_password = 'your_password'
        self.recipient_email = 'recipient@example.com'

    def execute(self) -> str:
        while True:
            try:
                derivative = self.status_tracker.get_derivative()
                if derivative is not None:
                    log = {
                        'timestamp': datetime.now().isoformat(),
                        'event': derivative
                    }
                    self.time_window.add_log(log)
                    error_patterns = self.error_detector.analyze_logs(self.time_window.get_logs())
                    self.metrics.report_critical_error(len(error_patterns))
                    if error_patterns:
                        logging.error(f"Critical error patterns detected: {len(error_patterns)}")
                        self.send_email_alert(len(error_patterns))

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
                charging_stations_status = json.loads(charging_stations_status_json)
                charging_stations_status = ChargingStationsStatus.from_json(charging_stations_status)
                return charging_stations_status.display()
        except Exception as e:
            logging.error(f"Error retrieving current status: {e}")
        return "No data available."

    def send_email_alert(self, error_count):
        subject = "Critical Error Pattern Detected in Charging Stations"
        body = f"Critical error patterns detected: {error_count} patterns.\nPlease investigate the issue immediately."

        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = self.recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, message.as_string())
            logging.info("Email alert sent successfully")
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cmds = None  # Define commands if needed
    terminal_screen = TerminalScreen()  # Assuming TerminalScreen is properly defined
    command = Command(cmds, terminal_screen)
    command.execute()
