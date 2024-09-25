from datetime import timezone, datetime
from unittest.mock import patch

import humanize
import pytest
from arcane import Task
from rich.markdown import Markdown

from cli.util import (
    clean_code_block_with_language_specifier,
    TaskFormatter,
)


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
        == "[link=https://arcane.engineer/dashboard/tasks/1/]Test Task[/link]"
    )
    assert formatter.format_branch().markup == Markdown("`test-branch`").markup
