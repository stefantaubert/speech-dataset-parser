import wave
from argparse import ArgumentParser, Namespace
from logging import getLogger
from pathlib import Path
from shutil import copy2
from typing import Generator, List, Tuple, cast

from textgrid import Interval, IntervalTier, TextGrid
from tqdm import tqdm

from speech_dataset_converter_cli.argparse_helper import (parse_existing_directory,
                                                          parse_non_empty_or_whitespace,
                                                          parse_non_existing_directory)
from speech_dataset_parser import GENDER_FEMALE
from speech_dataset_parser.parse import PARTS_SEP


def get_convert_ljs_to_generic_parser(parser: ArgumentParser):
  parser.description = "This command converts the LJSpeech dataset to a generic one."
  parser.add_argument("directory", type=parse_existing_directory, metavar="directory",
                      help="directory containing the LJSpeech content")
  parser.add_argument("output_directory", type=parse_non_existing_directory, metavar="output-directory",
                      help="output directory")
  parser.add_argument("--tier", type=parse_non_empty_or_whitespace, metavar="NAME",
                      help="name of the output tier", default="transcription")
  parser.add_argument("--n-digits", type=int, choices=range(17), metavar="DIGITS",
                      help="number of digits in textgrid", default=16)
  parser.add_argument("-s", "--symlink", action="store_true",
                      help="create symbolic links to the audio files instead of copies")
  return convert_to_generic_ns


def convert_to_generic_ns(ns: Namespace) -> bool:
  logger = getLogger(__name__)

  if ns.output_directory == ns.directory:
    logger.error("Parameter 'directory' and 'output_directory': The two directories need to be distinct!")
    return False

  try:
    convert_to_generic(ns.directory, ns.symlink, ns.n_digits,
                       ns.tier, ns.output_directory, ns.overwrite)
  except ValueError as ex:
    logger.debug(ex)
    assert len(ex.args) == 1
    logger.error(ex.args[0])
    return False

  return True


def convert_to_generic(directory: Path, symlink: bool, n_digits: int, tier: str, output_directory: Path) -> None:
  logger = getLogger(__name__)

  speaker_name = 'Linda Johnson'
  accent_name = "North American"
  language = "eng"
  gender = GENDER_FEMALE

  speaker_dir_out_abs = output_directory / \
      f"{speaker_name}{PARTS_SEP}{gender}{PARTS_SEP}{language}{PARTS_SEP}{accent_name}"

  for text, wav_file_relative in parse_files(directory):
    logger.debug(f"Processing '{str(wav_file_relative)}'...")
    wav_file_in = directory / wav_file_relative
    assert wav_file_in.is_file()

    wav_file_out = speaker_dir_out_abs / wav_file_relative
    grid_file_out = speaker_dir_out_abs / \
        wav_file_relative.parent / f"{wav_file_relative.stem}.TextGrid"

    wav_file_out.parent.mkdir(parents=True, exist_ok=True)
    grid = create_grid(wav_file_in, text, tier, n_digits)
    grid.write(grid_file_out)
    if symlink:
      wav_file_out.symlink_to(wav_file_in)
    else:
      copy2(wav_file_in, wav_file_out)


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
  metadata_csv = directory / 'metadata.csv'

  if not metadata_csv.is_file():
    raise ValueError("Metadata file was not found!")

  wav_dir = directory / 'wavs'

  logger = getLogger(__name__)

  lines = metadata_csv.read_text().splitlines()
  for line_nr, line in enumerate(tqdm(lines, desc="Parsing files", unit=" file(s)"), start=1):
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
