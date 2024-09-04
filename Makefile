install:
	pip install -U -e .[dev]

format:
	black .
	docformatter -i -r .
	ruff check --fix .
