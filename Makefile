.PHONY: format lint test coveragetest inttest quickinttest datatest build clean hooks

# Format python files in place, outputs error code if there are changes
format:
	python -m black pyconll/ tests/ examples/ scripts/

# Lint check on the files using pylint, yapf, mypy, etc and outputs error code
# if any of them have issues.
lint:
	python -m pylint --rcfile .pylintrc pyconll/ && \
	codespell pyconll/ docs/ scripts/ && \
	python -m black --check --quiet pyconll/ tests/ examples/ scripts/ && \
	python -m mypy pyconll/ scripts/

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

build:
	python -m build --sdist --wheel

clean:
	find . -path ./venv -prune -o -type d -name "__pycache__" -exec rm -rf {} +

	if [ -d 'dist' ]; then \
		rm -r dist; \
	fi

	if [ -d 'build' ]; then \
		rm -r build; \
	fi

	if [ -d 'pyconll.egg-info' ]; then \
		rm -r pyconll.egg-info; \
	fi