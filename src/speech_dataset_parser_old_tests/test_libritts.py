from pathlib import Path

from speech_dataset_parser_old.libritts import parse

LOCAL_PATH = Path('/data/datasets/libriTTS')


def test_all_utterances_are_included():
  res = parse(LOCAL_PATH)
  assert len(res) == 127073
  assert not res.items()[0].relative_audio_path.is_absolute()
  assert isinstance(res.items()[0].symbols, tuple)
  assert res.items()[-1].identifier == len(res) - 1


test_all_utterances_are_included()
