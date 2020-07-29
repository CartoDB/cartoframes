init:
	pip install -e .

test:
	pytest

docs:
	cd docs && make html

.PHONY: docs
