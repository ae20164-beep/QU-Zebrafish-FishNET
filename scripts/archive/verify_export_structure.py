import csv
import os

export_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels\FishNet Exported Data'

for fname, exp_cols in [('tanks.tab', 23), ('crosses.tab', 24), ('nursery.tab', 18)]:
    fpath = os.path.join(export_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        rows = list(csv.reader(f, delimiter='\t'))
    bad_rows = [i for i, r in enumerate(rows) if len(r) != exp_cols]
    print(f"{fname:12s}: Total {len(rows)} rows | Expected cols = {exp_cols} | Bad rows = {len(bad_rows)}")
    if bad_rows:
        print(f"   Bad row indices: {bad_rows}")
    else:
        last_id = rows[-1][20] if fname == "tanks.tab" else (rows[-1][7] if fname == "crosses.tab" else rows[-1][0])
        print(f"   First record: {rows[0][20] if fname=='tanks.tab' else rows[0][7] if fname=='crosses.tab' else rows[0][0]} | Last record: {last_id}")
