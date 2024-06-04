# Commands

## Overview
This document provides a detailed description of each command and option available in the PR Pilot CLI.

## Command Descriptions

### `pilot`
Create a new task for PR Pilot.

**Usage:**
```bash
pilot [OPTIONS] [PROMPT]...
```

**Options:**
- `--wait / --no-wait`: Wait for PR Pilot to finish the task.
- `--repo TEXT`: Github repository in the format owner/repo.
- `--snap`: Select a portion of your screen to add as an image to the task.
- `-e, --edit PATH`: Let PR Pilot edit a file for you.
- `--spinner / --no-spinner`: Display a loading indicator.
- `--quiet`: Disable all output on the terminal.
- `--cheap`: Use the cheapest GPT model (gpt-3.5-turbo).
- `--code`: Optimize prompt and settings for generating code.
- `-f, --file PATH`: Generate prompt from a template file.
- `--direct`: Do not feed the rendered template as a prompt into PR Pilot, but render it directly as output.
- `-o, --output PATH`: Output file for the result.
- `-m, --model TEXT`: GPT model to use.
- `--debug`: Display debug information.
- `--help`: Show this message and exit.

## Examples

**Basic Usage:**
```bash
pilot "Tell me about this project!"
```

**Edit a Local File:**
```bash
pilot --edit cli/cli.py "Make sure all functions and classes have docstrings."
```

**Generate Code and Save as a File:**
```bash
pilot -o test_utils.py --code "Write some unit tests for the utils.py file."
```

**Capture Part of Your Screen and Add to a Prompt:**
```bash
pilot -o component.html --code --snap "Write a Bootstrap5 component that looks like this."
```

**Organize Github Issues:**
```bash
pilot "Find all open Github issues labeled as 'bug', categorize and prioritize them"
```

**Generate Documentation with a Template:**
```bash
pilot --direct -f prompts/README.md.jinja2 -o README.md
```
