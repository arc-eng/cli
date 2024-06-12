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
pilot task "Tell me about this project!"
```

**📝 Ask PR Pilot to edit a local file for you:**

```bash
pilot edit cli/cli.py "Make sure all functions and classes have docstrings."
```

**⚡ Generate code quickly and save it as a file:**

```bash
pilot task -o test_utils.py --code "Write some unit tests for the utils.py file."
```

**🔍 Capture part of your screen and add it to a prompt:**

```bash
pilot task -o component.html --code --snap "Write a Bootstrap5 component that looks like this."
```

**📊 Get an organized view of your Github issues:**

```bash
pilot task "Find all open Github issues labeled as 'bug', categorize and prioritize them"
```

**📝 Generate parts of your documentation with a [template](./prompts/README.md.jinja2):**

```bash
pilot task --direct -f prompts/README.md.jinja2 -o README.md
```

To learn more about templates, check out the [prompts](./prompts) directory.

**📝 Execute a step-by-step plan:**

Break down more complex tasks into smaller steps with a plan:

```yaml
# document_cli.yaml

name: Document the CLI
prompt: |
  The CLI is great, but we need a comprehensive user documentation.
  The documentation should be stored as Markdown files in the repository.

steps:
  - name: Identify documentation needs
    output_file: doc_instructions.md
    prompt: |
      1. Read `cli/cli.py`
      2. Identify the key features of the CLI and how it works
      3. List the documentation files that need to be created and outline their content
      4. Create step-by-step instructions for creating the documentation

  - name: Document the CLI
    template: doc_instructions.md
```

Run it with `pilot plan document_cli.yaml`.

### ⚙️ Options and Parameters

The CLI has global parameters and options that can be used to customize its behavior.


```bash
Usage: pilot [OPTIONS] COMMAND [ARGS]...

  PR Pilot CLI - https://docs.pr-pilot.ai

Options:
  --wait / --no-wait        Wait for PR Pilot to finish the task.
  --repo TEXT               Github repository in the format owner/repo.
  --spinner / --no-spinner  Display a loading indicator.
  --quiet                   Disable all output on the terminal.
  -m, --model TEXT          GPT model to use.
  -b, --branch TEXT         Run the task on a specific branch.
  --sync                    Run task on your current branch and pull PR
                            Pilot's changes when done.
  --debug                   Display debug information.
  --help                    Show this message and exit.

Commands:
  edit  Let PR Pilot edit a file for you.
  plan  Let PR Pilot execute a plan for you.
  task  Create a new task for PR Pilot

```

Then there are three sub-commands.

Create a new task for PR Pilot using a prompt or prompt template.

```bash
Usage: pilot task [OPTIONS] [PROMPT]...

  Create a new task for PR Pilot

Options:
  --snap             Select a portion of your screen to add as an image to the
                     task.
  --cheap            Use the cheapest GPT model (gpt-3.5-turbo)
  --code             Optimize prompt and settings for generating code
  -f, --file PATH    Generate prompt from a template file.
  --direct           Do not feed the rendered template as a prompt into PR
                     Pilot, but render it directly as output.
  -o, --output PATH  Output file for the result.
  --help             Show this message and exit.

```

Edit a local file using PR Pilot.

```bash
Usage: pilot edit [OPTIONS] FILE_PATH PROMPT

  Let PR Pilot edit a file for you.

Options:
  --help  Show this message and exit.

```

Run a step-by-step plan with PR Pilot.

```bash
Usage: pilot plan [OPTIONS] FILE_PATH

  Let PR Pilot execute a plan for you.

Options:
  --help  Show this message and exit.

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