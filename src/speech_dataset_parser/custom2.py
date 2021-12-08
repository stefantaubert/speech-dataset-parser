from logging import getLogger
from pathlib import Path
from typing import Iterable, List, cast

from general_utils.main import get_all_files_in_all_subfolders, get_subfolders
from textgrid import TextGrid
from textgrid.textgrid import Interval, IntervalTier

from speech_dataset_parser.data import PreData, PreDataList, Symbols
from speech_dataset_parser.gender import (get_gender_from_str,
                                          is_gender_from_str_supported)
from speech_dataset_parser.language import (get_lang_from_str,
                                            is_lang_from_str_supported)
from speech_dataset_parser.text_format import (
    get_format_from_str, is_symbol_format_from_str_supported)

TIER_NAME = "transcript"
TIER_NAME = "words-ipa"

# default was 8 but praat has 15
DEFAULT_TEXTGRID_PRECISION = 15


def parse(dir_path: Path) -> PreDataList:
  logger = getLogger(__name__)
  if not dir_path.exists():
    logger.error("Dir not found!")
    raise Exception()

  result = PreDataList()
  language_folders = get_subfolders(dir_path)
  for language_folder in language_folders:
    is_known_language = is_lang_from_str_supported(language_folder.name)
    if not is_known_language:
      logger.info(f"Skipped unknown language \"{language_folder.name}\".")
      continue
    language = get_lang_from_str(language_folder.name)
    speaker_folders = get_subfolders(language_folder)
    for speaker_folder in speaker_folders:
      parts = speaker_folder.name.split(",")
      if len(parts) < 3:
        logger.info(
          f"Skipping speaker \"{speaker_folder.name}\" because it contains not all information ({speaker_folder.relative_to(dir_path)})!")
        continue
      speaker_name = ','.join(parts[0:-2]).strip()
      speaker_gender_str = parts[-2].strip()
      speaker_accent_str = parts[-1].strip()

      if len(speaker_name) == 0:
        logger.info(f"Skipped speaker with no name ({speaker_folder.relative_to(dir_path)}).")
        continue

      if len(speaker_accent_str) == 0:
        logger.info(f"Skipped speaker with no accent ({speaker_folder.relative_to(dir_path)}).")
        continue

      is_known_gender = is_gender_from_str_supported(speaker_gender_str)
      if not is_known_gender:
        logger.info(
          f"Skipped speaker with unknown gender \"{speaker_gender_str}\" ({speaker_folder.relative_to(dir_path)}).")
        continue
      speaker_gender = get_gender_from_str(speaker_gender_str)

      format_folders = get_subfolders(speaker_folder)
      for format_folder in format_folders:
        is_known_format = is_symbol_format_from_str_supported(format_folder.name)
        if not is_known_format:
          logger.info(
            f"Skipped unknown format \"{format_folder.name}\" ({format_folder.relative_to(dir_path)}).")
          continue
        symbol_format = get_format_from_str(format_folder.name)

        files = get_all_files_in_all_subfolders(format_folder)
        files = list(file.relative_to(dir_path) for file in files)
        textgrid_files = {str(file.parent / file.stem): file
                          for file in files if file.suffix.lower() == ".textgrid"}
        logger.info(f"Found {len(textgrid_files)} .TextGrid files.")

        audio_files = {str(file.parent / file.stem): file
                       for file in files if file.suffix.lower() in {".wav"}}
        logger.info(f"Found {len(audio_files)} audio files.")

        for path, grid_path in textgrid_files.items():
          if path not in audio_files:
            logger.info(f"Skipping \"{grid_path}\" because no corresponding audio file was found!")
            continue
          relative_audio_path = audio_files[path]

          grid = TextGrid()
          full_grid_path = dir_path / grid_path
          grid.read(full_grid_path, round_digits=DEFAULT_TEXTGRID_PRECISION)
          transcript_tier = cast(IntervalTier, grid.getFirst(TIER_NAME))
          transcript_tier_missing = transcript_tier is None
          if transcript_tier_missing:
            logger.info(
              f"Skipping \"{grid_path}\" because it does not contain a \"{TIER_NAME}\" tier.")
            continue
          symbols = tier_to_symbols(transcript_tier)
          entry = PreData(
            identifier=len(result),
            basename=grid_path.stem,
            relative_audio_path=relative_audio_path,
            speaker_accent=speaker_accent_str,
            speaker_gender=speaker_gender,
            speaker_name=speaker_name,
            symbols=symbols,
            symbols_format=symbol_format,
            symbols_language=language,
          )

          result.append(entry)

  logger.info(f"Collected {len(result)} transcripts.")

  return result


def tier_to_symbols(tier: IntervalTier, split_symbol: str = " ", join_symbol: str = " ") -> Symbols:
  words: List[Symbols] = []
  for interval in cast(Iterable[Interval], tier.intervals):
    if not interval_is_empty(interval):
      interval_text: str = interval.mark
      interval_text = interval_text.strip()
      symbols = interval_text.split(split_symbol)
      words.append(symbols)

  text = symbols_join(words, join_symbol)
  return text


def symbols_join(list_of_symbols: List[Symbols], join_symbol: str) -> Symbols:
  res = []
  for i, word in enumerate(list_of_symbols):
    res.extend(word)
    is_last_word = i == len(list_of_symbols) - 1
    if not is_last_word:
      res.append(join_symbol)
  return tuple(res)


def interval_is_empty(interval: Interval) -> bool:
  return interval.mark is None or len(str(interval.mark).strip()) == 0
