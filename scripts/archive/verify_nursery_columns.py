import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
p = os.path.join(ROOT_DIR, 'FishNet Exported Data', 'Nursery.tab')

labels = [
    "NUID",
    "Number of Fish",
    "Status",
    "Fish Crosses::Admin",
    "Fish Crosses::CUID",
    "Fish Crosses::Date Ended",
    "Fish Crosses::Date for transfer",
    "Fish Crosses::Date of Birth",
    "Fish Crosses::Date Started",
    "Fish Crosses::Maternal ID",
    "Fish Crosses::Paternal ID",
    "Fish Crosses::Protocol",
    "Fish Crosses::Set up by",
    "Lab Members Cross::Lab Name",
    "Tanks_Maternal::Genotype",
    "Tanks_Maternal::Notes",
    "Tanks_Paternal::Genotype",
    "Tanks_Paternal::Notes"
]

print(f"=== Total Expected Nursery Columns: {len(labels)} ===")
for i, l in enumerate(labels):
    print(f"Col {i+1:02d}: {l}")

with open(p, 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"\nTotal rows in Nursery.tab: {len(lines)}")
sample_row = lines[0].split('\t')
print(f"Sample row (Row 1) column count: {len(sample_row)}")
print("\n--- Column-by-Column Alignment Check (Row 1) ---")
for idx, (lbl, val) in enumerate(zip(labels, sample_row)):
    print(f"Col {idx+1:02d} | {lbl:<32} -> Value: '{val}'")

last_row = lines[-1].split('\t')
print("\n--- Last Row Alignment Check ---")
for idx, (lbl, val) in enumerate(zip(labels, last_row)):
    print(f"Col {idx+1:02d} | {lbl:<32} -> Value: '{val}'")
