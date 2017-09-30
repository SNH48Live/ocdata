import logging
import pathlib


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIGS_DIR = ROOT / 'config'
DATA_DIR = ROOT / 'data'
NUMERIC_DIR = DATA_DIR / 'numeric'
PLOTS_DIR = DATA_DIR / 'plots'

for directory in (CONFIGS_DIR, DATA_DIR, NUMERIC_DIR, PLOTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
del directory

_default_fmt = '[%(asctime)s] %(levelname)s: %(message)s'
_default_datefmt = '%Y-%m-%d %H:%M:%S'
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(
    fmt=_default_fmt,
    datefmt=_default_datefmt,
))
logger = logging.getLogger('ChinaSNH48')
logger.addHandler(_handler)
logger.setLevel(logging.DEBUG)
