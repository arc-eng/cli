import json
import time
import click.exceptions
from pr_pilot import Task
from pr_pilot.util import get_task
from rich.console import Console
from cli.status_indicator import StatusIndicator
from cli.user_config import UserConfig
from cli.util import clean_code_block_with_language_specifier, markdown_panel, get_api_host
import websockets
import asyncio

POLL_INTERVAL = 2  # seconds
MAX_RESULT_WAIT_TIME = 60 * 4  # 4 minutes
MAX_TITLE_LENGTH = 100
IGNORED_EVENT_ACTIONS = ["clone_repo"]


class TaskHandler:
    def __init__(self, task: Task, status_indicator: StatusIndicator):
        self.task = task
        self.dashboard_url = f"{get_api_host()}/dashboard/tasks/{task.id}"
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
        self.status.update_spinner_message("Just a sec ...")
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
                    task_title = self.task.title.replace("\n", " ")[0:MAX_TITLE_LENGTH]
                    self.status.update_spinner_message(task_title)
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
                    self.status.update_spinner_message(f"Opened Pull Request: {new_pr_url}")
                    self.status.success(start_again=True)

            # User wants output in a file
            if output_file:
                self.status.success(start_again=True)
                with open(output_file, "w") as f:
                    if code:
                        f.write(clean_code_block_with_language_specifier(result))
                        self.status.update_spinner_message(f"Code saved in {output_file}")
                    else:
                        f.write(result)
                        self.status.update_spinner_message(f"Result saved in {output_file}")

                self.status.success()
                self.status.stop()
                return result

            self.status.success()
            self.status.stop()
            if result:
                # If verbose mode is disabled, we still want to show the PR URL
                if new_pr_url:
                    result += f"\n\n🆕 [**PR #{self.task.pr_number}**]({new_pr_url})"
                if print_result:
                    self.console.print(markdown_panel("Result", result))
        finally:
            self.status.stop()

    async def stream_task_events(self, task_id):
        """
        Connect to the websocket and stream task events.
        :param task_id: The ID of the task to stream events for.
        """
        self.status.start()
        api_key = UserConfig().api_key
        websocket_host = get_api_host().replace("https://", "wss://").replace("http://", "ws://")
        websocket_url = f"{websocket_host}/ws/tasks/{task_id}/events/"
        headers = {"X-Api-Key": api_key}
        try:
            async with websockets.connect(websocket_url, extra_headers=headers) as websocket:
                async for message in websocket:
                    json_message = json.loads(message)
                    # self.console.print(json_message)
                    msg_type = json_message.get("type")
                    if msg_type == "title_update":
                        title = json_message.get("data")
                        self.task.title = title
                        self.status.update_spinner_message(title)
                    if msg_type == "status_update":
                        new_status = json_message.get("data").get("status")
                        message = json_message.get("data").get("message", "")
                        if new_status == "completed":
                            self.status.success()
                            self.status.stop()
                            self.console.print(markdown_panel("Result", message))
                            return
                        elif new_status == "failed":
                            self.status.fail()
                            self.status.stop()
                            self.console.print(markdown_panel("Task Failed", message))
                    if msg_type == "event":
                        event = json_message.get("data")
                        action = event.get("action")
                        if action not in IGNORED_EVENT_ACTIONS:
                            self.status.log_message(event.get("message"))
        except websockets.exceptions.ConnectionClosedError:
            self.status.update_spinner_message("Connection closed.")
            self.status.fail()
            self.status.stop()

    def start_streaming(self, task_id):
        """
        Start the asyncio event loop to stream task events.
        :param task_id: The ID of the task to stream events for.
        """
        asyncio.run(self.stream_task_events(task_id))
