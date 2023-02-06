init:
	pip install -U pip
	pip install -e .[tests]

lint:
	flake8 cartoframes tests

test:
	pytest tests/unit/

clean:
	rm -fr build/* dist/* .egg cartoframes.egg-info

dist:
	python setup.py sdist bdist_wheel --universal

send:
	twine upload dist/*

publish:
	clean dist send
