import os
import re

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
EXPORT_DIR = os.path.join(ROOT_DIR, 'FishNet Exported Data')

print("=== Adding Graduated Tanks T0182 and T0183 from Cross C0072 (AB T128) ===")

# 1. Update Crosses.tab
crosses_path = os.path.join(EXPORT_DIR, 'Crosses.tab')
with open(crosses_path, 'r', encoding='utf-8') as f:
    c_lines = [l for l in f.read().split('\r\n') if l.strip()]

new_cross_row = "\t".join([
    "0", "0", "42", "42", "?", "100.00%", "", "C0072", "", "10-Aug-26", "10/08/2026", "T0128", "", "AB x AB", "1", "T0128", "QU-IACUC 006/2023-AMM5", "Ahmad", "Retired", "", "Wt (AB)", "AB T128", "Wt (AB)", "AB T128"
])

if not any("C0072" in l for l in c_lines):
    c_lines.append(new_cross_row)
    with open(crosses_path, 'w', encoding='utf-8', newline='') as f:
        f.write('\r\n'.join(c_lines) + '\r\n')
    print(f"[OK] Appended Cross C0072 to {crosses_path}")
else:
    print("[INFO] Cross C0072 already present in Crosses.tab")

# 2. Update Nursery.tab
nursery_path = os.path.join(EXPORT_DIR, 'Nursery.tab')
with open(nursery_path, 'r', encoding='utf-8') as f:
    n_lines = [l for l in f.read().split('\r\n') if l.strip()]

new_nursery_row = "\t".join([
    "N0068", "42", "Graduate to system", "", "C0072", "", "10/09/2026", "10-Aug-26", "10/08/2026", "T0128", "T0128", "QU-IACUC 006/2023-AMM5", "Ahmad", "", "Wt (AB)", "AB T128", "Wt (AB)", "AB T128"
])

if not any("N0068" in l for l in n_lines):
    n_lines.append(new_nursery_row)
    with open(nursery_path, 'w', encoding='utf-8', newline='') as f:
        f.write('\r\n'.join(n_lines) + '\r\n')
    print(f"[OK] Appended Nursery N0068 to {nursery_path}")
else:
    print("[INFO] Nursery N0068 already present in Nursery.tab")

# 3. Update Tanks.tab
tanks_path = os.path.join(EXPORT_DIR, 'Tanks.tab')
with open(tanks_path, 'r', encoding='utf-8') as f:
    t_lines = [l for l in f.read().split('\r\n') if l.strip()]

# Row 1: T0182 (30 fish)
row_t0182 = "\t".join([
    "10-08-26", "", "C0072", "Zebrafish", "30", "Wt (AB)", "Huseyin Cagatay Yalcin", "", "AB T128", "30", "QU-IACUC 006/2023-AMM5", "", "D126", "", "", "", "Adult/Active", "", "3.5L", "180", "T0182", "10-08-28", "Zebrafish facility"
])

# Row 2: T0183 (12 fish)
row_t0183 = "\t".join([
    "10-08-26", "", "C0072", "Zebrafish", "12", "Wt (AB)", "Huseyin Cagatay Yalcin", "", "AB T128", "12", "QU-IACUC 006/2023-AMM5", "", "D126", "", "", "", "Adult/Active", "", "3.5L", "180", "T0183", "10-08-28", "Zebrafish facility"
])

updated_tanks = False
if not any("T0182" in l for l in t_lines):
    t_lines.append(row_t0182)
    updated_tanks = True

if not any("T0183" in l for l in t_lines):
    t_lines.append(row_t0183)
    updated_tanks = True

import time

def safe_write_lines(file_path, lines):
    content = '\r\n'.join(lines) + '\r\n'
    for attempt in range(5):
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            return True
        except PermissionError:
            time.sleep(0.5)
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False
    # If standard write fails due to lock, try append mode or fallback
    try:
        with open(file_path, 'a', encoding='utf-8', newline='') as f:
            pass
    except Exception as e:
        print(f"Could not unlock {file_path}: {e}")
    return False

if updated_tanks:
    if safe_write_lines(tanks_path, t_lines):
        print(f"[OK] Appended Tanks T0182 (30 fish) and T0183 (12 fish) to {tanks_path}")
    else:
        print(f"[WARN] Retrying writing to {tanks_path}")
else:
    print("[INFO] Tanks T0182 and T0183 already present in Tanks.tab")

# 4. Also update root FishNET.tab
root_fishnet_path = os.path.join(ROOT_DIR, 'FishNET.tab')
if os.path.exists(root_fishnet_path):
    with open(root_fishnet_path, 'r', encoding='utf-8') as f:
        fn_lines = [l for l in f.read().split('\r\n') if l.strip()]
    if not any("T0182" in l for l in fn_lines):
        fn_lines.append(row_t0182)
    if not any("T0183" in l for l in fn_lines):
        fn_lines.append(row_t0183)
    safe_write_lines(root_fishnet_path, fn_lines)
    print(f"[OK] Appended Tanks to root {root_fishnet_path}")

print("=== Graduated Tanks Appended Successfully ===")
