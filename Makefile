.PHONY: format lint test coveragetest inttest build gendocs clean hooks

# Format python files in place, outputs error code if there are changes
format:
	yapf -pri -e *.conllu pyconll/ tests/

# Lint check on the files using pylint and yapf, outputs error code if either complains
lint:
	pylint --rcfile .pylintrc pyconll/ && \
	yapf -prq -e *.conllu pyconll/ tests/

# Unit test scenario for fast CI builds and local testing
test:
	python -m pytest -vv --ignore tests/int

# Create coverage analysis for CI builds
coveragetest:
	coverage run --source pyconll -m pytest --ignore tests/int

# Integration test scenario for releases validation and support.
inttest:
	python -m pytest tests/int/test_corpora.py::test_ud_v2_6_data --log-cli-level info

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

hooks:
	find .githooks -type f -exec ln -sf ../../{} .git/hooks/ \;
