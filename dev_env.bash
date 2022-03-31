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
virtualenv -p python3.9 .venv

source ./.venv/bin/activate

python -m pip install --upgrade pip setuptools wheel

# ##############################################################################
# I want to use the GPU when possible.
pip3 install torch==1.10.2+cu113 torchvision==0.11.3+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html


# ##############################################################################
# I want to use the GPU when possible.
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi


# ##############################################################################
# NLP datasets - NOTE: we're using a larger than normal spacy model

python -c 'import nltk; nltk.download("words")'

python -m spacy download en_core_web_md


# ##############################################################################
# Use the 2nd line if you don't have traiter installed locally

# pip install -e ../../traiter/traiter
 pip install git+https://github.com/rafelafrance/traiter.git@master#egg=traiter


# ##############################################################################
# Dev only pip installs (not required because they're personal preference)
pip install -U tensorboard
pip install -U pynvim
pip install -U 'python-lsp-server[all]'
pip install -U pre-commit pre-commit-hooks
pip install -U autopep8 flake8 isort pylint yapf pydocstyle black
pip install -U jupyter jupyter_nbextensions_configurator ipyparallel
pip install -U jupyter_nbextensions_configurator jupyterlab_code_formatter

pip install -U jupyterlab
pip install -U jupyterlab_code_formatter
pip install -U jupyterlab-drawio
pip install -U jupyterlab-lsp
pip install -U jupyterlab-spellchecker
pip install -U jupyterlab-git
pip install -U aquirdturtle-collapsible-headings
pip install -U nbdime

jupyter labextension install jupyterlab_onedarkpro
jupyter server extension enable --py jupyterlab_git
jupyter serverextension enable --py jupyterlab_code_formatter
