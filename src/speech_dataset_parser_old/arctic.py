from logging import getLogger
from pathlib import Path
from typing import Tuple

from speech_dataset_parser_core.utils import (get_basename, get_filepaths,
                                              get_subfolders, read_lines)
from tqdm import tqdm

from speech_dataset_parser_old.data import PreData, PreDataList
from speech_dataset_parser_old.gender import Gender
from speech_dataset_parser_old.language import Language
from speech_dataset_parser_old.text_format import TextFormat

README_FILE = "README.md"


def parse(dir_path: Path) -> PreDataList:
  logger = getLogger(__name__)
  if not dir_path.exists():
    ex = ValueError(f"Directory not found: {dir_path}")
    logger.error("", exc_info=ex)
    raise ex

  readme_path = dir_path / README_FILE
  readme = read_lines(readme_path)
  readme = readme[34:58]
  speakers_dict = {}
  for speaker_details in readme:
    name, gender, accent, _, _ = speaker_details[1:-1].split("|")
    speakers_dict[name] = gender, accent

  speaker_folders = get_subfolders(dir_path)
  symbols_language = Language.ENG
  symbols_format = TextFormat.GRAPHEMES

  entries = PreDataList()

  logger.info("Parsing files...")
  for speaker_folder in tqdm(speaker_folders):
    speaker_name = get_basename(speaker_folder)
    if speaker_name not in speakers_dict.keys():
      logger.info(f"Skipping {speaker_name}")
      continue
    wavs = get_filepaths(speaker_folder / "wav")
    # count only 150, they do not contain good IPA
    # annotations = get_filepaths(speaker_folder / "annotation")
    textgrids = get_filepaths(speaker_folder / "textgrid")
    transcripts = get_filepaths(speaker_folder / "transcript")

    assert len(wavs) == len(textgrids) == len(transcripts)

    speaker_name = get_basename(speaker_folder)
    speaker_gender, speaker_accent = speakers_dict[speaker_name]
    gender = Gender.MALE if speaker_gender == "M" else Gender.FEMALE

    for i, (wav, transcript) in enumerate(zip(wavs, transcripts)):
      text_en = transcript.read_text()
      text_en = f"{text_en}."
      text_en_symbols = tuple(text_en)

      entry = PreData(
        identifier=0,
        basename=get_basename(wav),
        speaker_name=speaker_name,
        speaker_accent=speaker_accent,
        symbols=text_en_symbols,
        symbols_format=symbols_format,
        relative_audio_path=wav.relative_to(dir_path),
        speaker_gender=gender,
        symbols_language=symbols_language,
      )

      entries.append(entry)

  entries.sort(key=sort_arctic, reverse=False)
  entries.set_identifiers()

  logger.info(f"Parsed {len(entries)} entries from {len(speakers_dict)} speakers.")

  return entries


def sort_arctic(entry: PreData) -> Tuple[str, str]:
  return entry.speaker_name, entry.basename
