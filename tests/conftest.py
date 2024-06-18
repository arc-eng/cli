from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_create_task():
    with patch("cli.task_runner.create_task") as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_load_config():
    with patch('cli.cli.load_config') as mock:
        mock.return_value = {
            'quiet': True,
            'auto_sync': False,
            'api_key': 'test_api_key'
        }
        yield mock


@pytest.fixture(autouse=True)
def mock_list_tasks():
    with patch("cli.commands.history.list_tasks") as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_get_task():
    with patch("cli.task_handler.get_task") as mock:
        mock.return_value = MagicMock(
            id="1234",
            title="Mock title",
            status="completed",
            prompt="Mock prompt",
            result="Mock result"
        )
        yield mock


@pytest.fixture(autouse=True)
def mock_console():
    with patch("cli.task_handler.Console") as mock:
        yield mock
