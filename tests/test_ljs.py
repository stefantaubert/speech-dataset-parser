from pathlib import Path

from speech_dataset_parser.ljs import parse

LOCAL_PATH = Path('/data/datasets/LJSpeech-1.1')


def test_all_utterances_are_included():
  res = parse(LOCAL_PATH)
  assert len(res) == 13100
