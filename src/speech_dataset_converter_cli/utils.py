import os
import wave
from collections import OrderedDict
from pathlib import Path
from typing import Generator, List
from typing import OrderedDict as ODType
from typing import Set, Tuple, cast

from textgrid import Interval, IntervalTier, TextGrid


def get_files_dict(directory: Path, filetypes: Set[str]) -> ODType[str, Path]:
  result = OrderedDict(sorted(get_files_tuples(directory, filetypes)))
  return result


def get_files_tuples(directory: Path, filetypes: Set[str]) -> Generator[Tuple[str, Path], None, None]:
  filetypes_lower = {ft.lower() for ft in filetypes}
  all_files = get_all_files_in_all_subfolders(directory)
  resulting_files = (
    (str(file.relative_to(directory).parent / file.stem), file.relative_to(directory))
      for file in all_files if file.suffix.lower() in filetypes_lower
  )
  return resulting_files


def get_all_files_in_all_subfolders(directory: Path) -> Generator[Path, None, None]:
  for root, _, files in os.walk(directory):
    for name in files:
      file_path = Path(root) / name
      yield file_path


def get_subfolders(parent_dir: Path) -> List[Path]:
  names = get_subfolder_names(parent_dir)
  res = [parent_dir / x for x in names]
  return res


def get_subfolder_names(parent_dir: Path) -> List[str]:
  assert parent_dir.is_dir()
  _, subfolder_names, _ = next(os.walk(parent_dir))
  subfolder_names.sort()
  return subfolder_names


def read_lines(path: Path, encoding: str = 'utf-8') -> List[str]:
  assert isinstance(path, Path)
  assert path.is_file()
  with path.open(mode="r", encoding=encoding) as f:
    lines = f.readlines()
  res = [x.strip("\n") for x in lines]
  return res


def get_basename(filepath: Path) -> str:
  '''test.wav -> test'''
  return filepath.stem
  # basename, _ = os.path.splitext(os.path.basename(filepath))
  # return basename


def get_filepaths(parent_dir: Path) -> List[Path]:
  names = get_filenames(parent_dir)
  res = [parent_dir / x for x in names]
  return res


def get_filenames(parent_dir: Path) -> List[str]:
  assert parent_dir.is_dir()
  _, _, filenames = next(os.walk(parent_dir))
  return filenames


def get_wav_duration_s(wav_file: Path) -> float:
  with open(wav_file, mode="rb") as f:
    with cast(wave.Wave_read, wave.open(f, "rb")) as wav:
      duration_s = wav.getnframes() / wav.getframerate()
  return duration_s


def create_grid(wav_file: Path, text: str, tier_name: str, n_digits: int) -> TextGrid:
  assert wav_file.is_file()
  assert len(text) > 0
  duration_s = get_wav_duration_s(wav_file)
  duration_s = round(duration_s, n_digits)
  result = TextGrid(None, 0, duration_s)
  tier = IntervalTier(tier_name, 0, duration_s)
  symbols = list(text)
  tier.intervals.extend(get_intervals(symbols, duration_s, n_digits))
  result.append(tier)
  return result


def get_intervals(symbols: List[str], total_duration_s: float, n_digits: int) -> Generator[Interval, None, None]:
  symbols_count = len(symbols)
  for added_symbols_count, symbol in enumerate(symbols):
    min_time = added_symbols_count / symbols_count * total_duration_s
    max_time = (added_symbols_count + 1) / symbols_count * total_duration_s
    symbol_interval = Interval(round(min_time, n_digits), round(max_time, n_digits), symbol)
    yield symbol_interval
