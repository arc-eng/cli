readme:
	poetry run pilot --quiet task --direct -f prompts/README.md.jinja2 -o README.md
	sed -i '' 's/python -m cli.cli/pilot/g' README.md
	git add README.md
	git commit -m "docs: update README.md"
	git push
homebrew:
	# Generate a homebrew formula and open a PR on the tap repository
	poetry run pilot --no-spinner --no-sync --repo=PR-Pilot-AI/pr-pilot-homebrew task -f prompts/homebrew.md.jinja2
commit-hooks:
	# Install pre-commit hooks
	poetry install
	poetry run pre-commit install