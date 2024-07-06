import os
import socket
import socketserver
import webbrowser
from http.server import BaseHTTPRequestHandler

import click
import yaml
from rich.console import Console
from rich.prompt import Confirm

from cli.constants import CONFIG_LOCATION, CONFIG_API_KEY
from cli.util import get_api_host

PORT = 8043
API_KEY_PARAM = "key"
console = Console()


class AuthHandler(BaseHTTPRequestHandler):

    api_key = None

    def log_message(self, format, *args):
        # Override to mute the server output
        pass

    def do_GET(self):
        if self.path.startswith("/callback?"):
            query = self.path.split("?")[1]
            params = dict(qc.split("=") for qc in query.split("&"))
            api_key = params.get(API_KEY_PARAM)
            if api_key:
                AuthHandler.api_key = api_key
                console.print("[green]Authentication successful[/green]")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"API key saved. You can close this window.")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"API key not found in the request.")
        else:
            self.send_response(404)
            self.end_headers()


class UserConfig:
    """Class to manage user configuration settings."""

    def __init__(self, config_location: str = CONFIG_LOCATION):
        self.config_location = config_location
        self.config = {}
        self.load_config()

    def set(self, key, value):
        """Set a value in the configuration file."""
        self.config[key] = value

        with open(self.config_location, "w") as f:
            f.write(yaml.dump(self.config))
        console.print(
            f"Set [code]{key}[/code] to [code]{value}[/code] in [code]{CONFIG_LOCATION}[/code]"
        )

    def get(self, param):
        return self.config.get(param)

    def load_config(self):
        """Load the configuration from the default location. If it doesn't exist,
        run through the auth process and save config."""
        if os.path.exists(self.config_location):
            # Config file exists, load it
            with open(self.config_location) as f:
                self.config = yaml.safe_load(f)
            if os.getenv("PR_PILOT_API_KEY"):
                # Override the config file with the environment variable
                self.config[CONFIG_API_KEY] = os.getenv("PR_PILOT_API_KEY")
            return

        # Config file does not exist, create it
        if not os.getenv("PR_PILOT_API_KEY"):
            console.print(
                "[bold yellow]No configuration file found. "
                "Starting authentication ...[/bold yellow]"
            )
            self.config = {CONFIG_API_KEY: self.authenticate()}
            self.collect_user_preferences()
            with open(self.config_location, "w") as f:
                f.write(yaml.dump(self.config))
        else:
            console.print("[dim]Using API key from environment variable PR_PILOT_API_KEY[/dim]")
            self.config = {CONFIG_API_KEY: os.getenv("PR_PILOT_API_KEY")}

    def set_api_key_env_var(self):
        """Set the API key as an environment variable."""
        os.environ["PR_PILOT_API_KEY"] = self.api_key

    def collect_user_preferences(self):
        console.print(
            "Since it's the first time you're using PR Pilot, " "let's set some default values."
        )
        auto_sync = Confirm.ask(
            "When a new PR/branch is created, do you want it checked out automatically?",
            default=True,
        )
        self.set("auto_sync", auto_sync)
        verbose = Confirm.ask("Do you want to see detailed status messages?", default=True)
        self.set("verbose", verbose)
        console.print("Done! Change these values any time with [code]pilot config edit[/code]")

    @property
    def api_key(self):
        if CONFIG_API_KEY not in self.config:
            self.authenticate()
        return self.config[CONFIG_API_KEY]

    @property
    def auto_sync_enabled(self):
        return self.config.get("auto_sync", False)

    @property
    def verbose(self):
        return self.config.get("verbose", False)

    def authenticate(self) -> str:
        """Authenticate the CLI with PR Pilot."""
        key_name = f"CLI on {socket.gethostname()}"
        callback_url = f"http://localhost:{PORT}/callback"
        auth_url = f"{get_api_host()}/dashboard/cli-auth/?name={key_name}&callback={callback_url}"

        confirmed = Confirm.ask(
            "You'll login with your Github account and we'll create an API key for you. Continue?",
            default=True,
        )
        if not confirmed:
            raise click.Abort()

        webbrowser.open(auth_url)
        with socketserver.TCPServer(("", PORT), AuthHandler) as httpd:
            console.print("Waiting for API key ...")
            httpd.handle_request()
        if AuthHandler.api_key:
            return AuthHandler.api_key
        else:
            console.print("[red]Authentication failed[/red]")
            raise click.Abort()
