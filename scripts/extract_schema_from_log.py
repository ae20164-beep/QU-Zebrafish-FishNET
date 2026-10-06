import os
import re

recover_log = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Recover.log'

with open(recover_log, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Find all occurrences of field and table definitions
# Examples in FileMaker recover log:
# "Field ID 129: 'Field_Name' (Data type: Text, Table: 'Table_Name')"
field_matches = re.findall(r"Field\s+(?:ID\s+\d+:\s+)?'([^']+)'\s+.*?table\s+'([^']+)'", text, re.IGNORECASE)
tables = {}
for fname, tname in field_matches:
    if tname not in tables:
        tables[tname] = []
    if fname not in tables[tname]:
        tables[tname].append(fname)

print(f"Found {len(tables)} tables with fields:")
for tname, flist in tables.items():
    print(f"\n==========================================")
    print(f"Table: '{tname}' ({len(flist)} fields)")
    print(f"==========================================")
    for f in flist:
        print(f"  - {f}")

# Also search for table names specifically
all_tables = set(re.findall(r"Table\s+'([^']+)'", text, re.IGNORECASE))
print(f"\nAll Table Names mentioned: {all_tables}")
