.PHONY: test install dev venv clean pull push
.ONESHELL:

VENV=.venv
PY_VER=python3.11
PYTHON=./$(VENV)/bin/$(PY_VER)
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
	test -d $(VENV) || $(PY_VER) -m venv $(VENV)

clean:
	rm -r $(VENV)
	find -iname "*.pyc" -delete

pull:
	git subtree pull --prefix finder https://github.com/rafelafrance/label_finder.git main --squash
	git subtree pull --prefix ensemble https://github.com/rafelafrance/ocr_ensemble.git main --squash
	git subtree pull --prefix flora https://github.com/rafelafrance/FloraTraiter.git main --squash
	git subtree pull --prefix llm https://github.com/rafelafrance/traiter_llm.git main --squash
	git subtree pull --prefix reconcile https://github.com/rafelafrance/reconcile_traits.git main --squash
	git subtree pull --prefix server https://github.com/rafelafrance/digi_leap_server.git main --squash

push:
	git subtree push --prefix finder https://github.com/rafelafrance/label_finder.git main
	git subtree push --prefix ensemble https://github.com/rafelafrance/ocr_ensemble.git main
	git subtree push --prefix flora https://github.com/rafelafrance/FloraTraiter.git main
	git subtree push --prefix llm https://github.com/rafelafrance/traiter_llm.git main
	git subtree push --prefix reconcile https://github.com/rafelafrance/reconcile_traits.git main
	git subtree push --prefix server https://github.com/rafelafrance/digi_leap_server.git main
