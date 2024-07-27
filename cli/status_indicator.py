from rich.console import Console
from rich.markdown import Markdown
from yaspin import yaspin


MAX_MSG_LEN = 100


class StatusIndicator:

    def __init__(
        self, spinner=True, display_log_messages=True, console=None, display_spinner_text=True
    ):
        self.spinner = yaspin("Let's go", timer=True)
        self.visible = spinner
        self.display_spinner_text = display_spinner_text
        self.display_log_messages = display_log_messages
        self.console = console if console else Console()

    def update_spinner_message(self, text):
        if self.visible and self.display_spinner_text:
            self.spinner.text = text

    def log_message(self, text):
        if self.display_log_messages:
            self.spinner.hide()
            markdown_txt = Markdown(text)
            self.console.print("[green]✔[/green]", markdown_txt, sep=" ", end=" ")
            self.spinner.show()

    def success(self, start_again=False):
        if self.visible and self.display_log_messages:
            self.log_message(self.spinner.text)
            self.spinner.text = ""
            self.spinner.ok("✔ SUCCESS")
            if start_again:
                self.spinner.start()

    def fail(self):
        if self.visible:
            self.log_message(self.spinner.text)
            self.spinner.text = ""
            self.spinner.fail("❌ FAILURE")
            self.spinner.stop()

    def start(self):
        if self.visible:
            self.spinner.start()

    def stop(self):
        if self.visible:
            self.spinner.stop()
