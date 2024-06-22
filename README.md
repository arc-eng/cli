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
[![Unit Tests](https://github.com/PR-Pilot-AI/pr-pilot-cli/actions/workflows/unit_tests.yml/badge.svg)][tests]
[![PyPI](https://img.shields.io/pypi/v/pr-pilot-cli.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/pr-pilot-cli)][pypi status]
[![License](https://img.shields.io/pypi/l/pr-pilot-cli)][license]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
<br>

[pypi status]: https://pypi.org/project/pr-pilot-cli/
[tests]: https://github.com/PR-Pilot-AI/pr-pilot-cli/actions/workflows/unit_tests.yml
[codecov]: https://app.codecov.io/gh/magmax/python-inquirer
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black
[license]: https://github.com/PR-Pilot-AI/pr-pilot-cli/blob/main/LICENSE

[PR Pilot](https://docs.pr-pilot.ai) assists you in your daily workflow.

With a **simple and intuitive CLI**:
```bash
pilot edit main.py "Add docstrings to all functions and classes"
```

**It works with [the dev tools you trust and love](https://docs.pr-pilot.ai/integrations.html)** - exactly when and where you want it.

```bash
pilot task "Find all bug issues on Github and Linear opened yesterday, post them to #bugs-daily on Slack."
```

[Prompt templates](https://github.com/PR-Pilot-AI/pr-pilot-cli/tree/main/prompts) let you can create powerful,
**executable prompt-based commands**, defined as Jinja templates:

```markdown
I've made some changes and opened a new PR: #{{ env('PR_NUMBER') }}.

I need a PR title and a description that summarizes these changes in short, concise bullet points.
The PR description will also be used as merge commit message, so it should be clear and informative.

Use the following guidelines:

- Start title with a verb in the imperative mood (e.g., "Add", "Fix", "Update").
- At the very top, provide 1-sentence summary of the changes and their impact.
- Below, list the changes made in bullet points.

# Your task
Edit PR #{{ env('PR_NUMBER') }} title and description to reflect the changes made in this PR.
```

Send PR Pilot off to give any PR a title and description **according to your guidelines**:

```bash
➜ PR_NUMBER=153 pilot task -f generate-pr-description.md.jinja2 --save-command
✔ Task created: 7d5573d2-2717-4a96-8bae-035886420c74 (0:00:00.00)
✔ Update PR #153 title and description to reflect changes made (0:00:17.87)
╭──────────────────────────── Result ──────────────────────────────────────────╮
│ The PR title and description have been updated. You can view the PR here.    │
╰──────────────────────────────────────────────────────────────────────────────╯
```

The `--save-command` parameter makes this call **re-usable**:

```bash
➜ pilot task -f generate-pr-description.md.jinja2 --save-command

 Save the task parameters as a command:

  Name (e.g. generate-pr-desc): pr-description
  Short description: Generate title and description for a pull request

 Command saved to .pilot-commands.yaml
```

You can now run this command **for any PR** with `pilot run pr-description`:

```bash
➜ pilot run pr-description
Enter value for PR_NUMBER: 83
╭──────────── Result ─────────────╮
│ Here is the link to the PR #83  │
╰─────────────────────────────────╯
```

To learn more, please visit our **[User Guide](https://docs.pr-pilot.ai/user_guide.html)** and **[demo repository](https://github.com/PR-Pilot-AI/demo/tree/main)**.

## 📦 Installation
First, make sure you have [installed](https://github.com/apps/pr-pilot-ai/installations/new) PR Pilot in your repository.

Then, install the CLI using one of the following methods:

### pip
```
pip install --upgrade pr-pilot-cli
```

### Homebrew:
```
brew tap pr-pilot-ai/homebrew-tap
brew install pr-pilot-cli
```


## 🛠️ Usage

In your repository, use the `pilot` command:

```bash
pilot task "Tell me about this project!"
# 📝 Ask PR Pilot to edit a local file for you:
pilot edit cli/cli.py "Make sure all functions and classes have docstrings."
# ⚡ Generate code quickly and save it as a file:
pilot task -o test_utils.py --code "Write some unit tests for the utils.py file."
# 🔍 Capture part of your screen and add it to a prompt:
pilot task -o component.html --code --snap "Write a Bootstrap5 component that looks like this."
# 📊 Get an organized view of your Github issues:
pilot task "Find all open Github issues labeled as 'bug', categorize and prioritize them"
# 📝 Ask PR Pilot to analyze your test results using prompt templates:
pilot task -f prompts/analyze-test-results.md.jinja2
```

For more detailed examples, please visit our **[demo repository](https://github.com/PR-Pilot-AI/demo/tree/main)**.


### ⬇️ Grab commands from other repositories

Once saved in a repository, commands can be grabbed from anywhere:

```bash
➜  code pilot grab commands pr-pilot-ai/core

       pr-pilot-ai/core
       haiku             Writes a Haiku about your project
       test-analysis     Run unit tests, analyze the output & provide suggestions
       daily-report      Assemble a comprehensive daily report & send it to Slack
       pr-description    Generate PR Title & Description
       house-keeping     Organize & clean up cfg files (package.json, pom.xml, etc)
       readme-badges     Generate badges for your README file

[?] Grab:
   [ ] haiku
   [X] test-analysis
   [ ] daily-report
 > [X] pr-description
   [ ] house-keeping
   [ ] readme-badges


You can now use the following commands:

  pilot run test-analysis   Run unit tests, analyze the output & provide suggestions
  pilot run pr-description  Generate PR Title & Description
```

Our **[core repository](https://github.com/PR-Pilot-AI/core)** contains an ever-growing, curated list of commands
that we tested and handcrafted for you. You can grab them and use them in your own repositories.

### 📝 Execute a step-by-step plan

Break down more complex tasks into smaller steps with a plan:

```yaml
# add_page.yaml

name: Add a TODO Page
prompt: |
  We are adding a TODO page to the application.
  Users should be able to:
  - See a list of their TODOs
  - Cross of TODO items / mark them as done
  - Add new TODO items

steps:
  - name: Create HTML template
    prompt: |
      1. Look at templates/users.html to understand the basic structure
      2. Create templates/todo.html based on the example
  - name: Create view controller
    prompt: |
      The controller should handle all actions/calls from the UI.
      1. Look at views/users.py to understand the basic structure
      2. Create views/todo.py based on the example
  - name: Integrate the page
    prompt: |
      Integrate the new page into the application:
      1. Add a new route in urls.py, referencing the new view controller
      2. Add a new tab to the navigation in templates/base.html
  - name: Generate PR description
    template: prompts/generate-pr-description.md.jinja2
```
You can run this plan with:
```bash
pilot plan add_page.yaml
```

PR Pilot will then autonomously:
* Create a new branch and open a PR
* Implement the HTML template and view controller
* Integrate the new page into the navigation
* Look at all changes and create a PR description based on your preferences defined in `prompts/generate-pr-description.md.jinja2`

Save this as part of your code base. Next time you need a new page, simply adjust the plan and run it again.
If you don't like the result, simply close the PR and delete the branch.

You can iterate on the plan until you are satisfied with the result.

### ⚙️ Options and Parameters

The CLI has global parameters and options that can be used to customize its behavior.


```bash
Usage: pilot [OPTIONS] COMMAND [ARGS]...

  PR Pilot CLI - https://docs.pr-pilot.ai

  Delegate routine work to AI with confidence and predictability.

Options:
  --wait / --no-wait        Wait for PR Pilot to finish the task.
  --repo TEXT               Github repository in the format owner/repo.
  --spinner / --no-spinner  Display a loading indicator.
  --verbose                 Display status messages
  -m, --model TEXT          GPT model to use.
  -b, --branch TEXT         Run the task on a specific branch.
  --sync / --no-sync        Run task on your current branch and pull PR Pilots
                            changes when done.
  --debug                   Display debug information.
  --help                    Show this message and exit.

Commands:
  config   🔧 Customize PR Pilots behavior.
  edit     ✍️ Let PR Pilot edit a file for you.
  grab     🤲 Grab commands, prompts and plans from other repositories.
  history  📜 Access recent tasks.
  plan     📋 Let PR Pilot execute a plan for you.
  run      🚀 Run a saved command.
  task     ➕ Create a new task for PR Pilot.
  upgrade  ⬆️ Upgrade pr-pilot-cli to the latest version.

```

#### Commands

Hand over a task to PR Pilot.

```bash
Usage: pilot task [OPTIONS] [PROMPT]

  ➕ Create a new task for PR Pilot.

  Examples: https://github.com/pr-pilot-ai/pr-pilot-cli

Options:
  --snap             📸 Select a portion of your screen to add as an image to
                     the task.
  --cheap            💸 Use the cheapest GPT model (gpt-3.5-turbo)
  --code             💻 Optimize prompt and settings for generating code
  -f, --file PATH    📂 Generate prompt from a template file.
  --direct           🔄 Do not feed the rendered template as a prompt into PR
                     Pilot, but render it directly as output.
  -o, --output PATH  💾 Output file for the result.
  --save-command     💾 Save the task parameters as a command for later use.
  --help             Show this message and exit.

```

Let PR Pilot edit a file for you.

```bash
Usage: pilot edit [OPTIONS] FILE_PATH [PROMPT]

  ✍️ Let PR Pilot edit a file for you.

  Examples:

  - ✍️ Quickly add docstrings to a Python file:
    pilot edit main.py "Add docstrings for all classes, functions and parameters"

  - ♻️ Refactor and clean up code:
    pilot edit main.js "Break up large functions, organize the file and add comments"

  - 🧩 Implement placeholders:
    pilot edit "I left placeholder comments in the file. Please replace them with the actual code"

Options:
  --snap  📸 Add a screenshot to your prompt.
  --help  Show this message and exit.

```

Let PR Pilot execute a step-by-step plan.

```bash
Usage: pilot plan [OPTIONS] FILE_PATH

  📋 Let PR Pilot execute a plan for you.

  Learn more: https://docs.pr-pilot.ai/user_guide.html

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

# Enabled --sync by default
auto_sync: true

# Suppress status messages by default
verbose: false
```

## 🤝 Contributing
Contributors are welcome to improve the CLI by submitting pull requests or reporting issues. For more details, check the project's GitHub repository.

## 📜 License
The PR Pilot CLI is open-source software licensed under the GPL-3 license.
