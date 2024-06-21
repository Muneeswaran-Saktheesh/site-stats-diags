class StatsClient:
    """
    Mock StatsClient class for testing purposes.
    """

    def __init__(self, host='localhost', port=8125):
        self.host = host
        self.port = port
        self.calls = []

    def gauge(self, metric_name, value):
        """
        Mock method to simulate gauge metric reporting.

        Args:
            metric_name (str): The name of the metric.
            value (int): The value to report for the metric.
        """
        self.calls.append((metric_name, value))

    def assert_called_once_with(self, metric_name, value):
        """
        Asserts that the gauge method was called exactly once with the specified arguments.

        Args:
            metric_name (str): The expected name of the metric.
            value (int): The expected value to be reported.
        """
        if len(self.calls) != 1 or self.calls[0] != (metric_name, value):
            raise AssertionError(f"Expected call: gauge({metric_name}, {value}). Actual calls: {self.calls}")

    def clear_calls(self):
        """
        Clears recorded calls for re-use in another test.
        """
        self.calls = []
