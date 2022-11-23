import codecs
import json
from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from logging import Logger
from pathlib import Path
from shutil import copy2
from typing import Dict

from tqdm import tqdm

from speech_dataset_converter_cli.argparse_helper import (parse_codec, parse_existing_directory,
                                                          parse_non_empty_or_whitespace,
                                                          parse_non_existing_directory)
from speech_dataset_converter_cli.utils import create_grid
from speech_dataset_parser import GENDER_FEMALE
from speech_dataset_parser.parse import (DEFAULT_ENCODING, DEFAULT_N_DIGITS, DEFAULT_TIER_NAME,
                                         PARTS_SEP)


def get_structure_restoring_parser(parser: ArgumentParser):
  parser.description = "This command restores the original structure."
  parser.add_argument("directory", type=parse_existing_directory, metavar="LJ-SPEECH-DIRECTORY",
                      help="directory containing the LJSpeech content")
  parser.add_argument("output_directory", type=parse_non_existing_directory, metavar="OUTPUT-DIRECTORY",
                      help="output directory")
  parser.add_argument("-s", "--symlink", action="store_true",
                      help="create symbolic links to the audio files instead of copies")
  return restore_structure_ns


def restore_structure_ns(ns: Namespace, flogger: Logger, logger: Logger) -> bool:
  if ns.output_directory == ns.directory:
    logger.error("Parameter 'directory' and 'output_directory': The two directories need to be distinct!")
    return False

  successful = restore_structure(ns.directory, ns.symlink, ns.output_directory, flogger, logger)

  return successful


def restore_structure(directory: Path, symlink: bool, output_directory: Path, flogger: Logger, logger: Logger) -> bool:
  file_name_mapping_json_path = directory / "filename-mapping.json"
  try:
    with open(file_name_mapping_json_path, mode="r", encoding="UTF-8") as f:
      file_name_mapping: Dict[str, str] = json.load(f)
  except Exception as ex:
    flogger.debug(ex)
    flogger.error(
      f"Mapping file \"{file_name_mapping_json_path.absolute()}\" couldn't be read!")
    return False

  for from_path_rel, to_path_rel in tqdm(file_name_mapping.items()):
    from_path = directory / from_path_rel
    to_path = output_directory / to_path_rel

    try:
      to_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as ex:
      flogger.debug(ex)
      flogger.error(
        f"Parent folder \"{to_path.parent.absolute()}\" for file \"{to_path.absolute()}\" couldn't be created! Ignored.")
      lines_with_errors += 1
      continue

    if symlink:
      try:
        from_path.symlink_to(to_path)
      except Exception as ex:
        flogger.debug(ex)
        flogger.error(
          f"Symbolic link to file \"{to_path.absolute()}\" at \"{from_path.absolute()}\" couldn't be created! Ignored.")
        lines_with_errors += 1
        continue
    else:
      try:
        copy2(from_path, to_path)
      except Exception as ex:
        flogger.debug(ex)
        flogger.error(
          f"File \"{from_path.absolute()}\" couldn't be copied to \"{to_path.absolute()}\"! Ignored.")
        lines_with_errors += 1
        continue

  if lines_with_errors > 0:
    logger.warning(f"{lines_with_errors} files couldn't be copied!")

  all_successful = lines_with_errors == 0

  return all_successful
