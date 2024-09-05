from rich.console import Console
from rich.markdown import Markdown
from yaspin import yaspin


MAX_MSG_LEN = 100


class StatusIndicator:

    def __init__(
        self,
        spinner=True,
        display_log_messages=True,
        console=None,
        display_spinner_text=True,
        indent=0,
    ):
        self.spinner = yaspin("Let's go", timer=True)
        self.visible = spinner
        self.display_spinner_text = display_spinner_text
        self.display_log_messages = display_log_messages
        self.console = console if console else Console()
        self.indent = indent

    def update_spinner_message(self, text):
        if self.visible and self.display_spinner_text:
            self.spinner.text = text

    def hide(self):
        if self.visible:
            self.spinner.hide()

    def show(self):
        if self.visible:
            self.spinner.show()

    def log_message(self, text, character="✔", color="green", dim=False):
        if self.display_log_messages:
            self.hide()
            markdown_txt = Markdown(text)
            if dim:
                color = f"dim {color}"
                markdown_txt = Markdown(text, style="dim")
            indent_space = " " * self.indent
            self.console.print(
                f"{indent_space}[{color}]{character}[/{color}]", markdown_txt, sep=" ", end=" "
            )
            self.show()

    def warning(self, message):
        return self.log_message(message, "!", "yellow")

    def success(self, start_again=False, message="SUCCESS"):
        if self.visible and self.display_log_messages:
            self.log_message(self.spinner.text)
            self.spinner.text = ""
            self.spinner.ok(f"✔ {message}")
            if start_again:
                self.spinner.start()

    def fail(self, error=""):
        if self.visible:
            self.log_message(self.spinner.text)
            self.spinner.text = error
            self.spinner.fail("❌ FAILURE")
            self.spinner.stop()

    def start(self):
        if self.visible:
            self.spinner.start()

    def stop(self):
        if self.visible:
            self.spinner.stop()
