import json

with open('breeding_dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

meta = d['metadata']
print('Metadata:')
for k, v in meta.items():
    print(f'  {k}: {v}')

print('\nNewly added tanks check:')
for tuid in ['T0177', 'T0178', 'T0179', 'T0180', 'T0181']:
    if tuid in d['tank_stats']:
        t = d['tank_stats'][tuid]
        print(f"  {tuid}: {t['line']} | {t['sex_type']} | F:{t['female']}/M:{t['male']} (Tot:{t['total']}) | DOB:{t['dob']} | Status:{t['status']}")
