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
from speech_dataset_parser.types import GENDER_MALE


def get_convert_thchs_cslt_to_generic_parser(parser: ArgumentParser):
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
  parser.add_argument("-g", "--group", action="store_true", help="try to group same speakers")
  parser.add_argument("-p", "--add-punctuation-marks", action="store_true",
                      help="add question marks (？) after particles 吗, 呢 and 吧, otherwise add a dot (。)")
  return convert_to_generic_ns


def convert_to_generic_ns(ns: Namespace, flogger: Logger, logger: Logger) -> bool:
  if ns.output_directory == ns.directory:
    logger.error(
      "Parameter 'THCHS-DIRECTORY' and 'OUTPUT-DIRECTORY': The two directories need to be distinct!")
    return False

  successful = convert_to_generic(ns.directory, ns.symlink, ns.n_digits,
                                  ns.tier, ns.group, ns.output_directory, ns.encoding, ns.add_punctuation_marks, flogger, logger)

  return successful


QUESTION_PARTICLE_1 = '吗'
QUESTION_PARTICLE_2 = '呢'
# doesn't occur
QUESTION_PARTICLE_3 = '吧'

GROUPS = {
  "A2": "ABC2",
  "B2": "ABC2",
  "C2": "ABC2",

  "A4": "ABCD4",
  "B4": "ABCD4",
  "C4": "ABCD4",
  "D4": "ABCD4",

  "A6": "ABCD6",
  "B6": "ABCD6",
  "C6": "ABCD6",
  "D6": "ABCD6",

  "A7": "ABCD7",
  "B7": "ABCD7",
  "C7": "ABCD7",
  "D7": "ABCD7",

  "A8": "ABCD8",
  "B8": "ABCD8",
  "C8": "ABCD8",
  "D8": "ABCD8",

  "A11": "ABD11",
  "B11": "ABD11",
  "D11": "ABD11",

  "A23": "AC23",
  "C23": "AC23",

  "A13": "A13C12",
  "C12": "A13C12",

  "A19": "A19B15",
  "B15": "A19B15",

  "A22": "A22C21",
  "C21": "A22C21",

  "A32": "A32C31",
  "C31": "A32C31",
}

MALE_SPEAKERS = {"A9", "A33", "A35", "B21", "B34", "A8", "B8", "C8", "D8"}

ACCENTS = {
  "A4": "Mandarin",
  "B4": "Mandarin",
  "C4": "Mandarin",
  "D4": "Mandarin",
  "A6": "Mandarin",
  "B6": "Mandarin",
  "C6": "Mandarin",
  "D6": "Mandarin",
}


def convert_to_generic(directory: Path, symlink: bool, n_digits: int, tier: str, group: bool, output_directory: Path, encoding: str, add_punctuation: bool, flogger: Logger, logger: Logger) -> bool:
  file_name_mapping = OrderedDict()

  max_file_count = 4 * 250 if group else 250
  z_fill = len(str(max_file_count))

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

  file_counters = {}

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
        speaker_name, audio_nr = name.split("_")
      except Exception as ex:
        flogger.debug(ex)
        flogger.error(
          f"Line {line_nr}: '{line}' in file \"{words_path.absolute()}\" couldn't be parsed! Ignored.")
        lines_with_errors += 1
      # nr = int(nr)
      if group:
        speaker_name_new = GROUPS.get(speaker_name, speaker_name)
      else:
        speaker_name_new = speaker_name

      if speaker_name_new not in file_counters:
        file_counters[speaker_name_new] = 1

      # speaker_name_letter = speaker_name_part[0]
      # speaker_name_number = int(speaker_name_part[1:])
      speaker_gender = GENDER_MALE if speaker_name in MALE_SPEAKERS else GENDER_FEMALE
      wav_file_in = wavs_dir / speaker_name / f"{name}.wav"
      if not wav_file_in.exists():
        wav_file_in = wavs_dir / speaker_name / f"{name}.WAV"
      if not wav_file_in.exists():
        logger.info(f"Did not found wav file: \"{wav_file_in.absolute()}\"! Skipped.")
        lines_with_errors += 1
        continue

      # some lines end with a space, e.g. train L5: A11_102
      chinese = chinese.rstrip()
      # remove "l =" from transcription because it is not Chinese
      # 徐 希君 肖 金生 刘 文华 屈 永利 王开 宇 骆 瑛 等 也 被 分别 判处 l = 六年 至 十 五年 有期徒刑
      # occurs only in sentences with nr. 374, e.g. B22_374
      chinese = chinese.replace(" l = ", " ")
      if add_punctuation:
        is_question = str.endswith(chinese, QUESTION_PARTICLE_1) or str.endswith(
          chinese, QUESTION_PARTICLE_2) or str.endswith(
          chinese, QUESTION_PARTICLE_3)
        if is_question:
          chinese += "？"
        else:
          chinese += "。"

      speaker_dir_name = f"{speaker_name_new}{PARTS_SEP}{speaker_gender}{PARTS_SEP}{lang}"
      if speaker_name_new in ACCENTS:
        accent_name = ACCENTS[speaker_name]
        speaker_dir_name += f"{PARTS_SEP}{accent_name}"
      speaker_dir_out_abs = output_directory / speaker_dir_name

      file_stem = str(file_counters[speaker_name_new]).zfill(z_fill)
      wav_file_out = speaker_dir_out_abs / f"{file_stem}.wav"
      grid_file_out = speaker_dir_out_abs / f"{file_stem}.TextGrid"
      file_counters[speaker_name_new] += 1

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
