from logging import getLogger
from pathlib import Path
from typing import Tuple

from tqdm import tqdm

from speech_dataset_parser.data import PreData, PreDataList
from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import Language
from speech_dataset_parser.text_format import TextFormat
from speech_dataset_parser.utils import (get_basename, get_filepaths,
                                         get_subfolders, read_lines, read_text)

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
  lang = Language.ENG
  text_format = TextFormat.GRAPHEMES

  entries = PreDataList()

  logger.info("Parsing files...")
  for speaker_folder in tqdm(speaker_folders):
    speaker_name = get_basename(speaker_folder)
    if speaker_name not in speakers_dict.keys():
      logger.info(f"Skipping {speaker_name}")
      continue
    wavs = get_filepaths(speaker_folder / "wav")
    # count only 150, they do not contain good IPA
    annotations = get_filepaths(speaker_folder / "annotation")
    textgrids = get_filepaths(speaker_folder / "textgrid")
    transcripts = get_filepaths(speaker_folder / "transcript")

    assert len(wavs) == len(textgrids) == len(transcripts)

    speaker_name = get_basename(speaker_folder)
    speaker_gender, speaker_accent = speakers_dict[speaker_name]
    gender = Gender.MALE if speaker_gender == "M" else Gender.FEMALE

    for wav, transcript in zip(wavs, transcripts):
      text_en = read_text(transcript)
      text_en = f"{text_en}."

      entry = PreData(
        identifier=get_basename(wav),
        speaker_name=speaker_name,
        speaker_accent=speaker_accent,
        text=text_en,
        text_format=text_format,
        wav_path=wav,
        speaker_gender=gender,
        text_language=lang,
      )

      entries.append(entry)

  entries.sort(key=sort_arctic, reverse=False)
  logger.info(f"Parsed {len(entries)} entries from {len(speakers_dict)} speakers.")

  return entries


def sort_arctic(entry: PreData) -> Tuple[str, str]:
  return entry.speaker_name, entry.identifier
