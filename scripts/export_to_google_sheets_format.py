import os
import csv
import json
import re

def clean_fishline_no_tanks(raw):
    if not raw:
        return 'AB'
    s = str(raw).strip()
    s = re.sub(r'\bA13\b', 'AB', s, flags=re.I)
    s = re.sub(r'\bA1B\b', 'AB', s, flags=re.I)
    s = re.sub(r'\bGli\b', 'Fli', s, flags=re.I)
    s = re.sub(r'\bGaba\b', 'Gata', s, flags=re.I)
    s = re.sub(r'\bGatat\b', 'Gata', s, flags=re.I)
    s = re.sub(r'\bART\b', 'AB', s, flags=re.I)
    s = re.sub(r'\(?\bIn[\-\s_]*Tank\b\)?', '', s, flags=re.I)
    s = re.sub(r'\(\s*\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\s*\)', '', s)
    s = re.sub(r'\b\d{1,2}/\d{1,2}\b', '', s)
    s = re.sub(r'F2\+', 'F2', s, flags=re.I)
    s = re.sub(r'(?<!\()\+(?!ve\))', ' x ', s, flags=re.I)
    s = re.sub(r'\b(?:Tank|T|T\.|T\-)\s*0*([0-9]{1,4})\b', '', s, flags=re.I)
    s = re.sub(r'\b(AB|Fli|Gata|Casper|Casp|Cas)T?\s*0*([0-9]{1,4})\b', r'\1', s, flags=re.I)
    s = re.sub(r'\b\d{1,4}\b', '', s)
    s = re.sub(r'\b(?:Casp|Cas)\b', 'Casper', s, flags=re.I)
    s = re.sub(r'[\.,/_]+', ' ', s)
    s = re.sub(r'\b(?:vs|x)\b', ' x ', s, flags=re.I)
    s = re.sub(r'\bxAB\b', 'x AB', s, flags=re.I)
    s = re.sub(r'\(\s*\)', '', s)
    s = re.sub(r'\(\s*([FfMm])\s*\)', r'(\1)', s)
    s = re.sub(r'\(([FfMm])\)\s+(?!(?:x|vs)\b)([A-Za-z]+)', r'(\1) x \2', s, flags=re.I)
    s = re.sub(r'\bfrom\b', '', s, flags=re.I)
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\s*x\s+x\s*', ' x ', s, flags=re.I)
    s = re.sub(r'^\s*x\s*', '', s, flags=re.I)
    s = re.sub(r'\s*x\s*$', '', s, flags=re.I)
    s = re.sub(r'^(AB|Casper|Fli|Gata)\s*(\([FfMm]\))\s*x\s*(\([FfMm]\))$', r'\1 \2 x \1 \3', s, flags=re.I)
    s = re.sub(r'^AB\s*x\s*AB$', 'AB', s, flags=re.I)
    s = re.sub(r'\s+', ' ', s).strip()
    if not s or s.lower() in ['x', 'xx', 'tank', 'from']:
        return 'AB'
    return s

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

    # 2. Breeding Events (13 Columns as requested)
    events = data.get('events', [])
    events_csv = os.path.join(out_dir, '2_Breeding_Events.csv')
    with open(events_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Event_ID',
            'Date',
            'Fishline_Raw',
            'Line',
            'Mating_Type',
            'Tank_ID',
            'Eggs_0H',
            'SR_0H_Pct',
            'Live_0H',
            'SR_24H_Pct',
            'Live_24H',
            'Female_Tank',
            'Male_Tank'
        ])
        for ev in events:
            # Dual tank assignment: if cross, write specific tanks; if same tank, write same tank for both M and F
            f_tank = ev.get('female_tank') or ''
            m_tank = ev.get('male_tank') or ''
            if not f_tank and not m_tank:
                tanks = ev.get('tanks', [])
                if tanks:
                    f_tank = tanks[0]
                    m_tank = tanks[0]
            elif f_tank and not m_tank:
                m_tank = f_tank
            elif m_tank and not f_tank:
                f_tank = m_tank

            writer.writerow([
                ev.get('event_id', ''),
                ev.get('date', ''),
                clean_fishline_no_tanks(ev.get('fishline', '')),
                ev.get('line', 'AB'),
                'In-Tank' if ev.get('in_tank') else 'Pair-Wise',
                ev.get('fishline', ''),
                ev.get('eggs_0h', 0),
                ev.get('sr_0h', 0),
                ev.get('live_0h', 0),
                ev.get('sr_24h', 0),
                ev.get('live_24h', 0),
                f_tank,
                m_tank
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
        writer.writerow(['2026-10-06 23:45:00', 'Antigravity AI', 'SYSTEM_INITIALIZATION', f'Master Google Sheets Cloud Database synchronized with {len(tanks)} tanks and {len(events)} breeding events.'])
    print(f'Exported {audit_csv}')

if __name__ == '__main__':
    export_for_google_sheets()
