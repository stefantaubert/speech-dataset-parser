from pathlib import Path

from speech_dataset_parser.thchs_kaldi import parse

LOCAL_PATH = Path('/data/datasets/thchs/THCHS-30')


def test_all_utterances_are_included():
  res = parse(LOCAL_PATH)
  assert len(res) == 13085
