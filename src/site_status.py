from datetime import datetime
from io import StringIO
from tabulate import tabulate


class EV:
    def __init__(self, id, status, **kwargs):
        self.id = id
        self.status = status
        # Handle any additional keys
        for key, value in kwargs.items():
            setattr(self, key, value)


class SiteStatus:
    def __init__(self, charging_stations, datetime_str, evs, offline_chargers):
        # Filter out the 'action' key
        self.evs = [EV(**{k: v for k, v in ev.items() if k != 'action'}) for ev in evs]
        self.charging_stations = charging_stations
        self.datetime_str = datetime_str
        self.offline_chargers = offline_chargers

    @classmethod
    def from_json(cls, data):
        charging_stations = data['charging_stations']
        datetime_str = data['datetime']
        evs = data['evs']
        offline_chargers = data['offline_chargers']
        return cls(charging_stations, datetime_str, evs, offline_chargers)

    def display(self, dnsmasq_leases, charging_stations_status):
        output = StringIO()
        print("Site Status:", file=output)
        print(f"Action: response", file=output)
        print(f"DateTime: {self.datetime_str}", file=output)
        print("\nChargers:", file=output)

        headers = ["ID", "Status", "IP", "MAC", "Leased until"]
        chargers_with_ip = []

        for station in self.charging_stations:
            ip = charging_stations_status.get_ip_from_charger_id(station['id'])
            mac = dnsmasq_leases.get_mac_from_ip(ip) if ip else 'N/A'
            lease_time = dnsmasq_leases.get_lease_time_from_ip(ip) if ip else 'N/A'
            chargers_with_ip.append((station['id'], 'Online', ip or 'N/A', mac, lease_time))

        for offline_charger in self.offline_chargers:
            ip = charging_stations_status.get_ip_from_charger_id(offline_charger['id'])
            mac = dnsmasq_leases.get_mac_from_ip(ip) if ip else 'N/A'
            lease_time = dnsmasq_leases.get_lease_time_from_ip(ip) if ip else 'N/A'
            chargers_with_ip.append((offline_charger['id'], 'OFFLINE', ip or 'N/A', mac, lease_time))

        print(tabulate(chargers_with_ip, headers=headers, tablefmt="psql"), file=output)

        print("\nConnections:", file=output)
        print(charging_stations_status.display(), file=output)

        print("\nElectric Vehicles:", file=output)
        headers = ["ID", "Chg-ID", "Status", "Chg-Current", "Chg-Offer", "Chg-Fw.", "Sess.E", "Start Chg."]
        data = []

        for ev in self.evs:
            try:
                start_chg_time = datetime.strptime(ev.start_charging_time, "%Y-%m-%dT%H:%M:%S.%f%z").strftime(
                    "%y%m%d_%H%M")
            except (TypeError, ValueError):
                start_chg_time = 'UNKNOWN'
            data.append([ev.id, ev.charger_id, ev.status, None, None, None, None, start_chg_time])

        print(tabulate(data, headers=headers, tablefmt="psql", stralign="left"), file=output)
        return output.getvalue()
