import subprocess
from unittest.mock import Mock, patch

from cli.prompt_template import sh, PromptTemplate


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


def test_prompt_template_render():
    status = Mock()
    template_content = "Hello, {{ name }}!"
    template_file_path = "test_template.jinja"

    with open(template_file_path, "w") as f:
        f.write(template_content)

    prompt_template = PromptTemplate(
        template_file_path=template_file_path,
        repo="test_repo",
        model="test_model",
        status=status,
        name="World"
    )

    result = prompt_template.render()
    assert result == "Hello, World!"

    os.remove(template_file_path)
