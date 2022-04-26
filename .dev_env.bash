#!/usr/bin/env bash

if [[ ! -z "$VIRTUAL_ENV" ]]; then
  echo "'deactivate' before running this script."
  exit 1
fi

# mkdir .lsp_symlink
# cd .lsp_symlink
# ln -s /home home
# cd ..

rm -rf .venv
python3.9 -m venv .venv

source ./.venv/bin/activate

python -m pip install --upgrade pip setuptools wheel

# ##############################################################################
# I want to use the GPU when possible.
# pip3 install torch==1.10.2+cu113 torchvision==0.11.3+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
# pip3 install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu113


# ##############################################################################
# Install normal requirements
if [ -f requirements.txt ]; then python -m pip install -r requirements.txt; fi


# ##############################################################################
# NLP datasets - NOTE: we're using a larger than normal spacy model

python -c 'import nltk; nltk.download("words")'

python -m spacy download en_core_web_md


# ##############################################################################
# Use the 2nd line if you don't have traiter installed locally

python -m pip install -e ../../traiter/traiter
# python -m pip install git+https://github.com/rafelafrance/traiter.git@master#egg=traiter


# ##############################################################################
# Dev only pip installs (not required because they're personal preference)
python -m pip install -U tensorboard
python -m pip install -U pynvim
python -m pip install -U 'python-lsp-server[all]'
python -m pip install -U pre-commit pre-commit-hooks
python -m pip install -U autopep8 flake8 isort pylint yapf pydocstyle black
python -m pip install -U jupyter jupyter_nbextensions_configurator ipyparallel
python -m pip install -U jupyter_nbextensions_configurator jupyterlab_code_formatter
python -m pip install -U jupyterlab-git

python -m pip install -U jupyterlab
python -m pip install -U jupyterlab_code_formatter
python -m pip install -U jupyterlab-drawio
python -m pip install -U jupyterlab-lsp
python -m pip install -U jupyterlab-spellchecker
python -m pip install -U jupyterlab-git
python -m pip install -U aquirdturtle-collapsible-headings
python -m pip install -U nbdime

jupyter labextension install jupyterlab_onedarkpro
jupyter server extension enable --py jupyterlab_git
jupyter serverextension enable --py jupyterlab_code_formatter
