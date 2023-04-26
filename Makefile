.PHONY: test install dev venv clean
.ONESHELL:

# $(PIP_INSTALL) -e ../traiter --config-settings editable_mode=strict

VENV=.venv
PYTHON=./$(VENV)/bin/python3.10
PIP_INSTALL=$(PYTHON) -m pip install
SPACY_MODEL=$(PYTHON) -m spacy download en_core_web_md

test:
	$(PYTHON) -m unittest discover

install: venv
	$(PIP_INSTALL) -U pip setuptools wheel
	$(PIP_INSTALL) .
	$(PIP_INSTALL) git+https://github.com/rafelafrance/traiter.git@master#egg=traiter
	$(PIP_INSTALL) git+https://github.com/rafelafrance/traiter_plants.git@master#egg=traiter_plants
	$(SPACY_MODEL)

dev: venv
	source $(VENV)/bin/activate
	$(PIP_INSTALL) -U pip setuptools wheel
	$(PIP_INSTALL) -e .[dev]
	$(PIP_INSTALL) -e ../../traiter/traiter
	$(PIP_INSTALL) -e ../../traiter/plants
	$(SPACY_MODEL)
	pre-commit install

venv:
	test -d $(VENV) || python3.10 -m venv $(VENV)

clean:
	rm -r $(VENV)
	find -iname "*.pyc" -delete
