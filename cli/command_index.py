import yaml
from typing import List, Dict

class CommandIndex:
    def __init__(self, file_path: str = 'pilot-commands.yaml'):
        self.file_path = file_path
        self.commands = self._load_commands()

    def _load_commands(self) -> List[Dict]:
        try:
            with open(self.file_path, 'r') as file:
                data = yaml.safe_load(file)
                return data.get('commands', [])
        except FileNotFoundError:
            return []

    def save_commands(self) -> None:
        with open(self.file_path, 'w') as file:
            yaml.dump({'commands': self.commands}, file)

    def add_command(self, command: Dict) -> None:
        self.commands.append(command)
        self.save_commands()

    def get_commands(self) -> List[Dict]:
        return self.commands
