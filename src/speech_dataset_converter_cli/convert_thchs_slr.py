import codecs
import glob
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


def get_convert_thchs_slr_to_generic_parser(parser: ArgumentParser):
  parser.description = "This command converts the THCHS-30 dataset (OpenSLR version) to a generic one."
  parser.add_argument("directory", type=parse_existing_directory, metavar="THCHS-DIRECTORY",
                      help="directory containing the THCHS-30 content, i.e., \"data_thchs30\"")
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
  parser.add_argument("-p", "--add-punctuation-marks", action="store_true",
                      help="add question marks (？) after particles 吗, 呢 and 吧, otherwise add a dot (。)")
  return convert_to_generic_ns


def convert_to_generic_ns(ns: Namespace, flogger: Logger, logger: Logger) -> bool:
  if ns.output_directory == ns.directory:
    logger.error(
      "Parameter 'THCHS-DIRECTORY' and 'OUTPUT-DIRECTORY': The two directories need to be distinct!")
    return False

  successful = convert_to_generic(ns.directory, ns.symlink, ns.n_digits,
                                  ns.tier, ns.output_directory, ns.encoding, ns.add_punctuation_marks, flogger, logger)

  return successful


QUESTION_PARTICLE_1 = '吗'
QUESTION_PARTICLE_2 = '呢'
# doesn't occur
QUESTION_PARTICLE_3 = '吧'

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


def convert_to_generic(directory: Path, symlink: bool, n_digits: int, tier: str, output_directory: Path, encoding: str, add_punctuation: bool, flogger: Logger, logger: Logger) -> bool:
  file_name_mapping = OrderedDict()

  lines_with_errors = 0
  max_file_count = 250
  z_fill = len(str(max_file_count))

  sent_paths = directory / "data" / "*.trn"
  wav_paths = directory / "data" / "*.wav"

  existing_sent_files = set(glob.glob(str(sent_paths)))
  wav_files = [Path(file) for file in glob.glob(str(wav_paths))]
  generated_sent_files = [Path(f"{wav_file}.trn") for wav_file in wav_files]

  wavs_sents = sorted(tuple(zip(wav_files, generated_sent_files)))
  skipped = [wav_file for wav_file, sent_file_gen in wavs_sents if str(
    sent_file_gen) not in existing_sent_files]
  wavs_sents_filtered = [(wav_file, sent_file_gen) for wav_file,
                         sent_file_gen in wavs_sents if str(sent_file_gen) in existing_sent_files]

  if len(skipped) > 0:
    logger.info(
      f"Skipped: {len(skipped)} of {len(generated_sent_files)} because not both .txt and .wav files exist!")
    lines_with_errors = len(skipped)

  lang = "chi"

  file_counters = {}

  for wav_file_in, txt_file_in in tqdm(wavs_sents_filtered, desc="Converting", unit=" utterances"):
    try:
      txt_content = txt_file_in.read_text("UTF-8")
    except Exception as ex:
      logger.debug(ex)
      logger.error(f"File \"{txt_file_in.absolute()}\" couldn't be read!")
      lines_with_errors += 1
      continue

    txt_lines = txt_content.splitlines()
    if len(txt_lines) == 0:
      logger.error(f"File \"{txt_file_in.absolute()}\" has the wrong format!")
      lines_with_errors += 1
      continue

    chinese = txt_lines[0]
    chinese = chinese.rstrip()

    parts = wav_file_in.stem.split("_")
    if len(parts) != 2:
      logger.error(f"File \"{wav_file_in.absolute()}\" has the wrong format!")
      lines_with_errors += 1
      continue

    speaker_name = parts[0]

    if speaker_name not in file_counters:
      file_counters[speaker_name] = 1

    speaker_gender = GENDER_MALE if speaker_name in MALE_SPEAKERS else GENDER_FEMALE

    # some lines end with a space, e.g. train L5: A11_102
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

    speaker_dir_name = f"{speaker_name}{PARTS_SEP}{speaker_gender}{PARTS_SEP}{lang}"
    if speaker_name in ACCENTS:
      accent_name = ACCENTS[speaker_name]
      speaker_dir_name += f"{PARTS_SEP}{accent_name}"
    speaker_dir_out_abs = output_directory / speaker_dir_name

    file_stem = str(file_counters[speaker_name]).zfill(z_fill)
    wav_file_out = speaker_dir_out_abs / f"{file_stem}.wav"
    grid_file_out = speaker_dir_out_abs / f"{file_stem}.TextGrid"
    file_counters[speaker_name] += 1

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
