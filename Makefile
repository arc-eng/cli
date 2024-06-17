readme:
	poetry run pilot --quiet task --direct -f prompts/README.md.jinja2 -o README.md
	sed -i '' 's/python -m cli.cli/pilot/g' README.md
	git add README.md
	git commit -m "docs: update README.md"
	git push
pr-description:
	poetry run pilot --no-spinner task -f prompts/generate_pr_description.md.jinja2
homebrew:
	poetry run pilot --no-sync --repo=PR-Pilot-AI/pr-pilot-homebrew task -f prompts/homebrew.md.jinja2
daily-report:
	# Generate daily report
	poetry run pilot task -f prompts/slack-report.md.jinja2