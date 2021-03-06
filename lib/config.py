import logging
import pathlib


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIGS_DIR = ROOT / 'config'
DATA_DIR = ROOT / 'data'
INDEX = DATA_DIR / 'index.txt'
METADATA_DIR = DATA_DIR / 'metadata'
VIEWERS_DIR = DATA_DIR / 'viewers'
PLOTS_DIR = DATA_DIR / 'plots'
TRANSCRIPTS_DIR = DATA_DIR / 'transcripts'

for directory in (CONFIGS_DIR, DATA_DIR, METADATA_DIR, VIEWERS_DIR, PLOTS_DIR, TRANSCRIPTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
del directory

_default_fmt = '[%(asctime)s] %(levelname)s: %(message)s'
_default_datefmt = '%Y-%m-%dT%H:%M:%S'
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(
    fmt=_default_fmt,
    datefmt=_default_datefmt,
))
logger = logging.getLogger('ChinaSNH48')
logger.addHandler(_handler)
logger.setLevel(logging.DEBUG)
