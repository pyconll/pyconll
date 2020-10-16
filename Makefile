.PHONY: format lint test coveragetest inttest build gendocs clean hooks

format:
	yapf -pri -e *.conllu pyconll/ tests/

lint:
	pylint --rcfile .pylintrc pyconll/ && \
	yapf -prq -e *.conllu pyconll/ tests/

test:
	python -m pytest -vv --ignore tests/int

coveragetest:
	coverage run --source pyconll -m pytest --ignore tests/int

inttest:
	python -m pytest tests/int

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
