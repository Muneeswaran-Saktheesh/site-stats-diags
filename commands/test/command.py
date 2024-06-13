from src.terminal_screen import TerminalScreen
import multiprocessing
import time


class Command():
    def __init__(self, cmds, terminal: TerminalScreen):
        self.cmds = cmds
        self.terminal = terminal

    def execute(self) -> None:
        process = multiprocessing.Process(target=self.send_counter)
        self.terminal.display("Starting")
        process.start()

    def send_counter(self) -> None:
        counter = 0
        while True:
            time.sleep(2)
            counter += 1
            self.terminal.display(f"Counter: {counter}")