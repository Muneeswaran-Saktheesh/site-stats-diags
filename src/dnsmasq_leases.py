import os
import logging
from datetime import datetime
from tabulate import tabulate

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
            self._read_file(self.filename)
        except FileNotFoundError:
            base_filename = os.path.basename(self.filename)
            cwd = os.getcwd()
            file_path = os.path.join(cwd, base_filename)
            try:
                self._read_file(file_path)
            except FileNotFoundError:
                logging.error(f"Error: File {self.filename} not found.")
                logging.error(f"Error: File {file_path} not found.")

    def _read_file(self, filepath: str) -> None:
        """
        Reads a file and populates the entries.

        Args:
            filepath (str): The path to the file.
        """
        with open(filepath, 'r') as file:
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
            str: The MAC address or None if not found.
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
            str: The lease time or None if not found.
        """
        for entry in self.entries:
            if entry['ip_address'] == ip_address:
                return entry['lease_time']
        return None

    def display(self) -> None:
        """
        Displays the dnsmasq leases in a tabular format.
        """
        headers = ['Lease Time', 'MAC Address', 'IP Address', 'Hostname', 'Client ID']
        rows = [[entry['lease_time'], entry['mac_address'], entry['ip_address'], entry['hostname'], entry['client_id']]
                for entry in self.entries]
        print(tabulate(rows, headers=headers))

# Example usage:
# logging.basicConfig(level=logging.INFO)
# leases = DnsmasqLeases('/path/to/dnsmasq.leases')
# leases.read_leases()
# leases.display()
