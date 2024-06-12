readme:
	python -m cli.cli task --direct -f prompts/README.md.jinja2 -o README.md
pr-description:
	python -m cli.cli task -f prompts/generate_pr_description.md.jinja2