import os
import re

recover_log = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Recover.log'

with open(recover_log, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

tables = {}
current_table = None

for line in lines:
    m_tab = re.search(r"Recovering fields for table '([^']+)'", line)
    if m_tab:
        current_table = m_tab.group(1)
        if current_table not in tables:
            tables[current_table] = []
        continue
    
    if current_table and 'Recovering: field' in line:
        m_f = re.search(r"Recovering: field '([^']+)'", line)
        if m_f:
            f_name = m_f.group(1)
            if f_name not in tables[current_table]:
                tables[current_table].append(f_name)

print("Extracted Tables & Exact FileMaker Field Names:")
for t in ['Fish Crosses', 'Tanks', 'Nursery', 'Fish Lines', 'Facilities']:
    if t in tables:
        print(f"\n========================================")
        print(f"Table: '{t}' ({len(tables[t])} fields)")
        print(f"========================================")
        for f in tables[t]:
            print(f'  - "{f}"')
