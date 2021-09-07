from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import List, Tuple

from tqdm import tqdm

from speech_dataset_parser.data import PreData, PreDataList
from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import (get_lang_from_str,
                                            is_lang_from_str_supported)
from speech_dataset_parser.utils import get_subfolders, load_df

DATA_CSV_NAME = "data.csv"
AUDIO_FOLDER_NAME = "audio"


@dataclass
class Entry():
  entry_id: int
  text: str
  wav: str
  duration: float
  speaker: str
  gender: str
  accent: str
  lang: str


class Entries(list):
  def items(self) -> List[Entry]:
    return self

  @classmethod
  def load(cls, file_path: Path):
    data = load_df(file_path, sep="\t")
    data_loaded: List[Entry] = [Entry(*xi) for xi in data.values]
    res = cls(data_loaded)
    res.load_init()
    return res

  def load_init(self):
    for entry in self.items():
      entry.text = str(entry.text)
      entry.speaker = str(entry.speaker)
      entry.accent = str(entry.accent)


def sort_entries_key(entry: PreData) -> Tuple[str, Path]:
  return entry.speaker_name, entry.wav_path


def parse(dir_path: Path) -> PreDataList:
  logger = getLogger(__name__)
  if not dir_path.exists():
    ex = ValueError(f"Directory not found: {dir_path}")
    logger.error("", exc_info=ex)
    raise ex

  result = PreDataList()
  tmp: List[Tuple[Tuple, PreDataList]] = []

  subfolders = get_subfolders(dir_path)
  subfolder: Path
  for subfolder in tqdm(subfolders):
    data_path = subfolder / DATA_CSV_NAME
    entries = Entries.load(data_path)
    for entry in entries.items():
      if not is_lang_from_str_supported(entry.lang):
        logger.warning(
          f"Entry {entry.entry_id} couldn't be parsed because it contains an unknown language {entry.lang}!")
        continue
      gender = Gender.MALE if entry.gender == "m" else Gender.FEMALE
      wav_path = subfolder / AUDIO_FOLDER_NAME / entry.wav
      data = PreData(
        identifier=entry.entry_id,
        speaker_name=entry.speaker,
        speaker_accent=entry.accent,
        speaker_language=get_lang_from_str(entry.lang),
        wav_path=wav_path,
        speaker_gender=gender,
        text=entry.text,
      )
      sorting_keys = entry.speaker, subfolder, entry.entry_id
      tmp.append((sorting_keys, data))

  tmp.sort(key=lambda x: x[0])

  result = PreDataList([x for _, x in tmp])

  return result
