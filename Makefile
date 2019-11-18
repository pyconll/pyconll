.PHONY: docs clean

format:
	yapf -p -r -i pyconll/ tests/

lint:
	pylint --rcfile .pylintrc pyconll/

test:
	python -m pytest -vv

coveragetest:
	coverage run --source pyconll -m pytest

build:
	python setup.py sdist bdist_wheel

publish:
	python setup.py sdist bdist_wheel
	twine upload dist/*
	sleep 30s
	conda config --set anaconda_upload yes
	conda build meta.yaml
	conda config --set anaconda_upload no

publishtest:
	python setup.py sdist bdist_wheel
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

docs:
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
