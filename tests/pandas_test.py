# https://note.nkmk.me/python-pandas-duplicated-drop-duplicates/#subset

from pathlib import Path

import pandas as pd

Path_CSV = Path(__file__).parent / "testdata.csv"
print(f"Path:{Path_CSV}")

data_frame = pd.read_csv(Path_CSV, delimiter=",", header=None, names=["name", "age", "state", "point"])

print("Original:")
print(data_frame)
print()

print("Duplicated:")
print(data_frame.duplicated())
print()

print("Duplicated: name")
print(data_frame.duplicated(subset="state"))
print()


print("Duplicated: state")
print(data_frame.duplicated(subset="name"))
print()

print("Duplicated: name")
print(data_frame.duplicated(keep=False, subset=["name"]))
print()

print("Duplicated Data: name")
print(data_frame[data_frame.duplicated(keep=False, subset=["name"])])
print()


print("Duplicated: name, state")
print(data_frame.duplicated(keep=False, subset=["name", "state"]))
print()

print("Duplicated Data: name, state ")
print(data_frame[data_frame.duplicated(keep=False, subset=["name", "state"])])
print()
