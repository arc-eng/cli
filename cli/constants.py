import os

CONFIG_LOCATION = os.path.expanduser("~/.pr-pilot.yaml")
CONFIG_API_KEY = "api_key"
CODE_MODEL = "gpt-4o"
CHEAP_MODEL = "gpt-3.5-turbo"
POLL_INTERVAL = 2
CODE_PRIMER = (
    "Do not write anything to file, but ONLY respond with the code/content, no other text. "
    "Do not wrap it in triple backticks."
)
DEFAULT_MODEL = "gpt-4o"
