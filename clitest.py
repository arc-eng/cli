from rich.console import Console
from rich.markdown import Markdown
from rich.measure import measure_renderables
from rich.panel import Panel

console = Console()

if __name__ == "__main__":
    markdown = Markdown("This is a test\n\n")
    width, _ = measure_renderables(console, console.options, [markdown])
    console.print(Panel.fit(markdown, title="Result", width=60))
