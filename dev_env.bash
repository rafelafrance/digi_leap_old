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

pip3 install -U torch==1.9.1+cu111 torchvision==0.10.1+cu111 -f https://download.pytorch.org/whl/torch_stable.html

if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

pip install -U tensorboard
python -c 'import nltk; nltk.download("words")'

# Commonly used for dev
pip install -U pynvim
pip install -U 'python-lsp-server[all]'
pip install -U pre-commit pre-commit-hooks
pip install -U autopep8 flake8 isort pylint yapf pydocstyle black
pip install -U jupyter jupyter_nbextensions_configurator ipyparallel
pip install -U jupyter_nbextensions_configurator jupyterlab_code_formatter

# mypy stuff
pip install -U mypy
pip install -U data-science-types types-Pillow
