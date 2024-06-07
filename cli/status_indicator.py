from rich.console import Console
from yaspin import yaspin


class StatusIndicator:
    """
    A class to display status indicators using spinners and console messages.

    Attributes:
        spinner (yaspin.yaspin): The spinner object for displaying a spinner.
        visible (bool): Flag to control the visibility of the spinner.
        messages (bool): Flag to control the visibility of messages.
        console (rich.console.Console): The console object for displaying messages.
    """

    def __init__(self, spinner=True, messages=True, console=None):
        """
        Initializes the StatusIndicator with optional spinner and message visibility.

        Args:
            spinner (bool): Whether to display the spinner. Defaults to True.
            messages (bool): Whether to display messages. Defaults to True.
            console (rich.console.Console, optional): The console object for displaying messages. Defaults to None.
        """
        self.spinner = yaspin("Let's go", timer=True)
        self.visible = spinner
        self.messages = messages
        self.console = console if console else Console()

    def update(self, text):
        """
        Updates the spinner text or prints a message to the console.

        Args:
            text (str): The text to update the spinner with or print to the console.
        """
        if self.visible:
            self.spinner.text = text
        elif self.messages:
            self.console.print(f"[bold]>[/bold] {text}")

    def success(self):
        """
        Marks the spinner as successful and restarts it.
        """
        if self.visible:
            self.spinner.ok("✅ ")
            self.spinner.start()

    def fail(self):
        """
        Marks the spinner as failed and stops it.
        """
        if self.visible:
            self.spinner.fail("❌ ")
            self.spinner.stop()

    def start(self):
        """
        Starts the spinner.
        """
        if self.visible:
            self.spinner.start()

    def stop(self):
        """
        Stops the spinner.
        """
        if self.visible:
            self.spinner.stop()