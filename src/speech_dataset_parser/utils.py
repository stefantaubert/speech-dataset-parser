import os
import tarfile
from logging import getLogger
from pathlib import Path
from typing import List

import pandas as pd
import wget


def load_df(path: Path, sep: str) -> pd.DataFrame:
  data = pd.read_csv(path, header=None, sep=sep)
  return data


def get_basename(filepath: Path) -> str:
  '''test.wav -> test'''
  basename, _ = os.path.splitext(os.path.basename(filepath))
  return basename


def download_tar(download_url, dir_path: Path, tarmode: str = "r:gz") -> None:
  logger = getLogger(__name__)
  logger.info(f"Starting download of {download_url}...")
  dir_path.mkdir(parents=True, exist_ok=True)
  dest = wget.download(download_url, dir_path)
  downloaded_file = dir_path / dest
  logger.info(f"\nFinished download to {downloaded_file}")
  logger.info("Unpacking...")
  with tarfile.open(downloaded_file, tarmode) as tar:
    tar.extractall(dir_path)
  os.remove(downloaded_file)
  logger.info("Done.")


def get_filepaths(parent_dir: Path) -> List[Path]:
  names = get_filenames(parent_dir)
  res = [parent_dir / x for x in names]
  return res


def get_subfolders(parent_dir: Path) -> List[Path]:
  """return full paths"""
  names = get_subfolder_names(parent_dir)
  res = [parent_dir / x for x in names]
  return res


def read_lines(path: Path) -> List[str]:
  assert path.is_file()
  with open(path, "r", encoding='utf-8') as f:
    lines = f.readlines()
  res = [x.strip("\n") for x in lines]
  return res


def create_parent_folder(file: Path) -> Path:
  file.parent.mkdir(exist_ok=True, parents=True)
  return file.parent


def get_filenames(parent_dir: Path) -> List[str]:
  assert parent_dir.is_dir()
  _, _, filenames = next(os.walk(parent_dir))
  filenames.sort()
  return filenames


def get_subfolder_names(parent_dir: Path) -> List[str]:
  assert parent_dir.is_dir()
  _, subfolder_names, _ = next(os.walk(parent_dir))
  subfolder_names.sort()
  return subfolder_names


def read_text(path: Path) -> str:
  res = '\n'.join(read_lines(path))
  return res
