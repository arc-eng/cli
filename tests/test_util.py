import os
from datetime import timezone, datetime
from unittest.mock import patch, mock_open

import humanize
import pytest
import yaml
from pr_pilot import Task
from rich.markdown import Markdown

from cli.constants import CONFIG_API_KEY
from cli.util import (
    clean_code_block_with_language_specifier,
    load_config,
    TaskFormatter,
)


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


def test_load_config(mock_console):
    config_data = {CONFIG_API_KEY: "test_api_key"}

    # Make sure PR_PILOT_API_KEY env var has priority over config file
    with patch.dict(os.environ, {"PR_PILOT_API_KEY": "test_api_key_env"}):
        with patch("os.path.exists", return_value=False):
            with patch("builtins.open", mock_open(read_data=yaml.dump(config_data))):
                config = load_config()
                assert config == {CONFIG_API_KEY: "test_api_key_env"}


@pytest.fixture
def sample_task():
    return Task(
        id="1",
        github_project="test_project",
        github_user="test_user",
        created=datetime.now(timezone.utc),
        pr_number=1,
        status="running",
        title="Test Task",
        branch="test-branch",
    )


def test_task_formatter(sample_task):
    formatter = TaskFormatter(sample_task)
    assert (
        formatter.format_github_project()
        == "[link=https://github.com/test_project]test_project[/link]"
    )
    assert formatter.format_created_at() == humanize.naturaltime(sample_task.created)
    assert formatter.format_pr_link() == "[link=https://github.com/test_project/pull/1]#1[/link]"
    assert formatter.format_status() == "[bold yellow]running[/bold yellow]"
    assert (
        formatter.format_title()
        == "[link=https://app.pr-pilot.ai/dashboard/tasks/1/]Test Task[/link]"
    )
    assert formatter.format_branch().markup == Markdown("`test-branch`").markup
