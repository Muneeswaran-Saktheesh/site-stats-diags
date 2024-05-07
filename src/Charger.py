# charger.py

class Charger:
    """
    Represents a charger object.

    Attributes:
        charger_id (str): The ID of the charger.
        firmware_version (str): The firmware version of the charger.
        ip_address (str): The IP address of the charger.
        status (str): The status of the charger.
        connectors (list): A list of Connector objects associated with the charger.
    """

    def __init__(self, charger_id, firmware_version, ip_address, status, connectors):
        """
        Initializes a new Charger object.

        Args:
            charger_id (str): The ID of the charger.
            firmware_version (str): The firmware version of the charger.
            ip_address (str): The IP address of the charger.
            status (str): The status of the charger.
            connectors (list): A list of Connector objects associated with the charger.
        """
        self.charger_id = charger_id
        self.firmware_version = firmware_version
        self.ip_address = ip_address
        self.status = status
        self.connectors = connectors
