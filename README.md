# speech-dataset-parser

[![PyPI](https://img.shields.io/pypi/v/speech-dataset-parser.svg)](https://pypi.python.org/pypi/speech-dataset-parser)
[![PyPI](https://img.shields.io/pypi/pyversions/speech-dataset-parser.svg)](https://pypi.python.org/pypi/speech-dataset-parser)
[![MIT](https://img.shields.io/github/license/stefantaubert/speech-dataset-parser.svg)](https://github.com/stefantaubert/speech-dataset-parser/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/wheel/speech-dataset-parser.svg)](https://pypi.python.org/pypi/speech-dataset-parser)
[![PyPI](https://img.shields.io/pypi/implementation/speech-dataset-parser.svg)](https://pypi.python.org/pypi/speech-dataset-parser)
[![PyPI](https://img.shields.io/github/commits-since/stefantaubert/speech-dataset-parser/latest/master.svg)](https://pypi.python.org/pypi/speech-dataset-parser)

Library to parse speech datasets stored in a generic format based on TextGrids. A tool (CLI) for converting common datasets like LJ Speech into a generic format is included.
Speech datasets consists of pairs of .TextGrid and .wav files. The TextGrids need to contain a tier which has each symbol separated in an interval, e.g., `T|h|i|s| |i|s| |a| |t|e|x|t|.`

## Generic Format

The format is as follows: `{Dataset name}/{Speaker name};{Speaker gender};{Speaker language}[;{Speaker accent}]/[Subfolder(s)]/{Recordings as .wav- and .TextGrid-pairs}`

Example: `LJ Speech/Linda Johnson;2;eng;North American/wavs/...`

Speaker names can be any string (excluding `;` symbols).
Genders are defined via their [ISO/IEC 5218 Code](https://en.wikipedia.org/wiki/ISO/IEC_5218).
Languages are defined via their [ISO 639-2 Code](https://www.loc.gov/standards/iso639-2/php/code_list.php).
Accents are optional and can be any string (excluding `;` symbols).

## Installation

```sh
pip install speech-dataset-parser --user
```

## Library Usage

```py
from speech_dataset_parser import parse_dataset

entries = list(parse_dataset(folder..., grid-tier-name...))
```

The resulting `entries` list contains dataclass instances with these properties:

- `symbols: Tuple[str, ...]`
- `intervals: Tuple[float, ...]`
- `symbols_language: str`
- `speaker_name: str`
- `speaker_accent: str`
- `speaker_gender: int`
- `audio_file_abs: Path`
- `min_time: float`
- `max_time: float`

## CLI Usage

```sh
dataset-converter-cli [-h] [-v] {convert-ljs} ...
```

## CLI Features

- `convert-ljs`: convert LJ Speech dataset to a generic dataset

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

- tqdm
- TextGrid>=1.5
- ordered_set>=4.1.0

## Roadmap

- Supporting conversion of more datasets
- Adding tests

## License

MIT License

## Acknowledgments

Funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) – Project-ID 416228727 – CRC 1410

## Citation

If you want to cite this repo, you can use this BibTeX-entry:

```bibtex
@misc{tssdp22,
  author = {Taubert, Stefan},
  title = {speech-dataset-parser},
  year = {2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/stefantaubert/speech-dataset-parser}}
}
```
