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

[PR Pilot](https://docs.pr-pilot.ai) assist you in your daily workflow and works with the dev tools you trust and love - exactly when and where you want it.

```bash
pilot edit main.py "Add docstrings to all functions and classes"
```

With [prompt templates](https://github.com/PR-Pilot-AI/pr-pilot-cli/tree/main/prompts), you can create powerful,
reusable commands:

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

Send PR Pilot off to give any PR a title and description according to your guidelines:

```bash
PR_NUMBER=153 pilot task -f generate-pr-description.md.jinja2
```


## 📦 Installation

Two options are available for installing the CLI:


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

  Examples:

  - 📸 Create a Bootstrap5 component based on a screenshot:
    pilot task -o component.html --code --snap "Write a Bootstrap5 component that looks like this."

  - 🛠️ Refactor and clean up code:
    pilot edit main.js "Break up large functions, organize the file and add comments."

  - 🔄 Interact across services and tools:
    pilot task "Find all open Linear and Github issues labeled as 'bug' and send them to the #bugs Slack channel."

Options:
  --wait / --no-wait        Wait for PR Pilot to finish the task.
  --repo TEXT               Github repository in the format owner/repo.
  --spinner / --no-spinner  Display a loading indicator.
  --quiet / --chatty        Disable all status messages.
  -m, --model TEXT          GPT model to use.
  -b, --branch TEXT         Run the task on a specific branch.
  --sync / --no-sync        Run task on your current branch and pull PR
                            Pilot's changes when done.
  --debug                   Display debug information.
  --help                    Show this message and exit.

Commands:
  edit     ✍️ Let PR Pilot edit a file for you.
  history  📜 Access recent tasks.
  plan     📋 Let PR Pilot execute a plan for you.
  task     🛠️ Create a new task for PR Pilot.

```

#### Commands

Hand over a task to PR Pilot.

```bash
Usage: pilot task [OPTIONS] [PROMPT]

  🛠️ Create a new task for PR Pilot.

  Examples:

  - Generate unit tests for a Python file:
    pilot task -o test_utils.py --code "Write some unit tests for the utils.py file."

  - Create a Bootstrap5 component based on a screenshot:
    pilot task -o component.html --code --snap "Write a Bootstrap5 component that looks like this."

  - Send a list of all bug issues to Slack:
    pilot task "Find all open Github issues labeled as 'bug' and send them to the #bugs Slack channel."

Options:
  --snap             📸 Select a portion of your screen to add as an image to
                     the task.
  --cheap            💸 Use the cheapest GPT model (gpt-3.5-turbo)
  --code             💻 Optimize prompt and settings for generating code
  -f, --file PATH    📂 Generate prompt from a template file.
  --direct           🔄 Do not feed the rendered template as a prompt into PR
                     Pilot, but render it directly as output.
  -o, --output PATH  💾 Output file for the result.
  --help             Show this message and exit.

```

Let PR Pilot edit a file for you.

```bash
Usage: pilot edit [OPTIONS] FILE_PATH [PROMPT]

  ✍️ Let PR Pilot edit a file for you.

  Examples:

  - ✍️ Quickly add docstrings to a Python file:
    pilot edit main.py "Add docstrings for all classes, functions and parameters."

  - ♻️ Refactor and clean up code:
    pilot edit main.js "Break up large functions, organize the file and add comments."

  - 🧩 Implement placeholders:
    pilot edit "I left placeholder comments in the file. Please replace them with the actual code."

Options:
  --snap  📸 Add a screenshot to your prompt.
  --help  Show this message and exit.

```

Let PR Pilot execute a step-by-step plan.

```bash
Usage: pilot plan [OPTIONS] FILE_PATH

  📋 Let PR Pilot execute a plan for you.

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
quiet: true
```

## 🤝 Contributing
Contributors are welcome to improve the CLI by submitting pull requests or reporting issues. For more details, check the project's GitHub repository.

## 📜 License
The PR Pilot CLI is open-source software licensed under the GPL-3 license.