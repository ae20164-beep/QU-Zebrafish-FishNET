import os
import re
import json
from collections import defaultdict

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
EXPORT_DIR = os.path.join(ROOT_DIR, 'FishNet Exported Data')

print("=== Cross-Checking RAs & Sorting by PI ===")

# 1. Load Project Registry to map Project -> PI
booking_script = r'C:\Users\ae20164\OneDrive - Jordan University of Science and Technology (JUST)\zebrafish-booking-portal\scripts\sync-registry.js'
with open(booking_script, 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r'\{\s*num:\s*["\'](.*?)["\'],\s*base:\s*["\'](.*?)["\'],\s*ver:\s*["\'](.*?)["\'],\s*exp:\s*["\'](.*?)["\'],\s*pi:\s*["\'](.*?)["\'],\s*email:\s*["\'](.*?)["\'],\s*status:\s*["\'](.*?)["\']\s*\}'
matches = re.findall(pattern, code)

project_to_pi = {}
pi_to_projects = defaultdict(set)

def normalize_key(s):
    if not s: return ''
    s = re.sub(r'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u00A0]', '-', str(s))
    return re.sub(r'\s+', ' ', s).strip().lower()

for m in matches:
    num, base, ver, exp, pi, email, status = m
    p_norm = normalize_key(num)
    b_norm = normalize_key(base)
    project_to_pi[p_norm] = pi.strip()
    project_to_pi[b_norm] = pi.strip()
    pi_to_projects[pi.strip()].add(p_norm)
    pi_to_projects[pi.strip()].add(b_norm)

# 2. Extract Existing CITI and Registered Lab Users from Organized Folders and Local Registry
org_folder = r'X:\Projects\Organized List of Project -AE and AF'
known_pi_members = defaultdict(set)

if os.path.exists(org_folder):
    for pi_dir in os.listdir(org_folder):
        full_pi = os.path.join(org_folder, pi_dir)
        if not os.path.isdir(full_pi): continue
        for root, dirs, files in os.walk(full_pi):
            rel = os.path.relpath(root, full_pi).replace('\\', '/')
            if 'citi' in rel.lower():
                for d in dirs:
                    if d.lower() not in ['citis', 'citi', "citi's", 'forms', 'originals']:
                        clean_name = re.sub(r'citi.*', '', d, flags=re.IGNORECASE).strip()
                        if clean_name and len(clean_name) > 2:
                            known_pi_members[pi_dir].add(clean_name)

# 3. RA Registry Data Structure
# Format:
# {
#   "PI Name": [
#       { "name": "...", "email": "...", "verified_projects": [...], "status": "VERIFIED_RA" }
#   ]
# }

ra_registry = defaultdict(list)
for pi, members in known_pi_members.items():
    for m in sorted(members):
        ra_registry[pi].append({
            "name": m,
            "email": "",
            "verified_projects": list(pi_to_projects.get(pi, [])),
            "status": "CITI_VERIFIED"
        })

TEAM_REGISTRY_PATH = os.path.join(SCRIPTS_DIR, 'pi_team_registry.json')
with open(TEAM_REGISTRY_PATH, 'w', encoding='utf-8') as f:
    json.dump(ra_registry, f, indent=2, ensure_ascii=False)

print(f"[OK] RA Registry created and saved to {TEAM_REGISTRY_PATH}")
print(f"Total PIs with mapped RAs: {len(ra_registry)}")
for pi, members in ra_registry.items():
    print(f"  * {pi}: {len(members)} team member(s)")

print("\n=== Automated RA Cross-Check Ready ===")
