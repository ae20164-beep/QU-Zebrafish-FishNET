import csv
import re
import os
from collections import defaultdict

labels_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels'
done_dir = os.path.join(labels_dir, 'DONE')
breeding_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\breeding'

# 1. Load FishNET inventory
fishnet = {}
with open(os.path.join(labels_dir, 'FishNET.tab'), 'r', encoding='utf-8-sig', errors='ignore') as f:
    for row in list(csv.reader(f, delimiter='\t'))[1:]:
        if not row or not row[0].strip():
            continue
        tuid = row[0].strip().upper()
        notes = row[1].strip() if len(row) > 1 else ''
        f_cnt = int(row[2].strip()) if len(row) > 2 and row[2].strip().isdigit() else 0
        m_cnt = int(row[3].strip()) if len(row) > 3 and row[3].strip().isdigit() else 0
        tot = int(row[4].strip()) if len(row) > 4 and row[4].strip().isdigit() else (f_cnt + m_cnt)
        dob = row[6].strip() if len(row) > 6 else ''
        status = row[13].strip() if len(row) > 13 else 'Active'
        
        num_id = int(re.sub(r'\D', '', tuid)) if re.search(r'\d', tuid) else 0
        std_tuid = f'T{num_id:04d}'
        sex_type = 'Female-Only' if f_cnt > 0 and m_cnt == 0 else ('Male-Only' if m_cnt > 0 and f_cnt == 0 else ('Mixed' if f_cnt > 0 and m_cnt > 0 else 'Unsexed'))
        
        line = 'Other'
        nu = notes.upper()
        if 'AB' in nu or 'WILD' in nu:
            line = 'AB'
        elif 'CASP' in nu or 'CAS' in nu:
            line = 'Casper'
        elif 'FLI' in nu:
            line = 'Fli'
        elif 'GATA' in nu:
            line = 'Gata'
            
        fishnet[std_tuid] = {
            'tuid': std_tuid,
            'raw': tuid,
            'notes': notes,
            'line': line,
            'f': f_cnt,
            'm': m_cnt,
            'tot': tot,
            'dob': dob,
            'status': 'Active' if 'ACTIVE' in status.upper() or 'ADULT' in status.upper() else 'Euthanized',
            'sex_type': sex_type
        }

print(f"Loaded {len(fishnet)} tanks from FishNET.")

# Enhanced Tank Extraction Function
def extract_all_tanks(text):
    # Matches T123, T-123, T.123, AB106, Gata101, Tank 95, T 95, T93(M), T95(F)
    res = []
    # Pattern 1: T, T-, T., Tank followed by digits
    for m in re.finditer(r'(?:Tank|T|T\.|T\-)\s*0*([0-9]{1,4})\b', text, re.IGNORECASE):
        res.append(int(m.group(1)))
    # Pattern 2: Line name followed directly by digits, e.g. AB106, Gata101, Fli19, Cas114
    for m in re.finditer(r'(?:AB|Fli|Gata|Casper|Casp|Cas)\s*0*([0-9]{1,4})\b', text, re.IGNORECASE):
        val = int(m.group(1))
        if val not in res and val < 300: # avoid year numbers like 2025
            res.append(val)
    return [f'T{v:04d}' for v in sorted(res)]

# Check all 2026 data
p26_path = os.path.join(done_dir, '2026_breeding_complete.csv')
p26_rows = []
with open(p26_path, 'r', encoding='utf-8-sig') as f:
    p26_rows = list(csv.DictReader(f))

print(f"\nAuditing 2026 dataset ({len(p26_rows)} rows)...")

corrections = []
for idx, r in enumerate(p26_rows, 1):
    fl = r['Fishline']
    in_tank = r['In_Tank'].strip().lower() in ['yes', 'true']
    tanks = extract_all_tanks(fl)
    
    # Sex consistency check
    tank_info = []
    for t in tanks:
        if t in fishnet:
            tank_info.append(fishnet[t])
        else:
            tank_info.append({'tuid': t, 'sex_type': 'Not_In_FishNET', 'f': 0, 'm': 0, 'status': 'Unknown', 'line': 'Unknown', 'notes': 'Unknown'})
            
    # Check explicit sex annotations in text e.g. T93(M), T95(F)
    explicit_m = re.findall(r'T\s*0*([0-9]+)\s*\(\s*M\s*\)', fl, re.IGNORECASE)
    explicit_f = re.findall(r'T\s*0*([0-9]+)\s*\(\s*F\s*\)', fl, re.IGNORECASE)
    
    # Identify issues
    issue_type = []
    
    # 1. Single tank marked as in_tank but tank is Female-Only or Male-Only in FishNET
    if len(tanks) == 1:
        t_obj = tank_info[0]
        if t_obj['sex_type'] == 'Female-Only':
            issue_type.append(f"Female-Only tank {t_obj['tuid']} (F:{t_obj['f']}/M:0) used alone")
        elif t_obj['sex_type'] == 'Male-Only':
            issue_type.append(f"Male-Only tank {t_obj['tuid']} (F:0/M:{t_obj['m']}) used alone")
            
    # 2. Both tanks in pair are same sex in FishNET
    elif len(tanks) >= 2:
        sexes = [t['sex_type'] for t in tank_info]
        if all(s == 'Female-Only' for s in sexes):
            issue_type.append(f"Same-sex pairing: All tanks Female-Only ({', '.join(tanks)})")
        elif all(s == 'Male-Only' for s in sexes):
            issue_type.append(f"Same-sex pairing: All tanks Male-Only ({', '.join(tanks)})")
            
    # 3. Explicit annotation in log contradicts FishNET
    for em in explicit_m:
        stuid = f"T{int(em):04d}"
        if stuid in fishnet and fishnet[stuid]['sex_type'] == 'Female-Only':
            issue_type.append(f"Log wrote {stuid}(M) but FishNET has it as Female-Only (F:{fishnet[stuid]['f']}/M:0)")
    for ef in explicit_f:
        stuid = f"T{int(ef):04d}"
        if stuid in fishnet and fishnet[stuid]['sex_type'] == 'Male-Only':
            issue_type.append(f"Log wrote {stuid}(F) but FishNET has it as Male-Only (F:0/M:{fishnet[stuid]['m']})")
            
    if issue_type:
        corrections.append({
            'row': idx,
            'date': r['Date'],
            'text': fl,
            'tanks': tanks,
            'eggs': r['Total_Eggs_0H'],
            'sr_24': r['Survival_Rate_24H'],
            'issues': issue_type
        })

print(f"\nIdentified {len(corrections)} sex/population consistency issues in 2026 logs:")
for c in corrections:
    print(f"\nRow {c['row']:3d} | Date: {c['date']} | Text: '{c['text']}' | Eggs: {c['eggs']} | 24h SR: {c['sr_24']}%")
    for iss in c['issues']:
        print(f"   -> ISSUE: {iss}")
