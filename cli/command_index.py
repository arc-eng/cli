import os
from typing import List, Optional

from click import Command
from pydantic import BaseModel, Field
import yaml
from rich.console import Console

from cli.models import TaskParameters
from cli.status_indicator import StatusIndicator
from cli.task_runner import TaskRunner
from cli.util import pull_branch_changes

DEFAULT_FILE_PATH = '.pilot-commands.yaml'


class PilotCommand(BaseModel):
    # Should be lower case, no spaces, hyphens
    name: str = Field(..., description="Name of the command", pattern="^[a-z0-9-]+$")
    description: str = Field(..., description="Description of the command")
    params: TaskParameters = Field(..., description="CLI parameters for the command")

    def callback(self, *args, **kwargs):
        console = Console()
        if self.params.sync:
            # Get current branch from git
            current_branch = os.popen('git rev-parse --abbrev-ref HEAD').read().strip()
            if (current_branch not in ['master', 'main']):
                self.params.branch = current_branch
        status_indicator = StatusIndicator(spinner=self.params.spinner, messages=not self.params.quiet, console=console)
        runner = TaskRunner(status_indicator)
        finished_task = runner.run_task(self.params)
        if self.params.sync and finished_task.branch:
            pull_branch_changes(status_indicator, console, finished_task.branch, self.params.debug)
        status_indicator.stop()

    def to_click_command(self) -> Command:
        return Command(self.name, callback=self.callback, help=self.description)


class CommandIndex:
    """
    A class to manage the index of commands stored in a YAML file.
    """

    def __init__(self, file_path: str = DEFAULT_FILE_PATH):
        """
        Initialize the CommandIndex with the given file path.

        :param file_path: Path to the YAML file containing commands.
        """
        self.file_path = file_path
        self.commands = self._load_commands()

    def _load_commands(self) -> List[PilotCommand]:
        """
        Load commands from the YAML file.

        :return: A list of Command instances.
        """
        try:
            with open(self.file_path, 'r') as file:
                data = yaml.safe_load(file)
                return [PilotCommand(**cmd) for cmd in data.get('commands', [])]
        except FileNotFoundError:
            return []

    def save_commands(self) -> None:
        """
        Save the current list of commands to the YAML file.
        """
        with open(self.file_path, 'w') as file:
            yaml.dump({'commands': [cmd.model_dump(exclude_none=True) for cmd in self.commands]}, file)

    def add_command(self, command: PilotCommand) -> None:
        """
        Add a new command to the list and save it.

        :param command: The Command instance to add.

        :raises ValueError: If a command with the same name already exists.
        """
        for cmd in self.commands:
            if cmd.name == command.name:
                raise ValueError(f"Command with name '{command.name}' already exists")
        command.params.branch = None
        command.params.pr_number = None
        if command.params.file:
            command.params.prompt = None
        self.commands.append(command)
        self.save_commands()

    def get_commands(self) -> List[PilotCommand]:
        """
        Get the list of commands.

        :return: A list of Command instances.
        """
        return self.commands

    def get_command(self, command) -> Optional[PilotCommand]:
        """
        Get a command by name.

        :param command:
        :return:
        """
        for cmd in self.commands:
            if cmd.name == command:
                return cmd
        return None