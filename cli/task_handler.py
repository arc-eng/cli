import asyncio
import json

import click.exceptions
import websockets
from pr_pilot import Task
from rich.console import Console
from websockets.frames import CloseCode

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
        self.action_character_map = {
            "invoke_skill": "└─┐",
            "finish_skill": "┌─┘",
            "push_branch": "●",
            "checkout_branch": "○",
            "write_file": "✎",
            "list_directory": "▸",
            "search_code": "∷",
            "search": "⌕",
            "search_issues": "⌕",
            "read_github_issue": "≡",
            "read_pull_request": "≡",
            "read_files": "≡",
            # Add more mappings as needed
        }

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
        max_retries = 3
        retry_count = 0
        self.status.start()
        api_key = UserConfig().api_key
        websocket_host = get_api_host().replace("https://", "wss://").replace("http://", "ws://")
        websocket_url = f"{websocket_host}/ws/tasks/{task_id}/events/"
        headers = {"X-Api-Key": api_key}

        while retry_count < max_retries:
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
                                self.status.hide()
                                if output_file:
                                    await self.write_result_to_file(code, message, output_file)
                                elif print_result:
                                    self.console.print(
                                        markdown_panel(None, message, hide_frame=True)
                                    )
                                self.status.show()
                                return message
                            elif new_status == STATUS_FAILED:
                                self.status.fail()
                                raise click.ClickException(f"Task failed: {self.task.result}")
                        if msg_type == MSG_EVENT:
                            event = json_message.get("data")
                            action = event.get("action")
                            target = event.get("target")
                            if action not in IGNORED_EVENT_ACTIONS and log_messages:
                                character = self.action_character_map.get(action, "✔")
                                if action == "invoke_skill":
                                    self.status.log_message(
                                        event.get("message"),
                                        character=character,
                                        character_color="dim",
                                    )
                                    self.status.indent = 2
                                elif action == "finish_skill":
                                    self.status.indent = 0
                                    self.status.log_message(
                                        "Skill finished",
                                        character=character,
                                        character_color="dim",
                                        dim_text=True,
                                    )
                                elif action == "push_branch" or action == "checkout_branch":
                                    self.status.log_message(
                                        event.get("message"), character=character, dim_text=True
                                    )
                                else:
                                    self.status.log_message(
                                        event.get("message"), character=character
                                    )
                            if str(action).replace("_", "-") == "push-branch":
                                # The agent created a new branch, let's save it to the task object
                                self.task.branch = target.strip()
            except websockets.exceptions.ConnectionClosedError as e:
                if e.code == CloseCode.ABNORMAL_CLOSURE:
                    retry_count += 1
                    self.status.warning("Connection was interrupted, reconnecting...")
                else:
                    self.status.warning(
                        f"Unexpected Connection Error: {str(e.code)} - "
                        f"{str(e)}. Retry {retry_count} of {max_retries}."
                    )
                    await asyncio.sleep(1)

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
