import os
import sys
import json
import csv
import argparse
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
EXPORT_DIR = os.path.join(ROOT_DIR, 'FishNet Exported Data')

def get_next_ids():
    # 1. Next TUID
    tanks_path = os.path.join(EXPORT_DIR, 'Tanks.tab')
    max_tuid = 1
    if os.path.exists(tanks_path):
        with open(tanks_path, 'r', encoding='utf-8') as f:
            for l in f:
                parts = l.strip().split('\t')
                if len(parts) >= 21 and parts[20].startswith('T'):
                    try:
                        num = int(parts[20][1:])
                        max_tuid = max(max_tuid, num)
                    except: pass
    next_tuid = f"T{max_tuid + 1:04d}"

    # 2. Next CUID
    crosses_path = os.path.join(EXPORT_DIR, 'Crosses.tab')
    max_cuid = 1
    if os.path.exists(crosses_path):
        with open(crosses_path, 'r', encoding='utf-8') as f:
            for l in f:
                parts = l.strip().split('\t')
                if len(parts) >= 8 and parts[7].startswith('C'):
                    try:
                        num = int(parts[7][1:])
                        max_cuid = max(max_cuid, num)
                    except: pass
    next_cuid = f"C{max_cuid + 1:04d}"

    # 3. Next NUID
    nursery_path = os.path.join(EXPORT_DIR, 'Nursery.tab')
    max_nuid = 1
    if os.path.exists(nursery_path):
        with open(nursery_path, 'r', encoding='utf-8') as f:
            for l in f:
                parts = l.strip().split('\t')
                if len(parts) >= 1 and parts[0].startswith('N'):
                    try:
                        num = int(parts[0][1:])
                        max_nuid = max(max_nuid, num)
                    except: pass
    next_nuid = f"N{max_nuid + 1:04d}"

    return next_tuid, next_cuid, next_nuid

def ingest_tank_label(line_name, origin_notes, dob_str, count_num, tank_size='3.5L', protocol='QU-IACUC 006/2023-AMM5', lab='Zebrafish facility', staff='Ahmad'):
    next_tuid, next_cuid, next_nuid = get_next_ids()
    print(f"=== Ingesting Tank Label: {next_tuid} | Origin: {origin_notes} | Count: {count_num} ===")

    # Parse DOB
    dob_dt = None
    for fmt in ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%d-%b-%Y', '%b %d, %Y', '%B %d, %Y']:
        try:
            dob_dt = datetime.strptime(dob_str.strip(), fmt)
            break
        except: pass
    if not dob_dt:
        dob_dt = datetime.now()
    
    dob_fm = dob_dt.strftime('%d-%m-%y')
    dob_cross = dob_dt.strftime('%d-%b-%y')
    dob_std = dob_dt.strftime('%d/%m/%Y')
    
    # Turnover date (+2 years)
    try:
        turnover_dt = dob_dt.replace(year=dob_dt.year + 2)
    except:
        turnover_dt = dob_dt
    turnover_fm = turnover_dt.strftime('%d-%m-%y')

    # Genotype string
    if line_name.upper() == 'AB':
        genotype = 'Wt (AB)'
    elif line_name.upper() == 'FLI':
        genotype = 'Tg (fli1a:eGFP) Sidra [Fli]'
    elif line_name.upper() == 'GATA':
        genotype = 'Tg (gata1:dsRed) Sidra [Gata]'
    elif line_name.upper() == 'CASPER':
        genotype = 'Mu Mu (mitfaw2/w2; mpv17a9/a9) [Casper]'
    else:
        genotype = line_name

    # 1. Append Cross
    cross_row = "\t".join([
        "0", "0", str(count_num), str(count_num), "100.00%", "100.00%", "", next_cuid, "", dob_cross, dob_std,
        origin_notes, "", f"{line_name} x {line_name}", "1", origin_notes, protocol, staff, "Active", lab,
        genotype, origin_notes, genotype, origin_notes
    ])
    crosses_path = os.path.join(EXPORT_DIR, 'Crosses.tab')
    with open(crosses_path, 'a', encoding='utf-8', newline='') as f:
        f.write(cross_row + '\r\n')
    print(f"[OK] Appended Cross {next_cuid} to Crosses.tab")

    # 2. Append Nursery
    nursery_row = "\t".join([
        next_nuid, str(count_num), "Graduate to system", "", next_cuid, "", dob_std, dob_cross, dob_std,
        origin_notes, origin_notes, protocol, staff, lab, genotype, origin_notes, genotype, origin_notes
    ])
    nursery_path = os.path.join(EXPORT_DIR, 'Nursery.tab')
    with open(nursery_path, 'a', encoding='utf-8', newline='') as f:
        f.write(nursery_row + '\r\n')
    print(f"[OK] Appended Nursery {next_nuid} to Nursery.tab")

    # 3. Append Tank to Tanks.tab and FishNET.tab
    tank_row = "\t".join([
        dob_fm, "", next_cuid, "Zebrafish", "", genotype, "Huseyin Cagatay Yalcin", "", origin_notes,
        str(count_num), protocol, "", "D126", "", "", "", "Adult/Active", "", tank_size, "180", next_tuid,
        turnover_fm, lab
    ])
    tanks_path = os.path.join(EXPORT_DIR, 'Tanks.tab')
    with open(tanks_path, 'a', encoding='utf-8', newline='') as f:
        f.write(tank_row + '\r\n')
    print(f"[OK] Appended Tank {next_tuid} to Tanks.tab")

    root_fishnet_path = os.path.join(ROOT_DIR, 'FishNET.tab')
    with open(root_fishnet_path, 'a', encoding='utf-8', newline='') as f:
        f.write(tank_row + '\r\n')
    print(f"[OK] Appended Tank {next_tuid} to root FishNET.tab")

    # 4. Trigger master pipeline sync
    sync_script = os.path.join(SCRIPTS_DIR, 'sync_all_pipeline.py')
    os.system(f'python "{sync_script}"')
    print(f"\n*** TANK {next_tuid} SUCCESSFULLY GRADUATED AND ALL DATABASES SYNCHRONIZED! ***")
    return next_tuid, next_cuid, next_nuid

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FishNET Quick Ingestion Engine')
    parser.add_argument('--type', choices=['label', 'log'], default='label')
    parser.add_argument('--line', default='AB')
    parser.add_argument('--origin', default='AB T128')
    parser.add_argument('--dob', default=datetime.now().strftime('%d-%m-%Y'))
    parser.add_argument('--count', type=int, default=30)
    parser.add_argument('--size', default='3.5L')
    parser.add_argument('--protocol', default='QU-IACUC 006/2023-AMM5')
    parser.add_argument('--lab', default='Zebrafish facility')
    args = parser.parse_args()

    if args.type == 'label':
        ingest_tank_label(args.line, args.origin, args.dob, args.count, args.size, args.protocol, args.lab)
