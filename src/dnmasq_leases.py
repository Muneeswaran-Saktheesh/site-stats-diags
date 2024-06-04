from datetime import datetime
import os


class DnsmasqLeases:
    """
    Represents a handler for reading and managing dnsmasq leases.
    """

    def __init__(self, filename: str):
        """
        Initializes the DnsmasqLeases instance.

        Args:
            filename (str): The path to the dnsmasq leases file.
        """
        self.filename = filename
        self.entries = []

    def read_leases(self) -> None:
        """
        Reads the dnsmasq leases file and populates the entries.
        """
        try:
            with open(self.filename, 'r') as file:
                for line in file:
                    fields = line.split()
                    if len(fields) >= 5:
                        lease_time, mac_address, ip_address, hostname, client_id = fields[:5]
                        lease_time_formatted = self.convert_lease_time(lease_time)
                        entry = {
                            'lease_time': lease_time_formatted,
                            'mac_address': mac_address,
                            'ip_address': ip_address,
                            'hostname': hostname,
                            'client_id': client_id
                        }
                        self.entries.append(entry)
        except FileNotFoundError:
            base_filename = os.path.basename(self.filename)
            cwd = os.getcwd()
            file_path = os.path.join(cwd, base_filename)
            try:
                with open(file_path, 'r') as file:
                    for line in file:
                        fields = line.split()
                        if len(fields) >= 5:
                            lease_time, mac_address, ip_address, hostname, client_id = fields[:5]
                            lease_time_formatted = self.convert_lease_time(lease_time)
                            entry = {
                                'lease_time': lease_time_formatted,
                                'mac_address': mac_address,
                                'ip_address': ip_address,
                                'hostname': hostname,
                                'client_id': client_id
                            }
                            self.entries.append(entry)
            except FileNotFoundError:
                print(f"Error: File {self.filename} not found.")
                print(f"Error: File {file_path} not found.")

    def convert_lease_time(self, timestamp: str) -> str:
        """
        Converts the lease timestamp to a formatted string.

        Args:
            timestamp (str): The timestamp of the lease.

        Returns:
            str: The formatted lease time string.
        """
        return datetime.fromtimestamp(int(timestamp)).strftime("%y%m%d_%H%M")

    def get_mac_from_ip(self, ip_address: str) -> str:
        """
        Gets the MAC address associated with the given IP address.

        Args:
            ip_address (str): The IP address.

        Returns:
            str: The MAC address.
        """
        for entry in self.entries:
            if entry['ip_address'] == ip_address:
                return entry['mac_address']
        return None

    def get_lease_time_from_ip(self, ip_address: str) -> str:
        """
        Gets the lease time associated with the given IP address.

        Args:
            ip_address (str): The IP address.

        Returns:
            str: The lease time.
        """
        for entry in self.entries:
            if entry['ip_address'] == ip_address:
                return entry['lease_time']
        return None

    def display(self) -> None:
        """
        Displays the dnsmasq leases in a tabular format.
        """
        from tabulate import tabulate
        headers = ['Lease Time', 'MAC Address', 'IP Address', 'Hostname', 'Client ID']
        rows = [[entry['lease_time'], entry['mac_address'], entry['ip_address'], entry['hostname'], entry['client_id']]
                for entry in self.entries]
        print(tabulate(rows, headers=headers))