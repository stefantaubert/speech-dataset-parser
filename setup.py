from setuptools import find_packages, setup

setup(
    name="speech_dataset_parser",
    version="1.0.1",
    url="https://github.com/stefantaubert/speech-dataset-parser.git",
    author="Stefan Taubert",
    author_email="contact@stefantaubert.com",
    description="Parser for several speech datasets.",
    packages=["speech_dataset_parser"],
    install_requires=[
        "numpy==1.19.4; python_version >= '3.6'",
        "pandas==1.1.4",
        "python-dateutil==2.8.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "pytz==2020.4",
        "six==1.15.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "tqdm==4.54.0",
        "wget==3.2",
    ],
)
