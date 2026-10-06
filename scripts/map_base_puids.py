import os
import re
from collections import defaultdict
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
EXPORT_DIR = os.path.join(ROOT_DIR, 'FishNet Exported Data')

print("=== Base PUID Mapping Engine ===")

booking_script = r'C:\Users\ae20164\OneDrive - Jordan University of Science and Technology (JUST)\zebrafish-booking-portal\scripts\sync-registry.js'
with open(booking_script, 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r'\{\s*num:\s*"(.*?)",\s*base:\s*"(.*?)",\s*ver:\s*"(.*?)",\s*exp:\s*"(.*?)",\s*pi:\s*"(.*?)",\s*email:\s*"(.*?)",\s*status:\s*"(.*?)"\s*\}'
matches = re.findall(pattern, code)

# Clean base names to group versions together
def clean_base_key(base_str):
    b = base_str.strip()
    # Normalize spaces like "QU-IBC- 2022/013" -> "QU-IBC-2022/013"
    b = re.sub(r'QU-([A-Z]+)-\s*', r'QU-\1-', b)
    b = re.sub(r'QU-([A-Z]+)\s+', r'QU-\1-', b)
    # Remove suffix like (AB) or (Fli) or -P. harmala
    b = re.sub(r'\s*\([A-Za-z]+\)', '', b)
    b = re.sub(r'-P\.\s*[A-Za-z]+', '', b)
    return b.strip()

base_groups = defaultdict(list)
for m in matches:
    num, base, ver, exp, pi, email, status = m
    b_key = clean_base_key(base)
    base_groups[b_key].append({
        'num': num.strip(),
        'base': base.strip(),
        'ver': ver.strip(),
        'exp': exp.strip(),
        'pi': pi.strip(),
        'email': email.strip(),
        'status': status.strip()
    })

print(f"Total Unique Base Research Projects: {len(base_groups)}")

# Known existing PUID mappings from FileMaker
# P001 -> QU-IACUC-006/2023
# P002 -> QU-IBC-2018/031
puid_assignments = {}
counter = 1

# Ensure P001 and P002 match the core facility protocols
if 'QU-IACUC-006/2023' in base_groups:
    puid_assignments['QU-IACUC-006/2023'] = 'P001'
    counter = max(counter, 2)
if 'QU-IBC-2018/031' in base_groups:
    puid_assignments['QU-IBC-2018/031'] = 'P002'
    counter = max(counter, 3)

for b_key in base_groups:
    if b_key not in puid_assignments:
        puid_assignments[b_key] = f"P{counter:03d}"
        counter += 1

print("\n--- Base PUID Assignments ---")
for b_key, puid in sorted(puid_assignments.items(), key=lambda x: x[1]):
    versions = base_groups[b_key]
    active_v = [v for v in versions if v['status'] == 'ACTIVE']
    curr_v = active_v[0] if active_v else versions[0]
    print(f"[{puid}] Base: {b_key} | Current: {curr_v['num']} ({curr_v['status']}) | PI: {curr_v['pi']}")
