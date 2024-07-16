import unittest
from unittest.mock import MagicMock, patch
import logging
import json

from src.charging_stations_status import ChargingStationsStatus
from src.charging_stations_tracker import ChargingStationsStatusTracker
from src.site_status import SiteStatus
from src.charging_stations_status import Charger, Connector  # Import these classes if they exist in the same module

class TestChargingStationsStatusTracker(unittest.TestCase):
    @patch('src.charging_stations_status.ChargingStationsStatus.from_json')
    @patch('src.site_status.SiteStatus.from_json')
    @patch('src.redis_handler.RedisHandler', autospec=True)
    def test_integration_with_status_changes(self, mock_redis_handler, mock_site_status_from_json,
                                             mock_charging_stations_status_from_json):
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Starting test_integration_with_status_changes")

        # Mock RedisHandler instance
        redis_handler = mock_redis_handler.return_value

        # Mock RedisHandler responses for status data
        redis_handler.get_value.side_effect = [
            '{"chargers": [{"connectors": [{"id": 1, "status": "online"}], "id": "charger1"}]}',
            '{"evs": [{"charger_id": "charger1", "status": "online"}]}',
            '{"chargers": [{"connectors": [{"id": 1, "status": "available"}], "id": "charger1"}]}',
            '{"evs": [{"charger_id": "charger1", "status": "available"}]}',
            '{"chargers": [{"connectors": [{"id": 1, "status": "charging"}], "id": "charger1"}]}',
            '{"evs": [{"charger_id": "charger1", "status": "charging"}]}',
            '{"chargers": [{"connectors": [{"id": 1, "status": "offline"}], "id": "charger1"}]}',
            '{"evs": [{"charger_id": "charger1", "status": "offline"}]}'
        ]

        # Create mock objects for status
        def create_mock_status(charger_status, ev_status):
            mock_charging_status = MagicMock(spec=ChargingStationsStatus)
            mock_site_status = MagicMock(spec=SiteStatus)
            mock_charger = MagicMock()
            mock_charger.connectors = [MagicMock(id=1, status=charger_status)]
            mock_charging_status.chargers = [mock_charger]
            mock_charging_status.ocpp_error = 'NoError'
            mock_charging_status.ocpp_error_code = 'NoError'
            mock_charging_status.priority = False
            mock_ev = MagicMock()
            mock_ev.charger_id = "charger1"
            mock_ev.status = ev_status
            mock_site_status.evs = [mock_ev]
            return mock_charging_status, mock_site_status

        # Set up mock returns for each call
        mock_charging_stations_status_from_json.side_effect = [
            create_mock_status("online", "online")[0],
            create_mock_status("available", "available")[0],
            create_mock_status("charging", "charging")[0],
            create_mock_status("offline", "offline")[0]
        ]
        mock_site_status_from_json.side_effect = [
            create_mock_status("online", "online")[1],
            create_mock_status("available", "available")[1],
            create_mock_status("charging", "charging")[1],
            create_mock_status("offline", "offline")[1]
        ]

        tracker = ChargingStationsStatusTracker(redis_handler)

        # Simulate multiple calls to get_derivative to ensure it captures status changes
        for i in range(4):  # Four iterations to simulate status changes
            logging.debug(f"Iteration {i}")
            derivative = tracker.get_derivative()
            logging.debug(f"Derivative: {derivative}")

        # Assert the derivative output
        self.assertIsNotNone(derivative)
        self.assertIn('status_diff', derivative)
        self.assertIn('site_status_diff', derivative)
        self.assertIn('events', derivative)
        self.assertIsInstance(derivative['events'], list)
        self.assertGreaterEqual(len(derivative['events']), 1)

    @patch('src.charging_stations_status.ChargingStationsStatus.from_json')
    @patch('src.site_status.SiteStatus.from_json')
    @patch('src.redis_handler.RedisHandler', autospec=True)
    def test_critical_error_pattern(self, mock_redis_handler, mock_site_status_from_json,
                                    mock_charging_stations_status_from_json):
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Starting test_critical_error_pattern")

        # Mock RedisHandler instance
        redis_handler = mock_redis_handler.return_value

        # Mock RedisHandler responses for critical error pattern
        redis_handler.get_value.side_effect = [
            '{"chargers": [{"connectors": [{"id": 1, "status": "online"}], "id": "charger1"}]}',
            '{"evs": [{"charger_id": "charger1", "status": "online"}]}',
            '{"chargers": [{"connectors": [{"id": 1, "status": "available"}], "id": "charger1"}]}',
            '{"evs": [{"charger_id": "charger1", "status": "available"}]}',
            '{"chargers": [{"connectors": [{"id": 1, "status": "charging"}], "id": "charger1"}]}',
            '{"evs": [{"charger_id": "charger1", "status": "charging"}]}',
            '{"chargers": [{"connectors": [{"id": 1, "status": "charging"}], "id": "charger1"}]}',
            '{"evs": [{"charger_id": "charger1", "status": "charging"}]}',
            '{"chargers": [{"connectors": [{"id": 1, "status": "suspended_ev"}], "id": "charger1"}]}',
            '{"evs": [{"charger_id": "charger1", "status": "suspended_ev"}]}',
            '{"chargers": [{"connectors": [{"id": 1, "status": "offline"}], "id": "charger1"}]}',
            '{"evs": [{"charger_id": "charger1", "status": "offline"}]}'
        ]

        # Create mock objects for status
        def create_mock_status(charger_status, ev_status):
            mock_charging_status = MagicMock(spec=ChargingStationsStatus)
            mock_site_status = MagicMock(spec=SiteStatus)
            mock_charger = MagicMock()
            mock_charger.connectors = [MagicMock(id=1, status=charger_status)]
            mock_charging_status.chargers = [mock_charger]
            mock_ev = MagicMock()
            mock_ev.charger_id = "charger1"
            mock_ev.status = ev_status
            mock_site_status.evs = [mock_ev]
            return mock_charging_status, mock_site_status

        # Set up mock returns for each call
        mock_charging_stations_status_from_json.side_effect = [
            create_mock_status("online", "online")[0],
            create_mock_status("available", "available")[0],
            create_mock_status("charging", "charging")[0],
            create_mock_status("charging", "charging")[0],
            create_mock_status("suspended_ev", "suspended_ev")[0],
            create_mock_status("offline", "offline")[0]
        ]
        mock_site_status_from_json.side_effect = [
            create_mock_status("online", "online")[1],
            create_mock_status("available", "available")[1],
            create_mock_status("charging", "charging")[1],
            create_mock_status("charging", "charging")[1],
            create_mock_status("suspended_ev", "suspended_ev")[1],
            create_mock_status("offline", "offline")[1]
        ]

        tracker = ChargingStationsStatusTracker(redis_handler)

        # Simulate multiple calls to get_derivative to ensure it captures status changes
        for i in range(6):  # Six iterations to simulate critical error pattern
            logging.debug(f"Iteration {i}")
            derivative = tracker.get_derivative()
            logging.debug(f"Derivative: {derivative}")

        # Assert the derivative output
        self.assertIsNotNone(derivative)
        self.assertIn('status_diff', derivative)
        self.assertIn('site_status_diff', derivative)
        self.assertIn('events', derivative)
        self.assertIsInstance(derivative['events'], list)

        # Check for critical error event
        critical_error_detected = any(
            event.get('status') == 'critical_error_detected' for event in derivative['events']
        )

        self.assertTrue(critical_error_detected)

        # Log the critical error patterns and their count
        if critical_error_detected:
            logging.error("Critical error patterns detected")
            critical_error_count = sum(1 for event in derivative['events'] if event.get('status') == 'critical_error_detected')
            logging.error(f"Number of critical error patterns: {critical_error_count}")
            self.assertGreater(critical_error_count, 0)

if __name__ == '__main__':
    unittest.main()
