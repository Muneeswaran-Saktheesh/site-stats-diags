# collector.py
import json
from src import Charger
from src import Connector

def collect_charger_fields(charger):
    """
    Collects fields from a charger object in the JSON data and creates a Charger object.

    Args:
        charger (dict): A dictionary representing a charger object in the JSON data.

    Returns:
        Charger: A Charger object populated with the collected fields.
    """
    charger_id = charger["id"]
    firmware_version = charger["firmware_version"]
    ip_address = charger["ip_address"]
    status = charger["status"]
    connectors = [collect_connector_fields(connector) for connector in charger["connectors"]]
    return Charger(charger_id, firmware_version, ip_address, status, connectors)

def collect_connector_fields(connector):
    """
    Collects fields from a connector object in the JSON data and creates a Connector object.

    Args:
        connector (dict): A dictionary representing a connector object in the JSON data.

    Returns:
        Connector: A Connector object populated with the collected fields.
    """
    connector_id = connector["id"]
    status = connector["status"]
    ocpp_error_code = connector["ocpp_error_code"]
    if connector["ocpp_error"]:
        ocpp_error_info = connector["ocpp_error"]["info"]
        ocpp_error_timestamp = connector["ocpp_error"]["timestamp"]
    else:
        ocpp_error_info = None
        ocpp_error_timestamp = None
    return Connector(connector_id, status, ocpp_error_code, ocpp_error_info, ocpp_error_timestamp)

def collect_fields(chargers):
    """
    Collects fields from charger objects in the JSON data and creates Charger objects.

    Args:
        chargers (list): A list of dictionaries representing charger objects in the JSON data.

    Returns:
        list: A list of Charger objects populated with the collected fields.
    """
    return [collect_charger_fields(charger) for charger in chargers]

def main():
    """
    Main function to collect fields from JSON data and print information about chargers and connectors.
    """
    with open('chargers.json') as f:
        chargers_data = json.load(f)
        chargers = chargers_data["chargers"]
        charger_objects = collect_fields(chargers)
        for charger in charger_objects:
            print("Charger ID:", charger.charger_id)
            print("Firmware Version:", charger.firmware_version)
            print("IP Address:", charger.ip_address)
            print("Status:", charger.status)
            for connector in charger.connectors:
                print("Connector ID:", connector.connector_id)
                print("Status:", connector.status)
                print("OCPP Error Code:", connector.ocpp_error_code)
                print("OCPP Error Info:", connector.ocpp_error_info)
                print("OCPP Error Timestamp:", connector.ocpp_error_timestamp)
            print("--------------------")

if __name__ == "__main__":
    main()
