from unittest.mock import patch, MagicMock

import pytest

from cli.user_config import UserConfig


@pytest.fixture(autouse=True)
def mock_default_config_location(tmp_path):
    with patch("cli.user_config.CONFIG_LOCATION", tmp_path / "config.yaml"):
        yield tmp_path / "config.yaml"


@pytest.fixture(autouse=True)
def mock_create_task():
    with patch("cli.task_runner.create_task") as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_user_config():
    with patch("cli.cli.UserConfig") as mock:
        mock_config = MagicMock(spec=UserConfig)

        mock_config.verbose = False
        mock_config.auto_sync_enabled = False
        mock_config.api_key = "test_api_key"

        mock.return_value = mock_config
        yield mock_config


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
            result="Mock result",
        )
        yield mock


@pytest.fixture(autouse=True)
def mock_console():
    with patch("cli.task_handler.Console") as mock:
        yield mock
