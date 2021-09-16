from pathlib import Path

from speech_dataset_parser.thchs import parse

LOCAL_PATH = Path('/data/datasets/thchs/thchs_wav')


def test_ordered():
  res = parse(LOCAL_PATH)
  speakers = []
  data = {}
  for entry in res.items():
    if entry.speaker_name not in speakers:
      speakers.append(entry.speaker_name)
      data[entry.speaker_name] = []
    data[entry.speaker_name].append(entry.identifier)

  assert data["B15"][0] == "B15_250"
  assert data["B15"][-1] == "B15_499"
  assert speakers[0] == "A2"
  assert speakers[-1] == "D32"
  assert len(speakers) == 60


def test_all_utterances_are_included():
  res = parse(LOCAL_PATH)

  assert len(res) == 12495
