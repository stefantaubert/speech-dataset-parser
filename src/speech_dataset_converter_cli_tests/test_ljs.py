import tempfile
from logging import getLogger
from pathlib import Path
from shutil import rmtree

from speech_dataset_converter_cli.convert_ljs import convert_to_generic

LOCAL_PATH = Path('/data/datasets/LJSpeech-1.1')


def test_all_utterances_are_included():
  output_path = Path(tempfile.mkdtemp("-sdc-tests"))
  success = convert_to_generic(LOCAL_PATH, True, 16, "test", output_path, "UTF-8", getLogger())
  rmtree(output_path)
  assert success


test_all_utterances_are_included()
