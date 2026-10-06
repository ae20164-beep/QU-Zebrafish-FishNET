import csv
import os

labels_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels'
old_tab = os.path.join(labels_dir, 'FishNET.tab.bak')
new_tab = os.path.join(labels_dir, 'FishNET.tab')

old_dict = {}
headers_old = []
if os.path.exists(old_tab):
    with open(old_tab, 'r', encoding='utf-8-sig', errors='ignore') as f:
        reader = list(csv.reader(f, delimiter='\t'))
        if reader:
            headers_old = reader[0]
            for r in reader[1:]:
                if r and r[0].strip():
                    old_dict[r[0].strip().upper()] = r

new_dict = {}
headers_new = []
with open(new_tab, 'r', encoding='utf-8-sig', errors='ignore') as f:
    reader = list(csv.reader(f, delimiter='\t'))
    if reader:
        headers_new = reader[0]
        for r in reader[1:]:
            if r and r[0].strip():
                new_dict[r[0].strip().upper()] = r

print(f"Old tanks count: {len(old_dict)} | New tanks count: {len(new_dict)}")
print(f"Headers New: {headers_new}")

added = [k for k in new_dict if k not in old_dict]
removed = [k for k in old_dict if k not in new_dict]
print(f"\nNew tanks added ({len(added)}): {', '.join(added)}")
if removed:
    print(f"Tanks removed ({len(removed)}): {', '.join(removed)}")

modified = []
for k in new_dict:
    if k in old_dict:
        o = old_dict[k]
        n = new_dict[k]
        if o != n:
            diff_items = []
            for i in range(max(len(o), len(n))):
                ov = o[i].strip() if i < len(o) else ""
                nv = n[i].strip() if i < len(n) else ""
                hn = headers_new[i] if i < len(headers_new) else f"Col_{i}"
                if ov != nv:
                    diff_items.append(f"{hn}: '{ov}' -> '{nv}'")
            if diff_items:
                modified.append((k, diff_items))

print(f"\nModified tanks ({len(modified)}):")
for k, diffs in modified:
    print(f"  [{k}]: {', '.join(diffs)}")
