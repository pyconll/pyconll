.PHONY: format lint test coveragetest inttest quickinttest datatest build clean hooks

# Format python files in place, outputs error code if there are changes
format:
	python -m black pyconll/ tests/ examples/ scripts/

# Lint check on the files using pylint, yapf, mypy, etc and outputs error code
# if any of them have issues.
lint:
	@failed=""; \
	run() { "$$@" || failed="$$failed\n  $$*"; }; \
	run python -m pylint --rcfile .pylintrc pyconll/; \
	run python -m black --check --quiet pyconll/ tests/ examples/ scripts/; \
	run python -m mypy pyconll/ scripts/ examples/; \
	run codespell pyconll/ docs/ scripts/ examples/ CHANGELOG.md README.md --skip="docs/_build"; \
	if [ -n "$$failed" ]; then \
		printf "\nFailed commands:%b\n" "$$failed"; \
		exit 1; \
	fi

# Unit test scenario for fast CI builds and local testing
unittest:
	python -m pytest -vv --ignore tests/int

# Create coverage analysis for CI builds
coveragetest:
	coverage run --source pyconll -m pytest --ignore tests/int

# Integration test scenario for releases validation and support.
inttest:
	python -m pytest tests/int/ --corpora-skip-write --corpora-versions 2.17 --log-cli-level info

quickinttest:
	python -m pytest tests/int/ --corpora-skip-write --corpora-skip-fixture --corpora-versions 2.17 --log-cli-level info

# Data test scenario across all supported data sets to be run periodically.
datatest:
	python -m pytest tests/int --corpora-skip-write --log-cli-level info
