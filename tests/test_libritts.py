from pathlib import Path

from speech_dataset_parser.libritts import parse

LOCAL_PATH = Path('/data/datasets/libriTTS')


def test_all_utterances_are_included():
  res = parse(LOCAL_PATH)
  assert len(res) == 127073
