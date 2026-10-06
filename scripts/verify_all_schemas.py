import os
import csv

EXPORT_DIR = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels\FishNet Exported Data'

EXPECTED_HEADERS = {
    'Tanks.tab': [
        'Date of Birth', 'Date of Death', 'Dervitive Cross', 'Facility', 'Females', 
        'Genotype', 'Lab Member', 'Males', 'Notes', 'Number of Fish', 
        'Protocol', 'Rack Number', 'Room', 'Row Letter', 'Search', 
        'Space Number', 'Status', 'Subspace Number', 'Tank Size', 'tankCount', 
        'TUID', 'Turnover Date', 'Laboratories::Lab Name'
    ],
    'Crosses.tab': [
        '# of dead 0HPF', '# of dead 24HPF', '# survived 0HPF', '# survived 24HPF', 
        '0HPF SR', '24HPF SR', 'Admin', 'CUID', 'Date Ended', 'Date of Birth', 
        'Date Started', 'Maternal ID', 'Mating Outcome', 'Notes', 'Number of Tanks', 
        'Paternal ID', 'Protocol', 'Set up by', 'Status', 'Lab Members Cross::Lab Name', 
        'Tanks_Maternal::Genotype', 'Tanks_Maternal::Notes', 'Tanks_Paternal::Genotype', 'Tanks_Paternal::Notes'
    ],
    'Nursery.tab': [
        'NUID', 'Number of Fish', 'Status', 'Fish Crosses::Admin', 'Fish Crosses::CUID', 
        'Fish Crosses::Date Ended', 'Fish Crosses::Date for transfer', 'Fish Crosses::Date of Birth', 
        'Fish Crosses::Date Started', 'Fish Crosses::Maternal ID', 'Fish Crosses::Paternal ID', 
        'Fish Crosses::Protocol', 'Fish Crosses::Set up by', 'Lab Members Cross::Lab Name', 
        'Tanks_Maternal::Genotype', 'Tanks_Maternal::Notes', 'Tanks_Paternal::Genotype', 'Tanks_Paternal::Notes'
    ],
    'Projects.tab': [
        'PUID', 'Project Title', 'PI Name', 'Description', 'Active Status', 'Approved Date', 'Expiration Date'
    ],
    'Labs.tab': [
        'Lab ID', 'Lab Name', 'PI Name', 'PUID', 'Department', 'Building', 'Room'
    ]
}

def verify():
    all_ok = True
    for fname, expected_cols in EXPECTED_HEADERS.items():
        path = os.path.join(EXPORT_DIR, fname)
        if not os.path.exists(path):
            print(f"[FAIL] {fname} does not exist at {path}")
            all_ok = False
            continue
        with open(path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = list(csv.reader(f, delimiter='\t'))
            if not reader:
                print(f"[FAIL] {fname} is empty")
                all_ok = False
                continue
            headers = reader[0]
            if len(headers) != len(expected_cols):
                print(f"[FAIL] {fname}: Expected {len(expected_cols)} columns, got {len(headers)}")
                print(f"  Expected: {expected_cols}")
                print(f"  Got:      {headers}")
                all_ok = False
                continue
            mismatches = []
            for idx, (exp, actual) in enumerate(zip(expected_cols, headers)):
                if exp.strip() != actual.strip():
                    mismatches.append(f"Col {idx+1}: Expected '{exp}' vs Got '{actual}'")
            if mismatches:
                print(f"[FAIL] {fname} header mismatches: {mismatches}")
                all_ok = False
            else:
                print(f"[OK] {fname}: Exact match ({len(headers)} columns, {len(reader)-1} data rows).")
    
    if all_ok:
        print("\n*** ALL EXPORTED TAB FILES MATCH EXACT FILEMAKER PRO SPECIFICATIONS! ***")
    return all_ok

if __name__ == '__main__':
    verify()
