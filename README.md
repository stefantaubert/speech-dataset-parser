# speech-dataset-parser

[![PyPI](https://img.shields.io/pypi/v/speech-dataset-parser.svg)](https://pypi.python.org/pypi/speech-dataset-parser)
[![PyPI](https://img.shields.io/pypi/pyversions/speech-dataset-parser.svg)](https://pypi.python.org/pypi/speech-dataset-parser)
[![MIT](https://img.shields.io/github/license/stefantaubert/speech-dataset-parser.svg)](https://github.com/stefantaubert/speech-dataset-parser/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/wheel/speech-dataset-parser.svg)](https://pypi.python.org/pypi/speech-dataset-parser)
[![PyPI](https://img.shields.io/pypi/implementation/speech-dataset-parser.svg)](https://pypi.python.org/pypi/speech-dataset-parser)
[![PyPI](https://img.shields.io/github/commits-since/stefantaubert/speech-dataset-parser/latest/master.svg)](https://pypi.python.org/pypi/speech-dataset-parser)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7529425.svg)](https://doi.org/10.5281/zenodo.7529425)

Library to parse speech datasets stored in a generic format based on TextGrids. A tool (CLI) for converting common datasets like LJ Speech into a generic format is included.
Speech datasets consists of pairs of .TextGrid and .wav files. The TextGrids need to contain a tier which has each symbol separated in an interval, e.g., `T|h|i|s| |i|s| |a| |t|e|x|t|.`

## Generic Format

The format is as follows: `{Dataset name}/{Speaker name};{Speaker gender};{Speaker language}[;{Speaker accent}]/[Subfolder(s)]/{Recordings as .wav- and .TextGrid-pairs}`

Example: `LJ Speech/Linda Johnson;2;eng;North American/wavs/...`

Speaker names can be any string (excluding `;` symbols).
Genders are defined via their [ISO/IEC 5218 Code](https://en.wikipedia.org/wiki/ISO/IEC_5218).
Languages are defined via their [ISO 639-2 Code](https://www.loc.gov/standards/iso639-2/php/code_list.php) (bibliographic).
Accents are optional and can be any string (excluding `;` symbols).

## Installation

```sh
pip install speech-dataset-parser --user
```

## Library Usage

```py
from speech_dataset_parser import parse_dataset

entries = list(parse_dataset({folder}, {grid-tier-name}))
```

The resulting `entries` list contains dataclass-instances with these properties:

- `symbols: Tuple[str, ...]`: contains the mark of each interval
- `intervals: Tuple[float, ...]`: contains the max-time of each interval
- `symbols_language: str`: contains the language
- `speaker_name: str`: contains the name of the speaker
- `speaker_accent: str`: contains the accent of the speaker
- `speaker_gender: int`: contains the gender of the speaker
- `audio_file_abs: Path`: contains the absolute path to the speech audio
- `min_time: float`: the min-time of the grid
- `max_time: float`: the max-time of the grid (equal to `intervals[-1]`)

## CLI Usage

```txt
usage: dataset-converter-cli [-h] [-v] {convert-ljs,convert-l2arctic,convert-thchs,convert-thchs-cslt,restore-structure} ...

This program converts common speech datasets into a generic representation.

positional arguments:
  {convert-ljs,convert-l2arctic,convert-thchs,convert-thchs-cslt,restore-structure}
                                        description
    convert-ljs                         convert LJ Speech dataset to a generic dataset
    convert-l2arctic                    convert L2-ARCTIC dataset to a generic dataset
    convert-thchs                       convert THCHS-30 (OpenSLR Version) dataset to a generic dataset
    convert-thchs-cslt                  convert THCHS-30 (CSLT Version) dataset to a generic dataset
    restore-structure                   restore original dataset structure of generic datasets

optional arguments:
  -h, --help                            show this help message and exit
  -v, --version                         show program's version number and exit
```

## CLI Example

```sh
# Convert LJ Speech dataset with symbolic links to the audio files
dataset-converter-cli convert-ljs \
  "/data/datasets/LJSpeech-1.1" \
  "/tmp/ljs" \
  --tier "Symbols" \
  --symlink
```

## Dependencies

- `tqdm`
- `TextGrid>=1.5`
- `ordered_set>=4.1.0`
- `importlib_resources; python_version < '3.8'`

## Roadmap

- Supporting conversion of more datasets
- Adding more tests

## Contributing

If you notice an error, please don't hesitate to open an issue.

### Development setup

```sh
# update
sudo apt update
# install Python 3.7, 3.8, 3.9, 3.10 & 3.11 for ensuring that tests can be run
sudo apt install python3-pip \
  python3.7 python3.7-dev python3.7-distutils python3.7-venv \
  python3.8 python3.8-dev python3.8-distutils python3.8-venv \
  python3.9 python3.9-dev python3.9-distutils python3.9-venv \
  python3.10 python3.10-dev python3.10-distutils python3.10-venv \
  python3.11 python3.11-dev python3.11-distutils python3.11-venv
# install pipenv for creation of virtual environments
python3.8 -m pip install pipenv --user

# check out repo
git clone https://github.com/stefantaubert/speech-dataset-parser.git
cd speech-dataset-parser
# create virtual environment
python3.8 -m pipenv install --dev
```

## Running the tests

```sh
# first install the tool like in "Development setup"
# then, navigate into the directory of the repo (if not already done)
cd speech-dataset-parser
# activate environment
python3.8 -m pipenv shell
# run tests
tox
```

Final lines of test result output:

```log
py37: commands succeeded
py38: commands succeeded
py39: commands succeeded
py310: commands succeeded
py311: commands succeeded
congratulations :)
```

## License

MIT License

## Acknowledgments

Funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) – Project-ID 416228727 – CRC 1410

## Citation

If you want to cite this repo, you can use this BibTeX-entry generated by GitHub (see *About => Cite this repository*).

## Changelog

- v0.0.5 (unreleased)
  - Added:
    - Added option to parse LJ Speech `--use-un-normalized-text`
- v0.0.4 (2023-01-12)
  - Added:
    - Added support to parse [OpenSLR THCHS-30 version](https://www.openslr.org/18/)
    - Added returning of an exit code
  - Changed:
    - Changed default command to be parsing the OpenSLR version for THCHS-30 by renaming the previous command to `convert-thchs-cslt`
- v0.0.3 (2023-01-02)
  - added option to restore original file structure
  - added option to THCHS-30 to opt in for adding of punctuation
  - change file naming format to numbers with preceding zeros
- v0.0.2 (2022-09-08)
  - added support for L2Arctic
  - added support for THCHS-30
- v0.0.1 (2022-06-03)
  - Initial release
