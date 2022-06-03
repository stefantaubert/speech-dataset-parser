#!/bin/bash

# remove unused imports
autoflake --in-place --remove-all-unused-imports --ignore-init-module-imports . -r

rm -rf dist/; python3.8 -m build -o dist/

# pip install dist/pronunciation_dictionary_utils-0.0.1-py3-none-any.whl

# pip install -e .

pip uninstall pronunciation-dictionary-utils -y

# to testpypi (version 0.1.5)
pipenv run twine upload --repository testpypi dist/*
# https://test.pypi.org/project/pronunciation-dictionary-utils/

# to pypi
pipenv run twine upload --repository pypi dist/*
