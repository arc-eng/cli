import unittest
from unittest.mock import patch, MagicMock
import click
from click.testing import CliRunner
from cli.cli import main

class TestCli(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @patch('cli.cli.PlanExecutor')
    @patch('cli.cli.StatusIndicator')
    def test_main_with_plan(self, MockStatusIndicator, MockPlanExecutor):
        mock_status_indicator = MockStatusIndicator.return_value
        mock_runner = MockPlanExecutor.return_value

        result = self.runner.invoke(main, ['--plan', 'some_plan.yaml'])

        MockPlanExecutor.assert_called_once_with('some_plan.yaml', mock_status_indicator)
        mock_runner.run.assert_called_once()
        self.assertEqual(result.exit_code, 0)

    @patch('cli.cli.TaskRunner')
    @patch('cli.cli.StatusIndicator')
    def test_main_without_plan(self, MockStatusIndicator, MockTaskRunner):
        mock_status_indicator = MockStatusIndicator.return_value
        mock_runner = MockTaskRunner.return_value

        result = self.runner.invoke(main, ['some', 'prompt'])

        MockTaskRunner.assert_called_once_with(mock_status_indicator)
        mock_runner.run_task.assert_called_once()
        self.assertEqual(result.exit_code, 0)

    @patch('cli.cli.Console')
    @patch('cli.cli.StatusIndicator')
    def test_main_exception(self, MockStatusIndicator, MockConsole):
        mock_status_indicator = MockStatusIndicator.return_value
        mock_console = MockConsole.return_value

        with patch('cli.cli.TaskRunner.run_task', side_effect=Exception('Test exception')):
            result = self.runner.invoke(main, ['some', 'prompt'])

        mock_status_indicator.fail.assert_called_once()
        mock_console.print.assert_called_once_with('[bold red]An error occurred:[/bold red] <class 'Exception'> Test exception')
        self.assertEqual(result.exit_code, 0)

if __name__ == '__main__':
    unittest.main()
