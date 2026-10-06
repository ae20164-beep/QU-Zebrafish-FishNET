import os

folder = 'FishNet Exported Data'

print("=== PARSING EXACT PROJECTS.TAB (FileMaker) ===")
with open(os.path.join(folder, 'Projects.tab'), 'r', encoding='utf-8-sig', errors='replace') as f:
    text = f.read()

lines = text.split('\r\n')
print(f"Total Projects rows: {len(lines)}")
for i, l in enumerate(lines):
    if l.strip():
        cols = l.split('\t')
        pnum = cols[3] if len(cols) > 3 else ''
        puid = cols[4] if len(cols) > 4 else ''
        st = cols[5] if len(cols) > 5 else ''
        pi = cols[6] if len(cols) > 6 else ''
        date_end = cols[0] if len(cols) > 0 else ''
        print(f"Row {i+1} [{len(cols)} cols]: PUID={puid} | DateEnd={date_end} | Status={st} | PI={pi} | Protocol={pnum}")

print("\n=== PARSING EXACT LABS.TAB (FileMaker) ===")
with open(os.path.join(folder, 'Labs.tab'), 'r', encoding='utf-8-sig', errors='replace') as f:
    text = f.read()

lines = text.split('\r\n')
print(f"Total Labs rows: {len(lines)}")
for i, l in enumerate(lines):
    if l.strip():
        cols = l.split('\t')
        college = cols[0] if len(cols) > 0 else ''
        lab_name = cols[1] if len(cols) > 1 else ''
        pi = cols[2] if len(cols) > 2 else ''
        date_end = cols[4] if len(cols) > 4 else ''
        p_name = cols[5] if len(cols) > 5 else ''
        p_num = cols[6] if len(cols) > 6 else ''
        print(f"Row {i+1} [{len(cols)} cols]: College={college} | Lab={lab_name} | PI={pi} | DateEnd={date_end} | Protocol={p_num}")
