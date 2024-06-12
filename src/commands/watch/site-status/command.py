from src.redis_handler import RedisHandler
from src.site_status import SiteStatus
from src.charging_stations_status import ChargingStationsStatus
from src.dnsmasq_leases import DnsmasqLeases
import json
from src.terminal_screen import TerminalScreen
from functools import partial


class Command():
    def __init__(self, cmds, terminal_screen: TerminalScreen):
        self.cmds = cmds
        self.terminal_screen = terminal_screen
        self.redis_handler = RedisHandler()
        self.key_site_status = 'cgw/SiteStatus'
        self.key_charging_stations = 'cgw/ChargingStationsStatus'
        self.dnsmasq_leases = DnsmasqLeases("/data/dnsmasq/dnsmasq.leases")

    def execute(self) -> str:
        site_status = None
        try:
            site_status_json = self.redis_handler.get_value(self.key_site_status)
            if site_status_json is not None:
                site_status = json.loads(site_status_json)
        except Exception as e:
            # If Redis is not reachable, load site status from file
            try:
                with open('site_status.json', 'r') as f:
                    site_status = json.load(f)
            except FileNotFoundError:
                print("Warning: site_status.json not found.")
            except json.JSONDecodeError:
                print("Error: Unable to decode site_status.json.")

        charging_stations_status = None
        try:
            charging_stations_status_json = self.redis_handler.get_value(self.key_charging_stations)
            if charging_stations_status_json is not None:
                charging_stations_status = json.loads(charging_stations_status_json)
        except Exception as e:
            # If Redis is not reachable, load charging station status from file
            try:
                with open('charging_stations_status.json', 'r') as f:
                    charging_stations_status = json.load(f)
            except FileNotFoundError:
                print("Warning: charging_stations_status.py not found.")
            except json.JSONDecodeError:
                print("Error: Unable to decode charging_stations_status.py.")

        try:
            self.dnsmasq_leases.read_leases()
        except Exception as e:
            print(f"Error: {e}")

        charging_stations_status = ChargingStationsStatus.from_json(charging_stations_status)
        site_status = SiteStatus.from_json(site_status)

        partial_func = partial(site_status.display, self.dnsmasq_leases, charging_stations_status)
        self.terminal_screen.start_interval_process(interval_seconds=2, func=partial_func)

        return ""