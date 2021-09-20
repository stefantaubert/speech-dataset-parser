import os
import shutil
import tarfile
from logging import getLogger
from pathlib import Path

import wget
from general_utils import read_lines
from tqdm import tqdm

from speech_dataset_parser.data import PreData, PreDataList
from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import Language
from speech_dataset_parser.text_format import TextFormat


def download(dir_path: Path) -> None:
  logger = getLogger(__name__)
  logger.info("LJSpeech is not downloaded yet.")
  logger.info("Starting download...")
  dir_path.mkdir(parents=True, exist_ok=False)
  download_url = "https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2"
  dest = wget.download(download_url, dir_path)
  downloaded_file = dir_path / dest
  logger.info("\nFinished download to {}".format(downloaded_file))
  logger.info("Unpacking...")
  tar = tarfile.open(downloaded_file, "r:bz2")
  tar.extractall(dir_path)
  tar.close()
  logger.info("Done.")
  logger.info("Moving files...")
  dir_name = "LJSpeech-1.1"
  ljs_data_dir = dir_path / dir_name
  files = os.listdir(ljs_data_dir)
  for f in tqdm(files):
    shutil.move(ljs_data_dir / f, dir_path)
  logger.info("Done.")
  os.remove(downloaded_file)
  os.rmdir(ljs_data_dir)


def parse(dir_path: Path) -> PreDataList:
  logger = getLogger(__name__)
  if not dir_path.exists():
    ex = ValueError(f"Directory not found: {dir_path}")
    logger.error("", exc_info=ex)
    raise ex

  metadata_filepath = dir_path / 'metadata.csv'

  if not metadata_filepath.exists():
    ex = ValueError(f"Metadatafile not found: {metadata_filepath}")
    logger.error("", exc_info=ex)
    raise ex

  wav_dirpath = dir_path / 'wavs'

  if not wav_dirpath.exists():
    ex = ValueError(f"WAVs not found: {wav_dirpath}")
    logger.error("", exc_info=ex)
    raise ex

  result = PreDataList()
  speaker_name = 'Linda Johnson'
  accent_name = "North American"
  lang = Language.ENG
  gender = Gender.FEMALE
  text_format = TextFormat.GRAPHEMES

  lines = read_lines(metadata_filepath)
  logger.info("Parsing files...")
  for line in tqdm(lines):
    parts = line.split('|')
    basename = parts[0]
    # parts[1] contains years, in parts[2] the years are written out
    # ex. ['LJ001-0045', '1469, 1470;', 'fourteen sixty-nine, fourteen seventy;']
    wav_path = wav_dirpath / f'{basename}.wav'
    text = parts[2]

    entry = PreData(
      identifier=basename,
      speaker_name=speaker_name,
      speaker_accent=accent_name,
      text=text,
      text_format=text_format,
      wav_path=wav_path,
      speaker_gender=gender,
      text_language=lang
    )

    result.append(entry)

  result.sort(key=sort_ljs, reverse=False)
  logger.info("Done.")

  return result


def sort_ljs(entry: PreData) -> str:
  return entry.identifier
