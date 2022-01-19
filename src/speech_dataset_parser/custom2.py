# from copy import deepcopy
# from dataclasses import dataclass
# from logging import getLogger
# from pathlib import Path
# from shutil import copy2
# from typing import List

# from general_utils import load_obj, save_obj
# from general_utils.main import cast_as
# from tqdm import tqdm

# from speech_dataset_parser.data import PreData, PreDataList, Symbols
# from speech_dataset_parser.gender import Gender
# from speech_dataset_parser.language import Language
# from speech_dataset_parser.text_format import TextFormat

# DATA_NAME = "data.pkl"
# AUDIO_FOLDER_NAME = "audio"


# @dataclass()
# class Recording:
#   basename: str
#   symbols: Symbols
#   symbols_format: TextFormat
#   symbols_language: Language
#   speaker_name: str
#   speaker_accent: str
#   speaker_gender: Gender
#   absolute_audio_path: Path


# def save(recordings: List[Recording], target_dir_path: Path) -> None:
#   logger = getLogger(__name__)
#   new_data = PreDataList()
#   entry: Recording
#   new_identifier: int
#   for new_identifier, entry in tqdm(enumerate(recordings)):
#     target_file_name = f"{new_identifier}{entry.relative_audio_path.suffix.lower()}"
#     target_audio_path = target_dir_path / AUDIO_FOLDER_NAME / target_file_name
#     if not entry.absolute_audio_path.is_file():
#       logger.info(f"Audio does not exist: {entry.absolute_audio_path}")
#       raise Exception()

#     copy2(entry.absolute_audio_path, target_audio_path)

#     predata_entry = PreData(
#       identifier=new_identifier,
#       basename=entry.basename,
#       relative_audio_path=target_audio_path.relative_to(target_dir_path),
#       speaker_accent=entry.speaker_accent,
#       speaker_gender=entry.speaker_gender,
#       speaker_name=entry.speaker_name,
#       symbols=entry.symbols,
#       symbols_format=entry.symbols_format,
#       symbols_language=entry.symbols_language,
#     )

#     new_data.append(predata_entry)

#   target_data_path = target_dir_path / DATA_NAME
#   save_obj(new_data, target_data_path)
#   logger.info(f"Written output to: {target_dir_path}")


# def parse(dir_path: Path) -> PreDataList:
#   logger = getLogger(__name__)
#   data_path = dir_path / DATA_NAME
#   if not data_path.is_file():
#     logger.error("Data file not found!")
#     raise Exception()

#   result = cast_as(load_obj(data_path), PreDataList)
#   entry: PreData
#   for entry in result.items():
#     audio_path = dir_path / entry.relative_audio_path
#     if not audio_path.is_file():
#       logger.error(f"Audio file not found: {audio_path}")
#       raise Exception()

#   return result
