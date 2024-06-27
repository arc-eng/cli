import os
from typing import List, Optional

import yaml
from click import Command
from pydantic import BaseModel, Field
from rich.console import Console

from cli.models import TaskParameters
from cli.status_indicator import StatusIndicator
from cli.task_runner import TaskRunner
from cli.util import pull_branch_changes, is_git_repo, get_git_root

DEFAULT_FILE_PATH = ".pilot-commands.yaml"


class PilotCommand(BaseModel):
    # Should be lower case, no spaces, hyphens
    name: str = Field(..., description="Name of the command", pattern="^[a-z0-9-]+$")
    description: str = Field(..., description="Description of the command")
    params: TaskParameters = Field(..., description="CLI parameters for the command")

    def callback(self, *args, **kwargs):
        console = Console()
        if self.params.sync:
            # Get current branch from git
            current_branch = os.popen("git rev-parse --abbrev-ref HEAD").read().strip()
            if current_branch not in ["master", "main"]:
                self.params.branch = current_branch
        status_indicator = StatusIndicator(
            spinner=self.params.spinner, messages=not self.params.verbose, console=console
        )
        runner = TaskRunner(status_indicator)
        finished_task = runner.run_task(self.params)
        if self.params.sync and finished_task.branch:
            pull_branch_changes(status_indicator, console, finished_task.branch, self.params.debug)
        status_indicator.stop()

    def to_click_command(self) -> Command:
        return Command(self.name, callback=self.callback, help=self.description)


def find_pilot_commands_file() -> Optional[str]:
    """Discover the location of the .pilot-commands.yaml file.

    The file is searched for in the following order:
    1. The root of the current Git repository
    2. The home directory

    :return: The absolute path to the file, or None if not found.
    """
    # Check if the current directory is part of a Git repository
    if is_git_repo():
        git_root = get_git_root()
        if git_root:
            git_repo_file_path = os.path.join(git_root, ".pilot-commands.yaml")
            if os.path.isfile(git_repo_file_path):
                return os.path.abspath(git_repo_file_path)

    # If not found in the Git repository, check the home directory
    home_file_path = os.path.expanduser("~/.pilot-commands.yaml")
    if os.path.isfile(home_file_path):
        return os.path.abspath(home_file_path)

    # If the file is not found in either location, return None
    return None


class CommandIndex:
    """
    A class to manage the index of commands stored in a YAML file.
    """

    def __init__(self, file_path: str = None):
        """
        Initialize the CommandIndex with the given file path.

        :param file_path: Path to the YAML file containing commands.
        """
        self.file_path = file_path
        if not self.file_path:
            self.file_path = find_pilot_commands_file()
        self.commands = self._load_commands()

    def _load_commands(self) -> List[PilotCommand]:
        """
        Load commands from the YAML file.

        :return: A list of Command instances.
        """
        try:
            with open(self.file_path, "r") as file:
                data = yaml.safe_load(file)
                return [PilotCommand(**cmd) for cmd in data.get("commands", [])]
        except FileNotFoundError:
            return []

    def save_commands(self) -> None:
        """
        Save the current list of commands to the YAML file.
        """
        with open(self.file_path, "w") as file:
            yaml.dump(
                {"commands": [cmd.model_dump(exclude_none=True) for cmd in self.commands]},
                file,
            )

    def add_command(self, new_command: PilotCommand) -> None:
        """
        Add a new command to the list and save it.

        :param new_command: The Command instance to add.

        :raises ValueError: If a command with the same name already exists.
        """
        for cmd in self.commands:
            if cmd.name == new_command.name:
                raise ValueError(f"Command with name '{new_command.name}' already exists")
        new_command.params.branch = None
        new_command.params.pr_number = None
        if new_command.params.file:
            new_command.params.prompt = None
        self.commands.append(new_command)
        self.save_commands()

    def get_commands(self) -> List[PilotCommand]:
        """
        Get the list of commands.

        :return: A list of Command instances.
        """
        return self.commands

    def get_command(self, command_name) -> Optional[PilotCommand]:
        """
        Get a command by name.

        :param command_name:
        :return:
        """
        for cmd in self.commands:
            if cmd.name == command_name:
                return cmd
        return None

    def remove_command(self, command_name) -> None:
        """
        Remove a command by name.

        :param command_name:
        """
        self.commands = [cmd for cmd in self.commands if cmd.name != command_name]
        self.save_commands()
