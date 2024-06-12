import os
import shlex
import importlib
from typing import Dict, List, Union
from terminal_screen import TerminalScreen
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.shortcuts import CompleteStyle

class CmdDispatcher:
    """
    A command dispatcher class.
    """

    completer: Union[None, NestedCompleter] = None
    complete_style: CompleteStyle = CompleteStyle.READLINE_LIKE
    cmds_avail: List[os.DirEntry] = []
    cmds_dir: str = ""
    batchfilename: str = "commands.batch"

    def __init__(self, cmds_dir: str) -> None:
        self.cmds_dir = cmds_dir
        self.read_batch_file()

    def read_batch_file(self) -> bool:
        """
        Read commands from a batch file.

        Returns:
            bool: True if the batch file is successfully read, False otherwise.
        """
        try:
            with open(os.path.join(self.cmds_dir, self.batchfilename)) as file:
                self.batch = [line.rstrip() for line in file.readlines()]
            return True
        except FileNotFoundError:
            self.batch = []
            print("Cannot open batch file:", os.path.join(self.cmds_dir, self.batchfilename))
            return False

    def dispatch(self, cmd: str, cmds_dir: str, terminal: TerminalScreen, depth: int = 0) -> str:
        """
        Dispatch a command.

        Args:
            cmd (str): The command to dispatch.
            cmds_dir (str): The directory of commands.
            depth (int): The depth of command recursion.

        Returns:
            str: The output string from command.execute(), or None if execution fails.
        """
        if not cmd:
            return None

        cmds = shlex.split(cmd)
        depth -= 1

        try:
            command = cmds[depth]
        except IndexError:
            print("Command not implemented:", cmd)
            return None

        if command == 'q':
            exit(0)
        if command == '?':
            if not self.cmds_avail:
                print("No subcommands")
                return None

            names_list = [entry.name for entry in self.cmds_avail if not entry.name.startswith('__')]
            names_str = '\n'.join(names_list)
            terminal.display_string(names_str)
            return None

        for entry in self.cmds_avail:
            if command == entry.name:
                if len(cmds) > depth:
                    return self.dispatch(cmd, os.path.join(cmds_dir, command), terminal, depth + 1)
                return None

        module_path = ["commands"] + cmds[:depth]
        for x in cmds[:depth]:
            if os.path.exists(os.path.join(module_path, 'command.py')):
                break

        module_name = '.'.join(module_path) + '.command'
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            return str(e)

        command_module = getattr(module, 'command', None)
        if not command_module:
            return "Command module not found."

        command_instance = command_module(cmds, terminal)
        return command_instance.execute()
