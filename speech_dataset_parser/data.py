from dataclasses import dataclass
from typing import Generic, List

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


if __name__ == "__main__":
  x = PreDataList([PreData("", ",", "tarei", "atrien", Language.CHN)])
  print(x)
  print(type(x))
