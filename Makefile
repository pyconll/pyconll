.PHONY: format lint test coveragetest inttest datatest build gendocs clean hooks

# Format python files in place, outputs error code if there are changes
format:
	python -m yapf -pri -e *.conllu pyconll/ util/ tests/

# Lint check on the files using pylint, yapf, mypy, etc and outputs error code
# if any of them have issues.
lint:
	python -m pylint --rcfile .pylintrc pyconll/ util/ && \
	codespell pyconll/ docs/ && \
	python -m yapf -prq pyconll/ util/ tests/ && \
	python -m mypy pyconll/ util/

# Unit test scenario for fast CI builds and local testing
test:
	python -m pytest -vv --ignore tests/int

# Create coverage analysis for CI builds
coveragetest:
	coverage run --source pyconll -m pytest --ignore tests/int

# Integration test scenario for releases validation and support.
inttest:
	python -m pytest tests/int/ -m latest --log-cli-level info

# Data test scenario across all supported data sets to be run periodically.
datatest:
	python -m pytest tests/int --log-cli-level info

build:
	python setup.py sdist bdist_wheel

gendocs:
	pandoc --from=markdown --to=rst --output=README.rst README.md
	pandoc --from=markdown --to=plain --output=README README.md
	pandoc --from=markdown --to=rst --output=CHANGELOG.rst CHANGELOG.md
	pandoc --from=markdown --to=plain --output=CHANGELOG CHANGELOG.md

clean:
	if [ -d 'dist' ]; then \
		rm -r dist; \
	fi

	if [ -d 'build' ]; then \
		rm -r build; \
	fi

	if [ -d 'pyconll.egg-info' ]; then \
		rm -r pyconll.egg-info; \
	fi