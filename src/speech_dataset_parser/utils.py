import os
import tarfile
from pathlib import Path
from typing import List

import pandas as pd
import wget


def load_df(path: str, sep: str) -> pd.DataFrame:
  data = pd.read_csv(path, header=None, sep=sep)
  return data

def get_basename(filepath: str) -> str:
  '''test.wav -> test'''
  basename, _ = os.path.splitext(os.path.basename(filepath))
  return basename


def download_tar(download_url, dir_path, tarmode: str = "r:gz") -> None:
  print("Starting download of {}...".format(download_url))
  os.makedirs(dir_path, exist_ok=True)
  dest = wget.download(download_url, dir_path)
  downloaded_file = os.path.join(dir_path, dest)
  print("\nFinished download to {}".format(downloaded_file))
  print("Unpacking...")
  tar = tarfile.open(downloaded_file, tarmode)
  tar.extractall(dir_path)
  tar.close()
  os.remove(downloaded_file)
  print("Done.")


def get_filepaths(parent_dir: str) -> List[str]:
  names = get_filenames(parent_dir)
  res = [os.path.join(parent_dir, x) for x in names]
  return res


def get_subfolders(parent_dir: str) -> List[str]:
  """return full paths"""
  names = get_subfolder_names(parent_dir)
  res = [os.path.join(parent_dir, x) for x in names]
  return res


def read_lines(path: str) -> List[str]:
  assert os.path.isfile(path)
  with open(path, "r", encoding='utf-8') as f:
    lines = f.readlines()
  res = [x.strip("\n") for x in lines]
  return res


def create_parent_folder(file: str) -> str:
  path = Path(file)
  os.makedirs(path.parent, exist_ok=True)
  return path.parent


def get_filenames(parent_dir: str) -> List[str]:
  assert os.path.isdir(parent_dir)
  _, _, filenames = next(os.walk(parent_dir))
  filenames.sort()
  return filenames


def get_subfolder_names(parent_dir: str) -> List[str]:
  assert os.path.isdir(parent_dir)
  _, subfolder_names, _ = next(os.walk(parent_dir))
  subfolder_names.sort()
  return subfolder_names


def read_text(path: str) -> str:
  res = '\n'.join(read_lines(path))
  return res
