from dataclasses import dataclass
from typing import List, Optional, Dict
from tabulate import tabulate
from datetime import datetime
import json
import csv
from io import StringIO


@dataclass
class OcppError:
    """
    Represents an OCPP error with its attributes.
    """
    error_code: str
    info: str
    timestamp: str
    vendor_error_code: str
    vendor_id: str


@dataclass
class Connector:
    """
    Represents a connector with its attributes.
    """
    id: int
    ocpp_error: OcppError
    ocpp_error_code: str
    priority: bool
    status: str


@dataclass
class Charger:
    """
    Represents a charger with its connectors and attributes.
    """
    connectors: List[Connector]
    firmware_version: str
    id: str
    ip_address: str
    ocpp_error: OcppError
    ocpp_error_code: str
    status: str


@dataclass
class ChargingStationsStatus:
    """
    Represents the status of charging stations.
    """
    chargers: List[Charger]

    @classmethod
    def from_json(cls, json_dict: Optional[dict]) -> 'ChargingStationsStatus':
        """
        Create a ChargingStationsStatus object from JSON data.

        Args:
            json_dict (dict): JSON data representing the charging station status.

        Returns:
            ChargingStationsStatus: The created ChargingStationsStatus object.
        """
        if json_dict is None:
            return cls(chargers=[])

        chargers = []
        for charger_data in json_dict.get('chargers', []):
            connectors = []
            for connector_data in charger_data.get('connectors', []):
                ocpp_error_data = connector_data.get('ocpp_error', {})
                ocpp_error = OcppError(
                    error_code=ocpp_error_data.get('error_code', ''),
                    info=ocpp_error_data.get('info', ''),
                    timestamp=ocpp_error_data.get('timestamp', ''),
                    vendor_error_code=ocpp_error_data.get('vendor_error_code', ''),
                    vendor_id=ocpp_error_data.get('vendor_id', '')
                )
                connector = Connector(
                    id=connector_data.get('id', 0),
                    ocpp_error=ocpp_error,
                    ocpp_error_code=connector_data.get('ocpp_error_code', ''),
                    priority=connector_data.get('priority', False),
                    status=connector_data.get('status', '')
                )
                connectors.append(connector)
            ocpp_error_data = charger_data.get('ocpp_error', {})
            charger = Charger(
                connectors=connectors,
                firmware_version=charger_data.get('firmware_version', ''),
                id=charger_data.get('id', ''),
                ip_address=charger_data.get('ip_address', ''),
                ocpp_error=OcppError(
                    error_code=ocpp_error_data.get('error_code', ''),
                    info=ocpp_error_data.get('info', ''),
                    timestamp=ocpp_error_data.get('timestamp', ''),
                    vendor_error_code=ocpp_error_data.get('vendor_error_code', ''),
                    vendor_id=ocpp_error_data.get('vendor_id', '')
                ),
                ocpp_error_code=charger_data.get('ocpp_error_code', ''),
                status=charger_data.get('status', '')
            )
            chargers.append(charger)
        return cls(chargers=chargers)

    def to_json(self) -> dict:
        """
        Convert the ChargingStationsStatus object to JSON format.

        Returns:
            dict: JSON representation of the ChargingStationsStatus object.
        """
        chargers_json = []
        for charger in self.chargers:
            connectors_json = []
            for connector in charger.connectors:
                connectors_json.append({
                    'id': connector.id,
                    'ocpp_error': {
                        'error_code': connector.ocpp_error.error_code,
                        'info': connector.ocpp_error.info,
                        'timestamp': connector.ocpp_error.timestamp,
                        'vendor_error_code': connector.ocpp_error.vendor_error_code,
                        'vendor_id': connector.ocpp_error.vendor_id
                    },
                    'ocpp_error_code': connector.ocpp_error_code,
                    'priority': connector.priority,
                    'status': connector.status
                })
            chargers_json.append({
                'connectors': connectors_json,
                'firmware_version': charger.firmware_version,
                'id': charger.id,
                'ip_address': charger.ip_address,
                'ocpp_error': {
                    'error_code': charger.ocpp_error.error_code,
                    'info': charger.ocpp_error.info,
                    'timestamp': charger.ocpp_error.timestamp,
                    'vendor_error_code': charger.ocpp_error.vendor_error_code,
                    'vendor_id': charger.ocpp_error.vendor_id
                },
                'ocpp_error_code': charger.ocpp_error_code,
                'status': charger.status
            })
        return {'chargers': chargers_json}

    def get_ip_from_charger_id(self, charger_id: str) -> str:
        """
        Get the IP address associated with a charger ID.

        Args:
            charger_id (str): The ID of the charger.

        Returns:
            str: The IP address of the charger.
        """
        for charger in self.chargers:
            if charger.id == charger_id:
                return charger.ip_address
        return "IP not found"

    def read_previous_status(self, file_path: str) -> dict:
        """
        Read the previous status from a JSON file.

        Args:
            file_path (str): Path to the JSON file.

        Returns:
            dict: Previous status data.
        """
        try:
            with open(file_path, 'r') as json_file:
                previous_data = json.load(json_file)
                return {tuple(entry[:2]): entry[-1] for entry in previous_data}
        except FileNotFoundError:
            return {}

    def write_status_changes(self, file_path: str, status_changes: List[List[str]]):
        """
        Write status changes to a CSV file.

        Args:
            file_path (str): Path to the CSV file.
            status_changes (List[List[str]]): Status changes data.
        """
        if status_changes:
            with open(file_path, 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(status_changes)

    def display(self) -> str:
        """
        Display the charging stations status, compare with the previous status,
        and write changes to 'status_changes.csv'.

        Returns:
            str: The formatted text displaying charging stations status.
        """
        output = StringIO()
        previous_status = self.read_previous_status('tabledata.json')

        table_data = []
        status_changes = []

        for charger in self.chargers:
            ip_address = charger.ip_address  # Get the IP address of the charger
            for connector in charger.connectors:
                formatted_time = "UNKNOWN"
                if connector.ocpp_error.timestamp:
                    formatted_time = datetime.strptime(connector.ocpp_error.timestamp,
                                                       "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%y%m%d_%H%M")
                table_data.append([
                    charger.id,
                    connector.id,
                    connector.ocpp_error.error_code,
                    formatted_time,
                    connector.ocpp_error.info,
                    connector.status,
                    ip_address  # Include the IP address in the output
                ])

                # Check if status has changed
                prev_status = previous_status.get((charger.id, connector.id))
                if prev_status and prev_status != connector.status:
                    status_changes.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), charger.id, connector.status])

        # Sort table data by charger ID
        sorted_table_data = sorted(table_data, key=lambda x: x[0])

        headers = ["Chg ID", "Conn ID", "OCPP Err", "OCPP Err Ts", "Info", "Status", "IP Address"]
        table = tabulate(sorted_table_data, headers=headers, tablefmt="psql")
        print(table, file=output)

        # Write the data to JSON file
        with open('tabledata.json', 'w') as json_file:
            json.dump(sorted_table_data, json_file, indent=4)

        # Write status changes to CSV file
        self.write_status_changes('status_changes.csv', status_changes)

        return output.getvalue()

    def get_logs(self) -> List[Dict]:
        """
        Extract logs from the charging station status data.

        Returns:
            List[Dict]: List of log entries with relevant information.
        """
        logs = []
        for charger in self.chargers:
            for connector in charger.connectors:
                log_entry = {
                    "charger_id": charger.id,
                    "connector_id": connector.id,
                    "status": connector.status,
                    "timestamp": connector.ocpp_error.timestamp,
                    "error_code": connector.ocpp_error.error_code,
                    "info": connector.ocpp_error.info,
                    "ip_address": charger.ip_address
                }
                logs.append(log_entry)
        return logs


# Example usage
if __name__ == "__main__":
    # Define the path to the JSON file
    json_file_path = "charging_stations_status.json"

    # Read JSON data from the file
    with open(json_file_path, "r") as file:
        json_data = json.load(file)

    # Create a ChargingStationsStatus instance from the JSON data
    charger_data = ChargingStationsStatus.from_json(json_data)

    # Display the charging station status
    print(charger_data.display())

    # Get logs
    logs = charger_data.get_logs()
    for log in logs:
        print(log)
