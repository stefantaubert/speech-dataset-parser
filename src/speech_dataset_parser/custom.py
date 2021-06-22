import os
from dataclasses import dataclass
from logging import Logger, getLogger
from typing import List, Tuple

from tqdm.std import tqdm

from speech_dataset_parser.data import PreData, PreDataList
from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import Language
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


class Entries(list):
  def items(self) -> List[Entry]:
    return self

  @classmethod
  def load(cls, file_path: str):
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


def sort_entries_key(entry: PreData) -> Tuple[str, str]:
  return entry.speaker_name, entry.wav_path


def parse(dir_path: str, logger: Logger) -> PreDataList:
  if not os.path.exists(dir_path):
    ex = ValueError(f"Directory not found: {dir_path}")
    logger.error("", exc_info=ex)
    raise ex

  result = PreDataList()
  lang = Language.ENG
  tmp: List[Tuple[Tuple, PreDataList]] = []

  subfolders = get_subfolders(dir_path)
  for subfolder in tqdm(subfolders):
    data_path = os.path.join(subfolder, DATA_CSV_NAME)
    entries = Entries.load(data_path)
    for entry in entries.items():
      gender = Gender.MALE if entry.gender == "m" else Gender.FEMALE

      wav_path = os.path.join(subfolder, AUDIO_FOLDER_NAME, entry.wav)
      data = PreData(
        name=entry.entry_id,
        speaker_name=entry.speaker,
        speaker_accent=entry.accent,
        lang=lang,
        wav_path=wav_path,
        gender=gender,
        text=entry.text,
      )
      sorting_keys = entry.speaker, subfolder, entry.entry_id
      tmp.append((sorting_keys, data))

  tmp.sort(key=lambda x: x[0])

  result = PreDataList([x for _, x in tmp])

  return result
