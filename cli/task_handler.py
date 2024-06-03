import time

from pr_pilot import Task
from pr_pilot.util import get_task
from rich.console import Console
from rich.markdown import Markdown

from cli.status_indicator import StatusIndicator
from cli.util import clean_code_block_with_language_specifier

POLL_INTERVAL = 2  # seconds
MAX_RESULT_WAIT_TIME = 60 * 4  # 4 minutes


class TaskHandler:
    def __init__(self, task: Task, status_indicator: StatusIndicator):
        self.task = task
        self.dashboard_url = f"https://app.pr-pilot.ai/dashboard/tasks/{task.id}"
        self.console = Console()
        self.status = status_indicator

    def wait_for_result(self, output_file=None, quiet=False, code=False) -> str:
        """
        Wait for the task to finish and display the result.
        :param output_file: Optional file to save the result.
        :param quiet: If True, nothing will be printed on the command line.
        :param code: If True, the result will be treated as code
        :return:
        """

        self.status.update("Waiting for task result")
        self.status.start()
        try:
            start_time = time.time()
            task_title = None
            while self.task.status not in ["completed", "failed"]:
                if time.time() - start_time > MAX_RESULT_WAIT_TIME:
                    raise TimeoutError("The task took too long to complete.")
                self.task = get_task(self.task.id)
                if self.task.title and not self.task.title == "A title" and not task_title == self.task.title:
                    task_title = self.task.title
                    self.status.update(self.task.title)
                time.sleep(POLL_INTERVAL)
            if self.task.status == "failed":
                raise ValueError(f"Task failed: {self.task.result}")

            result = self.task.result

            if output_file:
                with open(output_file, "w") as f:
                    if code:
                        f.write(clean_code_block_with_language_specifier(result))
                        self.status.update(f"Code saved in {output_file}")
                    else:
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
