# from dataclasses import dataclass
# from logging import getLogger
# from pathlib import Path
# from typing import List, Tuple

# import pandas as pd
# from general_utils import get_subfolders
# from tqdm import tqdm

# from speech_dataset_parser_old.data import PreData, PreDataList, Symbols
# from speech_dataset_parser_old.gender import Gender
# from speech_dataset_parser_old.language import (Language, get_lang_from_str,
#                                             is_lang_from_str_supported)
# from speech_dataset_parser_old.text_format import TextFormat

# DATA_CSV_NAME = "data.csv"
# AUDIO_FOLDER_NAME = "audio"


# @dataclass
# class CustomEntry():
#   identifier: int
#   basename: str
#   symbols: Symbols
#   symbols_format: TextFormat
#   symbols_language: Language
#   speaker_name: str
#   speaker_accent: str
#   speaker_gender: Gender
#   relative_audio_path: Path


# class CustomEntries(list):
#   def items(self) -> List[CustomEntry]:
#     return self

#   @classmethod
#   def load(cls, file_path: Path):
#     data = pd.read_csv(file_path, header=None, sep="\t")
#     data_loaded: List[CustomEntry] = [CustomEntry(*xi) for xi in data.values]
#     res = cls(data_loaded)
#     res.load_init()
#     return res

#   def load_init(self):
#     for entry in self.items():
#       entry.symbols = str(entry.symbols)
#       entry.speaker_name = str(entry.speaker_name)
#       entry.speaker_accent = str(entry.speaker_accent)


# def sort_entries_key(entry: PreData) -> Tuple[str, Path]:
#   return entry.speaker_name, entry.relative_audio_path


# def parse(dir_path: Path) -> PreDataList:
#   logger = getLogger(__name__)
#   if not dir_path.exists():
#     ex = ValueError(f"Directory not found: {dir_path}")
#     logger.error("", exc_info=ex)
#     raise ex

#   result = PreDataList()
#   tmp: List[Tuple[Tuple, PreDataList]] = []
#   text_format = TextFormat.PHONES_IPA

#   subfolders = get_subfolders(dir_path)
#   subfolder: Path
#   for subfolder in tqdm(subfolders):
#     data_path = subfolder / DATA_CSV_NAME
#     entries = CustomEntries.load(data_path)
#     for entry in entries.items():
#       if not is_lang_from_str_supported(entry.text_language):
#         logger.warning(
#           f"Entry {entry.entry_id} couldn't be parsed because it contains an unknown language {entry.text_language}!")
#         continue
#       gender = Gender.MALE if entry.speaker_gender == "m" else Gender.FEMALE
#       wav_path = subfolder / AUDIO_FOLDER_NAME / entry.wav
#       data = PreData(
#         identifier=entry.entry_id,
#         speaker_name=entry.speaker_name,
#         speaker_accent=entry.speaker_accent,
#         symbols_language=get_lang_from_str(entry.text_language),
#         relative_audio_path=wav_path,
#         speaker_gender=gender,
#         symbols=entry.symbols,
#         symbols_format=text_format,
#       )
#       sorting_keys = entry.speaker_name, subfolder, entry.entry_id
#       tmp.append((sorting_keys, data))

#   tmp.sort(key=lambda x: x[0])

#   result = PreDataList([x for _, x in tmp])

#   return result
