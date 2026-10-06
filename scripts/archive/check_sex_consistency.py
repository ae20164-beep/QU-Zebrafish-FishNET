import csv
import re
import os

labels_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels'
done_dir = os.path.join(labels_dir, 'DONE')

# Load FishNET inventory
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
        status = row[13].strip() if len(row) > 13 else 'Active'
        
        num_id = int(re.sub(r'\D', '', tuid)) if re.search(r'\d', tuid) else 0
        std_tuid = f'T{num_id:04d}'
        sex_type = 'Female-Only' if f_cnt > 0 and m_cnt == 0 else ('Male-Only' if m_cnt > 0 and f_cnt == 0 else ('Mixed' if f_cnt > 0 and m_cnt > 0 else 'Unsexed'))
        fishnet[std_tuid] = {
            'tuid': std_tuid, 
            'raw': tuid, 
            'notes': notes, 
            'f': f_cnt, 
            'm': m_cnt, 
            'tot': tot,
            'status': status, 
            'sex_type': sex_type
        }

print(f"Loaded {len(fishnet)} tanks from FishNET.")
f_only = [t for t, d in fishnet.items() if d['sex_type'] == 'Female-Only']
m_only = [t for t, d in fishnet.items() if d['sex_type'] == 'Male-Only']
print(f"Female-Only tanks ({len(f_only)}): {', '.join(sorted(f_only))}")
print(f"Male-Only tanks ({len(m_only)}): {', '.join(sorted(m_only))}")

# Check 2026 complete breeding records
p26_path = os.path.join(done_dir, '2026_breeding_complete.csv')
inconsistencies = []

with open(p26_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader, 2):
        raw_line = row['Fishline']
        in_tank = row['In_Tank'].strip().lower() in ['yes', 'true']
        tanks_str = row['Tanks_Involved']
        tank_ids = [t.strip() for t in tanks_str.split(';') if t.strip()]
        
        tank_sexes = []
        for t in tank_ids:
            if t in fishnet:
                tank_sexes.append((t, fishnet[t]['sex_type'], fishnet[t]['f'], fishnet[t]['m'], fishnet[t]['status'], fishnet[t]['notes']))
            else:
                tank_sexes.append((t, 'NOT_IN_FISHNET', 0, 0, 'Unknown', 'Unknown'))
        
        # Check inconsistency rules:
        # 1. Single tank marked as in_tank, but the tank is Female-Only or Male-Only in FishNET
        if len(tank_ids) == 1 and in_tank:
            t_id, s_type, f_cnt, m_cnt, stat, notes = tank_sexes[0]
            if s_type in ['Female-Only', 'Male-Only']:
                inconsistencies.append({
                    'row': idx, 
                    'date': row['Date'], 
                    'line': raw_line, 
                    'issue': f"Single-sex reservoir {t_id} ({s_type}, F:{f_cnt}/M:{m_cnt}) marked as In-Tank spawn!",
                    'tanks': t_id,
                    'eggs': row['Total_Eggs_0H']
                })
        
        # 2. Single tank listed without In-Tank (and without partner) but it's single-sex
        if len(tank_ids) == 1 and not in_tank:
            t_id, s_type, f_cnt, m_cnt, stat, notes = tank_sexes[0]
            if s_type in ['Female-Only', 'Male-Only']:
                inconsistencies.append({
                    'row': idx, 
                    'date': row['Date'], 
                    'line': raw_line, 
                    'issue': f"Single-sex reservoir {t_id} ({s_type}, F:{f_cnt}/M:{m_cnt}) listed alone without partner tank!",
                    'tanks': t_id,
                    'eggs': row['Total_Eggs_0H']
                })

        # 3. Cross-pairing of two same-sex tanks (e.g. Female-Only x Female-Only or Male-Only x Male-Only)
        if len(tank_ids) >= 2:
            s_types = [ts[1] for ts in tank_sexes]
            if all(st == 'Female-Only' for st in s_types):
                inconsistencies.append({
                    'row': idx, 
                    'date': row['Date'], 
                    'line': raw_line, 
                    'issue': f"Both tanks in pair are Female-Only ({', '.join(tank_ids)})!",
                    'tanks': '; '.join(tank_ids),
                    'eggs': row['Total_Eggs_0H']
                })
            elif all(st == 'Male-Only' for st in s_types):
                inconsistencies.append({
                    'row': idx, 
                    'date': row['Date'], 
                    'line': raw_line, 
                    'issue': f"Both tanks in pair are Male-Only ({', '.join(tank_ids)})!",
                    'tanks': '; '.join(tank_ids),
                    'eggs': row['Total_Eggs_0H']
                })

print(f"\n--- Total potential discrepancies in 2026 data: {len(inconsistencies)} ---")
for inc in inconsistencies:
    print(f"Line {inc['row']:3d} [{inc['date']}]: {inc['issue']} | Text: '{inc['line']}' | Eggs: {inc['eggs']}")
