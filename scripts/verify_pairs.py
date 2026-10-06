import json

with open('breeding_dashboard_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== Crosses involving T0049 ===')
for p in data['pair_synergies']:
    if 'T0049' in p['pair_key']:
        print(f"{p['pair_key']}: line={p['line']}, dam_line={p.get('dam_line')}, sire_line={p.get('sire_line')}, outcross={p.get('is_outcross')}")

print('\n=== Top pure AB crosses ===')
ab_pure = [p for p in data['pair_synergies'] if p['line'] == 'AB']
for p in ab_pure[:5]:
    print(f"{p['pair_key']}: line={p['line']}, spawns={p['spawns']}, avg_clutch={p['avg_clutch']}, avg_sr24={p['avg_sr24']}%")
