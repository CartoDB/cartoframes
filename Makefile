init:
	pip install -r requirements.txt

docs:
	cd docs && make html

test:
	nosetests -v test/

dist:
	python setup.py sdist bdist_wheel --universal

publish: clean dist send

send:
	twine upload dist/*

clean:
	find . -name '*DS_Store' | xargs rm
	rm -fr build/* dist/* .egg cartoframes.egg-info

.PHONY: init docs test dist release clean send
