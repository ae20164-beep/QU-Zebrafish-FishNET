import os
import csv
import re
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
EXPORT_DIR = os.path.join(ROOT_DIR, 'FishNet Exported Data')

print("=== Synchronizing Projects.tab & Labs.tab with Booking Portal Registry ===")

# 1. Load active & historical protocols from booking portal registry
booking_script = r'C:\Users\ae20164\OneDrive - Jordan University of Science and Technology (JUST)\zebrafish-booking-portal\scripts\sync-registry.js'
with open(booking_script, 'r', encoding='utf-8') as f:
    code = f.read()

matches = re.findall(r'\{\s*num:\s*"(.*?)",\s*base:\s*"(.*?)",\s*ver:\s*"(.*?)",\s*exp:\s*"(.*?)",\s*pi:\s*"(.*?)",\s*email:\s*"(.*?)",\s*status:\s*"(.*?)"\s*\}', code)

protocols = []
for m in matches:
    num, base, ver, exp, pi, email, status = m
    protocols.append({
        'protocol_num': num.strip(),
        'base': base.strip(),
        'ver': ver.strip(),
        'exp_iso': exp.strip(),
        'pi': pi.strip(),
        'email': email.strip(),
        'status': 'Active' if status == 'ACTIVE' else ('Superseded' if status == 'SUPERSEDED' else ('Pending Renewal' if status == 'PENDING_RENEWAL' else 'Completed'))
    })

# Format date to dd-mm-yyyy for FileMaker
def fmt_date(d_str):
    if not d_str:
        return ''
    try:
        dt = datetime.strptime(d_str, '%Y-%m-%d')
        return dt.strftime('%d-%m-%Y')
    except:
        return d_str

# Facility Technologists Team (Vertical-tab separated in FileMaker)
CORE_TEAM = "Huseyin Cagatay Yalcin\x0bEnas Said Khalil Al Absi\x0bMohammed Sadique Kulamullathil\x0bAhmad Taleb Elwan"

# Build Projects.tab rows (7 columns)
# Col 1: Protocols Date End
# Col 2: Authorized Researchers / Team Members
# Col 3: Protocol Name
# Col 4: Protocol Number
# Col 5: Project ID (P001, P002...)
# Col 6: Status (Active, Completed, Superseded)
# Col 7: Principal Investigator (PI)

project_rows = []
for idx, p in enumerate(protocols):
    pid = f"P{idx+1:03d}"
    end_date = fmt_date(p['exp_iso'])
    p_num = p['protocol_num']
    pi_name = p['pi']
    status = p['status']
    proto_name = f"Zebrafish Research Protocol - {p_num} ({pi_name})" if "Facility" not in pi_name else "Zebrafish Maintenance and Breeding Practice at BRC Zebrafish Facility"
    
    # Row 1 of project entry
    row = [
        end_date,
        CORE_TEAM,
        proto_name,
        p_num,
        pid,
        status,
        pi_name
    ]
    project_rows.append('\t'.join(row))

projects_file = os.path.join(EXPORT_DIR, 'Projects.tab')
with open(projects_file, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(project_rows) + '\n')

print(f"[OK] Wrote {len(project_rows)} synchronized projects to {projects_file}")

# Build Labs.tab rows (8 columns)
# Col 1: Institution / Department (BRC, CHS, CAS, CMED, etc.)
# Col 2: Lab Name
# Col 3: Principal Investigator (PI)
# Col 4: [Empty]
# Col 5: Protocols Date End
# Col 6: Protocol Name
# Col 7: Protocol Number
# Col 8: [Tanks count or empty]

lab_rows = []
pi_set = {}
for p in protocols:
    pi = p['pi']
    if pi not in pi_set:
        pi_set[pi] = []
    pi_set[pi].append(p)

for pi, p_list in pi_set.items():
    dept = "BRC" if "Zebrafish" in pi or "Yalcin" in pi else "Health / Sciences"
    lab_name = "Zebrafish Core Facility" if "Zebrafish" in pi or "Yalcin" in pi else f"{pi} Research Group"
    
    for p in p_list:
        end_date = fmt_date(p['exp_iso'])
        p_num = p['protocol_num']
        p_name = f"Zebrafish Research - {p_num}" if "Zebrafish" not in pi else "Zebrafish Maintenance and Breeding Practice at BRC Zebrafish Facility"
        row = [
            dept,
            lab_name,
            pi,
            '',
            end_date,
            p_name,
            p_num,
            ''
        ]
        lab_rows.append('\t'.join(row))

labs_file = os.path.join(EXPORT_DIR, 'Labs.tab')
with open(labs_file, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(lab_rows) + '\n')

print(f"[OK] Wrote {len(lab_rows)} synchronized lab/PI records to {labs_file}")

# Re-run master sync pipeline
import subprocess
sync_script = os.path.join(SCRIPTS_DIR, 'sync_all_pipeline.py')
subprocess.run(['python', sync_script], cwd=ROOT_DIR)
print("\n*** PROJECTS & LABS SYNCHRONIZATION COMPLETE ***")
