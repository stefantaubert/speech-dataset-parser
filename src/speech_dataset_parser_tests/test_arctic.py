from pathlib import Path

from speech_dataset_parser.arctic import parse

LOCAL_PATH = Path('/data/datasets/l2arctic')


def test_all_utterances_are_included():
  res = parse(LOCAL_PATH)
  assert len(res) == 26867
