.PHONY: test install dev venv clean setup_subtrees fetch_subtrees
.ONESHELL:

VENV=.venv
PY_VER=python3.11
PYTHON=./$(VENV)/bin/$(PY_VER)
PIP_INSTALL=$(PYTHON) -m pip install
SPACY_MODEL=$(PYTHON) -m spacy download en_core_web_md
REPO=git+https://github.com/rafelafrance

test:
	$(PYTHON) -m unittest discover

install: venv
	$(PIP_INSTALL) -U pip setuptools wheel
	$(PIP_INSTALL) $(REPO)/common_utils.git@main#egg=common_utils
	$(PIP_INSTALL) $(REPO)/label_finder.git@main#egg=label_finder
	$(PIP_INSTALL) $(REPO)/ocr_ensemble.git@main#egg=ocr_ensemble
	$(PIP_INSTALL) $(REPO)/traiter.git@master#egg=traiter
	$(PIP_INSTALL) $(REPO)/FloraTraiter.git@main#egg=FloraTraiter
	$(PIP_INSTALL) $(REPO)/traiter_llm.git@main#egg=traiter_llm
	$(PIP_INSTALL) $(REPO)/reconcile_traits.git@main#egg=reconcile_traits
	$(PIP_INSTALL) .
	$(SPACY_MODEL)

dev: venv
	source $(VENV)/bin/activate
	$(PIP_INSTALL) -U pip setuptools wheel
	$(PIP_INSTALL) -e ../../misc/common_utils
	$(PIP_INSTALL) -e ../../digi-leap/label_finder
	$(PIP_INSTALL) -e ../../digi-leap/ocr_ensemble
	$(PIP_INSTALL) -e ../../digi-leap/reconcile_traits
	$(PIP_INSTALL) -e ../../traiter/traiter
	$(PIP_INSTALL) -e ../../traiter/FloraTraiter
	$(PIP_INSTALL) -e ../../traiter/traiter_llm
	$(PIP_INSTALL) -e .[dev]
	$(SPACY_MODEL)
	pre-commit install

venv:
	test -d $(VENV) || $(PY_VER) -m venv $(VENV)

clean:
	rm -r $(VENV)
	find -iname "*.pyc" -delete
