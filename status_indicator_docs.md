# StatusIndicator Class Documentation

## Overview
The `StatusIndicator` class is designed to display status indicators using spinners and console messages. It leverages the `yaspin` library for spinners and the `rich` library for console messages.

## Attributes
- `spinner` (`yaspin.yaspin`): The spinner object for displaying a spinner.
- `visible` (`bool`): Flag to control the visibility of the spinner.
- `messages` (`bool`): Flag to control the visibility of messages.
- `console` (`rich.console.Console`): The console object for displaying messages.

## Methods

### `__init__(self, spinner=True, messages=True, console=None)`
Initializes the `StatusIndicator` with optional spinner and message visibility.

**Parameters:**
- `spinner` (`bool`): Whether to display the spinner. Defaults to `True`.
- `messages` (`bool`): Whether to display messages. Defaults to `True`.
- `console` (`rich.console.Console`, optional): The console object for displaying messages. Defaults to `None`.

### `update(self, text)`
Updates the spinner text or prints a message to the console.

**Parameters:**
- `text` (`str`): The text to update the spinner with or print to the console.

### `success(self)`
Marks the spinner as successful and restarts it.

### `fail(self)`
Marks the spinner as failed and stops it.

### `start(self)`
Starts the spinner.

### `stop(self)`
Stops the spinner.