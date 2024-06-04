readme:
	poetry run python -m cli.cli --direct -f prompts/README.md.jinja2 -o README.md
