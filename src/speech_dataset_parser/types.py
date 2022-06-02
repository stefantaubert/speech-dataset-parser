from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

# DatasetLJSpeech = Literal["ljs"]
# DatasetArctic = Literal["arc"]

# DatasetTypes = Literal[DatasetLJSpeech, DatasetArctic]

GENDER_UNKNOWN = 0
GENDER_MALE = 1
GENDER_FEMALE = 2
GENDER_NOT_APPLICABLE = 9

GENDERS = {
  GENDER_UNKNOWN,
  GENDER_MALE,
  GENDER_FEMALE,
  GENDER_NOT_APPLICABLE
}


@dataclass()
class Entry:
  symbols: Tuple[str, ...]
  intervals: Tuple[float, ...]
  symbols_language: str
  speaker_name: str
  speaker_accent: str
  speaker_gender: int
  # relative path
  audio_file_rel: Path
  # absolute path
  audio_file_abs: Path
