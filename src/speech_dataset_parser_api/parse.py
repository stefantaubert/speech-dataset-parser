from pathlib import Path
from typing import Generator

from speech_dataset_parser_core.parse import parse_generic_core
from speech_dataset_parser_core.types import Entry


def parse_directory(directory: Path, tier_name: str, n_digits: int) -> Generator[Entry, None, None]:
  if not directory.is_dir():
    raise ValueError("Directory was not found!")

  if not 0 <= n_digits <= 16:
    raise ValueError("Parameter 'n_digits' needs to be in interval [0,16]")

  if not isinstance(n_digits, int):
    raise ValueError("Parameter 'n_digits' needs to be int!")

  return parse_generic_core(directory, tier_name, n_digits)
