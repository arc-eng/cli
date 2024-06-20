import subprocess
from unittest.mock import Mock, patch

from cli.prompt_template import sh


@patch("subprocess.run")
def test_shell_command_execution_with_success(mock_subprocess_run):
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["echo", "test"], returncode=0, stdout="test", stderr=""
    )
    status = Mock()
    assert sh("echo test", status) == "test"
    status.start.assert_called_once()
    status.update.assert_called()
    status.success.assert_called_once_with(start_again=False)
    status.stop.assert_called_once()


@patch("subprocess.run")
def test_shell_command_execution_with_failure(mock_subprocess_run):
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["echo", "test"], returncode=1, stdout="", stderr="error"
    )
    status = Mock()
    assert sh("echo test", status) == "error"
    status.start.assert_called_once()
    status.update.assert_called()
    status.fail.assert_called_once()
    status.stop.assert_called_once()


@patch("subprocess.run")
def test_shell_command_execution_with_list_input(mock_subprocess_run):
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["echo", "test"], returncode=0, stdout="test", stderr=""
    )
    status = Mock()
    assert sh(["echo", "test"], status) == "test"
    status.start.assert_called_once()
    status.update.assert_called()
    status.success.assert_called_once_with(start_again=False)
    status.stop.assert_called_once()
