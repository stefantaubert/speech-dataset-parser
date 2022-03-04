import os
import tarfile
from logging import getLogger
from pathlib import Path

import wget


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
