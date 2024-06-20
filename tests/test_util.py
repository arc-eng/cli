import os
import subprocess
import pytest
import yaml
from unittest.mock import patch, mock_open
from click.testing import CliRunner
from pr_pilot import Task
from cli.util import (
    clean_code_block_with_language_specifier,
    collect_user_preferences,
    load_config,
    pull_branch_changes,
    TaskFormatter,
    PaddedConsole
)
from cli.constants import CONFIG_LOCATION, CONFIG_API_KEY


@pytest.fixture
@patch("cli.util.Console")
def mock_console(mock_console_class):
    return mock_console_class.return_value


@pytest.fixture
@patch("cli.util.click.prompt")
def mock_click_prompt(mock_prompt):
    return mock_prompt


@pytest.fixture
@patch("cli.util.click.confirm")
def mock_click_confirm(mock_confirm):
    return mock_confirm


def test_clean_code_block_with_language_specifier():
    response = """```python
def foo():
    pass
```"""
    expected = "def foo():\n    pass"
    assert clean_code_block_with_language_specifier(response) == expected

    response = "def foo():\n    pass"
    expected = "def foo():\n    pass"
    assert clean_code_block_with_language_specifier(response) == expected


def test_collect_user_preferences(mock_console, mock_click_prompt, mock_click_confirm):
    mock_click_prompt.side_effect = ["test_api_key"]
    mock_click_confirm.side_effect = [True, False]

    with patch("builtins.open", mock_open()) as mocked_file:
        collect_user_preferences()
        mocked_file.assert_called_once_with(CONFIG_LOCATION, "w")
        handle = mocked_file()
        written_data = yaml.safe_load(handle.write.call_args[0][0])
        assert written_data == {
            CONFIG_API_KEY: "test_api_key",
            "auto_sync": True,
            "verbose": False,
        }


def test_load_config(mock_console):
    config_data = {CONFIG_API_KEY: "test_api_key"}

    with patch.dict(os.environ, {"PR_PILOT_API_KEY": "test_api_key_env"}):
        with patch("builtins.open", mock_open(read_data=yaml.dump(config_data))):
            config = load_config()
            assert config == config_data

    with patch("os.path.exists", return_value=False):
        with patch("builtins.open", mock_open(read_data=yaml.dump(config_data))):
            config = load_config()
            assert config == {CONFIG_API_KEY: "test_api_key_env"}


@patch("subprocess.run")
def test_pull_branch_changes(mock_subprocess_run, mock_console):
    mock_status_indicator = mock_console.status_indicator
    mock_status_indicator.start = patch("cli.util.StatusIndicator.start").start()
    mock_status_indicator.update = patch("cli.util.StatusIndicator.update").start()
    mock_status_indicator.success = patch("cli.util.StatusIndicator.success").start()
    mock_status_indicator.fail = patch("cli.util.StatusIndicator.fail").start()
    mock_status_indicator.stop = patch("cli.util.StatusIndicator.stop").start()

    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["git", "pull", "origin", "branch"], returncode=0, stdout="output", stderr=""
    )

    pull_branch_changes(mock_status_indicator, mock_console, "branch", debug=True)

    mock_status_indicator.start.assert_called_once()
    mock_status_indicator.update.assert_called_once_with("Pull latest changes from branch")
    mock_status_indicator.success.assert_called_once()
    mock_status_indicator.stop.assert_called_once()
    mock_console.print.assert_called_with("output")


@pytest.fixture
def sample_task():
    return Task(
        id="1",
        github_project="test_project",
        created=datetime(2023, 1, 1, tzinfo=timezone.utc),
        pr_number=1,
        status="running",
        title="Test Task",
        branch="test-branch"
    )


def test_task_formatter(sample_task):
    formatter = TaskFormatter(sample_task)
    assert formatter.format_github_project() == "[link=https://github.com/test_project]test_project[/link]"
    assert formatter.format_created_at() == humanize.naturaltime(sample_task.created)
    assert formatter.format_pr_link() == "[link=https://github.com/test_project/pull/1]#1[/link]"
    assert formatter.format_status() == "[bold yellow]running[/bold yellow]"
    assert formatter.format_title() == "[link=https://app.pr-pilot.ai/dashboard/tasks/1/]Test Task[/link]"
    assert formatter.format_branch() == Markdown("`test-branch`")


def test_padded_console(mock_console):
    padded_console = PaddedConsole(padding=(2, 2))
    padded_console.print("Test Content")
    mock_console.print.assert_called_once()
