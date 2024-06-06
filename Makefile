readme:
	python -m cli.cli --direct -f prompts/README.md.jinja2 -o README.md
pr-description:
	python -m cli.cli -f prompts/generate_pr_description.md.jinja2