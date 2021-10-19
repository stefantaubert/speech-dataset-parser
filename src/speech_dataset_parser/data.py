from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import Language
from speech_dataset_parser.text_format import TextFormat

Symbols = Tuple[str, ...]


@dataclass()
class PreData:
  identifier: int
  basename: str
  symbols: Symbols
  symbols_format: TextFormat
  symbols_language: Language
  speaker_name: str
  speaker_accent: str
  speaker_gender: Gender
  relative_audio_path: Path


class PreDataList(list):
  def items(self) -> List[PreData]:
    return self

  def __str__(self) -> str:
    whole_text = str.join(" ", [''.join(item.symbols) for item in self.items()])
    return whole_text

  def set_identifiers(self) -> None:
    for i, item in enumerate(self.items()):
      item.identifier = i
