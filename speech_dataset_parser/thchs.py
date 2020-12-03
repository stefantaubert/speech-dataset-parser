import os
from logging import Logger, getLogger
from typing import List, Tuple

from tqdm import tqdm

from speech_dataset_parser.data import PreData, PreDataList
from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import Language
from speech_dataset_parser.utils import download_tar, read_lines

QUESTION_PARTICLE_1 = '吗'
QUESTION_PARTICLE_2 = '呢'

MALE_SPEAKERS = {"A8", "A9", "A33", "A35", "B8", "B21", "B34", "C8", "D8"}

ACCENTS = {
  "D4": "Mandarin",  # Standard Mandarin
  "D6": "Mandarin",  # Standard Mandarin
}


def download(dir_path: str):
  download_tar("http://data.cslt.org/thchs30/zip/wav.tgz", dir_path)
  download_tar("http://data.cslt.org/thchs30/zip/doc.tgz", dir_path)


def parse(dir_path: str, logger: Logger = getLogger()) -> PreDataList:
  if not os.path.exists(dir_path):
    ex = ValueError(f"Directory not found: {dir_path}")
    logger.error("", exc_info=ex)
    raise ex

  train_words = os.path.join(dir_path, 'doc/trans/train.word.txt')
  test_words = os.path.join(dir_path, 'doc/trans/test.word.txt')
  train_wavs = os.path.join(dir_path, 'wav/train/')
  test_wavs = os.path.join(dir_path, 'wav/test/')

  parse_paths = [
    (train_words, train_wavs),
    (test_words, test_wavs)
  ]

  files: List[Tuple[Tuple[str, int, int], PreData]] = []
  lang = Language.CHN

  logger.info("Parsing files...")
  for words_path, wavs_dir in parse_paths:
    lines = read_lines(words_path)

    for x in tqdm(lines):
      pos = x.find(' ')
      name, chinese = x[:pos], x[pos + 1:]

      speaker_name, nr = name.split("_")
      speaker_gender = Gender.MALE if speaker_name in MALE_SPEAKERS else Gender.FEMALE
      nr = int(nr)
      speaker_name_letter = speaker_name[0]
      speaker_name_number = int(speaker_name[1:])
      wav_path = os.path.join(wavs_dir, speaker_name, name + '.wav')
      exists = os.path.exists(wav_path)
      if not exists:
        wav_path = os.path.join(wavs_dir, speaker_name, name + '.WAV')
      exists = os.path.exists(wav_path)
      if not exists:
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
        name=name,
        speaker_name=speaker_name,
        text=chinese,
        speaker_accent=accent_name,
        wav_path=wav_path,
        gender=speaker_gender,
        lang=lang
      )

      files.append((entry, (speaker_name_letter, speaker_name_number, nr)))

  files.sort(key=lambda tup: tup[1], reverse=False)
  res = PreDataList([x for x, _ in files])
  return res
