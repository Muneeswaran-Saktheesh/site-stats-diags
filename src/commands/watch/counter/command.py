from src.terminal_screen import TerminalScreen
import time


class Command():
    def __init__(self, cmds, terminal_screen: TerminalScreen):
        self.cmds = cmds
        self.terminal_screen = terminal_screen

    # Example function to be executed at intervals
    def example_interval_function(self) -> str:
        return f"Time: {time.strftime('%H:%M:%S')}"

    def execute(self) -> str:
        # Start the interval process (execute the function every 2 seconds in this example)
        self.terminal_screen.start_interval_process(interval_seconds=2, func=self.example_interval_function)

        return str(self.cmds)