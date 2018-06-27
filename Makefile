format:
	yapf -p -r -i pyconll/ tests/

test:
	python -m pytest -vv

coveragetest:
	coverage run --source pyconll -m pytest

build:
	python setup.py build

sdist:
	python setup.py sdist

publish:
	python setup.py sdist
	twine upload dist/*

publishtest:
	python setup.py sdist
	twine upload --repository-url https://test.pypi.org/legacy dist/*

docs:
	pandoc --from=markdown --to=rst --output=README.rst README.md
	pandoc --from=markdown --to=plain --output=README README.md

clean:
	if [ -d 'dist' ]; then \
		rm -r dist; \
	fi

	if [ -d 'build' ]; then \
		rm -r build; \
	fi
