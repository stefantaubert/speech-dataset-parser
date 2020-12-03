import glob
import os
import shutil
import tempfile
from logging import Logger, getLogger

from tqdm import tqdm

from speech_dataset_parser.data import PreData, PreDataList
from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import Language
from speech_dataset_parser.utils import (create_parent_folder, download_tar,
                                         read_lines)

# Warning: Script is not good as thchs normal.


def download(dir_path: str) -> None:
  download_url_kaldi = "http://www.openslr.org/resources/18/data_thchs30.tgz"
  tmp_dir = tempfile.mkdtemp()
  download_tar(download_url_kaldi, tmp_dir)
  subfolder_name = "data_thchs30"
  content_dir = os.path.join(tmp_dir, subfolder_name)
  parent = create_parent_folder(dir_path)
  dest = os.path.join(parent, subfolder_name)
  shutil.move(content_dir, dest)
  os.rename(dest, dir_path)


def parse(dir_path: str, logger: Logger = getLogger()) -> PreDataList:
  if not os.path.exists(dir_path):
    ex = ValueError(f"Directory not found: {dir_path}")
    logger.error("", exc_info=ex)
    raise ex

  sent_paths = os.path.join(dir_path, "data", "*.trn")
  wav_paths = os.path.join(dir_path, "data", "*.wav")
  sent_files = glob.glob(sent_paths)
  wav_files = glob.glob(wav_paths)
  sent_files_gen = ["{}.trn".format(x) for x in wav_files]

  wavs_sents = sorted(tuple(zip(wav_files, sent_files_gen)))
  skipped = [x for x in wavs_sents if x[1] not in sent_files]
  wavs_sents = [x for x in wavs_sents if x[1] in sent_files]

  logger.info(f"Skipped: {len(skipped)} of {len(sent_files_gen)}")
  # print(skipped)

  res = PreDataList()
  lang = Language.CHN
  logger.info("Parsing files...")
  for wav, sent_file in tqdm(wavs_sents):
    content = read_lines(sent_file)
    chn = content[0].strip()
    # remove "=" from chinese transcription because it is not correct
    # occurs only in sentences with nr. 374, e.g. B22_374
    chn = chn.replace("= ", '')
    basename = os.path.basename(wav)[:-4]
    speaker, nr = basename.split("_")
    nr = int(nr)
    #res.append((nr, speaker, basename, wav, chn, sent_file))

    # TODO Gender
    tmp = PreData(
      name=basename,
      speaker_name=speaker,
      speaker_accent=speaker,
      text=chn,
      wav_path=wav,
      gender=Gender.FEMALE,
      lang=lang,
    )

    res.append(tmp)
  print("Done.")

  x: PreData
  res.sort(key=lambda x: x.name)

  return res
