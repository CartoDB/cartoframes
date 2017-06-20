init:
	pip install -r requirements.txt

docs:
	cd docs && make html

test:
	nosetests -v test/

dist:
	python setup.py sdist
	python setup.py bdist_wheel

release:
	twine upload dist/*

.PHONY: init docs test dist release
