#!/bin/bash

prog_name="speech-dataset-parser"
cli_path=src/speech_dataset_parser_app/cli.py

mkdir -p ./dist

pipenv run cxfreeze \
  -O \
  --compress \
  --target-dir=dist \
  --bin-includes="libffi.so" \
  --target-name=cli \
  $cli_path

if [ $1 ]
then
  cd dist
  zip $prog_name-linux.zip ./ -r
  cd ..
  echo "zipped."
fi
