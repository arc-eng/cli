import asyncio
import json

import click.exceptions
import websockets
from pr_pilot import Task
from rich.console import Console

from cli.status_indicator import StatusIndicator
from cli.user_config import UserConfig
from cli.util import clean_code_block_with_language_specifier, markdown_panel, get_api_host

STATUS_FAILED = "failed"
STATUS_COMPLETED = "completed"
MSG_EVENT = "event"
MSG_STATUS_UPDATE = "status_update"
MSG_TITLE_UPDATE = "title_update"
MAX_TITLE_LENGTH = 100
IGNORED_EVENT_ACTIONS = ["clone_repo"]


class TaskHandler:
    def __init__(self, task: Task, status_indicator: StatusIndicator):
        self.task = task
        self.dashboard_url = f"{get_api_host()}/dashboard/tasks/{task.id}"
        self.console = Console()
        self.status = status_indicator
        self.task_runs_on_pr = self.task.pr_number is not None

    async def stream_task_events(
        self, task_id, output_file=None, log_messages=True, code=False, print_result=True
    ):
        """
        Connect to the websocket and stream task events until the task is completed or failed.
        :param task_id: The ID of the task to stream events for.
        :param output_file: Optional file to save the result.
        :param log_messages: Print status messages.
        :param code: If True, the result will be treated as code
        :param print_result: If True, the result will be printed on the command line.
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
                    msg_type = json_message.get("type")
                    if msg_type == MSG_TITLE_UPDATE:
                        title = json_message.get("data")
                        self.task.title = title
                        self.status.update_spinner_message(title)
                    if msg_type == MSG_STATUS_UPDATE:
                        new_status = json_message.get("data").get("status")
                        message = json_message.get("data").get("message", "")
                        self.task.result = message
                        if new_status == STATUS_COMPLETED:
                            self.status.success()
                            self.status.stop()
                            if output_file:
                                await self.write_result_to_file(code, message, output_file)
                            elif print_result:
                                self.console.print(markdown_panel(None, message, hide_frame=True))
                            return message
                        elif new_status == STATUS_FAILED:
                            self.status.fail()
                            self.status.stop()
                            raise click.ClickException(f"Task failed: {self.task.result}")
                    if msg_type == MSG_EVENT:
                        event = json_message.get("data")
                        action = event.get("action")
                        if action not in IGNORED_EVENT_ACTIONS and log_messages:
                            self.status.log_message(event.get("message"))
        except websockets.exceptions.ConnectionClosedError:
            self.status.update_spinner_message("Connection closed.")
            self.status.fail()
            self.status.stop()

    async def write_result_to_file(self, code, message, output_file):
        """Write the result to a file.
        :param code: If True, the result will be treated as code
        :param message: The message to write to the file
        :param output_file: The file to write the message to
        """
        with open(output_file, "w") as f:
            if code:
                self.status.log_message(f"Save code to `{output_file}`")
                f.write(clean_code_block_with_language_specifier(message))
            else:
                self.status.log_message(f"Save result to `{output_file}`")
                f.write(message)

    def wait_for_result(self, output_file=None, log_messages=True, code=False, print_result=True):
        """
        Start the asyncio event loop to stream task events.
        :param output_file: Optional file to save the result.
        :param log_messages: Print status messages.
        :param code: If True, the result will be treated as code
        :param print_result: If True, the result will be printed on the command line.
        """
        asyncio.run(
            self.stream_task_events(self.task.id, output_file, log_messages, code, print_result)
        )
