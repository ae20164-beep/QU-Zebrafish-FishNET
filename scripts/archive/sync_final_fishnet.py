import csv
import os
import re

export_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels\FishNet Exported Data'
labels_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels'
fishnet_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data'

# 1. Read Final Crosses.tab to map Paternal/Maternal tanks for each Cross ID
with open(os.path.join(export_dir, 'Crosses.tab'), 'r', encoding='utf-8-sig', errors='ignore') as f:
    crosses_rows = list(csv.reader(f, delimiter='\t'))

# Crosses schema: col 7: CUID, col 11: Maternal Tank, col 15: Paternal Tank
cross_parents = {}
for r in crosses_rows:
    if len(r) > 7 and r[7].strip():
        cuid = r[7].strip().upper()
        mat = r[11].strip().upper() if len(r) > 11 else ''
        pat = r[15].strip().upper() if len(r) > 15 else ''
        cross_parents[cuid] = {'mat': mat, 'pat': pat}

print(f"Loaded {len(cross_parents)} cross mappings from final Crosses.tab")

# 2. Read Final Tanks.tab
with open(os.path.join(export_dir, 'Tanks.tab'), 'r', encoding='utf-8-sig', errors='ignore') as f:
    tanks_rows = list(csv.reader(f, delimiter='\t'))

print(f"Loaded {len(tanks_rows)} tanks from final Tanks.tab")

# 3. Construct updated FishNET.tab rows
# Headers: ['TUID', 'NOTES', 'FEMALE', 'MALE', 'TOTAL', 'TANK ', 'DOB', 'DOD', 'TURNOVER', 'Derivative cross', 'PATERNAL X MATERNAL', 'PATERNAL', 'MATERNAL', 'STATUS']
fn_headers = ['TUID', 'NOTES', 'FEMALE', 'MALE', 'TOTAL', 'TANK ', 'DOB', 'DOD', 'TURNOVER', 'Derivative cross', 'PATERNAL X MATERNAL', 'PATERNAL', 'MATERNAL', 'STATUS']

fn_records = []
for r in tanks_rows:
    if len(r) < 21 or not r[20].strip():
        continue
    tuid = r[20].strip().upper()
    notes = r[8].strip() if len(r) > 8 else ''
    female = r[4].strip() if len(r) > 4 else ''
    male = r[7].strip() if len(r) > 7 else ''
    total = r[9].strip() if len(r) > 9 else ''
    tank_size = r[18].strip() if len(r) > 18 else ''
    dob = r[0].strip() if len(r) > 0 else ''
    dod = r[1].strip() if len(r) > 1 else ''
    turnover = r[21].strip() if len(r) > 21 else ''
    deriv_cross = r[2].strip().upper() if len(r) > 2 else ''
    status = r[16].strip() if len(r) > 16 else 'Adult/Active'
    
    # Resolve Paternal / Maternal from Crosses
    pat = ''
    mat = ''
    pat_x_mat = ''
    if deriv_cross and deriv_cross in cross_parents:
        pat = cross_parents[deriv_cross]['pat']
        mat = cross_parents[deriv_cross]['mat']
        if pat and mat:
            pat_x_mat = f"{pat}\x0b{mat}"
        elif pat:
            pat_x_mat = pat
        elif mat:
            pat_x_mat = mat

    fn_records.append([
        tuid, notes, female, male, total, tank_size, dob, dod, turnover, deriv_cross, pat_x_mat, pat, mat, status
    ])

# Sort tanks naturally by TUID number
def get_tuid_num(row):
    tuid = row[0]
    m = re.search(r'\d+', tuid)
    return int(m.group(0)) if m else 9999

fn_records.sort(key=get_tuid_num)

# Write updated FishNET.tab in Labels and FishNet Exported Data
def write_fn_tab(target_path):
    with open(target_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(fn_headers)
        for row in fn_records:
            writer.writerow(row)
    print(f"Wrote updated {target_path} ({len(fn_records)} tanks)")

write_fn_tab(os.path.join(labels_dir, 'FishNET.tab'))
write_fn_tab(os.path.join(export_dir, 'FishNET.tab'))
write_fn_tab(os.path.join(fishnet_dir, 'FishNET.tab'))
