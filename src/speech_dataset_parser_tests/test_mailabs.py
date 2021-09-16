
from pathlib import Path

from speech_dataset_parser.mailabs import parse

LOCAL_PATH = Path('/data/datasets/mailabs/all')


def test_all_utterances_are_included():
  res = parse(LOCAL_PATH)
  assert len(res) == 314990
