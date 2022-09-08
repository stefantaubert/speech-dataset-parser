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
from speech_dataset_parser.parse import (DEFAULT_ENCODING, DEFAULT_N_DIGITS, DEFAULT_TIER_NAME,
                                         PARTS_SEP)
from speech_dataset_parser.types import GENDER_MALE


def get_convert_thchs_to_generic_parser(parser: ArgumentParser):
  parser.description = "This command converts the THCHS-30 dataset to a generic one."
  parser.add_argument("directory", type=parse_existing_directory, metavar="THCHS-DIRECTORY",
                      help="directory containing the THCHS-30 content")
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
                                  ns.tier, ns.output_directory, ns.encoding, flogger, logger)

  return successful


QUESTION_PARTICLE_1 = '吗'
QUESTION_PARTICLE_2 = '呢'

MALE_SPEAKERS = {"A8", "A9", "A33", "A35", "B8", "B21", "B34", "C8", "D8"}

ACCENTS = {
  "D4": "Mandarin",  # Standard Mandarin
  "D6": "Mandarin",  # Standard Mandarin
}


def convert_to_generic(directory: Path, symlink: bool, n_digits: int, tier: str, output_directory: Path, encoding: str, flogger: Logger, logger: Logger) -> bool:

  train_words = directory / 'doc/trans/train.word.txt'
  test_words = directory / 'doc/trans/test.word.txt'
  train_wavs = directory / 'wav/train/'
  test_wavs = directory / 'wav/test/'

  parse_paths = [
    (train_words, train_wavs),
    (test_words, test_wavs)
  ]

  lang = "chi"
  lines_with_errors = 0

  logger.info("Parsing files...")
  for words_path, wavs_dir in parse_paths:

    try:
      words_content = words_path.read_text("UTF-8")
    except Exception as ex:
      logger.debug(ex)
      logger.error(f"File \"{words_path.absolute()}\" couldn't be read!")
      return False

    lines = words_content.splitlines()

    line: str
    for line_nr, line in enumerate(tqdm(lines, desc="Converting", unit=" file(s)"), start=1):
      pos = line.find(' ')
      try:
        name, chinese = line[:pos], line[pos + 1:]
        speaker_name, nr = name.split("_")
      except Exception as ex:
        flogger.error(
          f"Line {line_nr}: '{line}' in file \"{words_path.absolute()}\" couldn't be parsed! Ignored.")
        lines_with_errors += 1
      speaker_gender = GENDER_MALE if speaker_name in MALE_SPEAKERS else GENDER_FEMALE
      # nr = int(nr)
      # speaker_name_letter = speaker_name[0]
      # speaker_name_number = int(speaker_name[1:])
      wav_file_in = wavs_dir / speaker_name / f"{name}.wav"
      if not wav_file_in.exists():
        wav_file_in = wavs_dir / speaker_name / f"{name}.WAV"
      if not wav_file_in.exists():
        logger.info(f"Did not found wav file: \"{wav_file_in.absolute()}\"! Skipped.")
        lines_with_errors += 1
        continue

      # remove "l =" from transcription because it is not Chinese
      # 徐 希君 肖 金生 刘 文华 屈 永利 王开 宇 骆 瑛 等 也 被 分别 判处 l = 六年 至 十 五年 有期徒刑
      # occurs only in sentences with nr. 374, e.g. B22_374
      chinese = chinese.replace(" l = ", " ")
      is_question = str.endswith(chinese, QUESTION_PARTICLE_1) or str.endswith(
        chinese, QUESTION_PARTICLE_2)
      if is_question:
        chinese += "？"
      else:
        chinese += "。"

      speaker_dir_name = f"{speaker_name}{PARTS_SEP}{speaker_gender}{PARTS_SEP}{lang}"
      accent_name = speaker_name
      if speaker_name in ACCENTS.keys():
        accent_name = ACCENTS[speaker_name]
        speaker_dir_name += f"{PARTS_SEP}{accent_name}"
      speaker_dir_out_abs = output_directory / speaker_dir_name

      wav_file_out = speaker_dir_out_abs / f"{wav_file_in.stem}.wav"
      grid_file_out = speaker_dir_out_abs / f"{wav_file_in.stem}.TextGrid"

      try:
        grid = create_grid(wav_file_in, chinese, tier, n_digits)
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

  if lines_with_errors > 0:
    logger.warning(f"{lines_with_errors} lines couldn't be parsed!")

  all_successful = lines_with_errors == 0
  logger.info(f"Saved output to: '{output_directory.absolute()}'.")
  return all_successful
