.PHONY: test install dev venv clean setup_subtrees fetch_subtrees
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

setup_subtrees:
	git remote add -f label_finder https://github.com/rafelafrance/label_finder.git
	git checkout -b upstream/finder label_finder/main
	git subtree split -q --squash --prefix=finder --annotate='[finder] ' --rejoin -b merging/finder
	git checkout main
	git subtree add -q --squash --prefix=finder merging/finder

	git remote add -f ocr_ensemble https://github.com/rafelafrance/ocr_ensemble.git
	git checkout -b upstream/ensemble ocr_ensemble/main
	git subtree split -q --squash --prefix=ensemble --annotate='[ensemble] ' --rejoin -b merging/ensemble
	git checkout main
	git subtree add -q --squash --prefix=ensemble merging/ensemble

	git remote add -f traiter https://github.com/rafelafrance/traiter.git
	git checkout -b upstream/traiter traiter/master
	git subtree split -q --squash --prefix=traiter --annotate='[traiter] ' --rejoin -b merging/traiter
	git checkout main
	git subtree add -q --squash --prefix=traiter merging/traiter

	git remote add -f FloraTraiter https://github.com/rafelafrance/FloraTraiter.git
	git checkout -b upstream/flora FloraTraiter/main
	git subtree split -q --squash --prefix=flora --annotate='[flora] ' --rejoin -b merging/flora
	git checkout main
	git subtree add -q --squash --prefix=flora merging/flora

	git remote add -f traiter_llm https://github.com/rafelafrance/traiter_llm.git
	git checkout -b upstream/llm traiter_llm/main
	git subtree split -q --squash --prefix=llm --annotate='[llm] ' --rejoin -b merging/llm
	git checkout main
	git subtree add -q --squash --prefix=llm merging/llm

	git remote add -f reconcile_traits https://github.com/rafelafrance/reconcile_traits.git
	git checkout -b upstream/reconcile reconcile_traits/main
	git subtree split -q --squash --prefix=reconcile --annotate='[reconcile] ' --rejoin -b merging/reconcile
	git checkout main
	git subtree add -q --squash --prefix=reconcile merging/reconcile

	git remote add -f digi_leap_server https://github.com/rafelafrance/digi_leap_server.git
	git checkout -b upstream/server digi_leap_server/main
	git subtree split -q --squash --prefix=server --annotate='[server] ' --rejoin -b merging/server
	git checkout main
	git subtree add -q --squash --prefix=server merging/server

fetch_subtrees:
	git checkout upstream/finder
	git pull label_finder/main
	git subtree split -q --squash --prefix=finder --annotate='[finder] ' --rejoin -b merging/finder
	git checkout main
	git subtree merge -q --squash --prefix=finder merging/finder

	git checkout upstream/ensemble
	git pull ocr_ensemble/main
	git subtree split -q --squash --prefix=ensemble --annotate='[ensemble] ' --rejoin -b merging/ensemble
	git checkout main
	git subtree merge -q --squash --prefix=ensemble merging/ensemble

	git checkout upstream/traiter
	git pull traiter/master
	git subtree split -q --squash --prefix=traiter --annotate='[traiter] ' --rejoin -b merging/traiter
	git checkout main
	git subtree merge -q --squash --prefix=traiter merging/traiter

	git checkout upstream/flora
	git pull FloraTraiter/main
	git subtree split -q --squash --prefix=flora --annotate='[flora] ' --rejoin -b merging/flora
	git checkout main
	git subtree merge -q --squash --prefix=flora merging/flora

	git checkout upstream/llm
	git pull traiter_llm/main
	git subtree split -q --squash --prefix=llm --annotate='[llm] ' --rejoin -b merging/llm
	git checkout main
	git subtree merge -q --squash --prefix=llm merging/llm

	git checkout upstream/reconcile
	git pull reconcile_traits/main
	git subtree split -q --squash --prefix=reconcile --annotate='[reconcile] ' --rejoin -b merging/reconcile
	git checkout main
	git subtree merge -q --squash --prefix=reconcile merging/reconcile

	git checkout upstream/server
	git pull digi_leap_server/main
	git subtree split -q --squash --prefix=server --annotate='[server] ' --rejoin -b merging/server
	git checkout main
	git subtree merge -q --squash --prefix=server merging/server
