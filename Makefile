init:
	pip install -r requirements.txt

docs:
	cd docs && make html

test:
	nosetests -v test/

dist:
	python setup.py sdist bdist_wheel --universal

publish:
	python setup.py sdist bdist_wheel --universal
	twine upload dist/*
	rm -fr build/* dist/* .egg cartoframes.egg-info

.PHONY: init docs test dist release
