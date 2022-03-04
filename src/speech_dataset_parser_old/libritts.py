from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
from logging import getLogger
from multiprocessing import cpu_count
from pathlib import Path
from typing import List, Tuple

from general_utils import (get_basename, get_filepaths, get_subfolders,
                           read_lines)
from tqdm import tqdm

from speech_dataset_parser_old.data import PreData, PreDataList
from speech_dataset_parser_old.gender import Gender
from speech_dataset_parser_old.language import Language
from speech_dataset_parser_old.text_format import TextFormat

# found some invalid text at:
# train-clean-360/8635/295759/8635_295759_000008_000001.original.txt
# "With them were White Thun-der, who had charge of the "speech-belts," and Sil-ver Heels, who was swift of foot."
# and also some text which contains spaces between words
# e.g. train-clean-360/8635/295756/8635_295756_000030_000000.original.txt
# "Law rence soon tired of this place..."

SPEAKERS_TXT = "SPEAKERS.txt"


def parse(dir_path: Path) -> PreDataList:
  logger = getLogger(__name__)
  if not dir_path.exists():
    ex = ValueError(f"Directory not found: {dir_path}")
    logger.error("", exc_info=ex)
    raise ex

  speakers_path = dir_path / SPEAKERS_TXT
  speakers = read_lines(speakers_path)
  speakers = speakers[12:]
  speakers_dict = {}
  for speaker_details in speakers:
    s_id, gender, _, _, name = speaker_details.split(" | ")
    speakers_dict[s_id.strip()] = name.strip(), gender.strip()

  entries = PreDataList()

  logger.info("Detecting files...")
  arguments: List[Tuple[Path, Path, Gender, str, str]] = []
  for dataset_folder in tqdm(get_subfolders(dir_path)):
    logger.info(f"Parsing {get_basename(dataset_folder)}...")

    for speaker_folder in tqdm(get_subfolders(dataset_folder)):
      speaker_id = get_basename(speaker_folder)
      speaker_name, speaker_gender = speakers_dict[speaker_id]
      accent_name = speaker_name
      gender = Gender.MALE if speaker_gender == "M" else Gender.FEMALE

      for chapter_folder in get_subfolders(speaker_folder):
        files = get_filepaths(chapter_folder)
        wav_paths = [file for file in files if file.suffix == ".wav"]
        text_paths = [file for file in files if str(file).endswith(".normalized.txt")]
        if len(wav_paths) != len(text_paths):
          raise Exception()

        for wav_file, text_file in zip(wav_paths, text_paths):
          assert get_basename(wav_file) == get_basename(text_file)[:-len(".normalized")]
          arguments.append((wav_file, text_file, gender, accent_name, speaker_name))

  mt_method = partial(
    get_entry,
    dir_path=dir_path,
  )

  logger.info("Parsing content...")
  with ThreadPoolExecutor(max_workers=cpu_count() - 1) as ex:
    entries = PreDataList(tqdm(ex.map(mt_method, arguments), total=len(arguments)))
    #futures = [ex.submit(method) for method in methods]
    #entries = PreDataList(future.result() for future in futures)
  logger.info("Done.")

  entries.sort(key=sort_libri, reverse=False)
  entries.set_identifiers()

  logger.info(f"Parsed {len(entries)} entries from {len(speakers_dict)} speakers.")

  return entries


def get_entry(arguments: Tuple[Path, Path, Gender, str, str], dir_path: Path) -> PreData:
  wav_file, text_file, gender, accent_name, speaker_name = arguments
  text_en = text_file.read_text()
  text_en_symbols = tuple(text_en)

  entry = PreData(
    identifier=0,
    basename=get_basename(wav_file),
    speaker_name=speaker_name,
    speaker_accent=accent_name,
    symbols=text_en_symbols,
    symbols_format=TextFormat.GRAPHEMES,
    relative_audio_path=wav_file.relative_to(dir_path),
    speaker_gender=gender,
    symbols_language=Language.ENG,
  )

  return entry


def sort_libri(entry: PreData) -> Tuple[str, str]:
  return entry.speaker_name, entry.identifier
