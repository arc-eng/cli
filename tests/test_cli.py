import os
import pytest
from unittest.mock import MagicMock, patch
import click
from click.testing import CliRunner
from cli.cli import main

@pytest.fixture
def mock_load_config():
    with patch('cli.cli.load_config') as mock:
        mock.return_value = {
            'quiet': False,
            'auto_sync': True,
            'CONFIG_API_KEY': 'test_api_key'
        }
        yield mock

@pytest.fixture
def runner():
    return CliRunner()

@patch.dict(os.environ, {}, clear=True)
def test_main_loads_user_config(mock_load_config, runner):
    result = runner.invoke(main, ['--no-wait'])
    mock_load_config.assert_called_once()
    assert os.environ['PR_PILOT_API_KEY'] == 'test_api_key'
    assert result.exit_code == 0

@patch.dict(os.environ, {}, clear=True)
def test_main_sets_context_values(mock_load_config, runner):
    result = runner.invoke(main, ['--no-wait', '--repo', 'owner/repo', '--no-spinner', '--chatty', '--model', 'test-model', '--branch', 'test-branch', '--no-sync', '--debug'])
    ctx = main.make_context('main', [])
    assert ctx.obj['wait'] is False
    assert ctx.obj['repo'] == 'owner/repo'
    assert ctx.obj['spinner'] is False
    assert ctx.obj['quiet'] is False
    assert ctx.obj['model'] == 'test-model'
    assert ctx.obj['branch'] == 'test-branch'
    assert ctx.obj['sync'] is False
    assert ctx.obj['debug'] is True
    assert result.exit_code == 0
