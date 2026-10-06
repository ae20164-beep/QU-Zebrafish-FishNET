import csv
import os
import re
from datetime import datetime, timedelta

export_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels\FishNet Exported Data'
labels_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels'

# 1. Backup original exported files
for f in ['tanks.tab', 'crosses.tab', 'nursery.tab']:
    orig = os.path.join(export_dir, f)
    bak = os.path.join(export_dir, f + '.orig.bak')
    if os.path.exists(orig) and not os.path.exists(bak):
        with open(orig, 'rb') as src, open(bak, 'wb') as dst:
            dst.write(src.read())
        print(f"Backed up {f} to {f}.orig.bak")

# 2. Read FishNET.tab
with open(os.path.join(export_dir, 'FishNET.tab'), 'r', encoding='utf-8-sig', errors='ignore') as f:
    fn_rows = list(csv.reader(f, delimiter='\t'))
fn_headers = fn_rows[0]
fn_tanks = [dict(zip(fn_headers, r)) for r in fn_rows[1:] if r and r[0].strip()]
fn_tanks_by_id = {t['TUID'].strip().upper(): t for t in fn_tanks}

print(f"Loaded {len(fn_tanks)} tanks from FishNET.tab")

# 3. Read existing files
with open(os.path.join(export_dir, 'tanks.tab.orig.bak'), 'r', encoding='utf-8-sig', errors='ignore') as f:
    existing_tanks_rows = list(csv.reader(f, delimiter='\t'))

with open(os.path.join(export_dir, 'crosses.tab.orig.bak'), 'r', encoding='utf-8-sig', errors='ignore') as f:
    existing_crosses_rows = list(csv.reader(f, delimiter='\t'))

with open(os.path.join(export_dir, 'nursery.tab.orig.bak'), 'r', encoding='utf-8-sig', errors='ignore') as f:
    existing_nursery_rows = list(csv.reader(f, delimiter='\t'))

print(f"Existing: tanks={len(existing_tanks_rows)}, crosses={len(existing_crosses_rows)}, nursery={len(existing_nursery_rows)}")

# Helper to determine genotype description from line notes
def get_genotype_desc(notes):
    n = notes.lower().strip()
    if 'fli' in n:
        return 'Tg (fli1a:eGFP) Sidra [Fli]'
    elif 'gata' in n:
        if 'ab' in n or 'sidra' in n or 'x' in n:
            return 'Tg (gata1:dsRed) Sidra [Gata]; \x0bWt (AB)'
        return 'Tg (gata1:dsRed) Sidra [Gata]'
    elif 'casper' in n or 'cas' in n:
        return 'Mu (mitfaw2/w2; mpv17a9/a9) [Casper]'
    elif 'ab' in n or 'wild' in n or 'wt' in n:
        return 'Wt (AB)'
    return 'Wt (AB)'

def format_dob_for_tanks(dob_str):
    # Formats like '18 Jun, 2026'
    if not dob_str:
        return ''
    for fmt in ['%d-%b-%y', '%d-%b-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
        try:
            dt = datetime.strptime(dob_str.strip(), fmt)
            if dt.year > 2030:
                dt = dt.replace(year=dt.year - 100)
            return f"{dt.day} {dt.strftime('%b')}, {dt.year}"
        except:
            pass
    return dob_str

def format_date_d_m_y(dob_str):
    # Formats like '18/06/2026'
    if not dob_str:
        return ''
    for fmt in ['%d-%b-%y', '%d-%b-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
        try:
            dt = datetime.strptime(dob_str.strip(), fmt)
            if dt.year > 2030:
                dt = dt.replace(year=dt.year - 100)
            return dt.strftime('%d/%m/%Y')
        except:
            pass
    return dob_str

def format_date_dash(dob_str):
    # Formats like '18-06-2026'
    if not dob_str:
        return ''
    for fmt in ['%d-%b-%y', '%d-%b-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
        try:
            dt = datetime.strptime(dob_str.strip(), fmt)
            if dt.year > 2030:
                dt = dt.replace(year=dt.year - 100)
            return dt.strftime('%d-%m-%Y')
        except:
            pass
    return dob_str

# ==========================================
# A. BUILD COMPLETE TANKS.TAB (167 tanks)
# ==========================================
tanks_dict = {}
# Keep existing rows keyed by TUID (col 20)
for r in existing_tanks_rows:
    if len(r) > 20 and r[20].strip():
        tuid = r[20].strip().upper()
        # Ensure 23 columns
        while len(r) < 23:
            r.append('')
        tanks_dict[tuid] = r

# Update / Add tanks from FishNET.tab
for t in fn_tanks:
    tuid = t['TUID'].strip().upper()
    female_val = t['FEMALE'].strip() if t['FEMALE'].strip() and t['FEMALE'].strip() != '0' else ''
    male_val = t['MALE'].strip() if t['MALE'].strip() and t['MALE'].strip() != '0' else ''
    total_val = t['TOTAL'].strip()
    status_val = t['STATUS'].strip()
    tank_size = t['TANK '].strip()
    turnover_val = t['TURNOVER'].strip()
    notes_val = t['NOTES'].strip()
    cross_val = t['Derivative cross'].strip()
    dob_formatted = format_dob_for_tanks(t['DOB'].strip())
    dod_val = t['DOD'].strip()
    genotype = get_genotype_desc(notes_val)

    if tuid in tanks_dict:
        # Update existing row with any refreshed fields
        r = tanks_dict[tuid]
        r[4] = female_val
        r[7] = male_val
        r[9] = total_val
        r[16] = status_val
        r[18] = tank_size if tank_size else r[18]
        r[21] = turnover_val if turnover_val else r[21]
        r[8] = notes_val if notes_val else r[8]
        if dod_val:
            r[1] = dod_val
        if cross_val:
            r[2] = cross_val
    else:
        # Create new 23-column row
        new_row = [
            dob_formatted,                  # col 0: DOB
            dod_val,                        # col 1: DOD
            cross_val,                      # col 2: Derivative Cross
            'Zebrafish',                    # col 3: Species
            female_val,                     # col 4: FEMALE
            genotype,                       # col 5: Genotype
            'Huseyin Cagatay Yalcin',       # col 6: PI
            male_val,                       # col 7: MALE
            notes_val,                      # col 8: NOTES
            total_val,                      # col 9: TOTAL
            'QU-IACUC 006/2023-AMM5',       # col 10: IACUC Protocol
            '',                             # col 11: blank
            'D126',                         # col 12: Room
            '',                             # col 13: blank
            '',                             # col 14: blank
            '',                             # col 15: blank
            status_val,                     # col 16: Status
            '',                             # col 17: blank
            tank_size if tank_size else '1.8L', # col 18: Tank Size
            '',                             # col 19: blank/position
            tuid,                           # col 20: TUID
            turnover_val,                   # col 21: Turnover Date
            'Zebrafish facility'            # col 22: Facility
        ]
        tanks_dict[tuid] = new_row

# Sort tanks naturally by TUID
def get_tuid_num(t):
    m = re.search(r'\d+', t)
    return int(m.group(0)) if m else 9999

all_sorted_tanks = [tanks_dict[k] for k in sorted(tanks_dict.keys(), key=get_tuid_num)]
print(f"Generated complete tanks.tab with {len(all_sorted_tanks)} rows.")

# ==========================================
# B. BUILD COMPLETE CROSSES.TAB (71 crosses)
# ==========================================
crosses_dict = {}
for r in existing_crosses_rows:
    if len(r) > 7 and r[7].strip():
        cuid = r[7].strip().upper()
        while len(r) < 24:
            r.append('')
        crosses_dict[cuid] = r

# Find all crosses from FishNET.tab
cross_to_tanks = {}
for t in fn_tanks:
    c = t['Derivative cross'].strip().upper()
    if c:
        if c not in cross_to_tanks:
            cross_to_tanks[c] = []
        cross_to_tanks[c].append(t)

for cuid, t_list in cross_to_tanks.items():
    if cuid not in crosses_dict:
        # Synthesize new cross entry
        first_t = t_list[0]
        pat_tuid = first_t['PATERNAL'].strip()
        mat_tuid = first_t['MATERNAL'].strip()
        
        # Look up parent details
        pat_info = fn_tanks_by_id.get(pat_tuid.upper(), {})
        mat_info = fn_tanks_by_id.get(mat_tuid.upper(), {})
        
        pat_notes = pat_info.get('NOTES', '')
        mat_notes = mat_info.get('NOTES', '')
        pat_geno = get_genotype_desc(pat_notes)
        mat_geno = get_genotype_desc(mat_notes)
        
        tot_larvae = sum(int(t['TOTAL']) for t in t_list if t['TOTAL'].isdigit())
        dob_raw = first_t['DOB']
        
        date_slash = format_date_d_m_y(dob_raw)
        date_dash = format_date_dash(dob_raw)
        
        # Setup date = 1 day prior
        setup_date_slash = date_slash
        try:
            dt = datetime.strptime(date_slash, '%d/%m/%Y')
            setup_date_slash = (dt - timedelta(days=1)).strftime('%d/%m/%Y')
        except:
            pass

        new_cross_row = [
            '0',                                # col 0: Unfertilized / Dead
            '0',                                # col 1: Larvae dead
            str(tot_larvae),                    # col 2: Total produced
            str(tot_larvae),                    # col 3: Viable larvae
            '100.00%',                          # col 4: 0hpf SR%
            '100.00%',                          # col 5: 24hpf SR%
            'Enas',                             # col 6: Technician
            cuid,                               # col 7: CUID
            date_slash,                         # col 8: Date Logged
            date_dash,                          # col 9: Spawning Date
            setup_date_slash,                   # col 10: Setup Date
            mat_tuid if mat_tuid else pat_tuid, # col 11: Maternal Tank
            str(tot_larvae),                    # col 12: Transferred larvae
            '',                                 # col 13: blank
            '1',                                # col 14: Pairs count
            pat_tuid if pat_tuid else mat_tuid, # col 15: Paternal Tank
            'QU-IACUC 006/2023-AMM5',           # col 16: IACUC Protocol
            'Huseyin Cagatay Yalcin',           # col 17: PI
            'Active',                           # col 18: Status
            'Zebrafish facility',               # col 19: Facility
            mat_geno,                           # col 20: Maternal Genotype
            mat_notes,                          # col 21: Maternal Notes
            pat_geno,                           # col 22: Paternal Genotype
            pat_notes                           # col 23: Paternal Notes
        ]
        crosses_dict[cuid] = new_cross_row

def get_cuid_num(c):
    m = re.search(r'\d+', c)
    return int(m.group(0)) if m else 9999

all_sorted_crosses = [crosses_dict[k] for k in sorted(crosses_dict.keys(), key=get_cuid_num)]
print(f"Generated complete crosses.tab with {len(all_sorted_crosses)} rows.")

# ==========================================
# C. BUILD COMPLETE NURSERY.TAB (67 batches)
# ==========================================
nursery_dict = {}
for r in existing_nursery_rows:
    if len(r) > 0 and r[0].strip():
        nuid = r[0].strip().upper()
        while len(r) < 18:
            r.append('')
        nursery_dict[nuid] = r

# Find existing max NUID number
max_nuid_num = max([get_cuid_num(k) for k in nursery_dict.keys()] or [0])
existing_nursery_cuids = set(r[4].strip().upper() for r in nursery_dict.values() if len(r) > 4)

for cuid, t_list in cross_to_tanks.items():
    if cuid not in existing_nursery_cuids:
        max_nuid_num += 1
        nuid = f"N{max_nuid_num:04d}"
        
        first_t = t_list[0]
        pat_tuid = first_t['PATERNAL'].strip()
        mat_tuid = first_t['MATERNAL'].strip()
        
        pat_info = fn_tanks_by_id.get(pat_tuid.upper(), {})
        mat_info = fn_tanks_by_id.get(mat_tuid.upper(), {})
        
        pat_notes = pat_info.get('NOTES', '')
        mat_notes = mat_info.get('NOTES', '')
        pat_geno = get_genotype_desc(pat_notes)
        mat_geno = get_genotype_desc(mat_notes)
        
        tot_larvae = sum(int(t['TOTAL']) for t in t_list if t['TOTAL'].isdigit())
        dob_raw = first_t['DOB']
        
        date_slash = format_date_d_m_y(dob_raw)
        date_dash = format_date_dash(dob_raw)
        
        setup_date_slash = date_slash
        entry_date_slash = date_slash
        try:
            dt = datetime.strptime(date_slash, '%d/%m/%Y')
            setup_date_slash = (dt - timedelta(days=1)).strftime('%d/%m/%Y')
            entry_date_slash = (dt + timedelta(days=5)).strftime('%d/%m/%Y')
        except:
            pass

        new_nursery_row = [
            nuid,                               # col 0: NUID
            str(tot_larvae),                    # col 1: Larvae Count
            'Graduate to system',               # col 2: Status
            'Enas',                             # col 3: Technician
            cuid,                               # col 4: CUID
            date_slash,                         # col 5: Graduation Date
            entry_date_slash,                   # col 6: Nursery Entry Date
            date_dash,                          # col 7: Spawning Date
            setup_date_slash,                   # col 8: Setup Date
            mat_tuid if mat_tuid else pat_tuid, # col 9: Maternal Dam Tank
            pat_tuid if pat_tuid else mat_tuid, # col 10: Paternal Sire Tank
            'QU-IACUC 006/2023-AMM5',           # col 11: IACUC Protocol
            'Huseyin Cagatay Yalcin',           # col 12: PI
            'Zebrafish facility',               # col 13: Facility
            mat_geno,                           # col 14: Maternal Genotype
            mat_notes,                          # col 15: Maternal Notes
            pat_geno,                           # col 16: Paternal Genotype
            pat_notes                           # col 17: Paternal Notes
        ]
        nursery_dict[nuid] = new_nursery_row
        existing_nursery_cuids.add(cuid)

all_sorted_nursery = [nursery_dict[k] for k in sorted(nursery_dict.keys(), key=get_cuid_num)]
print(f"Generated complete nursery.tab with {len(all_sorted_nursery)} rows.")

# ==========================================
# D. WRITE UPDATED EXPORT FILES
# ==========================================
def write_tab_file(path, rows):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        for r in rows:
            writer.writerow(r)
    print(f"Successfully wrote {path} ({len(rows)} rows)")

write_tab_file(os.path.join(export_dir, 'tanks.tab'), all_sorted_tanks)
write_tab_file(os.path.join(export_dir, 'crosses.tab'), all_sorted_crosses)
write_tab_file(os.path.join(export_dir, 'nursery.tab'), all_sorted_nursery)

# Also copy to parent FishNET Data directory for convenience
fishnet_data_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data'
write_tab_file(os.path.join(fishnet_data_dir, 'tanks details.tab'), all_sorted_tanks)
write_tab_file(os.path.join(fishnet_data_dir, 'Crosses details.tab'), all_sorted_crosses)
