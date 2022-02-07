dist/speech-dataset-parser ljs convert \
  "/data/datasets/LJSpeech-1.1" \
  "/tmp/ljs" -s -o \
  --tier "Symbols"
  
pipenv run python src/speech_dataset_parser_app/cli.py ljs convert \
  "/data/datasets/LJSpeech-1.1" \
  "/tmp/ljs" -s -o \
  --tier "Symbols"
  