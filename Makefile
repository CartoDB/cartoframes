init:
	pip install -r requirements.txt

docs:
	cd docs && make html
	rm -r docs/_sources/ docs/_static
	mv -f docs/html/* docs/

test:
	nosetests -v test/

dist:
	python setup.py sdist
	python setup.py bdist_wheel

publish:
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg cartoframes.egg-info

.PHONY: init docs test dist release
