.ONESHELL:

PYTHON=python3.10
JUPYTER=jupyter
PRE_COMMIT=pre-commit

test:
	$(PYTHON) -m unittest discover

install:
	$(PYTHON) -m venv .venv
	source ./.venv/bin/activate
	$(PYTHON) -m pip install -U pip setuptools wheel
	$(PYTHON) -m pip install .

dev:
	$(PYTHON) -m venv .venv
	source ./.venv/bin/activate
	$(PYTHON) -m pip install -U pip setuptools wheel
	$(PYTHON) -m pip install -e .[dev]
	$(PRE_COMMIT) install

clean:
	rm -r .venv
