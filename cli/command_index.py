from typing import List
from pydantic import BaseModel, Field
import yaml
from cli.models import TaskParameters


class Command(BaseModel):
    # Should be lower case, no spaces, hyphens
    name: str = Field(..., description="Name of the command", example="generate-pr-description", pattern="^[a-z0-9-]+$")
    description: str = Field(..., description="Description of the command", example="Generate a PR description")
    params: TaskParameters = Field(..., description="CLI parameters for the command")


class CommandIndex:
    """
    A class to manage the index of commands stored in a YAML file.
    """

    def __init__(self, file_path: str = 'pilot-commands.yaml'):
        """
        Initialize the CommandIndex with the given file path.

        :param file_path: Path to the YAML file containing commands.
        """
        self.file_path = file_path
        self.commands = self._load_commands()

    def _load_commands(self) -> List[Command]:
        """
        Load commands from the YAML file.

        :return: A list of Command instances.
        """
        try:
            with open(self.file_path, 'r') as file:
                data = yaml.safe_load(file)
                return [Command(**cmd) for cmd in data.get('commands', [])]
        except FileNotFoundError:
            return []

    def save_commands(self) -> None:
        """
        Save the current list of commands to the YAML file.
        """
        with open(self.file_path, 'w') as file:
            yaml.dump({'commands': [cmd.dict() for cmd in self.commands]}, file)

    def add_command(self, command: Command) -> None:
        """
        Add a new command to the list and save it.

        :param command: The Command instance to add.
        """
        self.commands.append(command)
        self.save_commands()

    def get_commands(self) -> List[Command]:
        """
        Get the list of commands.

        :return: A list of Command instances.
        """
        return self.commands