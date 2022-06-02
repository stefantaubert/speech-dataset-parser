import os
from collections import OrderedDict
from pathlib import Path
from typing import Generator, List
from typing import OrderedDict as ODType
from typing import Set, Tuple


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
