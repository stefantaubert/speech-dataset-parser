import tempfile
from logging import getLogger
from pathlib import Path
from shutil import rmtree

from speech_dataset_converter_cli.convert_ljs import convert_to_generic
from speech_dataset_converter_cli.logging_configuration import configure_root_logger

LOCAL_PATH = Path('/data/datasets/LJSpeech-1.1')
configure_root_logger()


def xtest_all_utterances_are_included():
  output_path = Path(tempfile.mkdtemp("-tests", "sdc"))
  success = convert_to_generic(LOCAL_PATH, True, 16, "test", output_path,
                               "UTF-8", getLogger(), getLogger())
  rmtree(output_path)
  assert success
