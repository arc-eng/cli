import os
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from cli.cli import main
from cli.constants import CODE_PRIMER


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_task_handler():
    with patch("cli.task_runner.TaskHandler") as mock:
        mock.return_value = MagicMock(
            start_streaming=MagicMock(),
            wait_for_result=MagicMock(),
        )
        yield mock


@patch.dict(os.environ, {}, clear=True)
def test_main_loads_user_config(mock_user_config, runner):
    result = runner.invoke(main, ["history"])
    mock_user_config.return_value.set_api_key_env_var.assert_called_once()
    assert result.exit_code == 0


def test_code_param_includes_code_primer(runner, mock_engine):
    """The --code param should include the code primer in the prompt"""
    prompt = "This is a test prompt."
    result = runner.invoke(main, ["task", "--code", prompt])

    mock_engine.create_task.assert_called_once()
    called_prompt = mock_engine.create_task.call_args[0][1]
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


def test_save_command_param_saves_command(
    runner, mock_engine, mock_command_index, mock_click_prompt
):
    """The --save-command param should save the task parameters as a command"""
    prompt = "This is a test prompt."
    result = runner.invoke(main, ["task", "--save-command", prompt])
    mock_command_index.add_command.assert_called_once()
    assert result.exit_code == 0


def test_save_command_param_does_not_run_task(
    runner, mock_engine, mock_command_index, mock_click_prompt
):
    """The --save-command param should not run the task"""
    result = runner.invoke(main, ["task", "--save-command", "test-prompt"])
    mock_engine.assert_not_called()
    assert result.exit_code == 0


@patch("cli.commands.task.get_branch_if_pushed")
@patch("cli.task_runner.pull_branch_changes")
def test_sync_option_syncs_correctly(
    mock_pull_branch_changes,
    mock_get_branch_if_pushed,
    runner,
        mock_engine,
):
    """The --sync option should set the branch to the current branch"""
    mock_get_branch_if_pushed.return_value = "test-value"
    result = runner.invoke(main, ["--wait", "--sync", "task", "test-prompt"])
    mock_engine.create_task.assert_called_once()
    mock_pull_branch_changes.assert_called_once()
    assert mock_engine.create_task.call_args[1]["branch"] == "test-value"
    assert result.exit_code == 0


@patch("cli.commands.task.get_branch_if_pushed")
@patch("cli.task_runner.pull_branch_changes")
def test_sync_option_syncs_only_pushed_branches(
    mock_pull_branch_changes,
    mock_get_branch_if_pushed,
    runner,
        mock_engine,
):
    mock_get_branch_if_pushed.return_value = None
    result = runner.invoke(main, ["--wait", "--sync", "task", "test-prompt"])
    mock_engine.create_task.assert_called_once()
    assert mock_engine.create_task.call_args[1]["branch"] is None
    assert result.exit_code == 0
