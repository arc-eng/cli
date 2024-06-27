# Prompt Templates

## What are Prompt Templates?

Prompt templates in PR Pilot are a superset of [Jinja templates](https://jinja.palletsprojects.com/en/3.1.x/),
with three special functions available:

- `sh`: Execute shell commands and capture the output.
- `env`: Access environment variables.
- `subtask`: Let RP Pilot run a task and capture the output.
- `select`: Select an option from a list.

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

{{ subtask('domain_model.md.jinja2') }}

## Task Lifecycle

{{ subtask('task_lifecycle.md.jinja2') }}
```
You can then run this prompt template using the CLI:

```bash
pilot --direct -f task_processing_docs.md.jinja2 -o docs/task_processing.md
```

This will autonomously generate the documentation for the codebase based on the defined subtasks in the prompt template:
- `-f` specifies the prompt template file
- `-o` specifies the output file where the generated documentation will be saved
- `--direct` tells PR Pilot to render the template directly as output (instead of using it as a prompt)


## Select values from a list with `select`

Using the `select` function, you can present a list of options to the user and capture their selection. 
This is useful for creating interactive prompts that require user input:

```markdown
{% set pod=select('Select a pod', sh('kubectl get pods -o custom-columns=:metadata.name').split('\n')) %}

Here are the last 10 log lines of a Kubernetes pod named `{{ pod }}`:

{{ sh(['kubectl', '--tail=10', 'logs', pod]) }}

---

I want to know:
{{ env('QUESTION_ABOUT_LOGS') }}
```

In this example, the `select` function presents a list of pods retrieved using `kubectl get pods` and captures the user's selection:

```shell
➜ pilot --verbose task -f prompts/investigate-pod.md.jinja2
✔ Running shell command: kubectl get pods -o custom-columns=:metadata.name (0:00:00.22)
[?] Select a pod: 
   nginx-static-cf7f8fd89-dv6pf
   nginx-static-cf7f8fd89-qqvg7
   pr-pilot-app-868489cdf6-5qrt8
   pr-pilot-app-868489cdf6-8qjrk
   pr-pilot-app-868489cdf6-g9lh9
   pr-pilot-db-postgresql-0
   pr-pilot-redis-master-0
 > pr-pilot-worker-0
   pr-pilot-worker-1

✔ Running shell command: kubectl --tail=10 logs pr-pilot-worker-0 (0:00:00.24)
> Question about logs: Do you see any errors?
✔ Task created: a011fcbe-9069-4e34-892e-b89459da1ee1 (0:00:00.00)
✔ Investigate Errors in Kubernetes Pod `pr-pilot-worker-0` Logs (0:00:09.99)
╭────────────────────────────────────────────────────────────────────────────────────── Result ──────────────────────────────────────────────────────────────────────────────────────╮
│ Based on the provided log lines, there are no errors visible. All the log entries are marked with INFO level, indicating normal operation. Here is a summary of the log entries:   │
│                                                                                                                                                                                    │
│   1 A new branch named investigate-the-output was created.                                                                                                                         │
│   2 An HTTP POST request to the OpenAI API was successful (HTTP/1.1 200 OK).                                                                                                       │
│   3 A cost item for a conversation with the model gpt-4o was recorded.                                                                                                             │
│   4 The branch investigate-the-output was deleted because there were no changes.                                                                                                   │
│   5 The latest main branch was checked out.                                                                                                                                        │
│   6 The branch investigate-the-output was deleted.                                                                                                                                 │
│   7 The project PR-Pilot-AI/demo was checked for open source eligibility.                                                                                                          │
│   8 A discount of 0.0% was applied.                                                                                                                                                │
│   9 The total cost was recorded as 4.0 credits.                                                                                                                                    │
│  10 The remaining budget for the user mlamina was recorded as 291.82 credits.                                                                                                      │
│                                                                                                                                                                                    │
│ All these entries indicate normal operations without any errors.                                                                                                                   │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```