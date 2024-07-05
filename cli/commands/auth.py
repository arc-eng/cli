import os
import socket
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import click

API_KEY_FILE = os.path.expanduser("~/.pr_pilot_api_key")


class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/callback?"):
            query = self.path.split("?")[1]
            params = dict(qc.split("=") for qc in query.split("&"))
            api_key = params.get("api_key")
            if api_key:
                with open(API_KEY_FILE, "w") as f:
                    f.write(api_key)
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


@click.command()
def auth():
    """Authenticate the CLI with PR Pilot."""
    host_name = socket.gethostname()
    callback_url = f"http://{host_name}:8043/callback"
    auth_url = f"https://app.pr-pilot.ai/dashboard/cli-auth/?name={host_name}&callback={callback_url}"

    webbrowser.open(auth_url)

    server_address = ("", 8043)
    httpd = HTTPServer(server_address, AuthHandler)
    print("Starting server at http://localhost:8043")
    httpd.serve_forever()

if __name__ == "__main__":
    auth()
