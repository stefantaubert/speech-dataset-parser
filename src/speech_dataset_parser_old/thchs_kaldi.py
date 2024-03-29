import glob
import os
import shutil
import tempfile
from logging import getLogger
from pathlib import Path

from general_utils import get_basename, read_lines
from tqdm import tqdm

from speech_dataset_parser_old.data import PreData, PreDataList
from speech_dataset_parser_old.gender import Gender
from speech_dataset_parser_old.language import Language
from speech_dataset_parser_old.text_format import TextFormat
from speech_dataset_parser_old.utils import download_tar

# Warning: Script is not good as thchs normal.


def download(dir_path: Path) -> None:
  download_url_kaldi = "http://www.openslr.org/resources/18/data_thchs30.tgz"
  tmp_dir = tempfile.mkdtemp()
  download_tar(download_url_kaldi, tmp_dir)
  subfolder_name = "data_thchs30"
  content_dir = tmp_dir / subfolder_name
  parent = dir_path.parent.mkdir(parents=True, exist_ok=True)
  dest = parent / subfolder_name
  shutil.move(content_dir, dest)
  os.rename(dest, dir_path)


def parse(dir_path: Path) -> PreDataList:
  logger = getLogger(__name__)
  if not dir_path.exists():
    ex = ValueError(f"Directory not found: {dir_path}")
    logger.error("", exc_info=ex)
    raise ex

  sent_paths = dir_path / "data" / "*.trn"
  wav_paths = dir_path / "data" / "*.wav"
  existing_sent_files = set(glob.glob(str(sent_paths)))
  wav_files = [Path(file) for file in glob.glob(str(wav_paths))]
  generated_sent_files = [Path(f"{wav_file}.trn") for wav_file in wav_files]

  wavs_sents = sorted(tuple(zip(wav_files, generated_sent_files)))
  skipped = [wav_file for wav_file, sent_file_gen in wavs_sents if str(
    sent_file_gen) not in existing_sent_files]
  wavs_sents_filtered = [(wav_file, sent_file_gen) for wav_file,
                         sent_file_gen in wavs_sents if str(sent_file_gen) in existing_sent_files]

  logger.info(f"Skipped: {len(skipped)} of {len(generated_sent_files)}")

  res = PreDataList()
  lang = Language.CHN
  text_format = TextFormat.GRAPHEMES
  logger.info("Parsing files...")
  wav_file: Path
  sent_file: Path
  for wav_file, sent_file in tqdm(wavs_sents_filtered):
    content = read_lines(sent_file)
    chn = content[0].strip()
    # remove "=" from chinese transcription because it is not correct
    # occurs only in sentences with nr. 374, e.g. B22_374
    chn = chn.replace("= ", '')
    symbols = tuple(chn)

    basename = get_basename(wav_file)
    speaker, nr = basename.split("_")
    nr = int(nr)
    #res.append((nr, speaker, basename, wav, chn, sent_file))

    # TODO Gender
    tmp = PreData(
      identifier=0,
      basename=basename,
      speaker_name=speaker,
      speaker_accent=speaker,
      symbols=symbols,
      symbols_format=text_format,
      relative_audio_path=wav_file.relative_to(dir_path),
      speaker_gender=Gender.FEMALE,
      symbols_language=lang,
    )

    res.append(tmp)

  res.sort(key=sort_ds)
  res.set_identifiers()
  logger.info("Done.")

  return res


def sort_ds(entry: PreData) -> str:
  return entry.speaker_name
