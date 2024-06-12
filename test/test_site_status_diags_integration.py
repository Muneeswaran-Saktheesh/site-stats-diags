import json
import unittest
from unittest.mock import patch, MagicMock
import fakeredis
from src.charging_stations_status import ChargingStationsStatus
from src.site_status_diags import main
from src.dnsmasq_leases import DnsmasqLeases
from src.redis_handler import RedisHandler


class TestSiteStatusDiagsIntegration(unittest.TestCase):

    @patch('src.redis_handler.redis.StrictRedis', fakeredis.FakeStrictRedis)
    @patch('src.site_status.SiteStatus.display')
    def test_end_to_end_integration(self, mock_display):
        # Setup test data
        site_status_data = {"status": "active", "error": None}
        charging_status_data = {"chargers": []}
        dns_leases_data = """1711017257 3a:67:30:61:1d:26 172.22.0.20 * *
1711014315 3e:62:72:79:77:4b 172.22.0.139 * *
1711014277 0e:67:34:61:29:24 172.22.0.106 * *
1711009266 26:67:13:61:02:26 172.22.0.83 * *
1711006594 26:67:21:61:02:26 172.22.0.87 * *
1710876885 2e:60:5e:72:7d:50 172.22.0.30 * *
1710922775 3a:67:24:61:1d:26 172.22.0.89 * *
1710748030 3e:61:4f:73:02:3d 172.22.0.220 * *"""

        # Create a single instance of DnsmasqLeases
        dnsmasq_leases = DnsmasqLeases('dnsmasq.leases')

        # Mock the read_leases method
        dnsmasq_leases.read_leases = MagicMock(side_effect=lambda: setattr(dnsmasq_leases, 'leases', dns_leases_data.splitlines()))

        # Setup fakeredis
        redis_instance = fakeredis.FakeStrictRedis()
        redis_instance.set('cgw/SiteStatus', json.dumps(site_status_data))
        redis_instance.set('cgw/ChargingStationsStatus', json.dumps(charging_status_data))

        # Patch RedisHandler to use the fakeredis instance
        with patch.object(RedisHandler, 'get_value', side_effect=lambda key: redis_instance.get(key)):
            # Patch DnsmasqLeases to return the mock instance
            with patch('src.site_status_diags.DnsmasqLeases', return_value=dnsmasq_leases):
                # Call the main function
                main()

        # Ensure the display method was called with correct arguments
        mock_display.assert_called_once_with(
            dnsmasq_leases,
            ChargingStationsStatus.from_json(charging_status_data)
        )

        # Optionally, print out the results for manual verification
        print(f"Site Status: {site_status_data}")
        print(f"Charging Stations Status: {charging_status_data}")
        print(f"DNS Leases: {dns_leases_data}")

if __name__ == '__main__':
    unittest.main()
