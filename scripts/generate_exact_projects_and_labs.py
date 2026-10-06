import os
import re
from collections import defaultdict
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
EXPORT_DIR = os.path.join(ROOT_DIR, 'FishNet Exported Data')

print("=== Generating Exact Projects.tab & Labs.tab (Persistent Base PUIDs) ===")

booking_script = r'C:\Users\ae20164\OneDrive - Jordan University of Science and Technology (JUST)\zebrafish-booking-portal\scripts\sync-registry.js'
with open(booking_script, 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r'\{\s*num:\s*"(.*?)",\s*base:\s*"(.*?)",\s*ver:\s*"(.*?)",\s*exp:\s*"(.*?)",\s*pi:\s*"(.*?)",\s*email:\s*"(.*?)",\s*status:\s*"(.*?)"\s*\}'
matches = re.findall(pattern, code)

# Clean base names to group versions together
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

base_groups = defaultdict(list)
for m in matches:
    num, base, ver, exp, pi, email, status = m
    b_key = clean_base_key(base)
    base_groups[b_key].append({
        'num': num.strip(),
        'base': base.strip(),
        'ver': ver.strip(),
        'exp': fmt_date_dmY(exp),
        'pi': pi.strip(),
        'email': email.strip(),
        'status': 'Active' if status == 'ACTIVE' else ('Superseded' if status == 'SUPERSEDED' else ('Pending Renewal' if status == 'PENDING_RENEWAL' else 'Completed'))
    })

# Persistent PUID assignments
puid_assignments = {}
counter = 1
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

# Core Lab Technologists (Vertical Tab separated \x0b)
CORE_LAB_USERS = "Huseyin Cagatay Yalcin\x0bEnas Said Khalil Al Absi\x0bMohammed Sadique Kulamullathil\x0bAhmad Taleb Elwan"

# ==================== BUILD PROJECTS.TAB ====================
# 7 Columns:
# Col 1: Date End (e.g. 16-11-2026)
# Col 2: Lab Users (multiline with \x0b)
# Col 3: Protocol Name
# Col 4: Protocol Number
# Col 5: PUID (e.g. P001 - persistent per base project)
# Col 6: Status (Active, Completed, Superseded)
# Col 7: LUID / PI Name

project_records = []
for b_key, puid in sorted(puid_assignments.items(), key=lambda x: x[1]):
    versions = base_groups[b_key]
    # Pick the most relevant version (prefer ACTIVE, then latest)
    active_v = [v for v in versions if v['status'] == 'Active']
    v_target = active_v[0] if active_v else versions[-1]
    
    p_num = v_target['num']
    pi_name = v_target['pi']
    date_end = v_target['exp']
    st = v_target['status']
    
    if "Facility" in pi_name or "Yalcin" in pi_name and "006/2023" in p_num or "031" in p_num:
        p_name = "Zebrafish Maintenance and Breeding Practice at BRC Zebrafish Facility"
        l_users = CORE_LAB_USERS
    else:
        p_name = f"Zebrafish Research Protocol - {p_num}"
        l_users = f"{pi_name}\x0b{CORE_LAB_USERS}"

    row = [
        date_end,
        l_users,
        p_name,
        p_num,
        puid,
        st,
        pi_name
    ]
    project_records.append('\t'.join(row))

projects_path = os.path.join(EXPORT_DIR, 'Projects.tab')
with open(projects_path, 'w', encoding='utf-8', newline='') as f:
    f.write('\r\n'.join(project_records) + '\r\n')

print(f"[OK] Wrote {len(project_records)} clean projects with persistent PUIDs to {projects_path}")

# ==================== BUILD LABS.TAB ====================
# Layout matching Screenshot 1:
# Col 1: College (BRC, College of Health Sciences, College of Arts and Sciences, etc.)
# Col 2: Laboratory Name
# Col 3: Principal Investigator (PI)
# Col 4: [Empty spacer]
# Col 5: Valid Until (Date End)
# Col 6: Project Name
# Col 7: IUCAC/IBC Protocol Number

lab_records = []
# Group by PI
pi_labs = defaultdict(list)
for b_key, puid in sorted(puid_assignments.items(), key=lambda x: x[1]):
    versions = base_groups[b_key]
    active_v = [v for v in versions if v['status'] == 'Active']
    v_target = active_v[0] if active_v else versions[-1]
    pi_labs[v_target['pi']].append(v_target)

for pi, p_list in pi_labs.items():
    if "Facility" in pi or "Yalcin" in pi:
        college = "BRC"
        lab_name = "Zebrafish facility" if "Facility" in pi else "Dr. Huseyin Yalcin Lab"
    elif "Al-Asmakh" in pi or "Shafai" in pi:
        college = "College of Health Sciences"
        lab_name = f"{pi} Lab"
    elif "Shaito" in pi or "Benslimane" in pi:
        college = "BRC"
        lab_name = f"{pi} Lab"
    else:
        college = "College of Arts and Sciences"
        lab_name = f"{pi} Lab"

    # First project under this lab (fills header cols 1..4 + project cols 5..7)
    first_p = p_list[0]
    p_name_first = "Zebrafish Maintenance and Breeding Practice at BRC Zebrafish Facility" if "Facility" in pi else f"Zebrafish Research - {first_p['num']}"
    
    first_row = [
        college,
        lab_name,
        pi,
        '',
        first_p['exp'],
        p_name_first,
        first_p['num']
    ]
    lab_records.append('\t'.join(first_row))

    # Subsequent projects under the same Lab portal (empty header cols 1..4)
    for sub_p in p_list[1:]:
        p_name_sub = "Zebrafish Maintenance and Breeding Practice at BRC Zebrafish Facility" if "Facility" in pi else f"Zebrafish Research - {sub_p['num']}"
        sub_row = [
            '',
            '',
            '',
            '',
            sub_p['exp'],
            p_name_sub,
            sub_p['num']
        ]
        lab_records.append('\t'.join(sub_row))

labs_path = os.path.join(EXPORT_DIR, 'Labs.tab')
with open(labs_path, 'w', encoding='utf-8', newline='') as f:
    f.write('\r\n'.join(lab_records) + '\r\n')

print(f"[OK] Wrote {len(lab_records)} lab & portal rows matching exact FileMaker layout to {labs_path}")
print("\n*** PROJECTS & LABS GENERATION COMPLETE ***")
