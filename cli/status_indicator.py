from rich.console import Console
from yaspin import yaspin


class StatusIndicator:
    """
    Eine Klasse zur Anzeige von Statusindikatoren mit Spinners und Konsolennachrichten.

    Attribute:
        spinner (yaspin.yaspin): Das Spinner-Objekt zur Anzeige eines Spinners.
        visible (bool): Flag zur Steuerung der Sichtbarkeit des Spinners.
        messages (bool): Flag zur Steuerung der Sichtbarkeit von Nachrichten.
        console (rich.console.Console): Das Konsolenobjekt zur Anzeige von Nachrichten.
    """

    def __init__(self, spinner=True, messages=True, console=None):
        """
        Initialisiert den StatusIndicator mit optionaler Spinner- und Nachrichtensichtbarkeit.

        Args:
            spinner (bool): Ob der Spinner angezeigt werden soll. Standardmäßig True.
            messages (bool): Ob Nachrichten angezeigt werden sollen. Standardmäßig True.
            console (rich.console.Console, optional): Das Konsolenobjekt zur Anzeige von Nachrichten. Standardmäßig None.
        """
        self.spinner = yaspin("Let's go", timer=True)
        self.visible = spinner
        self.messages = messages
        self.console = console if console else Console()

    def update(self, text):
        """
        Aktualisiert den Spinner-Text oder druckt eine Nachricht auf die Konsole.

        Args:
            text (str): Der Text, mit dem der Spinner aktualisiert oder der auf der Konsole gedruckt wird.
        """
        if self.visible:
            self.spinner.text = text
        elif self.messages:
            self.console.print(f"[bold]>[/bold] {text}")

    def success(self):
        """
        Markiert den Spinner als erfolgreich und startet ihn neu.
        """
        if self.visible:
            self.spinner.ok("✅ ")
            self.spinner.start()

    def fail(self):
        """
        Markiert den Spinner als fehlgeschlagen und stoppt ihn.
        """
        if self.visible:
            self.spinner.fail("❌ ")
            self.spinner.stop()

    def start(self):
        """
        Startet den Spinner.
        """
        if self.visible:
            self.spinner.start()

    def stop(self):
        """
        Stoppt den Spinner.
        """
        if self.visible:
            self.spinner.stop()
