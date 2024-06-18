import os
from unittest.mock import patch, MagicMock

import click
import pytest
from click.testing import CliRunner

from cli.cli import main
from cli.constants import CODE_PRIMER


@pytest.fixture
def runner():
    return CliRunner()


@patch.dict(os.environ, {}, clear=True)
def test_main_loads_user_config(mock_load_config, runner):
    result = runner.invoke(main, ['history'])
    mock_load_config.assert_called_once()
    assert os.environ['PR_PILOT_API_KEY'] == 'test_api_key'
    assert result.exit_code == 0


def test_code_param_includes_code_primer(runner, mock_create_task):
    """The --code param should include the code primer in the prompt"""
    prompt = "This is a test prompt."
    result = runner.invoke(main, ['task', '--code', prompt])

    mock_create_task.assert_called_once()
    called_prompt = mock_create_task.call_args[0][1]
    assert CODE_PRIMER in called_prompt
    assert prompt in called_prompt
    assert result.exit_code == 0


@pytest.fixture
def mock_command_index():
    with patch("cli.commands.task.CommandIndex") as mock:
        yield mock.return_value


@pytest.fixture(autouse=True)
def mock_click_prompt():
    with patch("cli.commands.task.click.prompt") as mock:
        mock.return_value = "test-value"
        yield mock


def test_save_command_param_saves_command(runner, mock_create_task, mock_command_index, mock_click_prompt):
    """The --save-command param should save the task parameters as a command"""
    prompt = "This is a test prompt."
    result = runner.invoke(main, ['task', '--save-command', prompt])

    mock_create_task.assert_called_once()
    mock_command_index.add_command.assert_called_once()
    assert result.exit_code == 0
