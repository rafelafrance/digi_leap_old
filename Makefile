.ONESHELL:

PYTHON=python3
JUPYTER=jupyter
PRE_COMMIT=pre-commit

test:
	$(PYTHON) -m unittest discover

install:
	source ./.venv/bin/activate
	$(PYTHON) -m pip install -U pip setuptools wheel
	$(PYTHON) -m pip install .
	$(PYTHON) -m pip install git+https://github.com/rafelafrance/traiter.git@master#egg=traiter

dev:
	source ./.venv/bin/activate
	$(PYTHON) -m pip install -U pip setuptools wheel
	$(PYTHON) -m pip install -e .[dev]
	$(PYTHON) -m pip install -e ../traiter
	$(JUPYTER) labextension install jupyterlab_onedarkpro
	$(JUPYTER) server extension enable --py jupyterlab_git
	$(JUPYTER) serverextension enable --py jupyterlab_code_formatter
	$(PRE_COMMIT) install
