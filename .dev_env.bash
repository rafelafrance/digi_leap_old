#!/usr/bin/env bash

# #################################################################################
# Setup the virtual environment for development.
# You may need to "python -M pip install --user virtualenv" globally.
# This is not required but some form of project isolation (conda, virtual env, etc.)
# is strongly encouraged.

if [[ ! -z "$VIRTUAL_ENV" ]]; then
  echo "'deactivate' before running this script."
  exit 1
fi

rm -r .venv
python3.10 -m venv .venv

source ./.venv/bin/activate

# ##############################################################################
# Install normal requirements

python -m pip install --upgrade pip setuptools wheel
if [ -f requirements.txt ]; then python -m pip install -r requirements.txt; fi

# ##############################################################################
# I want to use the GPU when possible.

 python -m pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu113


# ##############################################################################
# NLP datasets - NOTE: we're using a larger than normal spacy model

python -c 'import nltk; nltk.download("words")'

python -m pip install -U spacy
python -m spacy download en_core_web_md
python -m spacy download en_core_web_lg


# ##############################################################################
# Use the 2nd line if you don't have traiter installed locally

python -m pip install -e ../../traiter/traiter
# python -m pip install git+https://github.com/rafelafrance/traiter.git@master#egg=traiter


# ##############################################################################
# Dev only pip installs (not required because they're personal preference)
python -m pip install -U tensorboard
python -m pip install -U neovim
python -m pip install -U 'python-lsp-server[all]'
python -m pip install -U pre-commit pre-commit-hooks
python -m pip install -U autopep8 flake8 isort pylint yapf pydocstyle black
python -m pip install -U bandit prospector pylama
python -m pip install -U jupyter jupyter_nbextensions_configurator ipyparallel

python -m pip install -U jupyterlab
python -m pip install -U jupyterlab-drawio
python -m pip install -U jupyterlab-lsp
python -m pip install -U jupyterlab-spellchecker
python -m pip install -U aquirdturtle-collapsible-headings
python -m pip install -U nbdime
python -m pip install -U jupyterlab-code-formatter==1.4.10
python -m pip install -U jupyterlab-git==0.36.0

jupyter labextension install jupyterlab_onedarkpro
jupyter server extension enable --py jupyterlab_git
jupyter serverextension enable --py jupyterlab_code_formatter


# ##############################################################################
# I Run pre-commit hooks (optional)

pre-commit install
