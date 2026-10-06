import csv
import os

export_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels\FishNet Exported Data'

def inspect(filename, rows_to_show=[0, 1, 5, 20, 50, -1]):
    fpath = os.path.join(export_dir, filename)
    with open(fpath, 'r', encoding='utf-8-sig', errors='ignore') as f:
        rows = list(csv.reader(f, delimiter='\t'))
    print(f"==================================================")
    print(f"File: {filename} (Total rows: {len(rows)})")
    print(f"==================================================")
    for idx in rows_to_show:
        if idx < len(rows) and (idx >= 0 or idx == -1):
            r = rows[idx]
            actual_idx = idx if idx >= 0 else len(rows) + idx
            print(f"\n--- Row {actual_idx} (len={len(r)}) ---")
            for c_idx, val in enumerate(r):
                print(f"  col {c_idx:2d}: '{val}'")

inspect('tanks.tab', [0, 10, 50, 100, -1])
inspect('crosses.tab', [0, 10, 25, -1])
inspect('nursery.tab', [0, 10, 25, -1])
