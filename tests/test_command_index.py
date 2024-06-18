import pytest
from cli.command_index import CommandIndex, Command
from cli.models import TaskParameters


@pytest.fixture
def command_index(tmp_path):
    file_path = tmp_path / ".pilot-commands.yaml"
    return CommandIndex(file_path=str(file_path))


def test_add_command(command_index):
    task_params = TaskParameters(wait=10, repo='test_repo', snap=False, quiet=False, cheap=False, code=False, file=None, direct=False, output=None, model='test_model', debug=False, prompt='test_prompt', branch=None)
    command = Command(name='test-command', description='Test command', params=task_params)
    command_index.add_command(command)

    commands = command_index.get_commands()
    assert len(commands) == 1
    assert commands[0].name == 'test-command'
    assert commands[0].description == 'Test command'
    assert commands[0].params.prompt == 'test_prompt'


def test_add_duplicate_command(command_index):
    task_params = TaskParameters(wait=10, repo='test_repo', snap=False, quiet=False, cheap=False, code=False, file=None, direct=False, output=None, model='test_model', debug=False, prompt='test_prompt', branch=None)
    command = Command(name='test-command', description='Test command', params=task_params)
    command_index.add_command(command)

    with pytest.raises(ValueError, match="Command with name 'test-command' already exists"):
        command_index.add_command(command)


def test_load_commands_from_file(command_index):
    task_params = TaskParameters(wait=10, repo='test_repo', snap=False, quiet=False, cheap=False, code=False, file=None, direct=False, output=None, model='test_model', debug=False, prompt='test_prompt', branch=None)
    command = Command(name='test-command', description='Test command', params=task_params)
    command_index.add_command(command)

    new_index = CommandIndex(file_path=command_index.file_path)
    commands = new_index.get_commands()
    assert len(commands) == 1
    assert commands[0].name == 'test-command'
    assert commands[0].description == 'Test command'
    assert commands[0].params.prompt == 'test_prompt'
