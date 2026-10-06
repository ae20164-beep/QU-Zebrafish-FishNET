import os
import re
import json
from collections import defaultdict
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
EXPORT_DIR = os.path.join(ROOT_DIR, 'FishNet Exported Data')

print("=== Building Comprehensive Projects & Labs with Multi-Version History ===")

# 1. Facility Core Technologists
# AE = Ahmad Elwan, EA = Enas Alabsi, AF = Aseela Fatimah, SA = Sadiq, FB = Dr. Fusun
FACILITY_CORE_USERS = (
    "Dr. Huseyin Cagatay Yalcin\x0b"
    "Enas Said Khalil Al Absi\x0b"
    "Mohammed Sadique Kulamullathil\x0b"
    "Ahmad Taleb Elwan\x0b"
    "Aseela Fatimah\x0b"
    "Dr. Fusun"
)

# 2. Extract all entries from sync-registry.js
booking_script = r'C:\Users\ae20164\OneDrive - Jordan University of Science and Technology (JUST)\zebrafish-booking-portal\scripts\sync-registry.js'
with open(booking_script, 'r', encoding='utf-8') as f:
    code = f.read()

# Match entries: { num: "...", base: "...", ver: "...", exp: "...", pi: "...", email: "...", status: "..." }
pattern = r'\{\s*num:\s*["\'](.*?)["\'],\s*base:\s*["\'](.*?)["\'],\s*ver:\s*["\'](.*?)["\'],\s*exp:\s*["\'](.*?)["\'],\s*pi:\s*["\'](.*?)["\'],\s*email:\s*["\'](.*?)["\'],\s*status:\s*["\'](.*?)["\']\s*\}'
matches = re.findall(pattern, code)

print(f"Extracted {len(matches)} protocol version records from booking portal registry.")

def clean_base_key(base_str):
    b = base_str.strip()
    b = re.sub(r'QU-([A-Z]+)-\s*', r'QU-\1-', b)
    b = re.sub(r'QU-([A-Z]+)\s+', r'QU-\1-', b)
    b = re.sub(r'\s*\([A-Za-z]+\)', '', b)
    b = re.sub(r'-P\.\s*[A-Za-z]+', '', b)
    return b.strip()

def fmt_date_dmY(d_str):
    if not d_str:
        return ''
    for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y']:
        try:
            dt = datetime.strptime(d_str.strip(), fmt)
            return dt.strftime('%d-%m-%Y')
        except:
            pass
    return d_str.strip()

# Group all versions under clean base projects
base_groups = defaultdict(list)
for m in matches:
    num, base, ver, exp, pi, email, status = m
    b_key = clean_base_key(base)
    st = 'Active' if status == 'ACTIVE' else ('Superseded' if status == 'SUPERSEDED' else ('Pending Renewal' if status == 'PENDING_RENEWAL' else 'Completed'))
    base_groups[b_key].append({
        'num': num.strip(),
        'base': base.strip(),
        'ver': ver.strip(),
        'exp': fmt_date_dmY(exp),
        'pi': pi.strip(),
        'email': email.strip(),
        'status': st
    })

# Scan Organized Projects folder for additional past versions if any
org_folder = r'X:\Projects\Organized List of Project -AE and AF'
if os.path.exists(org_folder):
    print(f"Scanning {org_folder} for version folders & approvals...")
    # Map any subfolders like 'QU-IBC-2022-013-AMM1', etc.

# Persistent PUID mapping
# P001: QU-IACUC-006/2023 (Facility)
# P002: QU-IBC-2018/031 (Facility)
# P003..: Unique base projects
puid_map = {}
counter = 1

if 'QU-IACUC-006/2023' in base_groups:
    puid_map['QU-IACUC-006/2023'] = 'P001'
    counter = max(counter, 2)
if 'QU-IBC-2018/031' in base_groups:
    puid_map['QU-IBC-2018/031'] = 'P002'
    counter = max(counter, 3)

for b_key in sorted(base_groups.keys()):
    if b_key not in puid_map:
        puid_map[b_key] = f"P{counter:03d}"
        counter += 1

print(f"Assigned persistent PUIDs for {len(puid_map)} base project families.")

# Load or initialize registered Research Assistants (RAs) / Team Members per PI
# We will create a JSON file 'pi_team_registry.json' that tracks verified RAs
TEAM_REGISTRY_PATH = os.path.join(SCRIPTS_DIR, 'pi_team_registry.json')
if os.path.exists(TEAM_REGISTRY_PATH):
    with open(TEAM_REGISTRY_PATH, 'r', encoding='utf-8') as f:
        pi_teams = json.load(f)
else:
    # Initialize empty list per PI - to be dynamically populated upon registration & cross-checking
    pi_teams = defaultdict(list)

# Load real descriptive project titles
TITLES_PATH = os.path.join(SCRIPTS_DIR, 'project_titles.json')
project_titles = {}
if os.path.exists(TITLES_PATH):
    with open(TITLES_PATH, 'r', encoding='utf-8') as f:
        project_titles = json.load(f)

def clean_alphanumeric(s):
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()

title_lookup = {clean_alphanumeric(k): v for k, v in project_titles.items()}

def resolve_project_title(p_num, b_key, is_facility):
    if is_facility:
        return "Zebrafish Maintenance and Breeding Practice at BRC Zebrafish Facility"
    ck_num = clean_alphanumeric(p_num)
    ck_base = clean_alphanumeric(b_key)
    res_title = None
    # 1. Exact or partial match on p_num
    for k, v in title_lookup.items():
        if k in ck_num or ck_num in k:
            res_title = v
            break
    # 2. Match on base key
    if not res_title:
        for k, v in title_lookup.items():
            if k in ck_base or ck_base in k:
                res_title = v
                break
    if not res_title:
        res_title = f"Zebrafish Research Protocol - {p_num}"
        
    # Clean any trailing funding metadata
    res_title = re.split(r'\s*(?:Funding Agency|Grant Number|Project\s*start|This\s*is|\*|Date:)', res_title, flags=re.IGNORECASE)[0].strip()
    return res_title

# ==================== BUILD PROJECTS.TAB ====================
# Columns:
# 1. Date End
# 2. Lab Users (Facility core for facility projects; PI + verified RAs for individual projects)
# 3. Protocol Name (Descriptive Research Title)
# 4. Protocol Number (specific version number)
# 5. PUID (permanent base PUID)
# 6. Status (Active, Superseded, Completed, Pending Renewal)
# 7. LUID / PI Name

project_rows = []

for b_key, puid in sorted(puid_map.items(), key=lambda x: x[1]):
    versions = base_groups[b_key]
    for v in versions:
        p_num = v['num']
        pi_name = v['pi']
        date_end = v['exp']
        status = v['status']
        
        is_facility = ("Facility" in pi_name) or ("006/2023" in p_num) or ("031" in p_num and "Facility" in b_key)
        p_name = resolve_project_title(p_num, b_key, is_facility)
        
        if is_facility:
            lab_users = FACILITY_CORE_USERS
            luid = "Zebrafish Core Facility (Dr. Huseyin Yalcin)"
        else:
            luid = pi_name
            # PI + verified registered RAs for this PI
            ra_raw = pi_teams.get(pi_name, [])
            ra_names = [r['name'] if isinstance(r, dict) else str(r) for r in ra_raw if r]
            if ra_names:
                lab_users = f"{pi_name}\x0b" + "\x0b".join(ra_names)
            else:
                lab_users = pi_name  # Starts with PI only; populated dynamically when RAs register

        row = [
            date_end,
            lab_users,
            p_name,
            p_num,
            puid,
            status,
            luid
        ]
        project_rows.append('\t'.join(row))

projects_path = os.path.join(EXPORT_DIR, 'Projects.tab')
with open(projects_path, 'w', encoding='utf-8', newline='') as f:
    f.write('\r\n'.join(project_rows) + '\r\n')

print(f"[OK] Wrote {len(project_rows)} project version rows with descriptive titles to {projects_path}")

# ==================== BUILD LABS.TAB ====================
# Columns:
# 1. College
# 2. Laboratory Name
# 3. Principal Investigator (PI)
# 4. [Empty spacer]
# 5. Valid Until (Date End)
# 6. Project Name
# 7. IUCAC/IBC Protocol Number

lab_rows = []
pi_projects_grouped = defaultdict(list)

# Group all version records by PI
for b_key, puid in sorted(puid_map.items(), key=lambda x: x[1]):
    versions = base_groups[b_key]
    for v in versions:
        pi_name = v['pi']
        pi_projects_grouped[pi_name].append(v)

for pi, p_list in pi_projects_grouped.items():
    if "Facility" in pi:
        college = "BRC"
        lab_name = "Zebrafish facility"
    elif "Yalcin" in pi:
        college = "BRC"
        lab_name = "Dr. Huseyin Yalcin Lab"
    elif "Al-Asmakh" in pi or "Shafai" in pi:
        college = "College of Health Sciences"
        lab_name = f"{pi} Lab"
    elif "Shaito" in pi or "Benslimane" in pi:
        college = "BRC"
        lab_name = f"{pi} Lab"
    else:
        college = "College of Arts and Sciences"
        lab_name = f"{pi} Lab"

    # First record for this Lab
    first_p = p_list[0]
    p_name_first = resolve_project_title(first_p['num'], first_p['base'], "Facility" in pi)
    
    first_row = [
        college,
        lab_name,
        pi,
        '',
        first_p['exp'],
        p_name_first,
        first_p['num']
    ]
    lab_rows.append('\t'.join(first_row))

    # Remaining versions / projects for this PI
    for sub_p in p_list[1:]:
        p_name_sub = resolve_project_title(sub_p['num'], sub_p['base'], "Facility" in pi)
        sub_row = [
            '',
            '',
            '',
            '',
            sub_p['exp'],
            p_name_sub,
            sub_p['num']
        ]
        lab_rows.append('\t'.join(sub_row))

labs_path = os.path.join(EXPORT_DIR, 'Labs.tab')
with open(labs_path, 'w', encoding='utf-8', newline='') as f:
    f.write('\r\n'.join(lab_rows) + '\r\n')

print(f"[OK] Wrote {len(lab_rows)} lab and project rows to {labs_path}")
print("=== COMPLETED PROJECTS & LABS MULTI-VERSION GENERATION ===")
