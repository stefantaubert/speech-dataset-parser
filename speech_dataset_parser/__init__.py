from speech_dataset_parser.arctic import parse as parse_arctic, download as download_arctic
from speech_dataset_parser.custom import parse as parse_custom
from speech_dataset_parser.libritts import parse as parse_libritts, download as download_libritts
from speech_dataset_parser.ljs import parse as parse_ljs, download as download_ljs
from speech_dataset_parser.thchs import parse as parse_thchs, download as download_thchs
from speech_dataset_parser.thchs_kaldi import parse as parse_thchs_kaldi, download as download_thchs_kaldi

from speech_dataset_parser.gender import Gender
from speech_dataset_parser.language import Language
from speech_dataset_parser.data import PreData, PreDataList