# https://note.nkmk.me/python-pandas-duplicated-drop-duplicates/#subset

import os
from pathlib import Path

import pandas as pd

os.chdir(Path.cwd())
Path_CSV = Path("./testdata").resolve()

data_frame = pd.read_csv(Path_CSV)

print(data_frame)

print(data_frame.duplicated())
