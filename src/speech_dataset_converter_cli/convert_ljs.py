import codecs
import json
from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from logging import Logger
from pathlib import Path
from shutil import copy2

from tqdm import tqdm

from speech_dataset_converter_cli.argparse_helper import (parse_codec, parse_existing_directory,
                                                          parse_non_empty_or_whitespace,
                                                          parse_non_existing_directory)
from speech_dataset_converter_cli.utils import create_grid
from speech_dataset_parser import GENDER_FEMALE
from speech_dataset_parser.parse import (DEFAULT_ENCODING, DEFAULT_N_DIGITS, DEFAULT_TIER_NAME,
                                         PARTS_SEP)


def get_convert_ljs_to_generic_parser(parser: ArgumentParser):
  parser.description = "This command converts the LJSpeech dataset to a generic one."
  parser.add_argument("directory", type=parse_existing_directory, metavar="LJ-SPEECH-DIRECTORY",
                      help="directory containing the LJSpeech content")
  parser.add_argument("output_directory", type=parse_non_existing_directory, metavar="OUTPUT-DIRECTORY",
                      help="output directory")
  parser.add_argument("-t", "--tier", type=parse_non_empty_or_whitespace, metavar="TIER-NAME",
                      help="name of the output tier", default=DEFAULT_TIER_NAME)
  parser.add_argument("-e", "--encoding", type=parse_codec, metavar="CODEC",
                      help="encoding of output grids", default=DEFAULT_ENCODING)
  parser.add_argument("-d", "--n-digits", type=int, choices=range(17), metavar="DIGITS",
                      help="number of digits in textgrid", default=DEFAULT_N_DIGITS)
  parser.add_argument("-s", "--symlink", action="store_true",
                      help="create symbolic links to the audio files instead of copies")
  return convert_to_generic_ns


def convert_to_generic_ns(ns: Namespace, flogger: Logger, logger: Logger) -> bool:
  if ns.output_directory == ns.directory:
    logger.error(
      "Parameter 'LJ-SPEECH-DIRECTORY' and 'OUTPUT-DIRECTORY': The two directories need to be distinct!")
    return False

  successful = convert_to_generic(ns.directory, ns.symlink, ns.n_digits,
                                  ns.tier, ns.output_directory, ns.encoding, flogger, logger)

  return successful


def convert_to_generic(directory: Path, symlink: bool, n_digits: int, tier: str, output_directory: Path, encoding: str, flogger: Logger, logger: Logger) -> bool:
  speaker_name = 'Linda Johnson'
  accent_name = "North American"
  language = "eng"
  gender = GENDER_FEMALE
  file_count = 13100
  z_fill = len(str(file_count))

  file_name_mapping = OrderedDict()

  speaker_dir_name = f"{speaker_name}{PARTS_SEP}{gender}{PARTS_SEP}{language}{PARTS_SEP}{accent_name}"
  speaker_dir_out_abs = output_directory / speaker_dir_name

  metadata_csv = directory / 'metadata.csv'
  wav_dir = directory / 'wavs'

  try:
    metadata_content = metadata_csv.read_text("UTF-8")
  except Exception as ex:
    logger.debug(ex)
    logger.error("Metadata file couldn't be read!")
    return False

  lines_with_errors = 0

  file_counter = 1

  # strip last empty line
  lines = metadata_content.strip().splitlines()
  for line_nr, line in enumerate(tqdm(lines, desc="Converting", unit=" file(s)"), start=1):
    parts = line.split('|')
    if not len(parts) == 3:
      flogger.error(f"Line {line_nr}: '{line}' couldn't be parsed! Ignored.")
      lines_with_errors += 1
      continue
    # parts[1] contains years, in parts[2] the years are written out
    # e.g. ['LJ001-0045', '1469, 1470;', 'fourteen sixty-nine, fourteen seventy;']
    basename = parts[0]
    wav_file_abs = wav_dir / f'{basename}.wav'
    if not wav_file_abs.is_file():
      flogger.error(f"Line {line_nr}: File '{str(wav_file_abs)}' was not found. Ignored.")
      lines_with_errors += 1
      continue

    text = parts[2]
    if len(text) == 0:
      flogger.error(f"Line {line_nr}: Empty line. Ignored.")
      lines_with_errors += 1
      continue

    wav_file_relative = wav_file_abs.relative_to(directory)

    #flogger.debug(f"Processing '{str(wav_file_relative)}'...")
    wav_file_in = directory / wav_file_relative
    assert wav_file_in.is_file()

    # stem_out = f"{speaker_dir_name};{wav_file_relative.stem}"
    stem_out = str(file_counter).zfill(z_fill)
    wav_file_out = speaker_dir_out_abs / f"{stem_out}.wav"
    grid_file_out = speaker_dir_out_abs / f"{stem_out}.TextGrid"
    file_counter += 1

    try:
      grid = create_grid(wav_file_in, text, tier, n_digits)
    except Exception as ex:
      flogger.debug(ex)
      flogger.error(f"Audio file \"{wav_file_in.absolute()}\" couldn't be read! Ignored.")
      lines_with_errors += 1
      continue

    try:
      grid_file_out.parent.mkdir(parents=True, exist_ok=True)
    except Exception as ex:
      flogger.debug(ex)
      flogger.error(
        f"Parent folder \"{grid_file_out.parent.absolute()}\" for grid \"{grid_file_out.absolute()}\" couldn't be created! Ignored.")
      lines_with_errors += 1
      continue

    try:
      with codecs.open(grid_file_out, 'w', encoding) as file:
        grid.write(file)
    except Exception as ex:
      flogger.debug(ex)
      flogger.error(f"Grid \"{grid_file_out.absolute()}\" couldn't be saved! Ignored.")
      lines_with_errors += 1
      continue

    if symlink:
      try:
        wav_file_out.symlink_to(wav_file_in)
      except Exception as ex:
        flogger.debug(ex)
        flogger.error(
          f"Symbolic link to audio file \"{wav_file_in.absolute()}\" at \"{wav_file_out.absolute()}\" couldn't be created! Ignored.")
        lines_with_errors += 1
        continue
    else:
      try:
        copy2(wav_file_in, wav_file_out)
      except Exception as ex:
        flogger.debug(ex)
        flogger.error(
          f"Audio file \"{wav_file_in.absolute()}\" couldn't be copied to \"{wav_file_out.absolute()}\"! Ignored.")
        lines_with_errors += 1
        continue

    hypothetical_grid_file_in = wav_file_in.parent / f"{wav_file_in.stem}.TextGrid"
    file_name_mapping[str(grid_file_out.relative_to(
      output_directory))] = str(hypothetical_grid_file_in.relative_to(directory))
    file_name_mapping[str(wav_file_out.relative_to(
      output_directory))] = str(wav_file_in.relative_to(directory))

  if lines_with_errors > 0:
    logger.warning(f"{lines_with_errors} lines couldn't be parsed!")

  all_successful = lines_with_errors == 0

  file_name_mapping_json_path = output_directory / "filename-mapping.json"
  try:
    with open(file_name_mapping_json_path, mode="w", encoding="UTF-8") as f:
      json.dump(file_name_mapping, f, indent=2)
  except Exception as ex:
    flogger.debug(ex)
    flogger.error(
      f"Mapping file \"{file_name_mapping_json_path.absolute()}\" couldn't be written!")
    all_successful = False

  logger.info(f"Saved output to: \"{output_directory.absolute()}\".")

  return all_successful
