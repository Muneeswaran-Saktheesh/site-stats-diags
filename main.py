# main.py
import os
from src.terminal_screen import TerminalScreen
from command_dispatcher import CmdDispatcher

COMMANDS_DIR = "./commands"

cmd_dispatcher = CmdDispatcher(COMMANDS_DIR)

terminal = TerminalScreen(COMMANDS_DIR)

def command_handler(command: str) -> str:
    return cmd_dispatcher.dispatch(command, COMMANDS_DIR, terminal)

terminal.set_command_handler(command_handler)

terminal.run()
