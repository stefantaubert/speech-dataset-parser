from argparse import ArgumentParser, Namespace
from logging import getLogger

from speech_dataset_parser_core.convert_ljs import convert_to_generic

from speech_dataset_parser_app.argparse_helper import (
    parse_existing_directory, parse_non_empty_or_whitespace, parse_path)


def get_convert_ljs_to_generic_parser(parser: ArgumentParser):
  parser.description = "This command converts the LJSpeech dataset to a generic one."
  parser.add_argument("directory", type=parse_existing_directory, metavar="directory",
                      help="directory containing the LJSpeech content")
  parser.add_argument("output_directory", type=parse_path, metavar="output-directory",
                      help="output directory")
  parser.add_argument("--tier", type=parse_non_empty_or_whitespace, metavar="NAME",
                      help="name of the tier", default="transcription")
  parser.add_argument("--n_digits", type=int, choices=range(17), metavar="DIGITS",
                      help="number of digits in textgrid", default=16)
  parser.add_argument("-s", "--symlink", action="store_true",
                      help="create symbolic links to the audio files instead of copies")
  parser.add_argument("-o", "--overwrite", action="store_true",
                      help="overwrite files")
  return convert_to_generic_ns


def convert_to_generic_ns(ns: Namespace):
  logger = getLogger(__name__)

  if ns.output_directory == ns.directory:
    logger.error("The two directories need to be distinct!")
    return

  convert_to_generic(ns.directory, ns.symlink, ns.n_digits,
                     ns.tier, ns.output_directory, ns.overwrite)
