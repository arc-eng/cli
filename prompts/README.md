# Prompt Templates

## What are Prompt Templates?

Prompt templates in PR Pilot are a superset of [Jinja templates](https://jinja.palletsprojects.com/en/3.1.x/),
with three special functions available:

- `sh`: Execute shell commands and capture the output.
- `env`: Access environment variables.
- `subtask`: Let RP Pilot run a task and capture the output.

## Example of a Prompt Template

An example of a prompt template is [analyze_test_results.md.jinja2](./analyze_test_results.md.jinja2). This template is designed to help analyze and 
report the results of unit tests. Here's a breakdown of its content:

```markdown
We ran our unit tests, here's the output:

---
{{ sh('pytest') }}
---

If the tests are green, do nothing. Otherwise:
1. Identify the parts of the code that are not working.
2. Read the relevant files to get a better understanding of the problem.
3. Write a short, concise, structured analysis of the test results.
{% if env('PR_NUMBER') %}
4. Comment on PR #{{ env('PR_NUMBER') }} with the analysis.
{% endif %}
```

### Explanation:

The goal is to dynamically generate a prompt that includes the output of running unit tests and provides instructions 
for PR Pilot on how to analyze the results. Here's what each part does:

- `{{ sh('pytest') }}`: This line dynamically inserts the output of the `pytest` command, which runs unit tests.
- `{% if env('PR_NUMBER') %}`: This conditional block checks if a PR number is set in the environment (e.g. when run as a Github Action). If it is, it includes a step to comment on the PR with the analysis of the test results.

## How to Use Prompt Templates

To use a prompt template, you can pass it as a file to PR Pilot using the `-f` or `--file` option. For example:

```bash
pilot -f analyze_test_results.md.jinja2
```

This will trigger the following:
1. Run the tests in the local environment
2. Capture the output of the tests as part of the prompt
3. Send the prompt to PR Pilot, where it will autonomously:
    1. Read the test results and identify failing parts
    2. Read the relevant files to understand the problem
    3. Write a structured analysis of the test results
    4. Optionally, comment on the PR with the analysis if a PR number is provided in the environment.

## Crafting Powerful Multi-Step Prompts with `subtask`

The `subtask` function allows you to run a task within a prompt template and capture the output. This enables you 
to dynamically generate complex documents or instructions by combining smaller, well-defined tasks.

### Example: Generating Code Documentation

Suppose you want to generate documentation for a codebase. You can create a document template that includes
multiple subtasks for generating documentation for different parts of the codebase. 

Here's a simplified example:

```markdown
# Task Processing in PR Pilot

The lifecycle of a task within PR Pilot involves several key components: `TaskEngine`, `TaskScheduler`, and `TaskWorker`.

## Domain Model

{% set domain_model_prompt %}
Read the following files:
- engine/task_engine.py
- engine/task_scheduler.py
- engine/task_worker.py
- engine/task.py

Generate a Mermaid class diagram to illustrate the domain model of the task processing in PR Pilot. Add a clear and concise text description.
{% endset %}

{{ subtask(domain_model_prompt) }}

## Task Lifecycle

{% set diagram_prompt %}
Read the following files:
- engine/task_engine.py
- engine/task_scheduler.py
- engine/task_worker.py

Generate a Mermaid sequence diagram to illustrate how these components work together to execute a task. 
Add a clear and concise text describing the interplay of the components.
{% endset %}

{{ subtask(diagram_prompt) }}
```

In this example, the `subtask` function is used to generate a class diagram and a sequence diagram for the codebase.
For better readability and maintainability, the prompts could even be stored in their own separate files and included in the main prompt template:

```markdown
# Task Processing in PR Pilot

The lifecycle of a task within PR Pilot involves several key components: `TaskEngine`, `TaskScheduler`, and `TaskWorker`.

## Domain Model

{{ include('domain_model.md.jinja2') }}

## Task Lifecycle

{{ include('task_lifecycle.md.jinja2') }}
```
You can then run this prompt template using the CLI:

```bash
pilot --direct -f task_processing_docs.md.jinja2 -o docs/task_processing.md
```

This will autonomously generate the documentation for the codebase based on the defined subtasks in the prompt template:
- `-f` specifies the prompt template file
- `-o` specifies the output file where the generated documentation will be saved
- `--direct` tells PR Pilot to render the template directly as output (instead of using it as a prompt)