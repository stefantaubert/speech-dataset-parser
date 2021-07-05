from dataclasses import dataclass
from typing import List

from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import Language


@dataclass()
class PreData:
  name: str
  speaker_name: str
  speaker_accent: str
  text: str
  wav_path: str
  gender: Gender
  lang: Language


class PreDataList(list):
  def items(self) -> List[PreData]:
    return self

  def __str__(self) -> str:
    whole_text = str.join(" ", [item.text for item in self.items()])
    return whole_text
