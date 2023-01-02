from itertools import islice
from pathlib import Path

from speech_dataset_parser import parse_dataset


def test_parse_ljs_from_local_path():
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


def test_parse_l2arctic_from_local_path():
  local_path = Path("/home/mi/env/data/speech-dataset-parser/l2arctic")
  res = list(islice(parse_dataset(local_path, "Symbols", 16), 10))

  assert len(res) == 10

  first_entry = res[0]
  assert first_entry.audio_file_abs == Path(
    '/home/mi/env/data/speech-dataset-parser/l2arctic/ABA;1;eng;Arabic/arctic_a0001.wav')
  assert first_entry.min_time == 0
  assert first_entry.max_time == 3.2
  assert first_entry.speaker_accent == "Arabic"
  assert first_entry.speaker_name == 'ABA'
  assert first_entry.speaker_gender == 1
  assert first_entry.symbols_language == "eng"
  assert len(first_entry.intervals) == 45
  assert len(first_entry.symbols) == 45
  assert first_entry.intervals[:3] == (0.0711111111111111, 0.1422222222222222, 0.2133333333333333)
  assert first_entry.symbols[:6] == ('A', 'u', 't', 'h', 'o', 'r')


def test_parse_thchs_from_local_path():
  local_path = Path("/home/mi/env/data/speech-dataset-parser/thchs")
  res = list(islice(parse_dataset(local_path, "Symbols", 16), 10))

  assert len(res) == 10

  first_entry = res[0]
  assert first_entry.audio_file_abs == Path(
    '/home/mi/env/data/speech-dataset-parser/thchs/A11;2;chi/A11_0.wav')
  assert first_entry.min_time == 0
  assert first_entry.max_time == 7.8
  assert first_entry.speaker_accent is None
  assert first_entry.speaker_name == 'A11'
  assert first_entry.speaker_gender == 2
  assert first_entry.symbols_language == "chi"
  assert len(first_entry.intervals) == 50
  assert len(first_entry.symbols) == 50
  assert first_entry.intervals[:3] == (0.156, 0.312, 0.468)
  assert first_entry.symbols[:6] == ('绿', ' ', '是', ' ', '阳', '春')
