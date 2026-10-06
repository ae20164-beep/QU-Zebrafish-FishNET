import json
import re

print("Updating process_all_breeding.py for strict pair line accuracy...")

with open('process_all_breeding.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's inspect where pair_synergies lines are set
old_ps_line = "ps['line'] = ev['line'] if ev['line'] != 'Other' else (unique_tanks.get(dam, {}).get('line') or ev['line'])"

new_ps_line = """line_dam = unique_tanks.get(dam, {}).get('line', 'Other')
            line_sire = unique_tanks.get(sire, {}).get('line', 'Other')
            if line_dam == line_sire and line_dam in ['AB', 'Casper', 'Fli', 'Gata']:
                ps['line'] = line_dam
                ps['is_outcross'] = False
            elif line_dam in ['AB', 'Casper', 'Fli', 'Gata'] and line_sire in ['AB', 'Casper', 'Fli', 'Gata']:
                ps['line'] = f"Outcross ({line_dam} x {line_sire})"
                ps['is_outcross'] = True
            else:
                ps['line'] = ev['line'] if ev['line'] != 'Other' else (line_dam or line_sire or 'Other')
                ps['is_outcross'] = False
            ps['dam_line'] = line_dam
            ps['sire_line'] = line_sire"""

if old_ps_line in code:
    code = code.replace(old_ps_line, new_ps_line)
    print("Replaced pair_synergies line assignment.")

# Also update the pair_synergies dict initialization
old_init = "'tank_a': '', 'tank_b': '', 'dam': '', 'sire': '', 'line': '',"
new_init = "'tank_a': '', 'tank_b': '', 'dam': '', 'sire': '', 'line': '', 'dam_line': '', 'sire_line': '', 'is_outcross': False,"
if old_init in code:
    code = code.replace(old_init, new_init)

# In pair_rankings serialization:
old_rank = "'avg_sr24': round(ps['sr24_sum'] / ps['spawns'], 1) if ps['spawns'] > 0 else 0.0,"
new_rank = """'avg_sr24': round(ps['sr24_sum'] / ps['spawns'], 1) if ps['spawns'] > 0 else 0.0,
            'dam_line': ps.get('dam_line', ''),
            'sire_line': ps.get('sire_line', ''),
            'is_outcross': ps.get('is_outcross', False),"""
if old_rank in code and "'dam_line': ps.get('dam_line', '')" not in code:
    code = code.replace(old_rank, new_rank)

with open('process_all_breeding.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved process_all_breeding.py.")
