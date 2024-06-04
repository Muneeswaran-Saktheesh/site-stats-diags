from redis_handler import RedisHandler
from site_status import SiteStatus
from charging_stations_status import ChargingStationsStatus
from dnmasq_leases import DnsmasqLeases
import json

if __name__ == "__main__":
    redis_handler = RedisHandler()

    key_site_status = 'cgw/SiteStatus'
    site_status = None
    try:
        site_status_json = redis_handler.get_value(key_site_status)
        if site_status_json is not None:
            site_status = json.loads(site_status_json)
    except Exception as e:
        print(f"Error: {e}")

    key_charging_stations = 'cgw/ChargingStationsStatus'
    charging_stations_status = None
    try:
        charging_stations_status_json = redis_handler.get_value(key_charging_stations)
        if charging_stations_status_json is not None:
            charging_stations_status = json.loads(charging_stations_status_json)
    except Exception as e:
        print(f"Error: {e}")

    dnsmasq_leases = DnsmasqLeases("/data/dnsmasq/dnsmasq.leases")
    try:
        dnsmasq_leases.read_leases()
    except Exception as e:
        print(f"Error: {e}")

    charging_stations_status = ChargingStationsStatus.from_json(charging_stations_status)
    site_status = SiteStatus.from_json(site_status)

    site_status.display(dnsmasq_leases, charging_stations_status)

