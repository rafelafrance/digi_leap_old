.PHONY: test install dev venv clean
.ONESHELL:

VENV=.venv
PYTHON=./$(VENV)/bin/python3.9
PIP_INSTALL=$(PYTHON) -m pip install
SPACY_MODEL=$(PYTHON) -m spacy download en_core_web_md

test:
	$(PYTHON) -m unittest discover

install: venv
	$(PIP_INSTALL) -U pip setuptools wheel
	$(PIP_INSTALL) .

dev: venv
	source $(VENV)/bin/activate
	$(PIP_INSTALL) -U pip setuptools wheel
	$(PIP_INSTALL) -e .[dev]
	pre-commit install

venv:
	test -d $(VENV) || python3.9 -m venv $(VENV)

clean:
	rm -r $(VENV)
	find -iname "*.pyc" -delete
