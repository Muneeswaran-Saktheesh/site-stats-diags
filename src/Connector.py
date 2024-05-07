# connector.py

class Connector:
    """
    Represents a connector object.

    Attributes:
        connector_id (int): The ID of the connector.
        status (str): The status of the connector.
        ocpp_error_code (str): The error code reported by OCPP (Open Charge Point Protocol).
        ocpp_error_info (str): Additional information about the OCPP error.
        ocpp_error_timestamp (str): The timestamp when the OCPP error occurred.
    """

    def __init__(self, connector_id, status, ocpp_error_code, ocpp_error_info, ocpp_error_timestamp):
        """
        Initializes a new Connector object.

        Args:
            connector_id (int): The ID of the connector.
            status (str): The status of the connector.
            ocpp_error_code (str): The error code reported by OCPP (Open Charge Point Protocol).
            ocpp_error_info (str): Additional information about the OCPP error.
            ocpp_error_timestamp (str): The timestamp when the OCPP error occurred.
        """
        self.connector_id = connector_id
        self.status = status
        self.ocpp_error_code = ocpp_error_code
        self.ocpp_error_info = ocpp_error_info
        self.ocpp_error_timestamp = ocpp_error_timestamp
