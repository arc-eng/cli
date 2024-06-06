import unittest
from unittest.mock import patch, MagicMock
from cli.task_runner import TaskRunner, TaskConfig
from cli.status_indicator import StatusIndicator

class TestTaskRunner(unittest.TestCase):

    @patch('cli.task_runner.load_config')
    @patch('cli.task_runner.os')
    def setUp(self, mock_os, mock_load_config):
        self.mock_status_indicator = MagicMock(spec=StatusIndicator)
        self.task_runner = TaskRunner(self.mock_status_indicator)
        mock_load_config.return_value = {
            'CONFIG_API_KEY': 'fake_api_key',
            'default_repo': 'fake_repo'
        }
        mock_os.getenv.return_value = 'fake_api_key'

    @patch('cli.task_runner.os.system')
    def test_take_screenshot(self, mock_system):
        mock_system.return_value = 0
        screenshot_path = self.task_runner.take_screenshot()
        self.assertEqual(screenshot_path, Path("/tmp/screenshot.png"))
        mock_system.assert_called_once_with("screencapture -i /tmp/screenshot.png")

    @patch('cli.task_runner.detect_repository')
    @patch('cli.task_runner.Console')
    @patch('cli.task_runner.PromptTemplate')
    @patch('cli.task_runner.create_task')
    def test_run_task(self, mock_create_task, mock_prompt_template, mock_console, mock_detect_repository):
        mock_detect_repository.return_value = 'fake_repo'
        mock_console_instance = mock_console.return_value
        mock_prompt_template_instance = mock_prompt_template.return_value
        mock_prompt_template_instance.render.return_value = 'rendered_prompt'
        mock_create_task.return_value.id = 'fake_task_id'

        config = TaskConfig(
            wait=False, repo=None, snap=False, edit=None, quiet=False, cheap=False,
            code=False, file=None, direct=False, output=None, model=None, debug=False, prompt=['test prompt']
        )

        self.task_runner.run_task(config)

        mock_console_instance.print.assert_any_call("No prompt provided.")
        mock_create_task.assert_called_once_with(
            'fake_repo', 'test prompt', log=False, gpt_model=None, image=None, branch=None
        )
        self.mock_status_indicator.start.assert_called()
        self.mock_status_indicator.stop.assert_called()
        self.mock_status_indicator.update.assert_any_call("Creating new task for fake_repo  ...")
        self.mock_status_indicator.success.assert_called()

if __name__ == '__main__':
    unittest.main()