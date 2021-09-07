
from pathlib import Path

from speech_dataset_parser.custom import parse

LOCAL_PATH = Path('/data/datasets/NNLV_pilot')


def test_all_utterances_are_included():
  res = parse(LOCAL_PATH)
  assert len(res) == 188
