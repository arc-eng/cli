<div align="center">
<img src="https://avatars.githubusercontent.com/ml/17635?s=140&v=" width="100" alt="PR Pilot Logo">
</div>

<p align="center">
  <a href="https://github.com/apps/pr-pilot-ai/installations/new"><b>Install</b></a> |
  <a href="https://docs.pr-pilot.ai">Documentation</a> | 
  <a href="https://www.pr-pilot.ai/blog">Blog</a> | 
  <a href="https://www.pr-pilot.ai">Website</a>
</p>

# PR Pilot CLI

PR Pilot gives you a natural language interface for your Github projects.
Given a prompt, it uses LLMs (Large Language Models) to autonomously fulfill tasks by interacting with your code base
and Github issues, enabling a wide variety of ground-breaking AI-assisted automation use cases.

## Installation

 > Make sure you have PR Pilot [installed in your repository](https://github.com/apps/pr-pilot-ai/installations/new)

To install the CLI, run the following command:

```bash
pip install --upgrade pr-pilot-cli
```

By default, the CLI will prompt you to input your API key if it is not already configured.

## Usage

After installation, open a terminal and `ls` into a repository you have installed PR Pilot in and talk to PR Pilot:

### Examples

Translate a file:

```bash
pilot --raw "translate the README into German" > README_German.md
```

Let it write some unit tests:

```bash
pilot "Write some unit tests for the utils.py file."
```

Find some information in your Github issues:

```bash
pilot "Do we have any open Github issues regarding the AuthenticationView class?"
```

For more information, check out our [User Guide](https://docs.pr-pilot.ai/user_guide.html).

### Options and Parameters

You can change the default settings with parameters and options:

```bash
Usage: pilot [OPTIONS] [PROMPT]...

Options:
  --wait / --no-wait  Wait for the result.
  --repo TEXT         Github repository in the format owner/repo.
  --chatty            Print more information.
  --raw               For piping. No pretty-print, no status indicator.
  --help              Show this message and exit.
```


## Features
- **Configuration Management**: Automatically manages API key configuration by prompting the user to input their API key if not already configured.
- **Task Creation**: Users can create tasks by specifying a repository and a prompt. The CLI handles task creation and optionally waits for the result.
- **Result Retrieval**: If the `--wait` option is used, the CLI waits for the task to complete and displays the result directly in the terminal.
- **Dashboard Link**: For tasks that are not awaited, the CLI provides a link to the task's dashboard for further monitoring.


## Configuration
The configuration file is located at `~/.pr-pilot.yaml`.

## Contributing
Contributors are welcome to improve the CLI by submitting pull requests or reporting issues. For more details, check the project's GitHub repository.

## License
The PR Pilot CLI is open-source software licensed under the GPL-3 license.
