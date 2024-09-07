import os
import subprocess
import tempfile
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
    status.update_spinner_message.assert_called()
    status.stop.assert_called_once()


@patch("subprocess.run")
def test_shell_command_execution_with_failure(mock_subprocess_run):
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["echo", "test"], returncode=1, stdout="", stderr="error"
    )
    status = Mock()
    assert sh("echo test", status) == "error"
    status.start.assert_called_once()
    status.update_spinner_message.assert_called()
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
    status.update_spinner_message.assert_called()
    status.stop.assert_called_once()


@patch("cli.prompt_template.is_git_repo")
@patch("cli.prompt_template.get_git_root")
def test_prompt_template_render(mock_is_git_repo, mock_get_git_root):
    status = Mock()
    template_content = "Hello, {{ name }}!"

    with tempfile.TemporaryDirectory() as tmpdirname:
        os.mkdir(os.path.join(tmpdirname, "test_repo"))
        template_file_path = "test_repo/test_model.jinja2"

        with open(os.path.join(tmpdirname, template_file_path), "w") as f:
            f.write(template_content)

        prompt_template = PromptTemplate(
            template_file_path=template_file_path,
            repo="test_repo",
            model="test_model",
            status=status,
            name="World",
            home=tmpdirname,
        )

        result = prompt_template.render()
        assert result == "Hello, World!"
        mock_is_git_repo.assert_not_called()
        mock_get_git_root.assert_not_called()


@patch("cli.prompt_template.is_git_repo")
@patch("cli.prompt_template.get_git_root")
def test_determine_template_home(mock_get_git_root, mock_is_git_repo):
    status = Mock()
    mock_is_git_repo.return_value = True
    mock_get_git_root.return_value = "/path/to/git/root"

    prompt_template = PromptTemplate(
        template_file_path="test_model.jinja2",
        repo="test_repo",
        model="test_model",
        status=status,
        name="World",
    )

    assert prompt_template.home == "/path/to/git/root"
    mock_is_git_repo.assert_called_once()
    mock_get_git_root.assert_called_once()


@patch("cli.prompt_template.is_git_repo")
@patch("cli.prompt_template.get_git_root")
def test_determine_template_home_no_git_repo(mock_get_git_root, mock_is_git_repo):
    status = Mock()
    mock_is_git_repo.return_value = False

    prompt_template = PromptTemplate(
        template_file_path="test_model.jinja2",
        repo="test_repo",
        model="test_model",
        status=status,
        name="World",
    )

    assert prompt_template.home == os.getcwd()
    mock_is_git_repo.assert_called_once()
    mock_get_git_root.assert_not_called()


@patch("cli.prompt_template.is_git_repo")
@patch("cli.prompt_template.get_git_root")
@patch("cli.prompt_template.os.getcwd")
def test_get_template_file_path__relative_to_cwd(mock_getcwd, mock_get_git_root, mock_is_git_repo):
    # Create temporary directory as "git repo"
    with tempfile.TemporaryDirectory() as tmpdirname:
        status = Mock()
        mock_is_git_repo.return_value = True
        mock_get_git_root.return_value = tmpdirname

        # Create a sub-directory and a file
        os.mkdir(os.path.join(tmpdirname, "test_repo"))
        template_file_path = "test_repo/test_model.jinja2"
        with open(os.path.join(tmpdirname, template_file_path), "w") as f:
            f.write("Hello, {{ name }}!")

        # Simulate "pilot run" command in sub-directory of the repo
        mock_getcwd.return_value = os.path.join(tmpdirname, "test_repo")
        prompt_template = PromptTemplate(
            template_file_path="test_model.jinja2",
            repo="test_repo",
            model="test_model",
            status=status,
            name="World",
        )

        # Should return the template path relative to the git root
        assert prompt_template.get_template_file_path() == "test_repo/test_model.jinja2"
        mock_is_git_repo.assert_called_once()
        mock_get_git_root.assert_called_once()


@patch("cli.prompt_template.is_git_repo")
@patch("cli.prompt_template.get_git_root")
@patch("cli.prompt_template.os.getcwd")
def test_get_template_file_path__relative_to_git_dir(
    mock_getcwd, mock_get_git_root, mock_is_git_repo
):
    # Create temporary directory as "git repo"
    with tempfile.TemporaryDirectory() as tmpdirname:
        status = Mock()
        mock_is_git_repo.return_value = True
        mock_get_git_root.return_value = tmpdirname

        # Create a sub-directory and a file
        os.mkdir(os.path.join(tmpdirname, "test_repo"))
        template_file_path = "test_repo/test_model.jinja2"
        with open(os.path.join(tmpdirname, template_file_path), "w") as f:
            f.write("Hello, {{ name }}!")

        # Simulate "pilot run" command in root of the repo
        mock_getcwd.return_value = tmpdirname
        prompt_template = PromptTemplate(
            template_file_path="test_repo/test_model.jinja2",
            repo="test_repo",
            model="test_model",
            status=status,
            name="World",
        )

        # Should return the template path relative to the git root
        assert prompt_template.get_template_file_path() == "test_repo/test_model.jinja2"
        mock_is_git_repo.assert_called_once()
        mock_get_git_root.assert_called_once()
