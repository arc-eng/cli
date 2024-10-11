# Update the README file using a template and commit the changes
readme:
	poetry run pilot task --direct -f prompts/README.md.jinja2 -o README.md
	sed -i '' 's/python -m cli.cli/pilot/g' README.md
	git add README.md
	git add prompts/README.md.jinja2
	git commit -m "docs: update README.md"
	git push

# Generate a Homebrew formula and copy it to the clipboard
homebrew:
	# Generate a homebrew formula and copy it to the clipboard
	poetry homebrew-formula --quiet --template=homebrew_formula.rb --output=- | pbcopy

# Install pre-commit hooks for the repository
commit-hooks:
	# Install pre-commit hooks
	poetry install
	poetry run pre-commit install
