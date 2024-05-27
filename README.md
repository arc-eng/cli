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

The PR Pilot CLI is a command-line interface tool designed to interact with the PR Pilot API. 
It allows users to quickly hand over work to PR Pilot from the command line.

## Features
- **Configuration Management**: Automatically manages API key configuration by prompting the user to input their API key if not already configured.
- **Task Creation**: Users can create tasks by specifying a repository and a prompt. The CLI handles task creation and optionally waits for the result.
- **Result Retrieval**: If the `--wait` option is used, the CLI waits for the task to complete and displays the result directly in the terminal.
- **Dashboard Link**: For tasks that are not awaited, the CLI provides a link to the task's dashboard for further monitoring.

## Installation

 > Make sure you have PR Pilot [installed in your repository](https://github.com/apps/pr-pilot-ai/installations/new)

To install the CLI, run the following command:

```bash
pip install --upgrade pr-pilot-cli
```

## Usage

After installation, create tasks using the following command:

```bash
pr-pilot --wait <repo> <prompt>
```

Replace `<repo>` and `<prompt>` with the appropriate repository and task prompt.

## Configuration
The configuration file is located at `~/.pr-pilot.yaml`.

## Contributing
Contributors are welcome to improve the CLI by submitting pull requests or reporting issues. For more details, check the project's GitHub repository.

## License
The PR Pilot CLI is open-source software licensed under the GPL-3 license.
