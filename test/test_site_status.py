import unittest
from unittest.mock import Mock
from io import StringIO

from datetime import datetime
from tabulate import tabulate

# Correct import paths
from src.charging_stations_status import ChargingStationsStatus
from src.dnmasq_leases import DnsmasqLeases
from src.site_status import SiteStatus

class TestSiteStatus(unittest.TestCase):
    def test_display(self):
        # Mock objects for DnsmasqLeases and ChargingStationsStatus
        dnsmasq_leases = Mock(spec=DnsmasqLeases)
        dnsmasq_leases.get_mac_from_ip.side_effect = lambda ip: '00:00:00:00:00:00' if ip else None
        dnsmasq_leases.get_lease_time_from_ip.side_effect = lambda ip: '2024-05-28 12:00:00' if ip else None

        charging_stations_status = Mock(spec=ChargingStationsStatus)
        charging_stations_status.get_ip_from_charger_id.side_effect = lambda charger_id: f'192.168.1.{charger_id}'
        charging_stations_status.display.return_value = 'Charging Stations Status Display'

        # Sample data for testing
        charging_stations = [{'id': 1, 'name': 'Station 1'}, {'id': 2, 'name': 'Station 2'}]
        datetime_str = '2024-05-28 12:00:00'
        evs = [{'id': 1, 'charger_id': 1, 'status': 'Charging', 'start_charging_time': '2024-05-28T12:00:00.000+0000'},
               {'id': 2, 'charger_id': 2, 'status': 'Idle', 'start_charging_time': None}]
        offline_chargers = [{'id': 3, 'name': 'Offline Charger'}]

        # Creating a SiteStatus object
        site_status = SiteStatus(charging_stations, datetime_str, evs, offline_chargers)

        # Expected output
        expected_output = StringIO()
        print("Site Status:", file=expected_output)
        print(f"Action: response", file=expected_output)
        print(f"DateTime: {datetime_str}", file=expected_output)
        print("\nChargers:", file=expected_output)
        headers = ["ID", "Status", "IP", "MAC", "Leased until"]
        chargers_with_ip = [
            (1, 'Online', '192.168.1.1', '00:00:00:00:00:00', '2024-05-28 12:00:00'),
            (2, 'Online', '192.168.1.2', '00:00:00:00:00:00', '2024-05-28 12:00:00'),
            (3, 'OFFLINE', '192.168.1.3', '00:00:00:00:00:00', '2024-05-28 12:00:00')
        ]
        print(tabulate(chargers_with_ip, headers=headers, tablefmt="psql"), file=expected_output)
        print("\nConnections:", file=expected_output)
        print(charging_stations_status.display(), file=expected_output)
        print("\nElectric Vehicles:", file=expected_output)
        headers = ["ID", "Chg-ID", "Status", "Chg-Current", "Chg-Offer", "Chg-Fw.", "Sess.E", "Start Chg."]
        data = [
            [1, 1, 'Charging', None, None, None, None, '240528_1200'],
            [2, 2, 'Idle', None, None, None, None, 'UNKNOWN']
        ]
        print(tabulate(data, headers=headers, tablefmt="psql", stralign="left"), file=expected_output)
        expected_output_str = expected_output.getvalue()

        # Actual output
        actual_output = site_status.display(dnsmasq_leases, charging_stations_status)

        # Asserting the outputs
        self.assertEqual(actual_output, expected_output_str)

if __name__ == '__main__':
    unittest.main()
