import codecs
from argparse import ArgumentParser, Namespace
from logging import Logger
from pathlib import Path
from shutil import copy2

from tqdm import tqdm

from speech_dataset_converter_cli.argparse_helper import (parse_codec, parse_existing_directory,
                                                          parse_non_empty_or_whitespace,
                                                          parse_non_existing_directory)
from speech_dataset_converter_cli.utils import create_grid
from speech_dataset_parser import GENDER_FEMALE
from speech_dataset_parser.parse import PARTS_SEP


def get_convert_ljs_to_generic_parser(parser: ArgumentParser):
  parser.description = "This command converts the LJSpeech dataset to a generic one."
  parser.add_argument("directory", type=parse_existing_directory, metavar="LJ-SPEECH-DIRECTORY",
                      help="directory containing the LJSpeech content")
  parser.add_argument("output_directory", type=parse_non_existing_directory, metavar="OUTPUT-DIRECTORY",
                      help="output directory")
  parser.add_argument("-t", "--tier", type=parse_non_empty_or_whitespace, metavar="TIER-NAME",
                      help="name of the output tier", default="transcription")
  parser.add_argument("-e", "--encoding", type=parse_codec, metavar="CODEC",
                      help="encoding of output grids", default="UTF-8")
  parser.add_argument("-d", "--n-digits", type=int, choices=range(17), metavar="DIGITS",
                      help="number of digits in textgrid", default=16)
  parser.add_argument("-s", "--symlink", action="store_true",
                      help="create symbolic links to the audio files instead of copies")
  return convert_to_generic_ns


def convert_to_generic_ns(ns: Namespace, flogger: Logger, logger: Logger) -> bool:
  if ns.output_directory == ns.directory:
    logger.error("Parameter 'directory' and 'output_directory': The two directories need to be distinct!")
    return False

  successful = convert_to_generic(ns.directory, ns.symlink, ns.n_digits,
                                  ns.tier, ns.output_directory, ns.encoding, flogger)

  return successful


def convert_to_generic(directory: Path, symlink: bool, n_digits: int, tier: str, output_directory: Path, encoding: str, logger: Logger) -> bool:
  speaker_name = 'Linda Johnson'
  accent_name = "North American"
  language = "eng"
  gender = GENDER_FEMALE

  speaker_dir_out_abs = output_directory / \
      f"{speaker_name}{PARTS_SEP}{gender}{PARTS_SEP}{language}{PARTS_SEP}{accent_name}"

  metadata_csv = directory / 'metadata.csv'
  wav_dir = directory / 'wavs'

  try:
    metadata_content = metadata_csv.read_text("UTF-8")
  except Exception as ex:
    logger.debug(ex)
    logger.error("Metadata file couldn't be read!")
    return False

  lines_with_errors = 0

  # strip last empty line
  lines = metadata_content.strip().splitlines()
  for line_nr, line in enumerate(tqdm(lines, desc="Creating files", unit=" file(s)"), start=1):
    parts = line.split('|')
    if not len(parts) == 3:
      logger.error(f"Line {line_nr}: '{line}' couldn't be parsed! Ignored.")
      lines_with_errors += 1
      continue
    # parts[1] contains years, in parts[2] the years are written out
    # e.g. ['LJ001-0045', '1469, 1470;', 'fourteen sixty-nine, fourteen seventy;']
    basename = parts[0]
    wav_file_abs = wav_dir / f'{basename}.wav'
    if not wav_file_abs.is_file():
      logger.error(f"Line {line_nr}: File '{str(wav_file_abs)}' was not found. Ignored.")
      lines_with_errors += 1
      continue

    text = parts[2]
    if len(text) == 0:
      logger.error(f"Line {line_nr}: Empty line. Ignored.")
      lines_with_errors += 1
      continue

    wav_file_relative = wav_file_abs.relative_to(directory)

    #logger.debug(f"Processing '{str(wav_file_relative)}'...")
    wav_file_in = directory / wav_file_relative
    assert wav_file_in.is_file()

    wav_file_out = speaker_dir_out_abs / wav_file_relative
    grid_file_out = speaker_dir_out_abs / \
        wav_file_relative.parent / f"{wav_file_relative.stem}.TextGrid"

    try:
      grid = create_grid(wav_file_in, text, tier, n_digits)
    except Exception as ex:
      logger.debug(ex)
      logger.error(f"Audio file \"{wav_file_in.absolute()}\" couldn't be read!")
      lines_with_errors += 1
      continue

    try:
      grid_file_out.parent.mkdir(parents=True, exist_ok=True)
    except Exception as ex:
      logger.debug(ex)
      logger.error(
        f"Parent folder \"{grid_file_out.parent.absolute()}\" for grid \"{grid_file_out.absolute()}\" couldn't be created!")
      lines_with_errors += 1
      continue

    try:
      with codecs.open(grid_file_out, 'w', encoding) as file:
        grid.write(file)
    except Exception as ex:
      logger.debug(ex)
      logger.error(f"Grid \"{grid_file_out.absolute()}\" couldn't be saved!")
      lines_with_errors += 1
      continue

    if symlink:
      try:
        wav_file_out.symlink_to(wav_file_in)
      except Exception as ex:
        logger.debug(ex)
        logger.error(
          f"Symbolic link to audio file \"{wav_file_in.absolute()}\" at \"{wav_file_out.absolute()}\" couldn't be created!")
        lines_with_errors += 1
        continue
    else:
      try:
        copy2(wav_file_in, wav_file_out)
      except Exception as ex:
        logger.debug(ex)
        logger.error(
          f"Audio file \"{wav_file_in.absolute()}\" couldn't be copied to \"{wav_file_out.absolute()}\"!")
        lines_with_errors += 1
        continue

  if lines_with_errors > 0:
    logger.warning(f"{lines_with_errors} lines couldn't be parsed!")

  all_successful = lines_with_errors == 0
  return all_successful
