readme:
	python -m cli.cli --quiet task --direct -f prompts/README.md.jinja2 -o README.md
	sed -i '' 's/python -m cli.cli/pilot/g' README.md
pr-description:
	python -m cli.cli task -f prompts/generate_pr_description.md.jinja2