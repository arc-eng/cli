import os
from unittest.mock import MagicMock, patch

import pytest

from cli.commands.grab import (
    clone_repository,
    prompt_user_for_commands,
    import_commands,
    copy_file_to_local_directory,
)


@pytest.fixture
def mock_console():
    return MagicMock()


@pytest.fixture
def mock_status_indicator():
    return MagicMock()


@pytest.fixture
def mock_command_index():
    return MagicMock()


def test_clone_repository(mock_status_indicator):
    with patch("subprocess.run") as mock_run:
        clone_repository(mock_status_indicator, "git@github.com:repo.git", "/tmp/dir")
        mock_run.assert_called_once_with(
            ["git", "clone", "--depth", "1", "git@github.com:repo.git", "/tmp/dir"],
            check=True,
            capture_output=True,
        )


def test_prompt_user_for_commands(mock_command_index):
    mock_command_index.get_commands.return_value = [
        MagicMock(name="cmd1"),
        MagicMock(name="cmd2"),
    ]
    with patch("inquirer.prompt") as mock_prompt:
        mock_prompt.return_value = {"commands": ["cmd1"]}
        answers = prompt_user_for_commands(mock_command_index, MagicMock())
        assert answers == {"commands": ["cmd1"]}
        mock_prompt.assert_called_once()


def test_import_commands(mock_command_index):
    mock_remote_index = MagicMock()
    mock_local_index = MagicMock()
    mock_remote_command = MagicMock()
    mock_remote_command.params.file = "file.txt"
    mock_remote_index.get_command.return_value = mock_remote_command
    mock_local_index.get_command.return_value = None

    with patch("cli.commands.grab.copy_file_to_local_directory") as mock_copy:
        answers = {"commands": ["cmd1"]}
        commands_imported, files_imported = import_commands(
            answers, mock_remote_index, mock_local_index, "/tmp/dir"
        )
        assert commands_imported == [mock_remote_command]
        assert files_imported == ["file.txt"]
        mock_copy.assert_called_once_with("/tmp/dir/file.txt", "file.txt")


def test_copy_file_to_local_directory():
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = "content"
        with patch("os.makedirs") as mock_makedirs:
            copy_file_to_local_directory("/source/path", "/dest/path")
            mock_open.assert_any_call("/source/path", "r")
            mock_open.assert_any_call("/dest/path", "w")
            mock_makedirs.assert_called_once_with(os.path.dirname("/dest/path"), exist_ok=True)
