# speech-dataset-parser

![Python](https://img.shields.io/github/license/stefantaubert/speech-dataset-parser)
![Python](https://img.shields.io/badge/python-3.9.0-green.svg)

Parser for several speech datasets.

## Setup

```sh
git clone https://github.com/stefantaubert/speech-dataset-parser.git
cd speech-dataset-parser
pipenv install --dev
```

## Add to another project

In the destination project run:

```sh
pipenv install -e git+https://github.com/stefantaubert/speech-dataset-parser.git@master#egg=speech_dataset_parser
```

## Downloads

### M-AILABS

Download from [here](https://www.caito.de/2019/01/the-m-ailabs-speech-dataset/).

```sh
mkdir m-ailabs
cd m-ailabs
wget http://www.caito.de/data/Training/stt_tts/de_DE.tgz
wget http://www.caito.de/data/Training/stt_tts/en_UK.tgz
wget http://www.caito.de/data/Training/stt_tts/en_US.tgz
wget http://www.caito.de/data/Training/stt_tts/es_ES.tgz
wget http://www.caito.de/data/Training/stt_tts/it_IT.tgz
wget http://www.caito.de/data/Training/stt_tts/uk_UK.tgz
wget http://www.caito.de/data/Training/stt_tts/ru_RU.tgz
wget http://www.caito.de/data/Training/stt_tts/fr_FR.tgz
wget http://www.caito.de/data/Training/stt_tts/pl_PL.tgz
tar xvfz *.tgz
rm *.tgz
```

/{lang}/{speaker_name},{gender},{accent}/{format}/grids and audios

eg 
/ENG/Linda Johnson,F,US/PHONEMES_ARPA/book1/chapter1/001.TextGrid
/ENG/Linda Johnson,F,US/PHONEMES_ARPA/book1/chapter1/001.wav
