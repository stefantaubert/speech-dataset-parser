from logging import getLogger
from pathlib import Path
from typing import Generator, Iterable, List, Optional, Tuple, cast

from general_utils import get_files_dict, get_subfolders
from textgrid import Interval, IntervalTier, TextGrid
from tqdm import tqdm

from speech_dataset_parser_core.globals import GENDERS
from speech_dataset_parser_core.types import Entry
from speech_dataset_parser_core.validation import (DirectoryNotExistsError,
                                                   ValidationError)


def parse_generic(directory: Path, tier_name: str, n_digits: int) -> Tuple[Optional[ValidationError], Optional[List[Entry]]]:
  if error := DirectoryNotExistsError.validate(directory):
    return error, None

  result = list(parse_generic_core(directory, tier_name, n_digits))
  return None, result


def parse_generic_core(directory: Path, tier_name: str, n_digits: int) -> Generator[Entry, None, None]:
  assert directory.is_dir()
  assert 0 <= n_digits <= 16
  assert isinstance(n_digits, int)

  logger = getLogger(__name__)

  speaker_dirs = get_subfolders(directory)

  for speaker_dir in speaker_dirs:
    speaker_parts = speaker_dir.name.split(",")
    if len(speaker_parts) not in {3, 4}:
      logger.error(f"{str(speaker_dir.relative_to(directory))}: Directory '{speaker_dir.name}' couldn't be parsed because not all information are provided in the name. Ignored.")
      continue
    speaker_name = speaker_parts[0]
    speaker_gender = speaker_parts[1]
    if not speaker_gender.isnumeric():
      logger.error(
        f"{str(speaker_dir.relative_to(directory))}: Gender code '{speaker_gender}' needs to be a number. Ignored.")
      continue
    speaker_gender = int(speaker_gender)
    if not speaker_gender in GENDERS:
      logger.error(
        f"{str(speaker_dir.relative_to(directory))}: Gender code '{speaker_gender}' not recognized. Ignored.")
      continue

    speaker_lang = speaker_parts[2]
    # TODO check lang code better
    if len(speaker_lang) != 3 or not speaker_lang.islower():
      logger.error(
        f"{str(speaker_dir.relative_to(directory))}: Language code '{speaker_lang}' is not valid (needs to be three lower-case letters). Ignored.")
      continue

    speaker_accent = None
    if len(speaker_parts) == 4:
      speaker_accent = speaker_parts[3]

    audio_files = get_files_dict(speaker_dir, {".wav"})
    grid_files = get_files_dict(speaker_dir, {".TextGrid"})

    for file_stem, grid_file_rel in tqdm(grid_files.items()):
      if file_stem not in audio_files:
        logger.error(f"{str(grid_file_rel)}: Audio file was not found. Ignored.")
        continue

      grid_file_abs = speaker_dir / grid_file_rel
      grid = TextGrid()
      grid.read(grid_file_abs, n_digits)
      tier = cast(Optional[IntervalTier], grid.getFirst(tier_name))
      if tier is None:
        logger.error(f"{str(grid_file_rel)}: Tier '{tier_name}' does not exist! Ignored.")
      symbols = (interval.mark for interval in cast(Iterable[Interval], tier.intervals))
      symbols = tuple(symbol if symbol is not None else "" for symbol in symbols)
      intervals = tuple(interval.maxTime for interval in cast(Iterable[Interval], tier.intervals))
      assert len(symbols) == len(intervals)

      audio_path = speaker_dir / audio_files[file_stem]
      audio_path_rel = audio_path.relative_to(directory)

      result = Entry(symbols, intervals, speaker_lang, speaker_name,
                     speaker_accent, speaker_gender, audio_path_rel)
      yield result
