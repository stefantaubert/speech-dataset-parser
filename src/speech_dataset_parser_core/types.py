from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Tuple

DatasetLJSpeech = Literal["ljs"]
DatasetArctic = Literal["arc"]

DatasetTypes = Literal[DatasetLJSpeech, DatasetArctic]


Symbols = Tuple[str, ...]
Language = str
Gender = int
Accent = str


@dataclass()
class Entry:
  symbols: Symbols
  symbols_language: Language
  speaker_name: str
  speaker_accent: Accent
  speaker_gender: Gender
  # relative path
  audio_file: Path
