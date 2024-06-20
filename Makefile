readme:
	poetry run pilot task --direct -f prompts/README.md.jinja2 -o README.md
	sed -i '' 's/python -m cli.cli/pilot/g' README.md
	git add README.md
	git commit -m "docs: update README.md"
	git push
homebrew:
	# Generate a homebrew formula and copy it to the clipboard
	poetry homebrew-formula --quiet --template=homebrew_formula.rb --output=- | pbcopy
commit-hooks:
	# Install pre-commit hooks
	poetry install
	poetry run pre-commit install