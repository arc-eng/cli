from yaspin import yaspin


class StatusIndicator:

    def __init__(self, visible=True):
        self.spinner = yaspin("Let's go", timer=True)
        self.visible = visible

    def update(self, text):
        self.spinner.text = text

    def success(self):
        if self.visible:
            self.spinner.ok("✅ ")
            self.spinner.start()

    def fail(self):
        if self.visible:
            self.spinner.fail("❌ ")
            self.spinner.stop()

    def start(self):
        if self.visible:
            self.spinner.start()

    def stop(self):
        if self.visible:
            self.spinner.stop()