from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_default_config_location(tmp_path):
    with patch("cli.user_config.CONFIG_LOCATION", tmp_path / "config.yaml"):
        path = tmp_path / "config.yaml"
        path.touch()
        yield path


@pytest.fixture(autouse=True)
def mock_create_task():
    with patch("cli.task_runner.create_task") as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_user_config(mock_default_config_location):
    mock_instance = MagicMock(authenticate=MagicMock())
    mock_instance.verbose = False
    mock_instance.auto_sync_enabled = False
    mock_instance.api_key = "test_api_key"
    mock_class = MagicMock(return_value=mock_instance)
    with patch("cli.task_runner.UserConfig", mock_class):
        with patch("cli.cli.UserConfig", mock_class):
            yield mock_class


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
