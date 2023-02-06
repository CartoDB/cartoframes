init:
	pip install -e .[tests]

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
