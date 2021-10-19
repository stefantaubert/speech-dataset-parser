"""
Parses the M-AILABS dataset. It ignores the mix folder because no concrete genders can be assigned so it is useless for TTS.
"""

from logging import getLogger
from pathlib import Path
from typing import Dict, Tuple

from general_utils import get_basename, get_subfolders, read_lines
from tqdm import tqdm

from speech_dataset_parser.data import PreData, PreDataList
from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import Language
from speech_dataset_parser.text_format import TextFormat

LANGUAGES: Dict[str, Language] = {
  "de_DE": Language.GER,
  "en_UK": Language.ENG,
  "en_US": Language.ENG,
  "es_ES": Language.ES,
  "it_IT": Language.IT,
  "uk_UK": Language.UK,
  "ru_RU": Language.RU,
  "fr_FR": Language.FR,
  "pl_PL": Language.PL,
}

ACCENTS: Dict[str, str] = {
  "de_DE": "default",
  "en_UK": "uk",
  "en_US": "us",
  "es_ES": "default",
  "it_IT": "default",
  "uk_UK": "default",
  "ru_RU": "default",
  "fr_FR": "default",
  "pl_PL": "default",
}


def parse(dir_path: Path) -> PreDataList:
  logger = getLogger(__name__)
  if not dir_path.exists():
    ex = ValueError(f"Directory not found: {dir_path}")
    logger.error("", exc_info=ex)
    raise ex

  data_paths: Tuple[Language, str, Gender, str, Path] = []

  language_dirs = get_subfolders(dir_path)
  for language_dir in language_dirs:
    logger.info(f"Parsing {language_dir}...")
    male_dir = language_dir / "by_book" / "male"
    female_dir = language_dir / "by_book" / "female"
    language_name = get_basename(language_dir)
    lang = LANGUAGES[language_name]
    accent = ACCENTS[language_name]

    if male_dir.exists():
      speaker_paths = get_subfolders(male_dir)
      for speaker_path in speaker_paths:
        speaker_name = get_basename(speaker_path)
        book_paths = get_subfolders(speaker_path)
        for book_path in book_paths:
          data_paths.append((lang, accent, Gender.MALE, speaker_name, book_path))

    if female_dir.exists():
      speaker_paths = get_subfolders(female_dir)
      for speaker_path in speaker_paths:
        speaker_name = get_basename(speaker_path)
        book_paths = get_subfolders(speaker_path)
        for book_path in book_paths:
          data_paths.append((lang, accent, Gender.FEMALE, speaker_name, book_path))

  result = PreDataList()
  text_format = TextFormat.GRAPHEMES

  book_path: Path
  for lang, accent_name, gender, speaker_name, book_path in tqdm(data_paths):
    metadata_path = book_path / "metadata.csv"
    wav_dirpath = book_path / 'wavs'
    lines = read_lines(metadata_path)
    for line in lines:
      parts = line.split('|')
      basename = parts[0]
      # parts[1] contains years, in parts[2] the years are written out
      # ex. ['LJ001-0045', '1469, 1470;', 'fourteen sixty-nine, fourteen seventy;']
      wav_path = wav_dirpath / f'{basename}.wav'
      text = parts[2]
      text_en_symbols = tuple(text)

      if not wav_path.is_file():
        print(f"file does not exist: {wav_path}")
        # These files do not exist:
        # en_UK/by_book/female/elizabeth_klett/jane_eyre/wavs/jane_eyre_27_f000439.wav
        # en_UK/by_book/female/elizabeth_klett/jane_eyre/wavs/jane_eyre_27_f000441.wav
        # en_US/by_book/female/judy_bieber/the_master_key/wavs/the_master_key_05_f000135.wav
        # en_US/by_book/female/mary_ann/midnight_passenger/wavs/midnight_passenger_05_f000269.wav
        # en_US/by_book/female/mary_ann/northandsouth/wavs/northandsouth_40_f000069.wav
        continue

      entry = PreData(
        identifier=0,
        basename=basename,
        speaker_name=speaker_name,
        speaker_accent=accent_name,
        symbols=text_en_symbols,
        symbols_format=text_format,
        relative_audio_path=wav_path.relative_to(dir_path),
        speaker_gender=gender,
        symbols_language=lang,
      )

      result.append(entry)

  result.sort(key=sort_ds, reverse=False)
  result.set_identifiers()
  logger.info(f"Parsed {len(result)} entries.")

  return result


def sort_ds(entry: PreData) -> Tuple[str, str]:
  return entry.speaker_name, entry.identifier
