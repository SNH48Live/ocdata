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
