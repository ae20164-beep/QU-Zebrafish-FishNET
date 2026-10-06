import csv
import os

export_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels\FishNet Exported Data'

# Read FishNET.tab
with open(os.path.join(export_dir, 'FishNET.tab'), 'r', encoding='utf-8-sig', errors='ignore') as f:
    fn_rows = list(csv.reader(f, delimiter='\t'))
fn_headers = fn_rows[0]
fn_data = [dict(zip(fn_headers, r)) for r in fn_rows[1:] if r and r[0].strip()]

# Read existing tanks.tab
with open(os.path.join(export_dir, 'tanks.tab'), 'r', encoding='utf-8-sig', errors='ignore') as f:
    existing_tanks = list(csv.reader(f, delimiter='\t'))
existing_tank_ids = {r[20].strip().upper(): r for r in existing_tanks if len(r) > 20 and r[20].strip()}

# Read existing crosses.tab
with open(os.path.join(export_dir, 'crosses.tab'), 'r', encoding='utf-8-sig', errors='ignore') as f:
    existing_crosses = list(csv.reader(f, delimiter='\t'))
existing_cross_ids = {r[7].strip().upper(): r for r in existing_crosses if len(r) > 7 and r[7].strip()}

# Read existing nursery.tab
with open(os.path.join(export_dir, 'nursery.tab'), 'r', encoding='utf-8-sig', errors='ignore') as f:
    existing_nursery = list(csv.reader(f, delimiter='\t'))
existing_nursery_ids = {r[0].strip().upper(): r for r in existing_nursery if len(r) > 0 and r[0].strip()}
existing_nursery_cuid = {r[4].strip().upper(): r for r in existing_nursery if len(r) > 4 and r[4].strip()}

print(f"FishNET.tab total tanks: {len(fn_data)}")
print(f"Existing tanks.tab tanks: {len(existing_tank_ids)}")
print(f"Existing crosses.tab crosses: {len(existing_cross_ids)}")
print(f"Existing nursery.tab entries: {len(existing_nursery_ids)}")

# Check tanks in FishNET.tab missing from tanks.tab
missing_tanks = [d for d in fn_data if d['TUID'].upper() not in existing_tank_ids]
print(f"\nTanks in FishNET.tab missing from tanks.tab: {len(missing_tanks)}")
for t in missing_tanks:
    print(f"  {t['TUID']}: Line={t['NOTES']} | Cross={t['Derivative cross']} | Pat={t['PATERNAL']} | Mat={t['MATERNAL']} | DOB={t['DOB']} | Stat={t['STATUS']}")

# Check all crosses referenced in FishNET.tab
all_fn_crosses = sorted(list(set(d['Derivative cross'].strip().upper() for d in fn_data if d['Derivative cross'].strip())))
print(f"\nTotal Cross IDs referenced in FishNET.tab: {len(all_fn_crosses)}")
print(f"Cross IDs in FishNET.tab: {', '.join(all_fn_crosses)}")

missing_crosses = [c for c in all_fn_crosses if c not in existing_cross_ids]
print(f"\nCross IDs in FishNET.tab missing from crosses.tab: {len(missing_crosses)} -> {missing_crosses}")
