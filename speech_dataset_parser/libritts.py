import os
from logging import Logger, getLogger

from tqdm import tqdm

from speech_dataset_parser.data import PreData, PreDataList
from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import Language
from speech_dataset_parser.utils import (get_basename, get_filepaths,
                                         get_subfolders, read_lines, read_text)

# found some invalid text at:
# train-clean-360/8635/295759/8635_295759_000008_000001.original.txt
# "With them were White Thun-der, who had charge of the "speech-belts," and Sil-ver Heels, who was swift of foot."


SPEAKERS_TXT = "SPEAKERS.txt"


def download(dir_path: str):
  pass


def parse(dir_path: str, logger: Logger = getLogger()) -> PreDataList:
  if not os.path.exists(dir_path):
    ex = ValueError(f"Directory not found: {dir_path}")
    logger.error("", exc_info=ex)
    raise ex

  speakers_path = os.path.join(dir_path, SPEAKERS_TXT)
  speakers = read_lines(speakers_path)
  speakers = speakers[12:]
  speakers_dict = {}
  for speaker_details in speakers:
    s_id, gender, _, _, name = speaker_details.split(" | ")
    speakers_dict[s_id.strip()] = name.strip(), gender.strip()

  lang = Language.ENG

  entries = PreDataList()

  logger.info("Parsing files...")
  for dataset_folder in tqdm(get_subfolders(dir_path)):
    logger.info(f"Parsing {get_basename(dataset_folder)}...")

    for speaker_folder in tqdm(get_subfolders(dataset_folder)):
      speaker_id = get_basename(speaker_folder)
      speaker_name, speaker_gender = speakers_dict[speaker_id]
      accent_name = speaker_name
      gender = Gender.MALE if speaker_gender == "M" else Gender.FEMALE

      for chapter_folder in get_subfolders(speaker_folder):
        files = get_filepaths(chapter_folder)
        wavs = [x for x in files if x.endswith(".wav")]
        texts = [x for x in files if x.endswith(".normalized.txt")]
        assert len(wavs) == len(texts)

        for wav_file, text_file in zip(wavs, texts):
          assert get_basename(wav_file) == get_basename(text_file)[:-len(".normalized")]
          text_en = read_text(text_file)

          entry = PreData(
            name=get_basename(wav_file),
            speaker_name=speaker_name,
            speaker_accent=accent_name,
            text=text_en,
            wav_path=wav_file,
            gender=gender,
            lang=lang
          )

          entries.append(entry)

  entries.sort(key=sort_libri, reverse=False)
  logger.info(f"Parsed {len(entries)} entries from {len(speakers_dict)} speakers.")

  return entries


def sort_libri(entry: PreData) -> str:
  return entry.speaker_name, entry.name
