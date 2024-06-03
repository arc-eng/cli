<div align="center">
<img src="https://avatars.githubusercontent.com/ml/17635?s=140&v=" width="100" alt="PR Pilot Logo">
</div>

<p align="center">
  <a href="https://github.com/apps/pr-pilot-ai/installations/new"><b>Install</b></a> |
  <a href="https://docs.pr-pilot.ai">Documentation</a> |
  <a href="https://www.pr-pilot.ai/blog">Blog</a> |
  <a href="https://www.pr-pilot.ai">Website</a>
</p>

# PR Pilot Command-Line Interface

[PR Pilot](https://docs.pr-pilot.ai) gives you a natural language interface for your Github projects.
Given a prompt, it uses LLMs (Large Language Models) to autonomously fulfill tasks by interacting with your code base
and Github issues.

Using [prompt templates](./prompts), you can create powerful,
reusable commands that can be executed by PR Pilot.

## 🛠️ Usage

Open a terminal and `ls` into a repository you have [installed](https://github.com/apps/pr-pilot-ai/installations/new) PR Pilot.

In your repository, use the `pilot` command:

```bash
pilot "Tell me about this project!"
```

**📝 Ask PR Pilot to edit a local file for you:**

```bash
pilot --edit cli/cli.py "Make sure all functions and classes have docstrings."
```

**⚡ Generate code quickly and save it as a file:**

```bash
pilot -o test_utils.py --code "Write some unit tests for the utils.py file."
```

**🔍 Capture part of your screen and add it to a prompt:**

```bash
pilot -o component.html --code --snap "Write a Bootstrap5 component that looks like this."
```

**📊 Get an organized view of your Github issues:**

```bash
pilot "Find all open Github issues labeled as 'bug', categorize and prioritize them"
```

**📝 Generate parts of your documentation with a [template](./prompts/README.md.jinja2):**

```bash
pilot --direct -f prompts/README.md.jinja2 -o README.md
```

For more examples, check out the [prompts](./prompts) directory in this repository.

### ⚙️ Options and Parameters

You can customize your interact with PR Pilot using parameters and options:

```bash
Usage: python -m cli.cli [OPTIONS] [PROMPT]...

  Create a new task for PR Pilot - https://docs.pr-pilot.ai

Options:
  --wait / --no-wait        Wait for PR Pilot to finish the task.
  --repo TEXT               Github repository in the format owner/repo.
  --snap                    Select a portion of your screen to add as an image
                            to the task.
  -e, --edit PATH           Let PR Pilot edit a file for you.
  --spinner / --no-spinner  Display a loading indicator.
  --quiet                   Disable all output on the terminal.
  --cheap                   Use the cheapest GPT model (gpt-3.5-turbo)
  --code                    Optimize prompt and settings for generating code
  -f, --file PATH           Generate prompt from a template file.
  --direct                  Do not feed the rendered template as a prompt into
                            PR Pilot, but render it directly as output.
  -o, --output PATH         Output file for the result.
  -m, --model TEXT          GPT model to use.
  --debug                   Display debug information.
  --help                    Show this message and exit.

```

## ⚙️ Configuration
The configuration file is located at `~/.pr-pilot.yaml`. 

```yaml
# Your API Key from https://app.pr-pilot.ai/dashboard/api-keys/
api_key: YOUR_API_KEY

# Default Github repository if not running CLI in a repository directory
default_repo: owner/repo
```

## 🤝 Contributing
Contributors are welcome to improve the CLI by submitting pull requests or reporting issues. For more details, check the project's GitHub repository.

## 📜 License
The PR Pilot CLI is open-source software licensed under the GPL-3 license.