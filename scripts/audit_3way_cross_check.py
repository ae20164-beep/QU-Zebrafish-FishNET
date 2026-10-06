import csv
import json
import os
import re
from datetime import datetime

def run_3way_audit():
    labels_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels'
    tanks_path = os.path.join(labels_dir, 'FishNet Exported Data', 'Tanks.tab')
    crosses_path = os.path.join(labels_dir, 'FishNet Exported Data', 'Crosses.tab')
    nursery_path = os.path.join(labels_dir, 'FishNet Exported Data', 'Nursery.tab')
    
    # 1. Load Nursery
    nursery = {}
    with open(nursery_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        for r in csv.reader(f, delimiter='\t'):
            if len(r) >= 8:
                nuid = r[0].strip().upper()
                count = r[1].strip()
                action = r[2].strip()
                cuid = r[4].strip().upper()
                grad_date = r[6].strip()
                mating_date = r[7].strip()
                set_date = r[8].strip() if len(r) > 8 else ''
                dam = r[9].strip() if len(r) > 9 else ''
                sire = r[10].strip() if len(r) > 10 else ''
                protocol = r[11].strip() if len(r) > 11 else ''
                staff = r[12].strip() if len(r) > 12 else ''
                dam_line = r[15].strip() if len(r) > 15 else ''
                sire_line = r[17].strip() if len(r) > 17 else ''
                
                nursery[nuid] = {
                    'nuid': nuid, 'count': count, 'action': action, 'cuid': cuid,
                    'grad_date': grad_date, 'mating_date': mating_date, 'set_date': set_date,
                    'dam': dam, 'sire': sire, 'protocol': protocol, 'staff': staff,
                    'dam_line': dam_line, 'sire_line': sire_line
                }

    nursery_by_cross = {}
    for nuid, n in nursery.items():
        if n['cuid']:
            if n['cuid'] not in nursery_by_cross:
                nursery_by_cross[n['cuid']] = []
            nursery_by_cross[n['cuid']].append(n)

    # 2. Load Crosses
    crosses = {}
    with open(crosses_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        for r in csv.reader(f, delimiter='\t'):
            if not r: continue
            # Find CUID in any column
            cuid = None
            cuid_idx = -1
            for idx, col in enumerate(r):
                c_match = re.search(r'\b(C\d{4})\b', col.strip().upper())
                if c_match:
                    cuid = c_match.group(1)
                    cuid_idx = idx
                    break
            if not cuid: continue
            
            # Find dates in the row
            dates = []
            for col in r:
                c_str = col.strip()
                if re.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$', c_str) or re.match(r'^\d{1,2}-[A-Za-z]{3}-\d{2,4}$', c_str):
                    dates.append(c_str)
            
            mating_date = dates[0] if dates else ''
            
            # Find parent tanks
            tanks_in_row = []
            for col in r:
                t_matches = re.findall(r'\bT\d{4}\b', col.strip().upper())
                for tm in t_matches:
                    if tm not in tanks_in_row:
                        tanks_in_row.append(tm)
            
            dam = tanks_in_row[0] if len(tanks_in_row) > 0 else ''
            sire = tanks_in_row[1] if len(tanks_in_row) > 1 else dam
            
            crosses[cuid] = {
                'cuid': cuid, 'date': mating_date, 'dam': dam, 'sire': sire, 'raw': r
            }

    # 3. Load Tanks
    tanks = []
    with open(tanks_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        for r in csv.reader(f, delimiter='\t'):
            if len(r) < 21: continue
            tuid = r[20].strip().upper()
            if not tuid or not tuid.startswith('T'): continue
            dob = r[0].strip()
            cuid = r[2].strip().upper()
            genotype = r[5].strip()
            notes = r[8].strip()
            total_fish = r[9].strip()
            protocol = r[10].strip()
            status = r[16].strip()
            turnover_date = r[21].strip() if len(r) > 21 else ''
            
            c_info = crosses.get(cuid, {})
            n_list = nursery_by_cross.get(cuid, [])
            
            tanks.append({
                'tuid': tuid, 'dob': dob, 'cuid': cuid, 'genotype': genotype, 'notes': notes,
                'total_fish': total_fish, 'protocol': protocol, 'status': status,
                'turnover_date': turnover_date, 'cross': c_info, 'nursery': n_list
            })

    print(f"Loaded {len(tanks)} Tanks, {len(crosses)} Crosses, {len(nursery)} Nursery records.")
    
    print("\n" + "="*110)
    print(f"{'TUID':6} | {'Tank DOB':10} | {'Derivative Cross':16} | {'Cross Date':12} | {'Nursery ID & Date':24} | {'Nursery Count':14} | {'Status':12}")
    print("="*110)
    
    discrepancies = []
    
    for t in tanks:
        if t['cuid']:
            c_info = t['cross']
            n_list = t['nursery']
            
            c_date = c_info.get('date', 'NO_CROSS')
            n_uids_dates = ', '.join([f"{n['nuid']} ({n['mating_date']})" for n in n_list]) or 'NO_NURSERY'
            n_counts = ', '.join([f"{n['nuid']}: {n['count']} fish" for n in n_list]) or '-'
            
            print(f"{t['tuid']:6} | {t['dob']:10} | {t['cuid']:16} | {c_date:12} | {n_uids_dates:24} | {n_counts:14} | {t['status']:12}")
            
            # Discrepancy checks:
            # 1. Date mismatch between Tank DOB, Cross Date, Nursery Mating Date
            for n in n_list:
                if c_date and n['mating_date'] and c_date != n['mating_date']:
                    discrepancies.append({
                        'type': 'Cross vs Nursery Date Mismatch',
                        'tuid': t['tuid'], 'cuid': t['cuid'], 'nuid': n['nuid'],
                        'cross_date': c_date, 'nursery_date': n['mating_date'], 'tank_dob': t['dob']
                    })
    
    print("\n" + "="*110)
    print(f"TOTAL DISCREPANCIES DETECTED: {len(discrepancies)}")
    for d in discrepancies:
        print(d)

if __name__ == '__main__':
    run_3way_audit()
