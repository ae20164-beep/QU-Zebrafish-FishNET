import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
p = os.path.join(ROOT_DIR, 'FishNet Exported Data', 'Tanks.tab')
with open(p, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

labels = [
    "Date of Birth",
    "Date of Death",
    "Dervitive Cross",
    "Facility",
    "Females",
    "Genotype",
    "Lab Member",
    "Males",
    "Notes",
    "Number of Fish",
    "Protocol",
    "Rack Number",
    "Room",
    "Row Letter",
    "Search",
    "Space Number",
    "Status",
    "Subspace Number",
    "Tank Size",
    "tankCount",
    "TUID",
    "Turnover Date",
    "Laboratories::Lab Name"
]

print(f"=== Total Expected Columns: {len(labels)} ===")
for i, l in enumerate(labels):
    print(f"Col {i+1:02d}: {l}")

print(f"\nTotal rows in Tanks.tab: {len(lines)}")
sample_row = lines[0].split('\t')
print(f"Sample row (Row 1) column count: {len(sample_row)}")
print("\n--- Column-by-Column Alignment Check ---")
for idx, (lbl, val) in enumerate(zip(labels, sample_row)):
    print(f"Col {idx+1:02d} | {lbl:<22} -> Value: '{val}'")

last_row = lines[-1].split('\t')
print("\n--- Last Row (T0183) Alignment Check ---")
for idx, (lbl, val) in enumerate(zip(labels, last_row)):
    print(f"Col {idx+1:02d} | {lbl:<22} -> Value: '{val}'")
