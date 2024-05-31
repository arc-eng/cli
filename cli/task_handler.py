from pr_pilot import Task
from pr_pilot.util import wait_for_result, get_task
from rich.console import Console
from rich.markdown import Markdown
from yaspin import yaspin


POLL_INTERVAL = 2  # seconds


class TaskHandler:
    def __init__(self, task: Task, show_spinner=True):
        self.task = task
        self.dashboard_url = f"https://app.pr-pilot.ai/dashboard/tasks/{task.id}"
        self.console = Console()
        self.spinner = yaspin()
        self.show_spinner = show_spinner

    def wait_for_result(self, output_file=None, raw=False) -> str:
        """
        Wait for the task to finish and display the result.
        :param output_file: Optional file to save the result.
        :param raw: If true, print the raw result without formatting or status indicator.
        :return:
        """
        if self.show_spinner:
            self.spinner.start()
            self.spinner.text = f"Running task: {self.dashboard_url}"
        try:
            result = wait_for_result(self.task, poll_interval=POLL_INTERVAL)

            self.console.line()
            if output_file:
                with open(output_file, "w") as f:
                    f.write(result)
                self.console.print(f"Result saved in {output_file}")
            elif raw:
                self.console.print(result)
            else:
                self.console.print(Markdown(result))
            self.console.line()
            return result
        except Exception as e:
            if self.show_spinner:
                self.spinner.fail("💥")
            self.console.print(f"Error: {e}")
        finally:
            if self.show_spinner:
                self.spinner.stop()
