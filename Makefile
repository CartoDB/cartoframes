init:
	pip install -r requirements.txt

docs:
	cd docs && make html

test:
	nosetests -v test/

.PHONY: init docs test
