from logging import getLogger
from pathlib import Path
from typing import List, Tuple

from general_utils import read_lines
from tqdm import tqdm

from speech_dataset_parser.data import PreData, PreDataList
from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import Language
from speech_dataset_parser.text_format import TextFormat
from speech_dataset_parser.utils import download_tar

QUESTION_PARTICLE_1 = '吗'
QUESTION_PARTICLE_2 = '呢'

MALE_SPEAKERS = {"A8", "A9", "A33", "A35", "B8", "B21", "B34", "C8", "D8"}

ACCENTS = {
  "D4": "Mandarin",  # Standard Mandarin
  "D6": "Mandarin",  # Standard Mandarin
}


def download(dir_path: Path) -> None:
  download_tar("http://data.cslt.org/thchs30/zip/wav.tgz", dir_path)
  download_tar("http://data.cslt.org/thchs30/zip/doc.tgz", dir_path)


def parse(dir_path: Path) -> PreDataList:
  logger = getLogger(__name__)
  if not dir_path.exists():
    ex = ValueError(f"Directory not found: {dir_path}")
    logger.error("", exc_info=ex)
    raise ex

  train_words = dir_path / 'doc/trans/train.word.txt'
  test_words = dir_path / 'doc/trans/test.word.txt'
  train_wavs = dir_path / 'wav/train/'
  test_wavs = dir_path / 'wav/test/'

  parse_paths = [
    (train_words, train_wavs),
    (test_words, test_wavs)
  ]

  files: List[Tuple[Tuple[str, int, int], PreData]] = []
  lang = Language.CHN
  text_format = TextFormat.GRAPHEMES

  logger.info("Parsing files...")
  for words_path, wavs_dir in parse_paths:
    lines = read_lines(words_path)

    x: str
    for x in tqdm(lines):
      pos = x.find(' ')
      name, chinese = x[:pos], x[pos + 1:]

      speaker_name, nr = name.split("_")
      speaker_gender = Gender.MALE if speaker_name in MALE_SPEAKERS else Gender.FEMALE
      nr = int(nr)
      speaker_name_letter = speaker_name[0]
      speaker_name_number = int(speaker_name[1:])
      wav_path = wavs_dir / speaker_name / f"{name}.wav"
      if not wav_path.exists():
        wav_path = wavs_dir / speaker_name / f"{name}.WAV"
      if not wav_path.exists():
        logger.info(f"Found no wav file: {wav_path}")
        continue

      # remove "=" from chinese transcription because it is not correct
      # occurs only in sentences with nr. 374, e.g. B22_374
      chinese = chinese.replace("= ", '')
      is_question = str.endswith(chinese, QUESTION_PARTICLE_1) or str.endswith(
        chinese, QUESTION_PARTICLE_2)
      if is_question:
        chinese += "？"
      else:
        chinese += "。"

      accent_name = speaker_name
      if speaker_name in ACCENTS.keys():
        accent_name = ACCENTS[speaker_name]

      entry = PreData(
        identifier=name,
        speaker_name=speaker_name,
        text=chinese,
        text_format=text_format,
        speaker_accent=accent_name,
        wav_path=wav_path,
        speaker_gender=speaker_gender,
        text_language=lang
      )

      files.append((entry, (speaker_name_letter, speaker_name_number, nr)))

  files.sort(key=lambda tup: tup[1], reverse=False)
  res = PreDataList([x for x, _ in files])
  return res
