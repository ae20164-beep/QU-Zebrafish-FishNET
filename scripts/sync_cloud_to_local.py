import os
import json
import csv
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

labels_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels'

# 1. Load Google Sheets cloud sync
cloud_path = os.path.join(labels_dir, 'google_sheets_live_sync.json')
with open(cloud_path, 'r', encoding='utf-8') as f:
    cloud_data = json.load(f)

cloud_tanks = {t['TUID']: t for t in cloud_data.get('tanks', []) if 'TUID' in t}
print(f"Loaded {len(cloud_tanks)} tanks from Google Sheets backup.")

# Check T0056 in cloud
t56_cloud = cloud_tanks.get('T0056')
print(f"Cloud T0056 Status: {t56_cloud.get('Status') if t56_cloud else 'NOT FOUND'}")

# 2. Check local Tanks.tab
tanks_tab = os.path.join(labels_dir, 'FishNet Exported Data', 'Tanks.tab')
with open(tanks_tab, 'r', encoding='utf-8-sig', errors='ignore') as f:
    lines = f.readlines()

new_lines = []
updated_count = 0
for l in lines:
    parts = l.split('\t')
    tuid = parts[0].strip()
    if tuid in cloud_tanks:
        cloud_status = cloud_tanks[tuid].get('Status', '').strip()
        # column 13 is status in Tanks.tab
        if len(parts) > 13 and cloud_status:
            current_status = parts[13].strip()
            # If cloud says Euthanized and local says Adult/Active
            if cloud_status == 'Euthanized' and current_status in ('Adult/Active', 'Active'):
                print(f"Updating {tuid} from '{current_status}' to 'Euthanized' based on Google Sheets!")
                parts[13] = 'Euthanized'
                updated_count += 1
                l = '\t'.join(parts)
    new_lines.append(l)

print(f"Total tanks updated in Tanks.tab: {updated_count}")

# 3. Write back Tanks.tab
if updated_count > 0:
    with open(tanks_tab, 'w', encoding='utf-8', newline='') as f:
        f.writelines(new_lines)
    print("Successfully wrote updated FishNet Exported Data/Tanks.tab!")

# Also check FishNET.tab
fishnet_tab = os.path.join(labels_dir, 'FishNET.tab')
if os.path.exists(fishnet_tab):
    with open(fishnet_tab, 'r', encoding='utf-8-sig', errors='ignore') as f:
        f_lines = f.readlines()
    new_f_lines = []
    f_updated = 0
    for l in f_lines:
        parts = l.split('\t')
        # in FishNET.tab, TUID is usually col 20 (index 20) and status is col 16
        if len(parts) > 20:
            tuid = parts[20].strip()
            if tuid in cloud_tanks:
                cloud_status = cloud_tanks[tuid].get('Status', '').strip()
                if cloud_status == 'Euthanized' and 'Active' in parts[16]:
                    print(f"Updating {tuid} in FishNET.tab col 16 from '{parts[16]}' to 'Euthanized'")
                    parts[16] = 'Euthanized'
                    f_updated += 1
                    l = '\t'.join(parts)
        new_f_lines.append(l)
    if f_updated > 0:
        with open(fishnet_tab, 'w', encoding='utf-8', newline='') as f:
            f.writelines(new_f_lines)
        print(f"Successfully wrote updated FishNET.tab ({f_updated} tanks updated)!")

# Also FishNet Exported Data/FishNET.tab
fn_tab = os.path.join(labels_dir, 'FishNet Exported Data', 'FishNET.tab')
if os.path.exists(fn_tab):
    with open(fn_tab, 'r', encoding='utf-8-sig', errors='ignore') as f:
        fn_lines = f.readlines()
    new_fn_lines = []
    fn_updated = 0
    for l in fn_lines:
        parts = l.split('\t')
        # col 0 is TUID, last col (or col 13) is status
        if len(parts) > 13:
            tuid = parts[0].strip()
            if tuid in cloud_tanks:
                cloud_status = cloud_tanks[tuid].get('Status', '').strip()
                if cloud_status == 'Euthanized' and 'Active' in parts[13]:
                    print(f"Updating {tuid} in FishNet Exported Data/FishNET.tab col 13 from '{parts[13].strip()}' to 'Euthanized'")
                    parts[13] = 'Euthanized\n'
                    fn_updated += 1
                    l = '\t'.join(parts)
        new_fn_lines.append(l)
    if fn_updated > 0:
        with open(fn_tab, 'w', encoding='utf-8', newline='') as f:
            f.writelines(new_fn_lines)
        print(f"Successfully wrote updated FishNet Exported Data/FishNET.tab ({fn_updated} tanks updated)!")
