readme:
	poetry run pilot --quiet task --direct -f prompts/README.md.jinja2 -o README.md
	sed -i '' 's/python -m cli.cli/pilot/g' README.md
pr-description:
	poetry run pilot task -f prompts/generate_pr_description.md.jinja2
homebrew:
	poetry run pilot --no-sync --repo=PR-Pilot-AI/pr-pilot-homebrew task -f prompts/homebrew.md.jinja2
