import wave
from logging import getLogger
from pathlib import Path
from shutil import copy2, rmtree
from typing import Generator, List, Optional, Tuple, cast

from textgrid import Interval, IntervalTier, TextGrid
from tqdm import tqdm

from speech_dataset_parser_core.validation import (DirectoryAlreadyExistsError,
                                                   DirectoryNotExistsError,
                                                   FileNotExistsError,
                                                   ValidationError)


class InvalidLineFormatError(ValidationError):
  def __init__(self, line_parts: str, line_nr: int) -> None:
    super().__init__()
    self.line_parts = line_parts
    self.line_nr = line_nr

  @classmethod
  def validate(cls, line_parts: str, line_nr: int):
    if not len(line_parts) == 3:
      return cls(line_parts, line_nr)
    return None

  @property
  def default_message(self) -> str:
    return


def convert_to_generic(directory: Path, use_audio_symlink: bool, n_digits: int, tier_name: str, output_directory: Path, overwrite: bool) -> Optional[ValidationError]:
  logger = getLogger(__name__)

  if error := DirectoryNotExistsError.validate(directory):
    return error

  metadata_csv = get_metafile_path(directory)

  if error := FileNotExistsError.validate(metadata_csv):
    return error

  if not overwrite and (error := DirectoryAlreadyExistsError.validate(output_directory)):
    return error

  speaker_name = 'Linda Johnson'
  accent_name = "North American"
  language = "eng"
  gender = 2

  speaker_dir_out_abs = output_directory / f"{speaker_name},{gender},{language},{accent_name}"

  if output_directory.exists():
    assert overwrite
    rmtree(output_directory)
    logger.info("Removed existing output directory.")

  for text, wav_file_relative in parse_files(directory):
    logger.debug(f"Processing '{str(wav_file_relative)}'...")
    wav_file_in = directory / wav_file_relative
    assert wav_file_in.is_file()

    wav_file_out = speaker_dir_out_abs / wav_file_relative
    grid_file_out = speaker_dir_out_abs / \
        wav_file_relative.parent / f"{wav_file_relative.stem}.TextGrid"

    if not overwrite and wav_file_out.is_file():
      logger.info(f"File '{str(wav_file_out)}' already exists. Skipped.")

    wav_file_out.parent.mkdir(parents=True, exist_ok=True)
    grid = create_grid(wav_file_in, text, tier_name, n_digits)
    grid.write(grid_file_out)
    if use_audio_symlink:
      wav_file_out.symlink_to(wav_file_in)
    else:
      copy2(wav_file_in, wav_file_out)

  logger.debug("Done.")


def get_wav_duration_s(wav_file: Path) -> float:
  with open(wav_file, mode="rb") as f:
    with cast(wave.Wave_read, wave.open(f, "rb")) as wav:
      duration_s = wav.getnframes() / wav.getframerate()
  return duration_s


def create_grid(wav_file: Path, text: str, tier_name: str, n_digits: int) -> TextGrid:
  assert wav_file.is_file()
  assert len(text) > 0
  duration_s = get_wav_duration_s(wav_file)
  duration_s = round(duration_s, n_digits)
  result = TextGrid(None, 0, duration_s)
  tier = IntervalTier(tier_name, 0, duration_s)
  symbols = list(text)
  tier.intervals.extend(get_intervals(symbols, duration_s, n_digits))
  result.append(tier)
  return result


def get_intervals(symbols: List[str], total_duration_s: float, n_digits: int) -> Generator[Interval, None, None]:
  symbols_count = len(symbols)
  for added_symbols_count, symbol in enumerate(symbols):
    min_time = added_symbols_count / symbols_count * total_duration_s
    max_time = (added_symbols_count + 1) / symbols_count * total_duration_s
    symbol_interval = Interval(round(min_time, n_digits), round(max_time, n_digits), symbol)
    yield symbol_interval


def parse_files(directory: Path) -> Generator[Tuple[str, Path], None, None]:
  assert directory.is_dir()
  metadata_csv = get_metafile_path(directory)
  assert metadata_csv.is_file()

  wav_dir = directory / 'wavs'

  logger = getLogger(__name__)
  logger.debug("Parsing files...")

  lines = metadata_csv.read_text().splitlines()
  for line_nr, line in enumerate(tqdm(lines), start=1):
    parts = line.split('|')
    if not len(parts) == 3:
      logger.error(f"Line {line_nr}: '{line}' couldn't be parsed! Ignored.")
      continue
    # parts[1] contains years, in parts[2] the years are written out
    # e.g. ['LJ001-0045', '1469, 1470;', 'fourteen sixty-nine, fourteen seventy;']
    basename = parts[0]
    wav_file_abs = wav_dir / f'{basename}.wav'
    if not wav_file_abs.is_file():
      logger.error(f"Line {line_nr}: File '{str(wav_file_abs)}' was not found. Ignored.")
      continue

    text_normalized = parts[2]
    if len(text_normalized) == 0:
      logger.error(f"Line {line_nr}: Empty line. Ignored.")
      continue

    wav_file_rel = wav_file_abs.relative_to(directory)
    yield text_normalized, wav_file_rel


def get_metafile_path(directory: Path) -> Path:
  return directory / 'metadata.csv'
