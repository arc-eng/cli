import time

import click.exceptions
from pr_pilot import Task
from pr_pilot.util import get_task
from rich.console import Console

from cli.status_indicator import StatusIndicator
from cli.util import clean_code_block_with_language_specifier, markdown_panel

POLL_INTERVAL = 2  # seconds
MAX_RESULT_WAIT_TIME = 60 * 4  # 4 minutes


class TaskHandler:
    def __init__(self, task: Task, status_indicator: StatusIndicator):
        self.task = task
        self.dashboard_url = f"https://app.pr-pilot.ai/dashboard/tasks/{task.id}"
        self.console = Console()
        self.status = status_indicator
        self.task_runs_on_pr = self.task.pr_number is not None

    def wait_for_result(self, output_file=None, verbose=True, code=False, print_result=True) -> str:
        """
        Wait for the task to finish and display the result.
        :param output_file: Optional file to save the result.
        :param verbose: Print status messages.
        :param code: If True, the result will be treated as code
        :param print_result: If True, the result will be printed on the command line.
        :return:
        """
        self.status.start()
        self.status.update("Just a sec ...")
        try:
            start_time = time.time()
            task_title = None
            while self.task.status not in ["completed", "failed"]:
                if time.time() - start_time > MAX_RESULT_WAIT_TIME:
                    raise TimeoutError("The task took too long to complete.")
                self.task = get_task(self.task.id)
                if (
                    self.task.title
                    and not self.task.title == "A title"
                    and not task_title == self.task.title
                ):
                    task_title = self.task.title
                    self.status.update(self.task.title)
                if self.task.status == "running":
                    time.sleep(POLL_INTERVAL)
            if self.task.status == "failed":
                raise click.ClickException(f"Task failed: {self.task.result}")

            result = self.task.result

            new_pr_url = None
            if not self.task_runs_on_pr and self.task.pr_number:
                # Task created a new PR
                new_pr_url = (
                    f"https://github.com/{self.task.github_project}/pull/{self.task.pr_number}"
                )
                if not self.task_runs_on_pr:
                    # We found a new PR number, let the user know
                    self.status.update(f"Opened Pull Request: {new_pr_url}")
                    self.status.success(start_again=True)

            # User wants output in a file
            if output_file:
                self.status.success(start_again=True)
                with open(output_file, "w") as f:
                    if code:
                        f.write(clean_code_block_with_language_specifier(result))
                        self.status.update(f"Code saved in {output_file}")
                    else:
                        f.write(result)
                        self.status.update(f"Result saved in {output_file}")

                self.status.success()
                self.status.stop()
                return result

            self.status.success()
            self.status.stop()
            if result:
                # If verbose mode is disabled, we still want to show the PR URL
                if not verbose and new_pr_url:
                    result += f"\n\n🆕 [**PR #{self.task.pr_number}**]({new_pr_url})"
                if print_result:
                    self.console.print(markdown_panel("Result", result))
        finally:
            self.status.stop()
