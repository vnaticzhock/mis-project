import json
import logging
import pickle
import re
from argparse import ArgumentParser, Namespace
from collections import Counter
from pathlib import Path
from random import random, seed
from typing import List, Dict

import torch
from tqdm.auto import tqdm

from utils import Vocab

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

def build_vocab(
    words: Counter, vocab_size: int, output_dir: Path, glove_path: Path
) -> None:
    common_words = {w for w, _ in words.most_common(vocab_size)}
    