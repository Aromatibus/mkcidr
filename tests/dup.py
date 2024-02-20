# https://note.nkmk.me/python-pandas-duplicated-drop-duplicates/#subset

from pathlib import Path

import pandas as pd

Path_CSV = Path("./testdata").resolve()

data_frame = pd.read_csv(Path_CSV)

print(data_frame)
