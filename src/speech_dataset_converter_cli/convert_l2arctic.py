import codecs
from argparse import ArgumentParser, Namespace
from logging import Logger
from pathlib import Path
from shutil import copy2

from tqdm import tqdm

from speech_dataset_converter_cli.argparse_helper import (parse_codec, parse_existing_directory,
                                                          parse_non_empty_or_whitespace,
                                                          parse_non_existing_directory)
from speech_dataset_converter_cli.utils import (create_grid, get_filenames, get_filepaths,
                                                get_subfolders)
from speech_dataset_parser import GENDER_FEMALE
from speech_dataset_parser.parse import (DEFAULT_ENCODING, DEFAULT_N_DIGITS, DEFAULT_TIER_NAME,
                                         PARTS_SEP)
from speech_dataset_parser.types import GENDER_MALE


def get_convert_l2arctic_to_generic_parser(parser: ArgumentParser):
  parser.description = "This command converts the L2-ARCTIC dataset to a generic one."
  parser.add_argument("directory", type=parse_existing_directory, metavar="L2-ARCTIC-DIRECTORY",
                      help="directory containing the L2-ARCTIC content")
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
    logger.error("Parameter 'directory' and 'output_directory': The two directories need to be distinct!")
    return False

  successful = convert_to_generic(ns.directory, ns.symlink, ns.n_digits,
                                  ns.tier, ns.output_directory, ns.encoding, flogger)

  return successful


def convert_to_generic(directory: Path, symlink: bool, n_digits: int, tier: str, output_directory: Path, encoding: str, logger: Logger) -> bool:
  language = "eng"
  readme_path = directory / "README.md"

  try:
    readme = readme_path.read_text("UTF-8")
  except Exception as ex:
    logger.debug(ex)
    logger.error("README.md couldn't be read!")
    return False

  #speaker_folders = get_subfolders(directory)

  lines_with_errors = 0

  # strip last empty line
  readme_lines = readme.splitlines()

  lines = readme_lines[34:58]

  for readme_line_nr, speaker_details in enumerate(lines, start=35):
    if not len(speaker_details) > 1:
      logger.error(f"Line {readme_line_nr}: '{speaker_details}' couldn't be parsed! Ignored.")
      lines_with_errors += 1
      continue

    parts = speaker_details[1:-1].split("|")

    if not len(parts) == 5:
      logger.error(
        f"README line {readme_line_nr}: '{speaker_details}' couldn't be parsed! Ignored.")
      lines_with_errors += 1
      continue

    name, gender, accent, _, _ = parts
    logger.info(f"Parsing {name} ({readme_line_nr - 34}/{len(lines)})...")
    speaker_gender = GENDER_MALE if gender == "M" else GENDER_FEMALE
    speaker_dir = directory / name
    wav_dir = speaker_dir / "wav"
    txt_dir = speaker_dir / "transcript"
    txt_files = get_filenames(txt_dir)

    speaker_dir_out_abs = output_directory / \
        f"{name}{PARTS_SEP}{speaker_gender}{PARTS_SEP}{language}{PARTS_SEP}{accent}"

    txt_file_name: str
    for txt_file_name in tqdm(txt_files, desc="Creating files", unit=" file(s)"):
      txt_file = txt_dir / txt_file_name
      wav_file_in = wav_dir / f"{Path(txt_file_name).stem}.wav"
      if not wav_file_in.is_file():
        logger.error(f"No .wav file found for transcript '{txt_file_name}'! Ignored.")
        continue

      wav_file_out = speaker_dir_out_abs / wav_file_in.name
      grid_file_out = speaker_dir_out_abs / f"{wav_file_in.stem}.TextGrid"

      try:
        text = txt_file.read_text("UTF-8")
      except Exception as ex:
        logger.debug(ex)
        logger.error(f"'{txt_file_name}' couldn't be read! Ignored.")
        continue

      # append '.' on end
      text += "."

      try:
        grid = create_grid(wav_file_in, text, tier, n_digits)
      except Exception as ex:
        logger.debug(ex)
        logger.error(f"Audio file \"{wav_file_in.absolute()}\" couldn't be read! Ignored.")
        lines_with_errors += 1
        continue

      try:
        grid_file_out.parent.mkdir(parents=True, exist_ok=True)
      except Exception as ex:
        logger.debug(ex)
        logger.error(
          f"Parent folder \"{grid_file_out.parent.absolute()}\" for grid \"{grid_file_out.absolute()}\" couldn't be created! Ignored.")
        lines_with_errors += 1
        continue

      try:
        with codecs.open(grid_file_out, 'w', encoding) as file:
          grid.write(file)
      except Exception as ex:
        logger.debug(ex)
        logger.error(f"Grid \"{grid_file_out.absolute()}\" couldn't be saved! Ignored.")
        lines_with_errors += 1
        continue

      if symlink:
        try:
          wav_file_out.symlink_to(wav_file_in)
        except Exception as ex:
          logger.debug(ex)
          logger.error(
            f"Symbolic link to audio file \"{wav_file_in.absolute()}\" at \"{wav_file_out.absolute()}\" couldn't be created! Ignored.")
          lines_with_errors += 1
          continue
      else:
        try:
          copy2(wav_file_in, wav_file_out)
        except Exception as ex:
          logger.debug(ex)
          logger.error(
            f"Audio file \"{wav_file_in.absolute()}\" couldn't be copied to \"{wav_file_out.absolute()}\"! Ignored.")
          lines_with_errors += 1
          continue

  if lines_with_errors > 0:
    logger.warning(f"{lines_with_errors} lines couldn't be parsed!")

  all_successful = lines_with_errors == 0
  logger.info(f"Saved output to: '{output_directory.absolute()}'.")
  return all_successful
