from dataclasses import dataclass
from pathlib import Path
from typing import List

from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import Language
from speech_dataset_parser.text_format import TextFormat


@dataclass()
class PreData:
  identifier: str
  text: str
  text_format: TextFormat
  speaker_name: str
  speaker_accent: str
  speaker_gender: Gender
  speaker_language: Language
  wav_path: Path


class PreDataList(list):
  def items(self) -> List[PreData]:
    return self

  def __str__(self) -> str:
    whole_text = str.join(" ", [item.text for item in self.items()])
    return whole_text
