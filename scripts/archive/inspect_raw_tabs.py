import os

folder = 'FishNet Exported Data'

with open(os.path.join(folder, 'Projects.tab'), 'rb') as f:
    raw_p = f.read()

# Let's inspect raw line endings and tab positions
tabs = raw_p.split(b'\t')
print(f"Projects.tab total tab-separated fields: {len(tabs)}")
for idx, t in enumerate(tabs[:30]):
    print(f"Field {idx+1}: {repr(t.decode('utf-8', errors='replace'))}")

print("\n" + "="*50 + "\n")

with open(os.path.join(folder, 'Labs.tab'), 'rb') as f:
    raw_l = f.read()

tabs_l = raw_l.split(b'\t')
print(f"Labs.tab total tab-separated fields: {len(tabs_l)}")
for idx, t in enumerate(tabs_l[:30]):
    print(f"Field {idx+1}: {repr(t.decode('utf-8', errors='replace'))}")
