from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.completion import NestedCompleter
from typing import Callable, Dict
import os
import threading
import time


class TerminalScreen:
    def __init__(self, cmds_dir: str):
        self.help_text = "Press Control-C to exit."
        self.command_handler: Callable[[str], str] = None  # Command handler function
        self.cmds_dir = cmds_dir
        self.completer: NestedCompleter = self.init_nested_cmds()
        self.running_threads: list[threading.Thread] = []  # List to store running threads

        # Initialize key bindings
        kb = KeyBindings()

        @kb.add("c-c")
        @kb.add("c-q")
        @kb.add("q")
        def _(event):
            "Pressing Ctrl-Q or Ctrl-C will exit the user interface."
            event.app.exit()

        # Initialize styles
        style = Style(
            [
                ("output-field", "bg:#ffffff #000000"),
                ("input-field", "bg:#ffffff #000000"),
                ("line", "#004400"),
            ]
        )

        # Initialize layout
        self.output_field = TextArea(style="class:output-field", text=self.help_text)
        self.input_field = TextArea(
            height=1,
            prompt=">>> ",
            style="class:input-field",
            multiline=False,
            wrap_lines=False,
            completer=self.completer
        )

        container = HSplit(
            [
                self.output_field,
                Window(height=1, char="-", style="class:line"),
                self.input_field,
            ]
        )

        # Attach accept handler to the input field
        def accept(buff):
            """
            Handle the acceptance of the input field.
            This function is called when the user hits Enter.
            """
            command = self.input_field.text
            self.handle_command(command)

        self.input_field.accept_handler = accept

        # Initialize application without running it
        self.application = Application(
            layout=Layout(container, focused_element=self.input_field),
            key_bindings=kb,
            style=style,
            mouse_support=True,
            full_screen=True,
        )

    def start_interval_process(self, interval_seconds: float, func: Callable[[], str]):
        """
        Start a subprocess executing a function at specified intervals.

        Args:
            interval_seconds (float): Interval in seconds between function executions.
            func (Callable[[], str]): Function to be executed at intervals, returning a string.
        """

        def execute_func(stop_event: threading.Event):
            while not stop_event.is_set():
                output_str = func()  # Execute the provided function
                self.display(output_str)  # Display the output in the terminal
                stop_event.wait(interval_seconds)  # Wait for the specified interval

        # Create an event to signal the thread to stop
        stop_event = threading.Event()

        # Start the interval execution in a separate thread
        interval_thread = threading.Thread(target=execute_func, args=(stop_event,))
        interval_thread.daemon = True  # Set as a daemon thread to exit with the main thread
        interval_thread.start()

        # Store the thread in the list
        self.running_threads.append((interval_thread, stop_event))

    def display_string(self, message: str) -> None:
        """
        Display a string in the output field.

        Args:
            message (str): The string to be displayed.
        """
        self.display(message)

    def start_counter_process(self):
        """
        Start a subprocess printing a counter into the output screen.
        """

        def counter():
            count = 1
            while True:
                self.display(f"Counter: {count}")
                count += 1
                time.sleep(1)  # Wait for 1 second

        # Start the counter subprocess in a separate thread
        counter_thread = threading.Thread(target=counter)
        counter_thread.daemon = True  # Set as a daemon thread to exit with the main thread
        counter_thread.start()

    def kill_threads(self):
        """
        Stop all running threads.
        """
        for thread, stop_event in self.running_threads:
            stop_event.set()  # Set the event to signal the thread to stop
            thread.join()  # Wait for the thread to complete (optional)

    def run(self):
        self.application.run()

    def handle_command(self, command: str) -> None:
        output_text: str = None
        if self.command_handler is not None:
            output_text = self.command_handler(command)
        self.display(output_text)

    def set_command_handler(self, handler: Callable[[str], str]):
        self.command_handler = handler

    def display(self, text: str) -> None:
        if text is not None:
            self.output_field.buffer.document = Document(
                text=text, cursor_position=len(text)
            )

    def init_nested_cmds(self) -> None:
        mydict = self.dir_2_dict(self.cmds_dir, d={})
        try:
            self.completer = NestedCompleter.from_nested_dict(mydict[self.cmds_dir])
        except KeyError as e:
            print(f"KeyError occurred: {e}")
            self.completer = None
            return None
        return self.completer

    def dir_2_dict(self, path: str, d: Dict) -> Dict:
        """
        Convert directory structure to nested dictionary.

        Args:
            path (str): The path to the directory.
            d (Dict): The dictionary to store directory structure.

        Returns:
            Dict: The nested dictionary representing directory structure.
        """
        name = os.path.basename(path)
        if os.path.isdir(path):
            if name not in d:
                d[name] = {}
            for x in os.listdir(path):
                if not x.startswith('__'):  # Exclude directories starting with double underscores
                    self.dir_2_dict(os.path.join(path, x), d[name])
        return d
