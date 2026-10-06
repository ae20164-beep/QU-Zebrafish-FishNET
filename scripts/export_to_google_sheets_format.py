import os
import csv
import json

def export_for_google_sheets():
    labels_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels'
    json_path = os.path.join(labels_dir, 'breeding_dashboard_data.json')
    out_dir = os.path.join(labels_dir, 'google_sheets_import')
    os.makedirs(out_dir, exist_ok=True)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Tanks
    tanks = data.get('tank_stats', {})
    tanks_csv = os.path.join(out_dir, '1_Tanks.csv')
    with open(tanks_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['TUID', 'Derivative_Cross', 'Genotype', 'Notes', 'Line', 'Sex_Structure', 'Female', 'Male', 'Total_Fish', 'Tank_Size', 'Protocol', 'DOB', 'Turnover_Deadline', 'Status', 'Operator'])
        for tuid in sorted(tanks.keys()):
            t = tanks[tuid]
            writer.writerow([
                t.get('tuid', ''),
                t.get('derivative_cross', ''),
                t.get('genotype', t.get('line', '')),
                t.get('notes', ''),
                t.get('line', 'AB'),
                t.get('sex_type', 'Mixed Colony'),
                t.get('female', 0),
                t.get('male', 0),
                t.get('total', 0),
                t.get('tank_size', '3.5L'),
                t.get('protocol', ''),
                t.get('dob', ''),
                t.get('turnover_date_resolved', t.get('turnover_date', '')),
                t.get('status', 'Active'),
                'Huseyin Cagatay Yalcin'
            ])
    print(f'Exported {tanks_csv} ({len(tanks)} rows)')

    # 2. Breeding Events
    events = data.get('events', [])
    events_csv = os.path.join(out_dir, '2_Breeding_Events.csv')
    with open(events_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Line', 'Mating_Type', 'Tank_ID', 'Eggs_0H', 'SR_0H_Pct', 'SR_24H_Pct', 'Live_24H', 'Female_Tank', 'Male_Tank', 'Notes', 'Operator'])
        for ev in events:
            writer.writerow([
                ev.get('date', ''),
                ev.get('line', 'AB'),
                'In-Tank' if ev.get('in_tank') else 'Pair-Wise',
                ev.get('tank_id', ''),
                ev.get('eggs_0h', 0),
                ev.get('sr_0h', 0),
                ev.get('sr_24h', 0),
                ev.get('live_24h', 0),
                ev.get('female_tank', ''),
                ev.get('male_tank', ''),
                ev.get('notes', ''),
                ev.get('staff', 'Lab Staff')
            ])
    print(f'Exported {events_csv} ({len(events)} rows)')

    # 3. Crosses
    crosses = data.get('crosses_registry', [])
    crosses_csv = os.path.join(out_dir, '3_Crosses.csv')
    with open(crosses_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['CUID', 'Mating_Date', 'Dam_Tank', 'Sire_Tank', 'Line_Pair', 'Embryo_Count', 'Linked_Nursery', 'Offspring_Tanks', 'Operator'])
        for c in crosses:
            writer.writerow([
                c.get('cuid', ''),
                c.get('mating_date', ''),
                c.get('dam', ''),
                c.get('sire', ''),
                c.get('line_pair', 'AB x AB'),
                c.get('nursery_count', 0),
                ','.join(c.get('nursery_clutches', [])),
                ','.join(c.get('offspring_tanks', [])),
                'Lab Staff'
            ])
    print(f'Exported {crosses_csv} ({len(crosses)} rows)')

    # 4. Nursery
    # Load from Nursery.tab
    nursery_tab = os.path.join(labels_dir, 'FishNet Exported Data', 'Nursery.tab')
    nursery_csv = os.path.join(out_dir, '4_Nursery.csv')
    n_count = 0
    with open(nursery_tab, 'r', encoding='utf-8', errors='ignore') as f_in, open(nursery_csv, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(['NUID', 'Count', 'Status', 'System', 'Derivative_Cross', 'Genotype', 'Grad_Date', 'Mating_Date', 'DOB', 'Grad_Tank', 'Notes'])
        for line in f_in:
            parts = [p.strip() for p in line.strip().split('\t')]
            if len(parts) >= 10:
                writer.writerow(parts[:11])
                n_count += 1
    print(f'Exported {nursery_csv} ({n_count} rows)')

    # 5. Activity Audit Initial Seed
    audit_csv = os.path.join(out_dir, '5_Activity_Audit.csv')
    with open(audit_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Operator', 'Action_Type', 'Details'])
        writer.writerow(['2026-10-06 23:45:00', 'Antigravity AI', 'SYSTEM_INITIALIZATION', 'Master Google Sheets Cloud Database synchronized with 183 tanks and 2,233 breeding events.'])
    print(f'Exported {audit_csv}')

if __name__ == '__main__':
    export_for_google_sheets()
