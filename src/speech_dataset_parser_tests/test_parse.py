from itertools import islice
from pathlib import Path

from speech_dataset_parser import parse_dataset


def test_component_from_local_path():
  local_path = Path("/home/mi/env/data/speech-dataset-parser/ljs")
  res = list(islice(parse_dataset(local_path, "Symbols", 16), 10))

  assert len(res) == 10

  first_entry = res[0]
  assert first_entry.audio_file_abs == Path(
    '/home/mi/env/data/speech-dataset-parser/ljs/Linda Johnson;2;eng;North American/wavs/LJ001-0001.wav')
  assert first_entry.min_time == 0
  assert first_entry.max_time == 9.65501133786848
  assert first_entry.speaker_accent == 'North American'
  assert first_entry.speaker_name == 'Linda Johnson'
  assert first_entry.speaker_gender == 2
  assert first_entry.symbols_language == "eng"
  assert len(first_entry.intervals) == 151
  assert len(first_entry.symbols) == 151
  assert first_entry.intervals[:3] == (0.0639404724362151, 0.1278809448724302, 0.1918214173086453)
  assert first_entry.symbols[:3] == ('P', 'r', 'i')
