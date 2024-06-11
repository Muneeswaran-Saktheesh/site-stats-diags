import json
import logging

from src.redis_handler import RedisHandler
from src.site_status import SiteStatus
from src.charging_stations_status import ChargingStationsStatus
from src.dnsmasq_leases import DnsmasqLeases

logging.basicConfig(level=logging.DEBUG)

def main():
    redis_handler = RedisHandler()
    dnsmasq_leases = DnsmasqLeases('dnsmasq.leases')  # Assuming the filename is 'dnsmasq.leases'

    try:
        site_status_json = redis_handler.get_value('cgw/SiteStatus')
        if site_status_json:
            site_status = SiteStatus.from_json(json.loads(site_status_json))
            logging.debug("Site status retrieved and parsed successfully.")
        else:
            logging.warning("Warning: No data found for key cgw/SiteStatus")
            site_status = None
    except Exception as e:
        logging.error(f"Error fetching site status: {e}")
        site_status = None

    try:
        charging_status_json = redis_handler.get_value('cgw/ChargingStationsStatus')
        if charging_status_json:
            charging_stations_status = ChargingStationsStatus.from_json(json.loads(charging_status_json))
            logging.debug("Charging stations status retrieved and parsed successfully.")
        else:
            logging.warning("Warning: No data found for key cgw/ChargingStationsStatus")
            charging_stations_status = None
    except Exception as e:
        logging.error(f"Error fetching charging stations status: {e}")
        charging_stations_status = None

    try:
        dnsmasq_leases.read_leases()
        logging.debug("Dnsmasq leases read successfully.")
    except Exception as e:
        logging.error(f"Error reading dnsmasq leases: {e}")

    if site_status and charging_stations_status:
        logging.debug("Both site status and charging stations status are available. Calling display method.")
        site_status.display(dnsmasq_leases, charging_stations_status)
    else:
        logging.error("Error: Unable to display statuses due to missing data.")
