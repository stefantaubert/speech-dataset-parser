from logging import getLogger
from pathlib import Path
from typing import Generator, Iterable, Optional, cast

from textgrid import Interval, IntervalTier, TextGrid
from tqdm import tqdm

from speech_dataset_parser.types import GENDERS, Entry
from speech_dataset_parser.utils import get_files_dict, get_subfolders

PARTS_SEP = ";"
DEFAULT_N_DIGITS = 16
DEFAULT_TIER_NAME = "transcription"
DEFAULT_ENCODING = "UTF-8"
DEFAULT_AUDIO_FORMAT = ".wav"
DEFAULT_SILENT = False


def parse_dataset(directory: Path, tier_name: str = DEFAULT_TIER_NAME, n_digits: int = DEFAULT_N_DIGITS, encoding: str = DEFAULT_ENCODING, audio_format: str = DEFAULT_AUDIO_FORMAT, silent: bool = DEFAULT_SILENT) -> Generator[Entry, None, None]:
  if not directory.is_dir():
    raise ValueError("Parameter 'directory': Directory was not found!")

  if not isinstance(tier_name, str):
    raise ValueError("Parameter 'tier_name: Value needs to be of type 'str'!")

  if n_digits not in range(1, 17):
    raise ValueError("Parameter 'n_digits': Value needs to be in interval [0, 16]!")

  if not isinstance(encoding, str):
    raise ValueError("Parameter 'encoding': Value needs to be of type 'str'!")

  logger = getLogger(__name__)

  speaker_dirs = get_subfolders(directory)
  iterator = speaker_dirs
  if not silent:
    iterator = tqdm(speaker_dirs, desc="Parsing dataset", unit=" speaker(s)")

  for speaker_dir in iterator:
    speaker_parts = speaker_dir.name.split(PARTS_SEP)
    if len(speaker_parts) not in {3, 4}:
      logger.warning(
        f"{str(speaker_dir.relative_to(directory))}: Directory '{speaker_dir.name}' couldn't be parsed because not all information are provided in the name. Ignored.")
      continue
    speaker_name = speaker_parts[0]
    speaker_gender = speaker_parts[1]
    if not speaker_gender.isnumeric():
      logger.warning(
        f"{str(speaker_dir.relative_to(directory))}: Gender code '{speaker_gender}' needs to be a number. Ignored.")
      continue
    speaker_gender = int(speaker_gender)
    if not speaker_gender in GENDERS:
      logger.warning(
        f"{str(speaker_dir.relative_to(directory))}: Gender code '{speaker_gender}' not recognized. Ignored.")
      continue

    speaker_lang = speaker_parts[2]
    # TODO check lang code better
    if len(speaker_lang) != 3 or not speaker_lang.islower():
      logger.warning(
        f"{str(speaker_dir.relative_to(directory))}: Language code '{speaker_lang}' is not valid (needs to be three lower-case letters). Ignored.")
      continue

    speaker_accent = None
    if len(speaker_parts) == 4:
      speaker_accent = speaker_parts[3]

    audio_files = get_files_dict(speaker_dir, {audio_format})
    grid_files = get_files_dict(speaker_dir, {".TextGrid"})

    for file_stem, grid_file_rel in grid_files.items():
      if file_stem not in audio_files:
        logger.warning(f"{str(grid_file_rel)}: Audio file was not found. Ignored.")
        continue

      grid_file_abs = speaker_dir / grid_file_rel
      grid = TextGrid()
      grid.read(grid_file_abs, n_digits, encoding)
      tier = cast(Optional[IntervalTier], grid.getFirst(tier_name))
      if tier is None:
        logger.warning(f"{str(grid_file_rel)}: Tier '{tier_name}' does not exist! Ignored.")
        continue
      symbols = (interval.mark for interval in cast(Iterable[Interval], tier.intervals))
      symbols = tuple(symbol if symbol is not None else "" for symbol in symbols)
      intervals = tuple(interval.maxTime for interval in cast(Iterable[Interval], tier.intervals))
      assert len(symbols) == len(intervals)

      audio_path = speaker_dir / audio_files[file_stem]

      result = Entry(symbols, intervals, speaker_lang, speaker_name,
                     speaker_accent, speaker_gender, audio_path, grid.minTime, grid.maxTime)
      yield result
