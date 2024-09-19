from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_default_config_location(tmp_path):
    with patch("cli.user_config.CONFIG_LOCATION", tmp_path / "config.yaml"):
        path = tmp_path / "config.yaml"
        path.touch()
        yield path


@pytest.fixture(autouse=True)
def mock_engine():
    with patch("cli.task_runner.ArcaneEngine") as mock:
        mock.return_value = MagicMock()
        yield mock.return_value


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
def mock_engine_in_history_command():
    with patch("cli.commands.history.ArcaneEngine") as mock:
        mock.return_value = MagicMock()
        yield mock.return_value


@pytest.fixture(autouse=True)
def mock_console():
    with patch("cli.task_handler.Console") as mock:
        yield mock
