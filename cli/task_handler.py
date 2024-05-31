from pr_pilot import Task
from pr_pilot.util import wait_for_result
from rich.console import Console
from rich.markdown import Markdown

from cli.status_indicator import StatusIndicator

POLL_INTERVAL = 2  # seconds


class TaskHandler:
    def __init__(self, task: Task, status_indicator: StatusIndicator):
        self.task = task
        self.dashboard_url = f"https://app.pr-pilot.ai/dashboard/tasks/{task.id}"
        self.console = Console()
        self.status = status_indicator

    def wait_for_result(self, output_file=None, quiet=False) -> str:
        """
        Wait for the task to finish and display the result.
        :param output_file: Optional file to save the result.
        :param quiet: If True, nothing will be printed on the command line.
        :return:
        """

        self.status.update("Waiting for task result")
        self.status.start()
        try:
            result = wait_for_result(self.task, poll_interval=POLL_INTERVAL)
            if output_file:
                with open(output_file, "w") as f:
                    f.write(result)
                self.status.update(f"Result saved in {output_file}")
                self.status.success()
            else:
                self.status.success()
                self.status.stop()
                if not quiet:
                    self.console.line()
                    self.console.print(Markdown(result))
                    self.console.line()

            return result
        except Exception as e:
            self.status.update(f"Error: {e}")
            self.status.fail()
