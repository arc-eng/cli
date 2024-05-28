"""
Unit tests for cli.py
"""
import unittest
from unittest.mock import patch
from click.testing import CliRunner
from cli.cli import main, load_config


class TestCLI(unittest.TestCase):
    def test_main_no_arguments(self):
        runner = CliRunner()
        result = runner.invoke(main)
        self.assertIn("Please provide a prompt.", result.output)

    @patch('cli.cli.load_config')
    def test_main_with_mocked_config(self, mock_load_config):
        mock_load_config.return_value = {'api_key': 'test_key'}
        runner = CliRunner()
        result = runner.invoke(main, ['--repo', 'user/repo', 'test prompt'])
        self.assertIn("Creating new task for repository user/repo", result.output)

if __name__ == '__main__':
    unittest.main()
