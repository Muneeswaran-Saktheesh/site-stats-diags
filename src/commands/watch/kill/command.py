from src.terminal_screen import TerminalScreen
import time


class Command():
    def __init__(self, cmds, terminal_screen: TerminalScreen):
        self.cmds = cmds
        self.terminal_screen = terminal_screen

    def execute(self) -> str:
        # Start the interval process (execute the function every 2 seconds in this example)
        self.terminal_screen.kill_threads()

        return "All Threads Killed"