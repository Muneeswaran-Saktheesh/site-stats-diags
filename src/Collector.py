import json

def collect_charger_fields(charger):
    """
    Collects fields from a charger object.

    Args:
        charger (dict): Charger object containing fields like id, firmware_version, ip_address, and status.

    Returns:
        tuple: A tuple containing charger_id, firmware_version, ip_address, and status.
    """
    charger_id = charger["id"]
    firmware_version = charger["firmware_version"]
    ip_address = charger["ip_address"]
    status = charger["status"]
    return charger_id, firmware_version, ip_address, status

def collect_connector_fields(connector):
    """
    Collects fields from a connector object.

    Args:
        connector (dict): Connector object containing fields like id, status, ocpp_error_code, ocpp_error_info, and ocpp_error_timestamp.

    Returns:
        tuple: A tuple containing connector_id, connector_status, ocpp_error_code, ocpp_error_info, and ocpp_error_timestamp.
    """
    connector_id = connector["id"]
    connector_status = connector["status"]
    ocpp_error_code = connector["ocpp_error_code"]
    if connector["ocpp_error"]:
        ocpp_error_info = connector["ocpp_error"]["info"]
        ocpp_error_timestamp = connector["ocpp_error"]["timestamp"]
    else:
        ocpp_error_info = None
        ocpp_error_timestamp = None
    return connector_id, connector_status, ocpp_error_code, ocpp_error_info, ocpp_error_timestamp

def collect_fields(chargers):
    """
    Collects fields from a list of charger objects.

    Args:
        chargers (list): List of charger objects.

    Returns:
        dict: A dictionary containing lists of collected fields like charger_ids, firmware_versions, ip_addresses, etc.
    """
    charger_ids = []
    firmware_versions = []
    ip_addresses = []
    statuses = []
    connector_ids = []
    connector_statuses = []
    ocpp_error_codes = []
    ocpp_error_infos = []
    ocpp_error_timestamps = []

    for charger in chargers:
        charger_id, firmware_version, ip_address, status = collect_charger_fields(charger)
        charger_ids.append(charger_id)
        firmware_versions.append(firmware_version)
        ip_addresses.append(ip_address)
        statuses.append(status)

        for connector in charger["connectors"]:
            connector_id, connector_status, ocpp_error_code, ocpp_error_info, ocpp_error_timestamp = collect_connector_fields(connector)
            connector_ids.append(connector_id)
            connector_statuses.append(connector_status)
            ocpp_error_codes.append(ocpp_error_code)
            ocpp_error_infos.append(ocpp_error_info)
            ocpp_error_timestamps.append(ocpp_error_timestamp)

    return {
        "charger_ids": charger_ids,
        "firmware_versions": firmware_versions,
        "ip_addresses": ip_addresses,
        "statuses": statuses,
        "connector_ids": connector_ids,
        "connector_statuses": connector_statuses,
        "ocpp_error_codes": ocpp_error_codes,
        "ocpp_error_infos": ocpp_error_infos,
        "ocpp_error_timestamps": ocpp_error_timestamps
    }

def main():
    with open('chargers.json') as f:
        chargers_data = json.load(f)
        chargers = chargers_data["chargers"]
        collected_fields = collect_fields(chargers)
        print(collected_fields)

if __name__ == "__main__":
    main()
