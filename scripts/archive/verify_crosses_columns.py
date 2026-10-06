import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
p = os.path.join(ROOT_DIR, 'FishNet Exported Data', 'Crosses.tab')

labels = [
    "# of dead 0HPF",
    "# of dead 24HPF",
    "# survived 0HPF",
    "# survived 24HPF",
    "0HPF SR",
    "24HPF SR",
    "Admin",
    "CUID",
    "Date Ended",
    "Date of Birth",
    "Date Started",
    "Maternal ID",
    "Mating Outcome",
    "Notes",
    "Number of Tanks",
    "Paternal ID",
    "Protocol",
    "Set up by",
    "Status",
    "Lab Members Cross::Lab Name",
    "Tanks_Maternal::Genotype",
    "Tanks_Maternal::Notes",
    "Tanks_Paternal::Genotype",
    "Tanks_Paternal::Notes"
]

print(f"=== Total Expected Crosses Columns: {len(labels)} ===")
for i, l in enumerate(labels):
    print(f"Col {i+1:02d}: {l}")

with open(p, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"\nTotal rows in Crosses.tab: {len(lines)}")
sample_row = lines[0].split('\t')
print(f"Sample row (Row 1) column count: {len(sample_row)}")
print("\n--- Column-by-Column Alignment Check (Row 1) ---")
for idx, (lbl, val) in enumerate(zip(labels, sample_row)):
    print(f"Col {idx+1:02d} | {lbl:<28} -> Value: '{val}'")

last_row = lines[-1].split('\t')
print("\n--- Last Row Alignment Check ---")
for idx, (lbl, val) in enumerate(zip(labels, last_row)):
    print(f"Col {idx+1:02d} | {lbl:<28} -> Value: '{val}'")
