import os
import csv
import json
import re
from datetime import datetime
from collections import defaultdict, Counter
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Reference date (Current date: Oct 1, 2026)
NOW = datetime(2026, 10, 1)

TAB_FILE = 'FishNET.tab'
EXCEL_REPORT_FILE = 'FishNET_Colony_Analytics_Report.xlsx'
HTML_DASHBOARD_FILE = 'FishNET_Interactive_Dashboard_Standard_Backup.html'


def parse_date(d_str):
    if not d_str or not isinstance(d_str, str):
        return None
    d_str = d_str.strip()
    for fmt in ['%d-%b-%y', '%d-%m-%y', '%d/%m/%y', '%Y-%m-%d', '%d-%b-%Y', '%d-%m-%Y']:
        try:
            return datetime.strptime(d_str, fmt)
        except ValueError:
            pass
    return None

def parse_volume(vol_str):
    if not vol_str:
        return 0.0
    m = re.search(r'([\d\.]+)', str(vol_str))
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return 0.0

def categorize_line(notes):
    """
    Categorizes notes strictly into the 4 primary lines: AB, Casper, Fli, Gata (or Other)
    """
    if not notes:
        return 'Other'
    n = notes.lower().strip()
    if 'casper' in n or 'cas/' in n or 'cas' in n.split():
        return 'Casper'
    elif 'fli' in n:
        return 'Fli'
    elif 'gata' in n:
        return 'Gata'
    elif 'ab' in n or 'wt' in n or 'wild' in n:
        return 'AB'
    return 'Other'

def is_active_status(status_str):
    if not status_str:
        return True
    s = status_str.lower().strip()
    if 'euth' in s or 'dead' in s or 'arch' in s or 'cull' in s:
        return False
    return True

TANK_COLS = [
    'Date of Birth', 'Date of Death', 'Dervitive Cross', 'Facility',
    'Females', 'Genotype', 'Lab Member', 'Males', 'Notes',
    'Number of Fish', 'Protocol', 'Rack Number', 'Room',
    'Row Letter', 'Search', 'Space Number', 'Status',
    'Subspace Number', 'Tank Size', 'tankCount', 'TUID',
    'Turnover Date', 'Laboratories::Lab Name'
]

# 1. Load Data
with open(TAB_FILE, 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.reader(f, delimiter='\t')
    raw_rows = list(reader)

records = []
has_header = False
if raw_rows and ('TUID' in raw_rows[0] or 'Date of Birth' in raw_rows[0]):
    has_header = True
    header = [h.strip().replace('\ufeff', '') for h in raw_rows[0]]
    data_rows = raw_rows[1:]
else:
    header = TANK_COLS
    data_rows = raw_rows

for r in data_rows:
    if not any(r): continue
    row_dict = {}
    for i, col in enumerate(header):
        row_dict[col] = r[i].strip() if i < len(r) else ''
    if row_dict.get('TUID'):
        records.append(row_dict)

tanks_dict = {r['TUID']: r for r in records}

# 2. Enrich Records
parents_map = {}
children_map = defaultdict(list)

for r in records:
    tuid = r['TUID']
    pat = r.get('PATERNAL', '').strip()
    mat = r.get('MATERNAL', '').strip()
    p_valid = pat if pat in tanks_dict else None
    m_valid = mat if mat in tanks_dict else None
    parents_map[tuid] = (p_valid, m_valid)
    if p_valid:
        children_map[p_valid].append(tuid)
    if m_valid and m_valid != p_valid:
        children_map[m_valid].append(tuid)

# Generation Depth & Ancestors
gen_depth = {}
def calc_depth(t):
    if t in gen_depth:
        return gen_depth[t]
    p, m = parents_map.get(t, (None, None))
    if not p and not m:
        gen_depth[t] = 0
        return 0
    dp = calc_depth(p) if p else 0
    dm = calc_depth(m) if m else 0
    gen_depth[t] = 1 + max(dp, dm)
    return gen_depth[t]

for t in tanks_dict:
    calc_depth(t)

# Kinship Matrix & Inbreeding (Tabular Method)
all_ids = sorted(list(tanks_dict.keys()), key=lambda x: (gen_depth[x], x))
A = defaultdict(lambda: defaultdict(float))

for i in all_ids:
    si, di = parents_map.get(i, (None, None))
    if si and di:
        A[i][i] = 1.0 + 0.5 * A[si][di]
    else:
        A[i][i] = 1.0
    for j in all_ids:
        if i == j:
            continue
        sj, dj = parents_map.get(j, (None, None))
        if sj and dj:
            val = 0.5 * (A[i][sj] + A[i][dj])
        elif sj:
            val = 0.5 * A[i][sj]
        elif dj:
            val = 0.5 * A[i][dj]
        else:
            val = 0.0
        A[i][j] = val
        A[j][i] = val

inbreeding_coeffs = {}
for i in all_ids:
    si, di = parents_map.get(i, (None, None))
    if si and di:
        inbreeding_coeffs[i] = round(0.5 * A[si][di], 4)
    else:
        inbreeding_coeffs[i] = 0.0

# Process calculations
for r in records:
    tuid = r['TUID']
    st_raw = r.get('STATUS', '')
    is_active = is_active_status(st_raw)
    r['Is_Active'] = is_active
    r['Status_Clean'] = 'Adult/Active' if is_active and 'juvenile' not in st_raw.lower() else ('Juvenile (<3m)' if is_active else 'Euthanized')
    
    r['Line_Category'] = categorize_line(r.get('NOTES', ''))
    r['Gen_Depth'] = gen_depth[tuid]
    r['Inbreeding_F'] = inbreeding_coeffs[tuid]
    r['Sire'] = parents_map[tuid][0] or ''
    r['Dam'] = parents_map[tuid][1] or ''
    r['Progeny_Count'] = len(children_map[tuid])
    r['Progeny_Tanks'] = ', '.join(children_map[tuid])
    
    # Counts
    r['Female_Count'] = int(r['FEMALE']) if r.get('FEMALE', '').isdigit() else 0
    r['Male_Count'] = int(r['MALE']) if r.get('MALE', '').isdigit() else 0
    r['Total_Count'] = int(r['TOTAL']) if r.get('TOTAL', '').isdigit() else 0
    r['Unsexed_Count'] = max(0, r['Total_Count'] - (r['Female_Count'] + r['Male_Count']))
    
    # Dates & Age
    dob = parse_date(r.get('DOB', ''))
    turnover = parse_date(r.get('TURNOVER', ''))
    dod = parse_date(r.get('DOD', ''))
    r['DOB_parsed'] = dob
    r['TURNOVER_parsed'] = turnover
    r['DOD_parsed'] = dod
    
    if dob:
        ref_end = dod if (dod and not is_active) else NOW
        age_days = (ref_end - dob).days
        r['Age_Days'] = age_days
        r['Age_Months'] = round(age_days / 30.4375, 1)
        r['Age_Years'] = round(age_days / 365.25, 2)
    else:
        r['Age_Days'] = None
        r['Age_Months'] = None
        r['Age_Years'] = None
        
    # Age Category
    if not is_active:
        r['Lifecycle_Stage'] = 'Euthanized / Archived'
    elif r['Age_Months'] is not None:
        if r['Age_Months'] < 3:
            r['Lifecycle_Stage'] = 'Juvenile / Nursery (<3m)'
        elif r['Age_Months'] <= 6:
            r['Lifecycle_Stage'] = 'Young Adult (3-6m)'
        elif r['Age_Months'] <= 12:
            r['Lifecycle_Stage'] = 'Prime Breeding (6-12m)'
        elif r['Age_Months'] <= 18:
            r['Lifecycle_Stage'] = 'Mature Stock (12-18m)'
        else:
            r['Lifecycle_Stage'] = 'Geriatric / Overdue (>18m)'
    else:
        r['Lifecycle_Stage'] = 'Active (Unknown Age)'
        
    # Turnover status
    if turnover and is_active:
        days_left = (turnover - NOW).days
        r['Days_To_Turnover'] = days_left
        if days_left < 0:
            r['Turnover_Urgency'] = 'OVERDUE'
            r['Turnover_Action'] = f'CRITICAL: {abs(days_left)} days past turnover. Immediate renewal cross or euthanasia required.'
        elif days_left <= 30:
            r['Turnover_Urgency'] = 'DUE SOON (<=30d)'
            r['Turnover_Action'] = f'HIGH: Turnover in {days_left} days. Setup renewal breeding tank now.'
        elif days_left <= 60:
            r['Turnover_Urgency'] = 'UPCOMING (31-60d)'
            r['Turnover_Action'] = f'MEDIUM: Turnover in {days_left} days. Schedule next generation cross.'
        elif days_left <= 90:
            r['Turnover_Urgency'] = 'UPCOMING (61-90d)'
            r['Turnover_Action'] = f'LOW: Turnover in {days_left} days. Monitor stock health.'
        else:
            r['Turnover_Urgency'] = 'FUTURE (>90d)'
            r['Turnover_Action'] = 'Normal active holding.'
    else:
        r['Days_To_Turnover'] = None
        r['Turnover_Urgency'] = 'N/A'
        r['Turnover_Action'] = 'Inactive or No turnover date set.'
        
    # Density & Volume
    tank_val = r.get('TANK', '') or r.get('TANK ', '')
    vol = parse_volume(tank_val)
    r['Volume_L'] = vol
    r['Tank_Display'] = tank_val
    if vol > 0 and r['Total_Count'] > 0:
        dens = round(r['Total_Count'] / vol, 2)
        r['Fish_Per_Liter'] = dens
        if dens < 1.0:
            r['Density_Status'] = 'Understocked (<1.0 fish/L)'
        elif dens <= 6.0:
            r['Density_Status'] = 'Optimal (1.0 - 6.0 fish/L)'
        elif dens <= 8.0:
            r['Density_Status'] = 'Moderate / Acceptable (6.1 - 8.0 fish/L)'
        else:
            r['Density_Status'] = 'OVERSTOCKED (>8.0 fish/L - Welfare Alert)'
    else:
        r['Fish_Per_Liter'] = 0.0
        r['Density_Status'] = 'Empty / Unknown'

# Cross Aggregations
cross_records = defaultdict(list)
for r in records:
    c_id = r.get('Derivative cross', '')
    if c_id:
        cross_records[c_id].append(r)

cross_stats = []
for c_id, clist in sorted(cross_records.items()):
    c_active_fish = sum(r['Total_Count'] for r in clist if r['Is_Active'])
    c_total_fish = sum(r['Total_Count'] for r in clist)
    c_females = sum(r['Female_Count'] for r in clist if r['Is_Active'])
    c_males = sum(r['Male_Count'] for r in clist if r['Is_Active'])
    dobs = [r.get('DOB', '') for r in clist if r.get('DOB', '')]
    first_dob = dobs[0] if dobs else ''
    parents_set = set((r.get('PATERNAL', ''), r.get('MATERNAL', '')) for r in clist)
    p_str = '; '.join([f'{p} x {m}' for p, m in parents_set if p or m])
    lines_set = set(r['Line_Category'] for r in clist)
    
    cross_stats.append({
        'Cross_ID': c_id,
        'Parental_Cross': p_str,
        'Lines': ', '.join(lines_set),
        'DOB': first_dob,
        'Tanks_Count': len(clist),
        'Active_Tanks': len([r for r in clist if r['Is_Active']]),
        'Total_Fish_Yield': c_total_fish,
        'Active_Fish': c_active_fish,
        'Active_Females': c_females,
        'Active_Males': c_males,
        'Avg_Fish_Per_Tank': round(c_total_fish / len(clist), 1) if clist else 0,
        'Tank_List': ', '.join(r['TUID'] for r in clist)
    })

# 4 Primary Lines Aggregations (AB, Casper, Fli, Gata)
target_lines = ['AB', 'Casper', 'Fli', 'Gata']
line_groups = defaultdict(list)
for r in records:
    line_groups[r['Line_Category']].append(r)

# Ensure all 4 lines exist in stats
line_stats = []
for l_name in target_lines + [l for l in line_groups if l not in target_lines]:
    l_list = line_groups[l_name]
    l_active = [r for r in l_list if r['Is_Active']]
    l_euth = [r for r in l_list if not r['Is_Active']]
    act_fish = sum(r['Total_Count'] for r in l_active)
    act_f = sum(r['Female_Count'] for r in l_active)
    act_m = sum(r['Male_Count'] for r in l_active)
    ages = [r['Age_Months'] for r in l_active if r['Age_Months'] is not None]
    avg_age = round(sum(ages)/len(ages), 1) if ages else 0
    inbreds = [r['Inbreeding_F'] for r in l_active]
    avg_f = round(sum(inbreds)/len(inbreds), 3) if inbreds else 0.0
    
    risk = 'Low'
    reasons = []
    if len(l_active) == 0:
        risk = 'Extinct / Inactive'
        reasons.append('No active tanks in facility')
    elif len(l_active) == 1:
        risk = 'CRITICAL (Single Tank)'
        reasons.append('Only 1 active holding tank')
    elif act_fish < 10:
        risk = 'HIGH (Low Biomass)'
        reasons.append(f'Only {act_fish} total fish remaining')
    
    if len(l_active) > 0:
        if act_f == 0 and act_m > 0:
            risk = 'CRITICAL (No Females)'
            reasons.append('Zero breeding females available')
        elif act_m == 0 and act_f > 0:
            risk = 'HIGH (No Males)'
            reasons.append('Zero breeding males available')
        if avg_age > 16:
            reasons.append('Colony is aging (>16m avg age)')
            if risk == 'Low':
                risk = 'MEDIUM (Aging Stock)'
                
    line_stats.append({
        'Line': l_name,
        'Active_Tanks': len(l_active),
        'Euthanized_Tanks': len(l_euth),
        'Total_Active_Fish': act_fish,
        'Active_Females': act_f,
        'Active_Males': act_m,
        'Sex_Ratio': f'{round(act_f/act_m, 2)}:1' if act_m > 0 else f'{act_f}:0',
        'Avg_Age_Months': avg_age,
        'Avg_Inbreeding_F': avg_f,
        'Risk_Level': risk,
        'Risk_Reasons': '; '.join(reasons) if reasons else 'Healthy colony size and demographics'
    })

# Risk & Bottleneck Alerts
alerts = []
for r in records:
    if not r['Is_Active']:
        continue
    if r['Turnover_Urgency'] == 'OVERDUE':
        alerts.append({
            'TUID': r['TUID'],
            'Line': r['Line_Category'],
            'Category': 'Turnover Overdue',
            'Severity': 'CRITICAL',
            'Description': f'Tank is {abs(r["Days_To_Turnover"])} days past standard 540-day turnover (DOB: {r.get("DOB", "")}).',
            'Action': 'Cross immediately with younger stock or evaluate for colony retirement.'
        })
    elif r['Turnover_Urgency'] == 'DUE SOON (<=30d)':
        alerts.append({
            'TUID': r['TUID'],
            'Line': r['Line_Category'],
            'Category': 'Turnover Due Soon',
            'Severity': 'HIGH',
            'Description': f'Reaches 540-day turnover in {r["Days_To_Turnover"]} days (DOB: {r.get("DOB", "")}).',
            'Action': 'Set up pairing crosses in the breeding room this week.'
        })
    if 'OVERSTOCKED' in r['Density_Status']:
        alerts.append({
            'TUID': r['TUID'],
            'Line': r['Line_Category'],
            'Category': 'Animal Welfare (Density)',
            'Severity': 'HIGH',
            'Description': f'High stocking density: {r["Fish_Per_Liter"]} fish/L in a {r["Volume_L"]}L tank ({r["Total_Count"]} fish).',
            'Action': 'Split stock into two tanks to maintain 4-6 fish/L welfare guidelines.'
        })
    if r['Total_Count'] > 0 and r['Age_Months'] and r['Age_Months'] >= 4:
        if r['Female_Count'] == 0 and r['Male_Count'] > 0:
            alerts.append({
                'TUID': r['TUID'],
                'Line': r['Line_Category'],
                'Category': 'Single-Sex Tank (All Males)',
                'Severity': 'MEDIUM',
                'Description': f'Tank contains only {r["Male_Count"]} males (0 females).',
                'Action': 'Identify compatible female tank for future crosses.'
            })
        elif r['Male_Count'] == 0 and r['Female_Count'] > 0:
            alerts.append({
                'TUID': r['TUID'],
                'Line': r['Line_Category'],
                'Category': 'Single-Sex Tank (All Females)',
                'Severity': 'MEDIUM',
                'Description': f'Tank contains only {r["Female_Count"]} females (0 males).',
                'Action': 'Identify compatible male tank for future crosses.'
            })

print(f'Total alerts: {len(alerts)}')

# 6. Generate Excel Report
wb = openpyxl.Workbook()

navy_fill = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')
soft_blue = PatternFill(start_color='E2E8F0', end_color='E2E8F0', fill_type='solid')
red_fill = PatternFill(start_color='FEE2E2', end_color='FEE2E2', fill_type='solid')
orange_fill = PatternFill(start_color='FFEDD5', end_color='FFEDD5', fill_type='solid')
green_fill = PatternFill(start_color='DCFCE7', end_color='DCFCE7', fill_type='solid')

white_bold = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
title_font = Font(name='Segoe UI', size=16, bold=True, color='0F172A')
subtitle_font = Font(name='Segoe UI', size=10, italic=True, color='64748B')
bold_font = Font(name='Segoe UI', size=11, bold=True, color='0F172A')
regular_font = Font(name='Segoe UI', size=10, color='1E293B')

thin_border = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)

align_center = Alignment(horizontal='center', vertical='center')
align_left = Alignment(horizontal='left', vertical='center')
align_right = Alignment(horizontal='right', vertical='center')

# TAB 1: Executive Summary
ws1 = wb.active
ws1.title = '1_Executive_Summary'
ws1.views.sheetView[0].showGridLines = True

ws1['A1'] = 'FishNET Zebrafish Colony Analytics & Pedigree Report'
ws1['A1'].font = title_font
ws1['A2'] = f'Report Date: {NOW.strftime("%B %d, %Y")} | Lines Analyzed: AB, Casper, Fli, Gata | Status: Active vs Euthanized'
ws1['A2'].font = subtitle_font

kpis = [
    ('Total Recorded Tanks', len(records), 'A4', 'B5'),
    ('Active Holding Tanks', len([r for r in records if r['Is_Active']]), 'C4', 'D5'),
    ('Total Active Fish', sum(r['Total_Count'] for r in records if r['Is_Active']), 'E4', 'F5'),
    ('Active Breeding Females', sum(r['Female_Count'] for r in records if r['Is_Active']), 'G4', 'H5'),
    ('Active Breeding Males', sum(r['Male_Count'] for r in records if r['Is_Active']), 'I4', 'J5'),
    ('Overdue Turnover Tanks', len([r for r in records if r['Turnover_Urgency'] == 'OVERDUE']), 'K4', 'L5'),
]

for title, val, top_l, bot_r in kpis:
    ws1.merge_cells(f'{top_l}:{bot_r}')
    c = ws1[top_l]
    c.value = f'{title}\n{val}'
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    c.fill = soft_blue
    c.font = Font(name='Segoe UI', size=12, bold=True, color='0F172A')
    for row in ws1[f'{top_l}:{bot_r}']:
        for cell in row:
            cell.border = thin_border

# Section: 4 Primary Lines
ws1['A7'] = 'Primary Genetic Lines Summary (AB, Casper, Fli, Gata)'
ws1['A7'].font = bold_font
ws1['A7'].fill = soft_blue

headers_lines_top = ['Primary Line', 'Active Tanks', 'Euthanized Tanks', 'Active Fish', 'Females', 'Males', 'Sex Ratio (F:M)', 'Avg Age (m)', 'Avg Inbreeding (F)', 'Colony Status']
for col_idx, h in enumerate(headers_lines_top, 1):
    c = ws1.cell(row=8, column=col_idx, value=h)
    c.font = white_bold
    c.fill = navy_fill
    c.alignment = align_center

curr_row = 9
for ls in line_stats:
    ws1.cell(row=curr_row, column=1, value=ls['Line']).alignment = align_left
    ws1.cell(row=curr_row, column=2, value=ls['Active_Tanks']).alignment = align_center
    ws1.cell(row=curr_row, column=3, value=ls['Euthanized_Tanks']).alignment = align_center
    ws1.cell(row=curr_row, column=4, value=ls['Total_Active_Fish']).alignment = align_center
    ws1.cell(row=curr_row, column=5, value=ls['Active_Females']).alignment = align_center
    ws1.cell(row=curr_row, column=6, value=ls['Active_Males']).alignment = align_center
    ws1.cell(row=curr_row, column=7, value=ls['Sex_Ratio']).alignment = align_center
    ws1.cell(row=curr_row, column=8, value=ls['Avg_Age_Months']).alignment = align_center
    ws1.cell(row=curr_row, column=9, value=ls['Avg_Inbreeding_F']).alignment = align_center
    ws1.cell(row=curr_row, column=10, value=ls['Risk_Level']).alignment = align_center
    for c_i in range(1, 11):
        cell = ws1.cell(row=curr_row, column=c_i)
        cell.font = regular_font
        cell.border = thin_border
        if 'CRITICAL' in ls['Risk_Level']:
            cell.fill = red_fill
        elif 'HIGH' in ls['Risk_Level'] or 'MEDIUM' in ls['Risk_Level']:
            cell.fill = orange_fill
        else:
            cell.fill = green_fill
    curr_row += 1

# Section: Age Breakdown
curr_row += 2
ws1.cell(row=curr_row, column=1, value='Colony Age Structure & Life-Cycle Distribution').font = bold_font
curr_row += 1

age_headers = ['Lifecycle Stage', 'Active Tanks', 'Total Fish', 'Percentage of Colony', 'Actionable Guidance']
for col_idx, h in enumerate(age_headers, 1):
    c = ws1.cell(row=curr_row, column=col_idx, value=h)
    c.font = white_bold
    c.fill = navy_fill
    c.alignment = align_center

active_tanks_all = [r for r in records if r['Is_Active']]
stage_groups = defaultdict(list)
for r in active_tanks_all:
    stage_groups[r['Lifecycle_Stage']].append(r)

stage_order = [
    ('Juvenile / Nursery (<3m)', 'Growing stock. Sexing and genotyping required at 3 months.'),
    ('Young Adult (3-6m)', 'Reaching sexual maturity. Ready for initial pairing tests.'),
    ('Prime Breeding (6-12m)', 'Optimal fecundity and clutch yields. Prime breeding candidates.'),
    ('Mature Stock (12-18m)', 'Approaching turnover. Plan replacement clutches immediately.'),
    ('Geriatric / Overdue (>18m)', 'Exceeded 540-day turnover. Euthanize or renew urgently.')
]

curr_row += 1
for st_name, guidance in stage_order:
    st_list = stage_groups[st_name]
    st_tanks = len(st_list)
    st_fish = sum(r['Total_Count'] for r in st_list)
    pct = f'{(st_fish / max(1, sum(r["Total_Count"] for r in active_tanks_all))) * 100:.1f}%'
    
    ws1.cell(row=curr_row, column=1, value=st_name).alignment = align_left
    ws1.cell(row=curr_row, column=2, value=st_tanks).alignment = align_center
    ws1.cell(row=curr_row, column=3, value=st_fish).alignment = align_center
    ws1.cell(row=curr_row, column=4, value=pct).alignment = align_center
    ws1.cell(row=curr_row, column=5, value=guidance).alignment = align_left
    for c_i in range(1, 6):
        cell = ws1.cell(row=curr_row, column=c_i)
        cell.font = regular_font
        cell.border = thin_border
        if 'Overdue' in st_name:
            cell.fill = red_fill
        elif 'Prime' in st_name:
            cell.fill = green_fill
    curr_row += 1

# TAB 2: Line Demographics Detailed
ws2 = wb.create_sheet(title='2_Line_Demographics')
ws2.views.sheetView[0].showGridLines = True
ws2['A1'] = 'Primary Genetic Lines (AB, Casper, Fli, Gata) Breakdown'
ws2['A1'].font = title_font
ws2['A2'] = f'Reference Date: {NOW.strftime("%Y-%m-%d")} | Total Strains: {len(line_stats)}'
ws2['A2'].font = subtitle_font

headers2 = ['Primary Line', 'Active Tanks', 'Euthanized Tanks', 'Active Fish', 'Active Females', 'Active Males', 'Sex Ratio (F:M)', 'Avg Age (Months)', 'Avg Inbreeding (F)', 'Colony Risk Status', 'Risk Analysis & Recommendations']
for col_idx, h in enumerate(headers2, 1):
    c = ws2.cell(row=4, column=col_idx, value=h)
    c.font = white_bold
    c.fill = navy_fill
    c.alignment = align_center

for r_idx, ls in enumerate(line_stats, 5):
    ws2.cell(row=r_idx, column=1, value=ls['Line']).alignment = align_left
    ws2.cell(row=r_idx, column=2, value=ls['Active_Tanks']).alignment = align_center
    ws2.cell(row=r_idx, column=3, value=ls['Euthanized_Tanks']).alignment = align_center
    ws2.cell(row=r_idx, column=4, value=ls['Total_Active_Fish']).alignment = align_center
    ws2.cell(row=r_idx, column=5, value=ls['Active_Females']).alignment = align_center
    ws2.cell(row=r_idx, column=6, value=ls['Active_Males']).alignment = align_center
    ws2.cell(row=r_idx, column=7, value=ls['Sex_Ratio']).alignment = align_center
    ws2.cell(row=r_idx, column=8, value=ls['Avg_Age_Months']).alignment = align_center
    ws2.cell(row=r_idx, column=9, value=ls['Avg_Inbreeding_F']).alignment = align_center
    ws2.cell(row=r_idx, column=10, value=ls['Risk_Level']).alignment = align_center
    ws2.cell(row=r_idx, column=11, value=ls['Risk_Reasons']).alignment = align_left
    for c_i in range(1, 12):
        cell = ws2.cell(row=r_idx, column=c_i)
        cell.font = regular_font
        cell.border = thin_border
        if 'CRITICAL' in ls['Risk_Level']:
            cell.fill = red_fill
        elif 'HIGH' in ls['Risk_Level'] or 'MEDIUM' in ls['Risk_Level']:
            cell.fill = orange_fill
        else:
            cell.fill = green_fill

# TAB 3: Turnover Action Plan
ws3 = wb.create_sheet(title='3_Turnover_Action_Plan')
ws3.views.sheetView[0].showGridLines = True
ws3['A1'] = 'Turnover Schedule & Renewal Action Plan'
ws3['A1'].font = title_font
ws3['A2'] = 'Active tanks prioritized by turnover urgency (540 days post-DOB standard window).'
ws3['A2'].font = subtitle_font

headers3 = ['TUID', 'Status', 'Notes / Genotype', 'Primary Line', 'Tank Vol', 'Total Fish', 'Females', 'Males', 'DOB', 'Turnover Date', 'Days to Turnover', 'Urgency Status', 'Recommended Colony Action']
for col_idx, h in enumerate(headers3, 1):
    c = ws3.cell(row=4, column=col_idx, value=h)
    c.font = white_bold
    c.fill = navy_fill
    c.alignment = align_center

active_tanks_sorted_turnover = sorted([r for r in records if r['Is_Active']], key=lambda x: (x['Days_To_Turnover'] if x['Days_To_Turnover'] is not None else 9999))

for r_idx, r in enumerate(active_tanks_sorted_turnover, 5):
    ws3.cell(row=r_idx, column=1, value=r['TUID']).alignment = align_center
    ws3.cell(row=r_idx, column=2, value=r['Status_Clean']).alignment = align_center
    ws3.cell(row=r_idx, column=3, value=r.get('NOTES', '')).alignment = align_left
    ws3.cell(row=r_idx, column=4, value=r['Line_Category']).alignment = align_center
    ws3.cell(row=r_idx, column=5, value=r['Tank_Display']).alignment = align_center
    ws3.cell(row=r_idx, column=6, value=r['Total_Count']).alignment = align_center
    ws3.cell(row=r_idx, column=7, value=r['Female_Count']).alignment = align_center
    ws3.cell(row=r_idx, column=8, value=r['Male_Count']).alignment = align_center
    ws3.cell(row=r_idx, column=9, value=r.get('DOB', '')).alignment = align_center
    ws3.cell(row=r_idx, column=10, value=r.get('TURNOVER', '')).alignment = align_center
    ws3.cell(row=r_idx, column=11, value=r['Days_To_Turnover']).alignment = align_center
    ws3.cell(row=r_idx, column=12, value=r['Turnover_Urgency']).alignment = align_center
    ws3.cell(row=r_idx, column=13, value=r['Turnover_Action']).alignment = align_left
    
    for c_i in range(1, 14):
        cell = ws3.cell(row=r_idx, column=c_i)
        cell.font = regular_font
        cell.border = thin_border
        if r['Turnover_Urgency'] == 'OVERDUE':
            cell.fill = red_fill
        elif 'DUE SOON' in r['Turnover_Urgency']:
            cell.fill = orange_fill

# TAB 4: Pedigree & Lineage Matrix
ws4 = wb.create_sheet(title='4_Pedigree_Lineage_Matrix')
ws4.views.sheetView[0].showGridLines = True
ws4['A1'] = 'FishNET Pedigree, Kinship & Lineage Matrix'
ws4['A1'].font = title_font
ws4['A2'] = 'Status (Active vs Euthanized), Generation depth, inbreeding coefficients (F), and progeny counts.'
ws4['A2'].font = subtitle_font

headers4 = ['TUID', 'Status', 'Primary Line', 'Gen Depth', 'Sire (Paternal)', 'Dam (Maternal)', 'Cross ID', 'Inbreeding (F)', 'Progeny Tanks Count', 'Progeny Tanks List', 'Notes / Genotype']
for col_idx, h in enumerate(headers4, 1):
    c = ws4.cell(row=4, column=col_idx, value=h)
    c.font = white_bold
    c.fill = navy_fill
    c.alignment = align_center

for r_idx, r in enumerate(records, 5):
    ws4.cell(row=r_idx, column=1, value=r['TUID']).alignment = align_center
    ws4.cell(row=r_idx, column=2, value=r.get('STATUS', '')).alignment = align_center
    ws4.cell(row=r_idx, column=3, value=r['Line_Category']).alignment = align_center
    ws4.cell(row=r_idx, column=4, value=f'F{r["Gen_Depth"]}' if r['Gen_Depth'] > 0 else 'F0 / Founder').alignment = align_center
    ws4.cell(row=r_idx, column=5, value=r['Sire']).alignment = align_center
    ws4.cell(row=r_idx, column=6, value=r['Dam']).alignment = align_center
    ws4.cell(row=r_idx, column=7, value=r.get('Derivative cross', '')).alignment = align_center
    ws4.cell(row=r_idx, column=8, value=r['Inbreeding_F']).alignment = align_center
    ws4.cell(row=r_idx, column=9, value=r['Progeny_Count']).alignment = align_center
    ws4.cell(row=r_idx, column=10, value=r['Progeny_Tanks']).alignment = align_left
    ws4.cell(row=r_idx, column=11, value=r.get('NOTES', '')).alignment = align_left
    for c_i in range(1, 12):
        cell = ws4.cell(row=r_idx, column=c_i)
        cell.font = regular_font
        cell.border = thin_border
        if not r['Is_Active']:
            cell.fill = soft_blue
        elif r['Inbreeding_F'] >= 0.5:
            ws4.cell(row=r_idx, column=8).fill = orange_fill

# TAB 5: Cross Performance
ws5 = wb.create_sheet(title='5_Cross_Performance')
ws5.views.sheetView[0].showGridLines = True
ws5['A1'] = 'Clutch & Derivative Cross Performance Tracker'
ws5['A1'].font = title_font
ws5['A2'] = f'Total Crosses: {len(cross_stats)} | Tracking yields for C0001 - C0071'
ws5['A2'].font = subtitle_font

headers5 = ['Cross ID', 'Parental Pairing (Sire x Dam)', 'Primary Lines', 'Cross DOB', 'Tanks Spawned', 'Active Tanks', 'Total Progeny Yield', 'Active Fish', 'Active Females', 'Active Males', 'Avg Fish / Tank', 'Spawned Tanks List']
for col_idx, h in enumerate(headers5, 1):
    c = ws5.cell(row=4, column=col_idx, value=h)
    c.font = white_bold
    c.fill = navy_fill
    c.alignment = align_center

for r_idx, cs in enumerate(cross_stats, 5):
    ws5.cell(row=r_idx, column=1, value=cs['Cross_ID']).alignment = align_center
    ws5.cell(row=r_idx, column=2, value=cs['Parental_Cross']).alignment = align_left
    ws5.cell(row=r_idx, column=3, value=cs['Lines']).alignment = align_center
    ws5.cell(row=r_idx, column=4, value=cs['DOB']).alignment = align_center
    ws5.cell(row=r_idx, column=5, value=cs['Tanks_Count']).alignment = align_center
    ws5.cell(row=r_idx, column=6, value=cs['Active_Tanks']).alignment = align_center
    ws5.cell(row=r_idx, column=7, value=cs['Total_Fish_Yield']).alignment = align_center
    ws5.cell(row=r_idx, column=8, value=cs['Active_Fish']).alignment = align_center
    ws5.cell(row=r_idx, column=9, value=cs['Active_Females']).alignment = align_center
    ws5.cell(row=r_idx, column=10, value=cs['Active_Males']).alignment = align_center
    ws5.cell(row=r_idx, column=11, value=cs['Avg_Fish_Per_Tank']).alignment = align_center
    ws5.cell(row=r_idx, column=12, value=cs['Tank_List']).alignment = align_left
    for c_i in range(1, 13):
        cell = ws5.cell(row=r_idx, column=c_i)
        cell.font = regular_font
        cell.border = thin_border

# TAB 6: Tank Density & Welfare
ws6 = wb.create_sheet(title='6_Tank_Density_Welfare')
ws6.views.sheetView[0].showGridLines = True
ws6['A1'] = 'Tank Stocking Density & Welfare Compliance'
ws6['A1'].font = title_font
ws6['A2'] = 'Active tanks density evaluation (Target: 2.0 - 6.0 fish/L. Welfare threshold: < 8.0 fish/L).'
ws6['A2'].font = subtitle_font

headers6 = ['TUID', 'Status', 'Notes', 'Primary Line', 'Tank Size', 'Volume (L)', 'Total Fish', 'Density (Fish/L)', 'Compliance Status', 'Welfare Action']
for col_idx, h in enumerate(headers6, 1):
    c = ws6.cell(row=4, column=col_idx, value=h)
    c.font = white_bold
    c.fill = navy_fill
    c.alignment = align_center

active_density_tanks = sorted([r for r in records if r['Is_Active']], key=lambda x: x['Fish_Per_Liter'], reverse=True)

for r_idx, r in enumerate(active_density_tanks, 5):
    ws6.cell(row=r_idx, column=1, value=r['TUID']).alignment = align_center
    ws6.cell(row=r_idx, column=2, value=r['Status_Clean']).alignment = align_center
    ws6.cell(row=r_idx, column=3, value=r.get('NOTES', '')).alignment = align_left
    ws6.cell(row=r_idx, column=4, value=r['Line_Category']).alignment = align_center
    ws6.cell(row=r_idx, column=5, value=r['Tank_Display']).alignment = align_center
    ws6.cell(row=r_idx, column=6, value=r['Volume_L']).alignment = align_center
    ws6.cell(row=r_idx, column=7, value=r['Total_Count']).alignment = align_center
    ws6.cell(row=r_idx, column=8, value=r['Fish_Per_Liter']).alignment = align_center
    ws6.cell(row=r_idx, column=9, value=r['Density_Status']).alignment = align_center
    
    act_note = 'Compliant'
    if 'OVERSTOCKED' in r['Density_Status']:
        act_note = 'Split tank immediately into secondary holding tank.'
    elif 'Understocked' in r['Density_Status']:
        act_note = 'Consider consolidating or moving to 1.8L tank.'
    ws6.cell(row=r_idx, column=10, value=act_note).alignment = align_left
    
    for c_i in range(1, 11):
        cell = ws6.cell(row=r_idx, column=c_i)
        cell.font = regular_font
        cell.border = thin_border
        if 'OVERSTOCKED' in r['Density_Status']:
            cell.fill = red_fill
        elif 'Understocked' in r['Density_Status']:
            cell.fill = soft_blue

# TAB 7: Risk Alerts
ws7 = wb.create_sheet(title='7_Risk_Bottleneck_Alerts')
ws7.views.sheetView[0].showGridLines = True
ws7['A1'] = 'Colony Management Risk & Bottleneck Alerts'
ws7['A1'].font = title_font
ws7['A2'] = f'Total Active Actionable Alerts: {len(alerts)}'
ws7['A2'].font = subtitle_font

headers7 = ['Alert ID', 'Tank / Line', 'Primary Line', 'Alert Category', 'Severity', 'Risk Description', 'Recommended Management Action']
for col_idx, h in enumerate(headers7, 1):
    c = ws7.cell(row=4, column=col_idx, value=h)
    c.font = white_bold
    c.fill = navy_fill
    c.alignment = align_center

for r_idx, alt in enumerate(alerts, 5):
    ws7.cell(row=r_idx, column=1, value=f'ALT-{r_idx-4:03d}').alignment = align_center
    ws7.cell(row=r_idx, column=2, value=alt['TUID']).alignment = align_center
    ws7.cell(row=r_idx, column=3, value=alt['Line']).alignment = align_center
    ws7.cell(row=r_idx, column=4, value=alt['Category']).alignment = align_left
    ws7.cell(row=r_idx, column=5, value=alt['Severity']).alignment = align_center
    ws7.cell(row=r_idx, column=6, value=alt['Description']).alignment = align_left
    ws7.cell(row=r_idx, column=7, value=alt['Action']).alignment = align_left
    for c_i in range(1, 8):
        cell = ws7.cell(row=r_idx, column=c_i)
        cell.font = regular_font
        cell.border = thin_border
        if alt['Severity'] == 'CRITICAL':
            cell.fill = red_fill
        elif alt['Severity'] == 'HIGH':
            cell.fill = orange_fill

for ws in wb.worksheets:
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.row < 4:
                continue
            val_str = str(cell.value or '')
            if '\n' in val_str:
                val_str = max(val_str.split('\n'), key=len)
            max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

try:
    wb.save(EXCEL_REPORT_FILE)
    print(f'Excel Report written successfully: {EXCEL_REPORT_FILE}')
except PermissionError:
    alt_file = 'FishNET_Colony_Analytics_Report_v2.xlsx'
    wb.save(alt_file)
    print(f'Excel file locked; saved to: {alt_file}')

# Convert records to JSON serializable dictionary (handling datetime objects)
raw_records_json = json.dumps(records, default=str)



html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FishNET Zebrafish Colony & Pedigree Intelligence Dashboard</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- SheetJS (xlsx parser for in-browser file upload) -->
    <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
    <!-- Vis.js Network for Interactive Pedigree -->
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background-color: #0b1120; color: #f1f5f9; }
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .glass-card { background: #1e293b; border: 1px solid #334155; }
        .tab-btn.active { background-color: #0d9488; color: #ffffff; border-color: #14b8a6; }
        #pedigree-network { width: 100%; height: 680px; border-radius: 0.75rem; background: #0f172a; border: 1px solid #334155; }
        .badge { padding: 0.25rem 0.5rem; border-radius: 0.375rem; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
        .badge-critical { background-color: #ef4444; color: #ffffff; }
        .badge-high { background-color: #f97316; color: #ffffff; }
        .badge-optimal { background-color: #10b981; color: #ffffff; }
        .badge-info { background-color: #0284c7; color: #ffffff; }
        .badge-archive { background-color: #64748b; color: #ffffff; }
        /* Custom scrollbars */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }
    </style>
</head>
<body class="min-h-screen">

    <!-- Top Navigation Header -->
    <header class="glass sticky top-0 z-50 px-6 py-4 border-b border-slate-700/60 shadow-xl">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-teal-500 flex items-center justify-center font-bold text-xl text-slate-900 shadow-lg shadow-teal-500/20">
                    🐟
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                        FishNET Colony & Pedigree Intelligence
                        <span id="activeBadge" class="text-xs font-semibold px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-400 border border-teal-500/30">v2.4 Active</span>
                    </h1>
                    <p class="text-xs text-slate-400">Primary Lines: <b class="text-amber-400">AB</b> • <b class="text-sky-400">Casper</b> • <b class="text-green-400">Fli</b> • <b class="text-pink-400">Gata</b></p>
                </div>
            </div>

            <!-- Navigation Tabs & Upload Button -->
            <div class="flex flex-wrap items-center gap-2">
                <nav class="flex flex-wrap gap-1.5">
                    <button onclick="switchTab('dashboard')" id="tab-btn-dashboard" class="tab-btn active px-3.5 py-1.5 rounded-lg text-xs font-medium border border-slate-700 text-slate-300 hover:text-white transition">📊 Overview</button>
                    <button onclick="switchTab('pedigree')" id="tab-btn-pedigree" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-medium border border-slate-700 text-slate-300 hover:text-white transition">🌳 Pedigree Explorer</button>
                    <button onclick="switchTab('turnover')" id="tab-btn-turnover" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-medium border border-slate-700 text-slate-300 hover:text-white transition">⏰ Turnover & Renewal (<span id="tabCountTurnover">0</span>)</button>
                    <button onclick="switchTab('demographics')" id="tab-btn-demographics" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-medium border border-slate-700 text-slate-300 hover:text-white transition">🧬 4 Lines Matrix</button>
                    <button onclick="switchTab('crosses')" id="tab-btn-crosses" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-medium border border-slate-700 text-slate-300 hover:text-white transition">📋 Crosses (<span id="tabCountCrosses">0</span>)</button>
                    <button onclick="switchTab('welfare')" id="tab-btn-welfare" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-medium border border-slate-700 text-slate-300 hover:text-white transition">⚖️ Density</button>
                    <button onclick="switchTab('alerts')" id="tab-btn-alerts" class="tab-btn px-3.5 py-1.5 rounded-lg text-xs font-medium border border-slate-700 text-slate-300 hover:text-white transition">⚠️ Alerts (<span id="tabCountAlerts">0</span>)</button>
                </nav>

                <!-- File Upload Trigger -->
                <label class="cursor-pointer px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-teal-600 hover:bg-teal-500 text-white shadow-lg shadow-teal-600/30 transition flex items-center gap-1.5">
                    <span>📁 Upload File</span>
                    <input type="file" id="fileUploader" accept=".xlsx,.xls,.tab,.tsv,.csv,.txt" class="hidden" onchange="handleFileUpload(event)">
                </label>
            </div>
        </div>
    </header>

    <!-- File Status & Quick Info Bar -->
    <div class="max-w-7xl mx-auto px-6 pt-4">
        <div class="glass px-4 py-2.5 rounded-xl border border-slate-700/50 flex flex-col md:flex-row items-center justify-between gap-3 text-xs">
            <div class="flex items-center gap-2 text-slate-300">
                <span class="w-2.5 h-2.5 rounded-full bg-teal-400 animate-pulse"></span>
                <span>Active Dataset: <b id="currentDatasetLabel" class="text-teal-300">Default FishNET.tab</b> (<span id="loadedRecordsCount">166</span> total rows)</span>
            </div>
            <div class="flex items-center gap-3">
                <label class="flex items-center gap-1.5 text-slate-300 cursor-pointer">
                    <input type="checkbox" id="showEuthanizedToggle" checked onchange="toggleEuthanizedFilter()" class="rounded bg-slate-800 border-slate-700 text-teal-500 focus:ring-0">
                    <span>Include Euthanized/Archived in Pedigree</span>
                </label>
                <button onclick="resetToDefaultData()" class="text-slate-400 hover:text-white underline text-[11px]">Reset to Default</button>
            </div>
        </div>
    </div>

    <main class="max-w-7xl mx-auto p-6 space-y-6">

        <!-- ==================== TAB 1: OVERVIEW DASHBOARD ==================== -->
        <section id="tab-dashboard" class="tab-content space-y-6">
            <!-- Metric KPI Stat Cards -->
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <div class="glass p-4 rounded-xl shadow-lg border-l-4 border-teal-500">
                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Tanks</p>
                    <p id="kpiActiveTanks" class="text-2xl font-bold text-teal-400 mt-1">0</p>
                    <p class="text-xs text-slate-400 mt-1"><span id="kpiTotalTanks">0</span> total records</p>
                </div>
                <div class="glass p-4 rounded-xl shadow-lg border-l-4 border-cyan-500">
                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Fish</p>
                    <p id="kpiActiveFish" class="text-2xl font-bold text-cyan-400 mt-1">0</p>
                    <p class="text-xs text-slate-400 mt-1">Total living biomass</p>
                </div>
                <div class="glass p-4 rounded-xl shadow-lg border-l-4 border-pink-500">
                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Breeding Females</p>
                    <p id="kpiFemales" class="text-2xl font-bold text-pink-400 mt-1">0</p>
                    <p id="kpiFemalesPct" class="text-xs text-slate-400 mt-1">0% of colony</p>
                </div>
                <div class="glass p-4 rounded-xl shadow-lg border-l-4 border-blue-500">
                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Breeding Males</p>
                    <p id="kpiMales" class="text-2xl font-bold text-blue-400 mt-1">0</p>
                    <p id="kpiMalesPct" class="text-xs text-slate-400 mt-1">0% of colony</p>
                </div>
                <div class="glass p-4 rounded-xl shadow-lg border-l-4 border-amber-500">
                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Unique Crosses</p>
                    <p id="kpiCrosses" class="text-2xl font-bold text-amber-400 mt-1">0</p>
                    <p class="text-xs text-slate-400 mt-1">Derivative clutches</p>
                </div>
                <div class="glass p-4 rounded-xl shadow-lg border-l-4 border-rose-500">
                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Overdue Turnover</p>
                    <p id="kpiOverdue" class="text-2xl font-bold text-rose-400 mt-1">0</p>
                    <p class="text-xs text-rose-400 mt-1">>540 days old</p>
                </div>
            </div>

            <!-- Charts Row 1 -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="glass p-5 rounded-xl shadow-lg">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="font-bold text-base text-slate-200">🧬 4 Primary Lines (AB, Casper, Fli, Gata)</h3>
                        <span class="text-xs text-slate-400">Active Fish & Tank Counts</span>
                    </div>
                    <div class="h-64">
                        <canvas id="chartStrains"></canvas>
                    </div>
                </div>

                <div class="glass p-5 rounded-xl shadow-lg">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="font-bold text-base text-slate-200">⏳ Colony Lifecycle & Age Structure</h3>
                        <span class="text-xs text-slate-400">Distribution by Stage</span>
                    </div>
                    <div class="h-64">
                        <canvas id="chartAgeStructure"></canvas>
                    </div>
                </div>
            </div>

            <!-- Charts Row 2 -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="glass p-5 rounded-xl shadow-lg">
                    <h3 class="font-bold text-base text-slate-200 mb-3">⚖️ Sex Breakdown (Active Fish)</h3>
                    <div class="h-56">
                        <canvas id="chartSexRatio"></canvas>
                    </div>
                </div>

                <div class="glass p-5 rounded-xl shadow-lg">
                    <h3 class="font-bold text-base text-slate-200 mb-3">📦 Tank Volume Sizes</h3>
                    <div class="h-56">
                        <canvas id="chartTankSizes"></canvas>
                    </div>
                </div>

                <div class="glass p-5 rounded-xl shadow-lg">
                    <h3 class="font-bold text-base text-slate-200 mb-3">📈 Inbreeding Coefficient (F)</h3>
                    <div class="h-56">
                        <canvas id="chartInbreeding"></canvas>
                    </div>
                </div>
            </div>
        </section>

                <!-- ==================== TAB 2: PEDIGREE EXPLORER (4 INTERACTIVE MODES) ==================== -->
        <section id="tab-pedigree" class="tab-content hidden space-y-4">
            <div class="glass p-5 rounded-xl shadow-lg">
                <!-- Pedigree Header & Mode Selector -->
                <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-700">
                    <div>
                        <div class="flex items-center gap-2">
                            <h2 class="text-lg font-bold text-white flex items-center gap-2">
                                🌳 Colony Lineage & Pedigree Architecture
                            </h2>
                            <span class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-400 border border-teal-500/30">4 Viewing Modes</span>
                        </div>
                        <p class="text-xs text-slate-400 mt-0.5">Toggle between 3-gen family cards, clean line trees, collapsible table hierarchy, and the global network map.</p>
                    </div>

                    <!-- 4 Mode Sub-Tab Navigation -->
                    <div class="flex flex-wrap items-center gap-1.5 bg-slate-900/80 p-1.5 rounded-xl border border-slate-700">
                        <button onclick="switchPedigreeMode('focal')" id="ped-btn-focal" class="ped-mode-btn active px-3 py-1.5 rounded-lg text-xs font-semibold bg-teal-600 text-white transition flex items-center gap-1.5 shadow-sm">
                            <span>🎯 3-Gen Family Tree</span>
                        </button>
                        <button onclick="switchPedigreeMode('lines')" id="ped-btn-lines" class="ped-mode-btn px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5">
                            <span>🌿 Line Trees (4 Lines)</span>
                        </button>
                        <button onclick="switchPedigreeMode('table')" id="ped-btn-table" class="ped-mode-btn px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5">
                            <span>📑 Collapsible Tree Table</span>
                        </button>
                        <button onclick="switchPedigreeMode('network')" id="ped-btn-network" class="ped-mode-btn px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5">
                            <span>🕸️ Global Network Map</span>
                        </button>
                    </div>
                </div>

                <!-- Biological Husbandry Callout (Mixed Batches & Outcrosses) -->
                <div class="mt-4 p-3.5 rounded-xl bg-gradient-to-r from-teal-950/40 via-slate-900/60 to-indigo-950/40 border border-teal-800/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
                    <div class="flex items-center gap-2.5">
                        <span class="p-2 rounded-lg bg-teal-500/20 text-teal-300 text-sm">🔀</span>
                        <div>
                            <span class="font-bold text-teal-300">Husbandry Principle: Pooled Batches (...Mix Tanks):</span>
                            <p class="text-slate-300 text-[11px] mt-0.5">Tanks tagged with <b>🔀 Mix</b> contain larvae pooled from multiple separate single-pair matings. Inter-breeding these cohorts maintains high heterozygosity and actively suppresses inbreeding depression ($F 	o 0$).</p>
                        </div>
                    </div>
                    <span class="px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-teal-400 font-mono text-[11px] shrink-0">
                        33 Pooled Cohorts Identified
                    </span>
                </div>

                <!-- ==================== SUB-VIEW 1: FOCUSED 3-GEN FAMILY TREE ==================== -->
                <div id="ped-subview-focal" class="ped-subview mt-4 space-y-4">
                    <!-- Focal Controls & Search -->
                    <div class="glass-card p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-3">
                        <div class="flex flex-wrap items-center gap-2">
                            <label class="text-xs font-semibold text-slate-300">Select Focal Tank:</label>
                            <select id="focalTankSelect" onchange="changeFocalTank(this.value)" class="bg-slate-800 text-sm px-3 py-1.5 rounded-lg border border-slate-700 text-teal-300 font-bold focus:outline-none focus:border-teal-500">
                                <!-- Populated dynamically -->
                            </select>
                            <input type="text" id="focalSearchInput" placeholder="Quick search (e.g. T0135)..." class="bg-slate-800 text-xs px-3 py-1.5 rounded-lg border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 w-44">
                            <button onclick="searchAndFocusTank()" class="px-3 py-1.5 bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold rounded-lg transition">Focus</button>
                        </div>

                        <!-- Breadcrumb Trail & Action Buttons -->
                        <div class="flex flex-wrap items-center gap-2">
                            <button onclick="copyLineageTrail()" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition flex items-center gap-1">
                                <span>📋 Copy Lineage Path</span>
                            </button>
                            <button onclick="printPedigreeCard()" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition flex items-center gap-1 shadow-sm">
                                <span>🖨️ Export Pedigree Card</span>
                            </button>
                        </div>
                    </div>

                    <!-- Lineage Breadcrumb Trail Bar -->
                    <div class="p-3 bg-slate-900/90 rounded-xl border border-slate-800 flex items-center justify-between gap-2 overflow-x-auto text-xs font-mono">
                        <div class="flex items-center gap-2 text-slate-300" id="focalBreadcrumbTrail">
                            <!-- Populated dynamically -->
                        </div>
                    </div>

                    <!-- 5-Column Visual Family Tree Grid -->
                    <div class="grid grid-cols-1 md:grid-cols-5 gap-3.5 min-h-[460px]">
                        <!-- Column 1: Grandparents -->
                        <div class="glass-card p-3 rounded-xl space-y-3">
                            <div class="border-b border-slate-700 pb-1.5 flex items-center justify-between">
                                <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">👴👵 Grandparents</span>
                                <span class="text-[10px] text-slate-500">Ancestors (2-gen)</span>
                            </div>
                            <div id="treeColGrandparents" class="space-y-2 text-xs">
                                <!-- Populated dynamically -->
                            </div>
                        </div>

                        <!-- Column 2: Parents -->
                        <div class="glass-card p-3 rounded-xl space-y-3">
                            <div class="border-b border-slate-700 pb-1.5 flex items-center justify-between">
                                <span class="text-xs font-bold text-sky-400 uppercase tracking-wider">👨👩 Parents</span>
                                <span class="text-[10px] text-slate-500">Direct Sire & Dam</span>
                            </div>
                            <div id="treeColParents" class="space-y-2 text-xs">
                                <!-- Populated dynamically -->
                            </div>
                        </div>

                        <!-- Column 3: Focal Tank (Hero Card) -->
                        <div class="glass-card p-3.5 rounded-xl space-y-3 border-2 border-teal-500/60 shadow-xl shadow-teal-950/40 bg-gradient-to-b from-slate-900 via-slate-900/90 to-teal-950/20">
                            <div class="border-b border-teal-500/40 pb-1.5 flex items-center justify-between">
                                <span class="text-xs font-bold text-teal-300 uppercase tracking-wider flex items-center gap-1">
                                    <span>🎯 Target Focus Tank</span>
                                </span>
                                <span id="focalHeroGenBadge" class="badge badge-optimal">F0 Founder</span>
                            </div>
                            <div id="treeColFocal" class="space-y-2">
                                <!-- Populated dynamically -->
                            </div>
                        </div>

                        <!-- Column 4: Direct Offspring (Children) -->
                        <div class="glass-card p-3 rounded-xl space-y-3">
                            <div class="border-b border-slate-700 pb-1.5 flex items-center justify-between">
                                <span class="text-xs font-bold text-emerald-400 uppercase tracking-wider">👶 Offspring (F1)</span>
                                <span id="treeOffspringCountBadge" class="text-[10px] text-emerald-400 font-bold">0 Tanks</span>
                            </div>
                            <div id="treeColOffspring" class="space-y-2 max-h-[460px] overflow-y-auto pr-1 text-xs">
                                <!-- Populated dynamically -->
                            </div>
                        </div>

                        <!-- Column 5: Grandchildren -->
                        <div class="glass-card p-3 rounded-xl space-y-3">
                            <div class="border-b border-slate-700 pb-1.5 flex items-center justify-between">
                                <span class="text-xs font-bold text-purple-400 uppercase tracking-wider">🌱 Grandchildren</span>
                                <span id="treeGrandchildrenCountBadge" class="text-[10px] text-purple-400 font-bold">0 Tanks</span>
                            </div>
                            <div id="treeColGrandchildren" class="space-y-2 max-h-[460px] overflow-y-auto pr-1 text-xs">
                                <!-- Populated dynamically -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ==================== SUB-VIEW 2: LINE-BY-LINE HIERARCHICAL TREES ==================== -->
                <div id="ped-subview-lines" class="ped-subview hidden mt-4 space-y-4">
                    <!-- Line Selector Tabs -->
                    <div class="flex flex-wrap items-center justify-between gap-3 bg-slate-900/80 p-3 rounded-xl border border-slate-700">
                        <div class="flex flex-wrap items-center gap-2">
                            <button onclick="selectLineTree('AB')" id="line-tree-btn-AB" class="line-tree-btn active px-3.5 py-1.5 rounded-lg text-xs font-bold bg-amber-500 text-slate-950 transition">
                                🟡 AB Lineage Tree (<span id="lineTreeCountAB">0</span>)
                            </button>
                            <button onclick="selectLineTree('Casper')" id="line-tree-btn-Casper" class="line-tree-btn px-3.5 py-1.5 rounded-lg text-xs font-bold text-sky-400 bg-slate-800 hover:bg-slate-700 transition">
                                🔵 Casper Lineage Tree (<span id="lineTreeCountCasper">0</span>)
                            </button>
                            <button onclick="selectLineTree('Fli')" id="line-tree-btn-Fli" class="line-tree-btn px-3.5 py-1.5 rounded-lg text-xs font-bold text-green-400 bg-slate-800 hover:bg-slate-700 transition">
                                🟢 Fli Lineage Tree (<span id="lineTreeCountFli">0</span>)
                            </button>
                            <button onclick="selectLineTree('Gata')" id="line-tree-btn-Gata" class="line-tree-btn px-3.5 py-1.5 rounded-lg text-xs font-bold text-pink-400 bg-slate-800 hover:bg-slate-700 transition">
                                🟣 Gata Lineage Tree (<span id="lineTreeCountGata">0</span>)
                            </button>
                        </div>
                        <div class="text-xs text-slate-400">
                            Showing generation depth from top founders downward.
                        </div>
                    </div>

                    <!-- Line Tiers Container -->
                    <div id="lineTreeTiersContainer" class="space-y-6">
                        <!-- Populated dynamically: Generation Tiers -->
                    </div>
                </div>

                <!-- ==================== SUB-VIEW 3: COLLAPSIBLE TREE TABLE ==================== -->
                <div id="ped-subview-table" class="ped-subview hidden mt-4 space-y-4">
                    <div class="glass-card p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-3">
                        <div class="flex flex-wrap items-center gap-2">
                            <input type="text" id="treeTableSearchInput" onkeyup="filterTreeTable()" placeholder="Search Tank, Line, Parents..." class="bg-slate-800 text-xs px-3 py-1.5 rounded-lg border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 w-56">
                            <select id="treeTableLineFilter" onchange="filterTreeTable()" class="bg-slate-800 text-xs px-3 py-1.5 rounded-lg border border-slate-700 text-slate-200">
                                <option value="ALL">All Lines</option>
                                <option value="AB">AB</option>
                                <option value="Casper">Casper</option>
                                <option value="Fli">Fli</option>
                                <option value="Gata">Gata</option>
                            </select>
                            <select id="treeTableStatusFilter" onchange="filterTreeTable()" class="bg-slate-800 text-xs px-3 py-1.5 rounded-lg border border-slate-700 text-slate-200">
                                <option value="ALL">All Statuses</option>
                                <option value="ACTIVE">Adult / Active Only</option>
                                <option value="EUTH">Euthanized Only</option>
                            </select>
                        </div>

                        <div class="flex items-center gap-2">
                            <button onclick="expandAllTreeRows()" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-lg border border-slate-700 transition">Expand All</button>
                            <button onclick="collapseAllTreeRows()" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-lg border border-slate-700 transition">Collapse All</button>
                            <button onclick="exportTreeTableCSV()" class="px-3 py-1.5 bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold rounded-lg transition flex items-center gap-1">
                                <span>📥 Export CSV</span>
                            </button>
                        </div>
                    </div>

                    <div class="table-container max-h-[550px] overflow-y-auto">
                        <table class="w-full text-left text-xs" id="pedigreeTreeTable">
                            <thead class="bg-slate-900/90 text-slate-400 sticky top-0 uppercase tracking-wider text-[11px] border-b border-slate-700">
                                <tr>
                                    <th class="p-3">Tank ID & Line</th>
                                    <th class="p-3">Generation</th>
                                    <th class="p-3">Status</th>
                                    <th class="p-3">Fish (F/M/Total)</th>
                                    <th class="p-3">Inbreeding (F)</th>
                                    <th class="p-3">Genetic Category / Mix Pool</th>
                                    <th class="p-3">Sire × Dam</th>
                                    <th class="p-3">Progeny</th>
                                    <th class="p-3 text-center">Action</th>
                                </tr>
                            </thead>
                            <tbody id="pedigreeTreeTableBody" class="divide-y divide-slate-800 text-slate-200">
                                <!-- Populated dynamically -->
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- ==================== SUB-VIEW 4: GLOBAL NETWORK MAP (VIS.JS) ==================== -->
                <div id="ped-subview-network" class="ped-subview hidden mt-4 space-y-4">
                    <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-700">
                        <div class="flex flex-wrap items-center gap-2">
                            <div class="relative">
                                <input type="text" id="pedigreeSearch" placeholder="Search Tank (e.g. T0135)..." 
                                    class="bg-slate-800 text-sm px-3 py-1.5 rounded-lg border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-teal-500">
                                <button onclick="searchPedigreeNode()" class="px-3 py-1.5 bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold rounded-lg transition ml-1">Locate</button>
                            </div>

                            <select id="lineFilter" onchange="filterPedigreeByLine()" class="bg-slate-800 text-sm px-3 py-1.5 rounded-lg border border-slate-700 text-slate-200 focus:outline-none focus:border-teal-500">
                                <option value="ALL">All 4 Lines</option>
                                <option value="AB">AB Lineage</option>
                                <option value="Casper">Casper Lineage</option>
                                <option value="Fli">Fli Lineage</option>
                                <option value="Gata">Gata Lineage</option>
                            </select>

                            <button onclick="resetPedigreeView()" class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-medium rounded-lg transition">Reset View</button>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
                        <!-- Network Canvas -->
                        <div class="lg:col-span-3">
                            <div id="pedigree-network"></div>
                            <div class="flex flex-wrap items-center gap-4 mt-2 text-xs text-slate-400">
                                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-amber-400 inline-block"></span> <b>AB</b></span>
                                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-sky-400 inline-block"></span> <b>Casper</b></span>
                                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-green-400 inline-block"></span> <b>Fli</b></span>
                                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-pink-400 inline-block"></span> <b>Gata</b></span>
                                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-slate-500 inline-block"></span> <b>Euthanized/Archived</b></span>
                                <span class="flex items-center gap-1.5"><span class="w-4 h-0.5 bg-blue-500 inline-block"></span> Paternal (Sire)</span>
                                <span class="flex items-center gap-1.5"><span class="w-4 h-0.5 border-t border-dashed border-pink-500 inline-block"></span> Maternal (Dam)</span>
                            </div>
                        </div>

                        <!-- Node Inspector Card -->
                        <div class="glass-card p-4 rounded-xl space-y-4">
                            <div class="border-b border-slate-700 pb-2">
                                <span id="inspectStatus" class="badge badge-optimal">Active Tank</span>
                                <h3 id="inspectTUID" class="text-2xl font-black text-teal-400 mt-1">Select a Tank</h3>
                                <p id="inspectLine" class="text-xs font-semibold text-slate-300">Click any tank node to inspect</p>
                            </div>

                            <div class="space-y-2 text-xs">
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Status:</span>
                                    <span id="inspectStatusCol" class="font-bold text-slate-200">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Genotype / Notes:</span>
                                    <span id="inspectNotes" class="font-medium text-slate-200 text-right max-w-[160px]">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Genetic Category:</span>
                                    <span id="inspectGeneticType" class="font-semibold text-teal-300 text-right max-w-[160px]">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">DOB:</span>
                                    <span id="inspectDOB" class="font-medium text-slate-200">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Turnover Date:</span>
                                    <span id="inspectTurnover" class="font-medium text-slate-200">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Fish Count:</span>
                                    <span id="inspectCounts" class="font-bold text-teal-300">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Inbreeding (F):</span>
                                    <span id="inspectInbreeding" class="font-bold text-amber-400">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Parents (Sire x Dam):</span>
                                    <span id="inspectParents" class="font-semibold text-sky-400">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Cross ID:</span>
                                    <span id="inspectCross" class="font-semibold text-purple-400">-</span>
                                </div>
                            </div>

                            <!-- Action Buttons -->
                            <div class="space-y-2 pt-2">
                                <button onclick="highlightAncestors()" class="w-full py-2 bg-blue-600/80 hover:bg-blue-600 text-white rounded-lg text-xs font-semibold transition flex items-center justify-center gap-1.5">
                                    ⬆️ Trace Ancestors (Parents & Grandparents)
                                </button>
                                <button onclick="highlightDescendants()" class="w-full py-2 bg-purple-600/80 hover:bg-purple-600 text-white rounded-lg text-xs font-semibold transition flex items-center justify-center gap-1.5">
                                    ⬇️ Trace Progeny & Descendants
                                </button>
                                <button onclick="clearHighlights()" class="w-full py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white rounded-lg text-xs transition">
                                    Clear Highlight
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- ==================== TAB 3: TURNOVER ACTION PLAN ==================== -->
        <section id="tab-turnover" class="tab-content hidden space-y-4">
            <div class="glass p-5 rounded-xl shadow-lg">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-700">
                    <div>
                        <h2 class="text-lg font-bold text-white flex items-center gap-2">
                            ⏰ Colony Turnover Schedule & Renewal Action Plan
                        </h2>
                        <p class="text-xs text-slate-400 mt-0.5">Zebrafish standard lifecycle renewal: 540 days post-DOB (18 months).</p>
                    </div>

                    <div class="flex items-center gap-2">
                        <select id="turnoverFilter" onchange="renderTurnoverTable()" class="bg-slate-800 text-sm px-3 py-1.5 rounded-lg border border-slate-700 text-slate-200">
                            <option value="ALL">All Active Tanks</option>
                            <option value="OVERDUE">🚨 Overdue Only (>540d)</option>
                            <option value="SOON">⚠️ Due Soon (<=30d)</option>
                            <option value="UPCOMING">Upcoming (31-90d)</option>
                        </select>
                    </div>
                </div>

                <div class="overflow-x-auto mt-4 max-h-[600px]">
                    <table class="w-full text-left text-xs text-slate-300">
                        <thead class="bg-slate-800/90 text-slate-400 uppercase tracking-wider sticky top-0">
                            <tr>
                                <th class="p-3">TUID</th>
                                <th class="p-3">Status</th>
                                <th class="p-3">Genotype / Notes</th>
                                <th class="p-3 text-center">Line</th>
                                <th class="p-3 text-center">Fish (F/M/Tot)</th>
                                <th class="p-3 text-center">DOB</th>
                                <th class="p-3 text-center">Turnover Date</th>
                                <th class="p-3 text-center">Days Left</th>
                                <th class="p-3 text-center">Urgency</th>
                                <th class="p-3">Recommended Colony Action</th>
                            </tr>
                        </thead>
                        <tbody id="turnoverTableBody" class="divide-y divide-slate-800">
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ==================== TAB 4: 4 LINES DEMOGRAPHICS ==================== -->
        <section id="tab-demographics" class="tab-content hidden space-y-4">
            <div class="glass p-5 rounded-xl shadow-lg">
                <h2 class="text-lg font-bold text-white mb-1">🧬 4 Primary Lines (AB, Casper, Fli, Gata) Matrix</h2>
                <p class="text-xs text-slate-400 mb-4">Complete demographic parameters, active vs euthanized status, sex ratios, and inbreeding coefficients.</p>

                <div id="linesCardsContainer" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                </div>
            </div>
        </section>

        <!-- ==================== TAB 5: CROSS PERFORMANCE ==================== -->
        <section id="tab-crosses" class="tab-content hidden space-y-4">
            <div class="glass p-5 rounded-xl shadow-lg">
                <h2 class="text-lg font-bold text-white mb-1">📋 Clutch & Derivative Cross Performance Tracker</h2>
                <p class="text-xs text-slate-400 mb-4">Tracking crosses, parental combinations, and adult survivorship yields.</p>

                <div class="overflow-x-auto max-h-[600px]">
                    <table class="w-full text-left text-xs text-slate-300">
                        <thead class="bg-slate-800/90 text-slate-400 uppercase tracking-wider sticky top-0">
                            <tr>
                                <th class="p-3">Cross ID</th>
                                <th class="p-3">Parental Pairing (Sire x Dam)</th>
                                <th class="p-3 text-center">Primary Line</th>
                                <th class="p-3 text-center">Cross DOB</th>
                                <th class="p-3 text-center">Tanks Spawned</th>
                                <th class="p-3 text-center">Active Fish</th>
                                <th class="p-3 text-center">Females / Males</th>
                                <th class="p-3 text-center">Avg / Tank</th>
                                <th class="p-3">Resulting Tanks</th>
                            </tr>
                        </thead>
                        <tbody id="crossesTableBody" class="divide-y divide-slate-800">
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ==================== TAB 6: DENSITY & WELFARE ==================== -->
        <section id="tab-welfare" class="tab-content hidden space-y-4">
            <div class="glass p-5 rounded-xl shadow-lg">
                <h2 class="text-lg font-bold text-white mb-1">⚖️ Stocking Density & Animal Welfare Compliance</h2>
                <p class="text-xs text-slate-400 mb-4">Welfare standard: Optimal range is 2.0 to 6.0 fish/liter. Density > 8.0 fish/liter flags welfare review.</p>

                <div class="overflow-x-auto max-h-[600px]">
                    <table class="w-full text-left text-xs text-slate-300">
                        <thead class="bg-slate-800/90 text-slate-400 uppercase tracking-wider sticky top-0">
                            <tr>
                                <th class="p-3">TUID</th>
                                <th class="p-3">Status</th>
                                <th class="p-3">Notes</th>
                                <th class="p-3 text-center">Line</th>
                                <th class="p-3 text-center">Tank Size</th>
                                <th class="p-3 text-center">Volume (L)</th>
                                <th class="p-3 text-center">Fish Count</th>
                                <th class="p-3 text-center">Density (Fish/L)</th>
                                <th class="p-3 text-center">Compliance Status</th>
                            </tr>
                        </thead>
                        <tbody id="densityTableBody" class="divide-y divide-slate-800">
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ==================== TAB 7: RISK ALERTS ==================== -->
        <section id="tab-alerts" class="tab-content hidden space-y-4">
            <div class="glass p-5 rounded-xl shadow-lg">
                <h2 class="text-lg font-bold text-white mb-1">⚠️ Active Colony Risk & Bottleneck Alerts</h2>
                <p class="text-xs text-slate-400 mb-4">Urgent management actions required for turnover renewal, high density, and sex imbalances.</p>

                <div id="alertsContainer" class="space-y-3">
                </div>
            </div>
        </section>

    </main>

    <!-- Embedded Core Analysis & Interactive Engine -->
    <script>
        // Initial Dataset
        const DEFAULT_RECORDS = __RECORDS_JSON__;
        let currentRecords = JSON.parse(JSON.stringify(DEFAULT_RECORDS));
        
        // State
        let computedData = null;
        let network = null;
        let selectedNodeId = null;
        let chartInstances = {};

        // Reference Date (Oct 1, 2026 or Current Date)
        const REF_DATE = new Date(2026, 9, 1); // Oct 1, 2026

        // 4 Primary Lines Definition
        const TARGET_LINES = ['AB', 'Casper', 'Fli', 'Gata'];

        // Line Colors
        const LINE_COLORS = {
            'AB': { bg: '#fbbf24', border: '#d97706', text: '#78350f' },
            'Casper': { bg: '#38bdf8', border: '#0284c7', text: '#0c4a6e' },
            'Fli': { bg: '#4ade80', border: '#16a34a', text: '#14532d' },
            'Gata': { bg: '#f472b6', border: '#db2777', text: '#831843' },
            'Other': { bg: '#cbd5e1', border: '#64748b', text: '#1e293b' },
            'Euthanized': { bg: '#64748b', border: '#334155', text: '#f8fafc' }
        };

        function categorizeLine(notes) {
            if (!notes) return 'Other';
            const n = notes.toLowerCase().trim();
            if (n.includes('casper') || n.includes('cas/') || n.split(/\s+/).includes('cas')) return 'Casper';
            if (n.includes('fli')) return 'Fli';
            if (n.includes('gata')) return 'Gata';
            if (n.includes('ab') || n.includes('wt') || n.includes('wild')) return 'AB';
            return 'Other';
        }

        function isStatusActive(status) {
            if (!status) return true;
            const s = status.toLowerCase().trim();
            if (s.includes('euth') || s.includes('dead') || s.includes('arch') || s.includes('cull')) return false;
            return true;
        }

        function parseDateString(dStr) {
            if (!dStr) return null;
            dStr = dStr.trim();
            
            // Format 29-Jun-26, 18-Jun-2026
            const monthMap = {
                'jan': 0, 'feb': 1, 'mar': 2, 'apr': 3, 'may': 4, 'jun': 5,
                'jul': 6, 'aug': 7, 'sep': 8, 'oct': 9, 'nov': 10, 'dec': 11
            };
            const parts = dStr.split(/[-/]/);
            if (parts.length === 3) {
                let day = parseInt(parts[0]);
                let monStr = parts[1].toLowerCase().substring(0, 3);
                let year = parseInt(parts[2]);
                if (year < 100) year += 2000;
                
                if (monthMap[monStr] !== undefined) {
                    return new Date(year, monthMap[monStr], day);
                }
                let month = parseInt(parts[1]) - 1;
                if (!isNaN(month) && month >= 0 && month <= 11) {
                    return new Date(year, month, day);
                }
            }
            const d = new Date(dStr);
            return isNaN(d.getTime()) ? null : d;
        }

        function parseVolume(volStr) {
            if (!volStr) return 0.0;
            const m = String(volStr).match(/([\\d\\.]+)/);
            return m ? parseFloat(m[1]) : 0.0;
        }

        // Full In-Browser Analytics Calculation Engine
        function runFullAnalysis(records) {
            const tanksMap = {};
            records.forEach(r => {
                tanksMap[r['TUID']] = r;
            });

            const parentsMap = {};
            const childrenMap = {};

            records.forEach(r => {
                const tuid = r['TUID'];
                const pat = (r['PATERNAL'] || '').trim();
                const mat = (r['MATERNAL'] || '').trim();
                const pValid = tanksMap[pat] ? pat : null;
                const mValid = tanksMap[mat] ? mat : null;
                parentsMap[tuid] = [pValid, mValid];

                if (pValid) {
                    if (!childrenMap[pValid]) childrenMap[pValid] = [];
                    childrenMap[pValid].push(tuid);
                }
                if (mValid && mValid !== pValid) {
                    if (!childrenMap[mValid]) childrenMap[mValid] = [];
                    childrenMap[mValid].push(tuid);
                }
            });

            // Generation depth
            const genDepth = {};
            function calcDepth(t) {
                if (genDepth[t] !== undefined) return genDepth[t];
                const [p, m] = parentsMap[t] || [null, null];
                if (!p && !m) {
                    genDepth[t] = 0;
                    return 0;
                }
                const dp = p ? calcDepth(p) : 0;
                const dm = m ? calcDepth(m) : 0;
                genDepth[t] = 1 + Math.max(dp, dm);
                return genDepth[t];
            }
            Object.keys(tanksMap).forEach(t => calcDepth(t));

            // Kinship Matrix & Inbreeding
            const allIds = Object.keys(tanksMap).sort((a, b) => (genDepth[a] - genDepth[b]) || a.localeCompare(b));
            const A = {};
            allIds.forEach(id => { A[id] = {}; });

            allIds.forEach(i => {
                const [si, di] = parentsMap[i] || [null, null];
                if (si && di && A[si] && A[si][di] !== undefined) {
                    A[i][i] = 1.0 + 0.5 * A[si][di];
                } else {
                    A[i][i] = 1.0;
                }
                allIds.forEach(j => {
                    if (i === j) return;
                    const [sj, dj] = parentsMap[j] || [null, null];
                    let val = 0.0;
                    if (sj && dj) {
                        val = 0.5 * ((A[i][sj] || 0.0) + (A[i][dj] || 0.0));
                    } else if (sj) {
                        val = 0.5 * (A[i][sj] || 0.0);
                    } else if (dj) {
                        val = 0.5 * (A[i][dj] || 0.0);
                    }
                    A[i][j] = val;
                    if (A[j]) A[j][i] = val;
                });
            });

            const inbreedingCoeffs = {};
            allIds.forEach(i => {
                const [si, di] = parentsMap[i] || [null, null];
                if (si && di && A[si] && A[si][di] !== undefined) {
                    inbreedingCoeffs[i] = parseFloat((0.5 * A[si][di]).toFixed(4));
                } else {
                    inbreedingCoeffs[i] = 0.0;
                }
            });

            // Enrich all records
            const enriched = records.map(r => {
                const tuid = r['TUID'];
                const stRaw = r['STATUS'] || '';
                const isActive = isStatusActive(stRaw);
                const line = categorizeLine(r['NOTES']);
                
                const female = parseInt(r['FEMALE']) || 0;
                const male = parseInt(r['MALE']) || 0;
                const total = parseInt(r['TOTAL']) || 0;
                const unsexed = Math.max(0, total - (female + male));

                const dob = parseDateString(r['DOB']);
                const turnover = parseDateString(r['TURNOVER']);
                const dod = parseDateString(r['DOD']);

                let ageMonths = null;
                if (dob) {
                    const refEnd = (!isActive && dod) ? dod : REF_DATE;
                    const diffDays = Math.round((refEnd - dob) / (1000 * 60 * 60 * 24));
                    ageMonths = parseFloat((diffDays / 30.4375).toFixed(1));
                }

                let lifecycle = 'Active (Unknown Age)';
                if (!isActive) {
                    lifecycle = 'Euthanized / Archived';
                } else if (ageMonths !== null) {
                    if (ageMonths < 3) lifecycle = 'Juvenile / Nursery (<3m)';
                    else if (ageMonths <= 6) lifecycle = 'Young Adult (3-6m)';
                    else if (ageMonths <= 12) lifecycle = 'Prime Breeding (6-12m)';
                    else if (ageMonths <= 18) lifecycle = 'Mature Stock (12-18m)';
                    else lifecycle = 'Geriatric / Overdue (>18m)';
                }

                let daysToTurnover = null;
                let turnoverUrgency = 'N/A';
                let turnoverAction = 'Inactive or No date set.';

                if (turnover && isActive) {
                    daysToTurnover = Math.round((turnover - REF_DATE) / (1000 * 60 * 60 * 24));
                    if (daysToTurnover < 0) {
                        turnoverUrgency = 'OVERDUE';
                        turnoverAction = `CRITICAL: ${Math.abs(daysToTurnover)} days past turnover. Renewal cross or euthanasia required.`;
                    } else if (daysToTurnover <= 30) {
                        turnoverUrgency = 'DUE SOON (<=30d)';
                        turnoverAction = `HIGH: Turnover in ${daysToTurnover} days. Setup renewal breeding tank now.`;
                    } else if (daysToTurnover <= 60) {
                        turnoverUrgency = 'UPCOMING (31-60d)';
                        turnoverAction = `MEDIUM: Turnover in ${daysToTurnover} days. Schedule next generation cross.`;
                    } else if (daysToTurnover <= 90) {
                        turnoverUrgency = 'UPCOMING (61-90d)';
                        turnoverAction = `LOW: Turnover in ${daysToTurnover} days. Monitor stock health.`;
                    } else {
                        turnoverUrgency = 'FUTURE (>90d)';
                        turnoverAction = 'Normal active holding.';
                    }
                }

                const tankVal = r['TANK '] || r['TANK'] || '';
                const vol = parseVolume(tankVal);
                let fishPerLiter = 0.0;
                let densityStatus = 'Empty / Unknown';

                if (vol > 0 && total > 0) {
                    fishPerLiter = parseFloat((total / vol).toFixed(2));
                    if (fishPerLiter < 1.0) densityStatus = 'Understocked (<1.0 fish/L)';
                    else if (fishPerLiter <= 6.0) densityStatus = 'Optimal (1.0 - 6.0 fish/L)';
                    else if (fishPerLiter <= 8.0) densityStatus = 'Moderate / Acceptable (6.1 - 8.0 fish/L)';
                    else densityStatus = 'OVERSTOCKED (>8.0 fish/L - Welfare Alert)';
                }

                return {
                    ...r,
                    Is_Active: isActive,
                    Status_Clean: !isActive ? 'Euthanized' : (stRaw.toLowerCase().includes('juv') ? 'Juvenile (<3m)' : 'Adult/Active'),
                    Line_Category: line,
                    Gen_Depth: genDepth[tuid] || 0,
                    Inbreeding_F: inbreedingCoeffs[tuid] || 0.0,
                    Sire: parentsMap[tuid] ? parentsMap[tuid][0] || '' : '',
                    Dam: parentsMap[tuid] ? parentsMap[tuid][1] || '' : '',
                    Progeny_Count: childrenMap[tuid] ? childrenMap[tuid].length : 0,
                    Progeny_Tanks: childrenMap[tuid] ? childrenMap[tuid].join(', ') : '',
                    Female_Count: female,
                    Male_Count: male,
                    Total_Count: total,
                    Unsexed_Count: unsexed,
                    Age_Months: ageMonths,
                    Lifecycle_Stage: lifecycle,
                    Days_To_Turnover: daysToTurnover,
                    Turnover_Urgency: turnoverUrgency,
                    Turnover_Action: turnoverAction,
                    Volume_L: vol,
                    Tank_Display: tankVal,
                    Fish_Per_Liter: fishPerLiter,
                    Density_Status: densityStatus
                };
            });

            // Aggregate by 4 Primary Lines
            const lineStats = [];
            const allCategories = ['AB', 'Casper', 'Fli', 'Gata'];
            
            // Check if there are other categories
            enriched.forEach(r => {
                if (!allCategories.includes(r.Line_Category) && !allCategories.includes(r.Line_Category)) {
                    allCategories.push(r.Line_Category);
                }
            });

            allCategories.forEach(lName => {
                const list = enriched.filter(r => r.Line_Category === lName);
                const activeList = list.filter(r => r.Is_Active);
                const euthList = list.filter(r => !r.Is_Active);

                const actFish = activeList.reduce((acc, r) => acc + r.Total_Count, 0);
                const actF = activeList.reduce((acc, r) => acc + r.Female_Count, 0);
                const actM = activeList.reduce((acc, r) => acc + r.Male_Count, 0);

                const ages = activeList.map(r => r.Age_Months).filter(a => a !== null);
                const avgAge = ages.length ? parseFloat((ages.reduce((a,b)=>a+b,0)/ages.length).toFixed(1)) : 0;

                const inbreds = activeList.map(r => r.Inbreeding_F);
                const avgF = inbreds.length ? parseFloat((inbreds.reduce((a,b)=>a+b,0)/inbreds.length).toFixed(3)) : 0.0;

                let risk = 'Optimal';
                const reasons = [];
                if (activeList.length === 0) {
                    risk = 'Extinct / Inactive';
                    reasons.push('No active tanks');
                } else if (activeList.length === 1) {
                    risk = 'CRITICAL (Single Tank)';
                    reasons.push('Only 1 active tank remaining');
                } else if (actFish < 10) {
                    risk = 'HIGH (Low Biomass)';
                    reasons.push(`Only ${actFish} total fish`);
                }

                if (activeList.length > 0) {
                    if (actF === 0 && actM > 0) {
                        risk = 'CRITICAL (No Females)';
                        reasons.push('0 breeding females available');
                    } else if (actM === 0 && actF > 0) {
                        risk = 'HIGH (No Males)';
                        reasons.push('0 breeding males available');
                    }
                    if (avgAge > 16) {
                        reasons.push('Aging stock (>16m avg age)');
                        if (risk === 'Optimal') risk = 'MEDIUM (Aging Stock)';
                    }
                }

                lineStats.push({
                    Line: lName,
                    Active_Tanks: activeList.length,
                    Euthanized_Tanks: euthList.length,
                    Total_Active_Fish: actFish,
                    Active_Females: actF,
                    Active_Males: actM,
                    Sex_Ratio: actM > 0 ? `${(actF/actM).toFixed(2)}:1` : `${actF}:0`,
                    Avg_Age_Months: avgAge,
                    Avg_Inbreeding_F: avgF,
                    Risk_Level: risk,
                    Risk_Reasons: reasons.length ? reasons.join('; ') : 'Healthy colony demographics'
                });
            });

            // Cross Aggregations
            const crossMap = {};
            enriched.forEach(r => {
                const cId = (r['Derivative cross'] || '').trim();
                if (cId) {
                    if (!crossMap[cId]) crossMap[cId] = [];
                    crossMap[cId].push(r);
                }
            });

            const crossStats = Object.keys(crossMap).sort().map(cId => {
                const clist = crossMap[cId];
                const activeList = clist.filter(r => r.Is_Active);
                const totalFish = clist.reduce((acc, r) => acc + r.Total_Count, 0);
                const activeFish = activeList.reduce((acc, r) => acc + r.Total_Count, 0);
                const activeF = activeList.reduce((acc, r) => acc + r.Female_Count, 0);
                const activeM = activeList.reduce((acc, r) => acc + r.Male_Count, 0);

                const parentsSet = Array.from(new Set(clist.map(r => `${r.PATERNAL || '?'} x ${r.MATERNAL || '?'}`)));
                const linesSet = Array.from(new Set(clist.map(r => r.Line_Category)));

                return {
                    Cross_ID: cId,
                    Parental_Cross: parentsSet.join('; '),
                    Lines: linesSet.join(', '),
                    DOB: clist[0].DOB || '',
                    Tanks_Count: clist.length,
                    Active_Tanks: activeList.length,
                    Total_Fish_Yield: totalFish,
                    Active_Fish: activeFish,
                    Active_Females: activeF,
                    Active_Males: activeM,
                    Avg_Fish_Per_Tank: parseFloat((totalFish / clist.length).toFixed(1)),
                    Tank_List: clist.map(r => r.TUID).join(', ')
                };
            });

            // Risk Alerts
            const alerts = [];
            enriched.forEach(r => {
                if (!r.Is_Active) return;
                if (r.Turnover_Urgency === 'OVERDUE') {
                    alerts.push({
                        TUID: r.TUID,
                        Line: r.Line_Category,
                        Category: 'Turnover Overdue',
                        Severity: 'CRITICAL',
                        Description: `Tank is ${Math.abs(r.Days_To_Turnover)} days past 540-day turnover (DOB: ${r.DOB || 'N/A'}).`,
                        Action: 'Cross immediately or evaluate for colony retirement.'
                    });
                } else if (r.Turnover_Urgency.includes('DUE SOON')) {
                    alerts.push({
                        TUID: r.TUID,
                        Line: r.Line_Category,
                        Category: 'Turnover Due Soon',
                        Severity: 'HIGH',
                        Description: `Reaches turnover in ${r.Days_To_Turnover} days (DOB: ${r.DOB || 'N/A'}).`,
                        Action: 'Schedule next-generation cross this week.'
                    });
                }
                if (r.Density_Status.includes('OVERSTOCKED')) {
                    alerts.push({
                        TUID: r.TUID,
                        Line: r.Line_Category,
                        Category: 'Animal Welfare (Density)',
                        Severity: 'HIGH',
                        Description: `Stocking density of ${r.Fish_Per_Liter} fish/L in ${r.Volume_L}L tank (${r.Total_Count} fish).`,
                        Action: 'Split tank into secondary holding tank.'
                    });
                }
                if (r.Total_Count > 0 && r.Age_Months && r.Age_Months >= 4) {
                    if (r.Female_Count === 0 && r.Male_Count > 0) {
                        alerts.push({
                            TUID: r.TUID,
                            Line: r.Line_Category,
                            Category: 'Single-Sex Tank (All Males)',
                            Severity: 'MEDIUM',
                            Description: `Contains only ${r.Male_Count} males (0 females).`,
                            Action: 'Identify compatible female tank for future cross.'
                        });
                    } else if (r.Male_Count === 0 && r.Female_Count > 0) {
                        alerts.push({
                            TUID: r.TUID,
                            Line: r.Line_Category,
                            Category: 'Single-Sex Tank (All Females)',
                            Severity: 'MEDIUM',
                            Description: `Contains only ${r.Female_Count} females (0 males).`,
                            Action: 'Identify compatible male tank for future cross.'
                        });
                    }
                }
            });

            return {
                records: enriched,
                lineStats: lineStats,
                crossStats: crossStats,
                alerts: alerts
            };
        }

        // Update UI Elements
        function updateDashboardUI(data) {
            computedData = data;
            const records = data.records;
            const lineStats = data.lineStats;
            const crossStats = data.crossStats;
            const alerts = data.alerts;

            const activeRecords = records.filter(r => r.Is_Active);
            const totalActiveFish = activeRecords.reduce((a, r) => a + r.Total_Count, 0);
            const totalFemales = activeRecords.reduce((a, r) => a + r.Female_Count, 0);
            const totalMales = activeRecords.reduce((a, r) => a + r.Male_Count, 0);
            const overdueCount = activeRecords.filter(r => r.Turnover_Urgency === 'OVERDUE').length;

            // KPIs
            document.getElementById('loadedRecordsCount').innerText = records.length;
            document.getElementById('kpiActiveTanks').innerText = activeRecords.length;
            document.getElementById('kpiTotalTanks').innerText = records.length;
            document.getElementById('kpiActiveFish').innerText = totalActiveFish.toLocaleString();
            document.getElementById('kpiFemales').innerText = totalFemales.toLocaleString();
            document.getElementById('kpiFemalesPct').innerText = `${( (totalFemales / Math.max(1, totalActiveFish)) * 100 ).toFixed(1)}% of colony`;
            document.getElementById('kpiMales').innerText = totalMales.toLocaleString();
            document.getElementById('kpiMalesPct').innerText = `${( (totalMales / Math.max(1, totalActiveFish)) * 100 ).toFixed(1)}% of colony`;
            document.getElementById('kpiCrosses').innerText = crossStats.length;
            document.getElementById('kpiOverdue').innerText = overdueCount;

            // Tab badges
            document.getElementById('tabCountTurnover').innerText = overdueCount;
            document.getElementById('tabCountCrosses').innerText = crossStats.length;
            document.getElementById('tabCountAlerts').innerText = alerts.length;

            // Render Subsections
            renderCharts(data);
            renderTurnoverTable();
            renderLinesCards();
            renderCrossesTable();
            renderDensityTable();
            renderAlerts();
            renderPedigreeNetwork();
        }

        // Render Charts
        function renderCharts(data) {
            const records = data.records;
            const lineStats = data.lineStats;
            const activeRecords = records.filter(r => r.Is_Active);

            // Destroy existing charts if reloading
            Object.values(chartInstances).forEach(c => c.destroy());
            chartInstances = {};

            // 1. Strains Chart (4 Primary Lines)
            const targetLines = ['AB', 'Casper', 'Fli', 'Gata'];
            const lineLabels = targetLines;
            const lineFishCounts = targetLines.map(l => {
                const st = lineStats.find(x => x.Line === l);
                return st ? st.Total_Active_Fish : 0;
            });
            const lineTankCounts = targetLines.map(l => {
                const st = lineStats.find(x => x.Line === l);
                return st ? st.Active_Tanks : 0;
            });

            chartInstances['strains'] = new Chart(document.getElementById('chartStrains'), {
                type: 'bar',
                data: {
                    labels: lineLabels,
                    datasets: [
                        { label: 'Active Fish', data: lineFishCounts, backgroundColor: ['#fbbf24', '#38bdf8', '#4ade80', '#f472b6'], borderRadius: 6 },
                        { label: 'Active Tanks', data: lineTankCounts, backgroundColor: '#64748b', borderRadius: 6 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#cbd5e1' } } },
                    scales: {
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                    }
                }
            });

            // 2. Lifecycle Structure
            const stageOrder = ['Juvenile / Nursery (<3m)', 'Young Adult (3-6m)', 'Prime Breeding (6-12m)', 'Mature Stock (12-18m)', 'Geriatric / Overdue (>18m)'];
            const stageCounts = stageOrder.map(st => activeRecords.filter(r => r.Lifecycle_Stage === st).length);

            chartInstances['age'] = new Chart(document.getElementById('chartAgeStructure'), {
                type: 'bar',
                data: {
                    labels: stageOrder,
                    datasets: [{
                        label: 'Active Tanks',
                        data: stageCounts,
                        backgroundColor: ['#38bdf8', '#4ade80', '#10b981', '#f59e0b', '#f43f5e'],
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 9 } } }
                    }
                }
            });

            // 3. Sex Ratio Doughnut
            const totalF = activeRecords.reduce((a, r) => a + r.Female_Count, 0);
            const totalM = activeRecords.reduce((a, r) => a + r.Male_Count, 0);
            const totalU = activeRecords.reduce((a, r) => a + r.Unsexed_Count, 0);

            chartInstances['sex'] = new Chart(document.getElementById('chartSexRatio'), {
                type: 'doughnut',
                data: {
                    labels: ['Females', 'Males', 'Juvenile / Unsexed'],
                    datasets: [{
                        data: [totalF, totalM, totalU],
                        backgroundColor: ['#ec4899', '#3b82f6', '#94a3b8'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom', labels: { color: '#cbd5e1', font: { size: 10 } } } }
                }
            });

            // 4. Tank Sizes
            const tankSizes = ['1.8L', '2.8L', '3.5L', '6.0L', '8.0L'];
            const tankCounts = [1.8, 2.8, 3.5, 6.0, 8.0].map(v => activeRecords.filter(r => r.Volume_L === v).length);

            chartInstances['tanks'] = new Chart(document.getElementById('chartTankSizes'), {
                type: 'pie',
                data: {
                    labels: tankSizes,
                    datasets: [{
                        data: tankCounts,
                        backgroundColor: ['#0284c7', '#0d9488', '#8b5cf6', '#f59e0b', '#ec4899'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom', labels: { color: '#cbd5e1', font: { size: 10 } } } }
                }
            });

            // 5. Inbreeding Chart
            const f0 = activeRecords.filter(r => r.Inbreeding_F === 0.0).length;
            const fHalf = activeRecords.filter(r => r.Inbreeding_F > 0.0 && r.Inbreeding_F < 0.5).length;
            const fSib = activeRecords.filter(r => r.Inbreeding_F >= 0.5).length;

            chartInstances['inbreeding'] = new Chart(document.getElementById('chartInbreeding'), {
                type: 'bar',
                data: {
                    labels: ['F = 0.0 (Outbred)', '0 < F < 0.5', 'F >= 0.5 (Incross)'],
                    datasets: [{
                        label: 'Tanks',
                        data: [f0, fHalf, fSib],
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } }
                    }
                }
            });
        }

        // Render Turnover Table
        function renderTurnoverTable() {
            const tbody = document.getElementById('turnoverTableBody');
            tbody.innerHTML = '';
            if (!computedData) return;

            const filterVal = document.getElementById('turnoverFilter').value;
            let activeTanks = computedData.records.filter(r => r.Is_Active);
            activeTanks.sort((a, b) => (a.Days_To_Turnover !== null ? a.Days_To_Turnover : 9999) - (b.Days_To_Turnover !== null ? b.Days_To_Turnover : 9999));

            activeTanks.forEach(r => {
                const urg = r.Turnover_Urgency;
                if (filterVal === 'OVERDUE' && urg !== 'OVERDUE') return;
                if (filterVal === 'SOON' && !urg.includes('DUE SOON')) return;
                if (filterVal === 'UPCOMING' && !urg.includes('UPCOMING')) return;

                const badgeClass = urg === 'OVERDUE' ? 'badge-critical' : (urg.includes('DUE SOON') ? 'badge-high' : 'badge-optimal');
                const daysTxt = r.Days_To_Turnover !== null ? (r.Days_To_Turnover < 0 ? `${Math.abs(r.Days_To_Turnover)}d past` : `${r.Days_To_Turnover}d`) : '-';

                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/50 transition';
                tr.innerHTML = `
                    <td class="p-3 font-bold text-teal-400">${r.TUID}</td>
                    <td class="p-3"><span class="badge badge-optimal">${r.Status_Clean}</span></td>
                    <td class="p-3 max-w-[200px] truncate" title="${r.NOTES || ''}">${r.NOTES || ''}</td>
                    <td class="p-3 text-center font-semibold">${r.Line_Category}</td>
                    <td class="p-3 text-center font-mono">${r.Female_Count}F / ${r.Male_Count}M / <b>${r.Total_Count}</b></td>
                    <td class="p-3 text-center">${r.DOB || ''}</td>
                    <td class="p-3 text-center">${r.TURNOVER || ''}</td>
                    <td class="p-3 text-center font-bold ${r.Days_To_Turnover && r.Days_To_Turnover < 0 ? 'text-rose-400' : 'text-slate-300'}">${daysTxt}</td>
                    <td class="p-3 text-center"><span class="badge ${badgeClass}">${urg}</span></td>
                    <td class="p-3 text-slate-300">${r.Turnover_Action}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Render 4 Primary Lines Cards
        function renderLinesCards() {
            const container = document.getElementById('linesCardsContainer');
            container.innerHTML = '';
            if (!computedData) return;

            const targetLines = ['AB', 'Casper', 'Fli', 'Gata'];
            targetLines.forEach(lName => {
                const ls = computedData.lineStats.find(x => x.Line === lName) || {
                    Line: lName, Active_Tanks: 0, Euthanized_Tanks: 0, Total_Active_Fish: 0, Active_Females: 0, Active_Males: 0, Sex_Ratio: '0:0', Avg_Age_Months: 0, Avg_Inbreeding_F: 0, Risk_Level: 'No Data', Risk_Reasons: 'No records found'
                };

                const borderCol = ls.Risk_Level.includes('CRITICAL') ? 'border-rose-500' : (ls.Risk_Level.includes('HIGH') || ls.Risk_Level.includes('MEDIUM') ? 'border-amber-500' : 'border-teal-500');
                const badgeClass = ls.Risk_Level.includes('CRITICAL') ? 'badge-critical' : (ls.Risk_Level.includes('HIGH') || ls.Risk_Level.includes('MEDIUM') ? 'badge-high' : 'badge-optimal');

                const card = document.createElement('div');
                card.className = `glass-card p-4 rounded-xl border-l-4 ${borderCol} space-y-3`;
                card.innerHTML = `
                    <div class="flex items-start justify-between">
                        <div>
                            <h3 class="font-bold text-lg text-white">${ls.Line}</h3>
                            <p class="text-xs text-slate-400">${ls.Active_Tanks} active tanks (${ls.Euthanized_Tanks} euthanized)</p>
                        </div>
                        <span class="badge ${badgeClass}">${ls.Risk_Level}</span>
                    </div>

                    <div class="grid grid-cols-3 gap-2 text-center bg-slate-800/60 p-2.5 rounded-lg text-xs">
                        <div>
                            <p class="text-slate-400 text-[10px]">TOTAL FISH</p>
                            <p class="font-bold text-sm text-teal-400 mt-0.5">${ls.Total_Active_Fish}</p>
                        </div>
                        <div>
                            <p class="text-slate-400 text-[10px]">FEMALES</p>
                            <p class="font-bold text-sm text-pink-400 mt-0.5">${ls.Active_Females}</p>
                        </div>
                        <div>
                            <p class="text-slate-400 text-[10px]">MALES</p>
                            <p class="font-bold text-sm text-blue-400 mt-0.5">${ls.Active_Males}</p>
                        </div>
                    </div>

                    <div class="space-y-1 text-xs">
                        <div class="flex justify-between text-slate-300">
                            <span class="text-slate-400">Sex Ratio (F:M):</span>
                            <span class="font-semibold">${ls.Sex_Ratio}</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span class="text-slate-400">Average Age:</span>
                            <span class="font-semibold">${ls.Avg_Age_Months} months</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span class="text-slate-400">Average Inbreeding (F):</span>
                            <span class="font-semibold text-amber-400">${ls.Avg_Inbreeding_F}</span>
                        </div>
                    </div>

                    <div class="bg-slate-900/80 p-2 rounded text-[11px] text-slate-400 border border-slate-800">
                        <b>Status:</b> ${ls.Risk_Reasons}
                    </div>
                `;
                container.appendChild(card);
            });
        }

        // Render Crosses Table
        function renderCrossesTable() {
            const tbody = document.getElementById('crossesTableBody');
            tbody.innerHTML = '';
            if (!computedData) return;

            computedData.crossStats.forEach(cs => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/50 transition';
                tr.innerHTML = `
                    <td class="p-3 font-bold text-purple-400">${cs.Cross_ID}</td>
                    <td class="p-3 font-semibold text-slate-200">${cs.Parental_Cross}</td>
                    <td class="p-3 text-center font-medium">${cs.Lines}</td>
                    <td class="p-3 text-center">${cs.DOB}</td>
                    <td class="p-3 text-center font-bold text-teal-400">${cs.Tanks_Count} (${cs.Active_Tanks} act)</td>
                    <td class="p-3 text-center font-bold text-teal-300">${cs.Active_Fish}</td>
                    <td class="p-3 text-center font-mono">${cs.Active_Females}F / ${cs.Active_Males}M</td>
                    <td class="p-3 text-center">${cs.Avg_Fish_Per_Tank}</td>
                    <td class="p-3 text-slate-400 max-w-[200px] truncate" title="${cs.Tank_List}">${cs.Tank_List}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Render Density Table
        function renderDensityTable() {
            const tbody = document.getElementById('densityTableBody');
            tbody.innerHTML = '';
            if (!computedData) return;

            const activeDensity = computedData.records.filter(r => r.Is_Active);
            activeDensity.sort((a, b) => b.Fish_Per_Liter - a.Fish_Per_Liter);

            activeDensity.forEach(r => {
                const dClass = r.Density_Status.includes('OVERSTOCKED') ? 'badge-critical' : (r.Density_Status.includes('Understocked') ? 'badge-info' : 'badge-optimal');
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/50 transition';
                tr.innerHTML = `
                    <td class="p-3 font-bold text-teal-400">${r.TUID}</td>
                    <td class="p-3"><span class="badge badge-optimal">${r.Status_Clean}</span></td>
                    <td class="p-3 max-w-[200px] truncate">${r.NOTES || ''}</td>
                    <td class="p-3 text-center">${r.Line_Category}</td>
                    <td class="p-3 text-center">${r.Tank_Display}</td>
                    <td class="p-3 text-center">${r.Volume_L}L</td>
                    <td class="p-3 text-center font-bold text-slate-200">${r.Total_Count}</td>
                    <td class="p-3 text-center font-bold ${r.Density_Status.includes('OVERSTOCKED') ? 'text-rose-400' : 'text-teal-400'}">${r.Fish_Per_Liter}</td>
                    <td class="p-3 text-center"><span class="badge ${dClass}">${r.Density_Status}</span></td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Render Alerts
        function renderAlerts() {
            const container = document.getElementById('alertsContainer');
            container.innerHTML = '';
            if (!computedData) return;

            computedData.alerts.forEach(alt => {
                const borderCol = alt.Severity === 'CRITICAL' ? 'border-rose-500' : (alt.Severity === 'HIGH' ? 'border-amber-500' : 'border-blue-500');
                const badgeClass = alt.Severity === 'CRITICAL' ? 'badge-critical' : (alt.Severity === 'HIGH' ? 'badge-high' : 'badge-info');

                const card = document.createElement('div');
                card.className = `glass-card p-4 rounded-xl border-l-4 ${borderCol} flex flex-col md:flex-row md:items-center justify-between gap-4`;
                card.innerHTML = `
                    <div class="space-y-1">
                        <div class="flex items-center gap-2">
                            <span class="badge ${badgeClass}">${alt.Severity}</span>
                            <span class="font-bold text-teal-400">${alt.TUID}</span>
                            <span class="text-xs text-slate-400">• ${alt.Line} • <b>${alt.Category}</b></span>
                        </div>
                        <p class="text-xs text-slate-300">${alt.Description}</p>
                    </div>
                    <div class="bg-slate-900/80 px-3 py-2 rounded-lg border border-slate-800 text-xs text-teal-300 md:max-w-xs">
                        <b>Action:</b> ${alt.Action}
                    </div>
                `;
                container.appendChild(card);
            });
        }

        
        // ==================== 4-MODE PEDIGREE ENGINE ====================
        let currentPedigreeMode = 'focal';
        let currentFocalTUID = 'T0135';
        let currentLineTree = 'AB';
        let treeTableExpandedNodes = new Set(['AB', 'Casper', 'Fli', 'Gata']);

        function switchPedigreeMode(mode) {
            currentPedigreeMode = mode;
            ['focal', 'lines', 'table', 'network'].forEach(m => {
                const sub = document.getElementById('ped-subview-' + m);
                const btn = document.getElementById('ped-btn-' + m);
                if (sub) {
                    if (m === mode) {
                        sub.classList.remove('hidden');
                    } else {
                        sub.classList.add('hidden');
                    }
                }
                if (btn) {
                    if (m === mode) {
                        btn.className = 'ped-mode-btn active px-3 py-1.5 rounded-lg text-xs font-semibold bg-teal-600 text-white transition flex items-center gap-1.5 shadow-sm';
                    } else {
                        btn.className = 'ped-mode-btn px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5';
                    }
                }
            });

            if (mode === 'focal') {
                populateFocalDropdown();
                renderFocalPedigreeTree(currentFocalTUID);
            } else if (mode === 'lines') {
                renderLineTrees(currentLineTree);
            } else if (mode === 'table') {
                renderTreeTable();
            } else if (mode === 'network') {
                setTimeout(renderPedigreeNetwork, 50);
            }
        }

        function populateFocalDropdown() {
            if (!computedData) return;
            const select = document.getElementById('focalTankSelect');
            if (!select) return;
            const records = computedData.records;
            select.innerHTML = '';

            // Group by Line
            const lines = ['AB', 'Casper', 'Fli', 'Gata', 'Other'];
            lines.forEach(ln => {
                const grp = records.filter(r => r.Line_Category === ln);
                if (grp.length > 0) {
                    const optGroup = document.createElement('optgroup');
                    optGroup.label = `${ln} Line (${grp.length} tanks)`;
                    grp.forEach(r => {
                        const opt = document.createElement('option');
                        opt.value = r.TUID;
                        const mixTag = r.Is_Mix ? ' [🔀 Mix]' : '';
                        const stTag = !r.Is_Active ? ' (Euthanized)' : '';
                        opt.innerText = `${r.TUID} - Gen F${r.Gen_Depth} (Fish: ${r.Total_Count})${mixTag}${stTag}`;
                        if (r.TUID === currentFocalTUID) opt.selected = true;
                        optGroup.appendChild(opt);
                    });
                    select.appendChild(optGroup);
                }
            });
        }

        function changeFocalTank(tuid) {
            currentFocalTUID = tuid;
            renderFocalPedigreeTree(tuid);
        }

        function searchAndFocusTank() {
            const val = (document.getElementById('focalSearchInput').value || '').trim().toUpperCase();
            if (!val || !computedData) return;
            const found = computedData.records.find(r => r.TUID.toUpperCase() === val || r.TUID.toUpperCase().endsWith(val.replace(/^T0*/, '')));
            if (found) {
                currentFocalTUID = found.TUID;
                const select = document.getElementById('focalTankSelect');
                if (select) select.value = found.TUID;
                renderFocalPedigreeTree(found.TUID);
            } else {
                alert(`Tank '${val}' not found in colony records.`);
            }
        }

        function renderFocalPedigreeTree(tuid) {
            if (!computedData) return;
            const records = computedData.records;
            const tanksMap = {};
            records.forEach(r => { tanksMap[r.TUID] = r; });

            const focal = tanksMap[tuid] || records[0];
            if (!focal) return;
            currentFocalTUID = focal.TUID;

            const select = document.getElementById('focalTankSelect');
            if (select && select.value !== focal.TUID) select.value = focal.TUID;

            // 1. Build Breadcrumb Ancestry Trail
            const trail = [];
            let curr = focal;
            const visited = new Set();
            while (curr && !visited.has(curr.TUID)) {
                visited.add(curr.TUID);
                trail.unshift(curr);
                const p = curr.Sire || curr.Dam;
                curr = p ? tanksMap[p] : null;
            }

            const trailEl = document.getElementById('focalBreadcrumbTrail');
            if (trailEl) {
                let trailHtml = '';
                trail.forEach((node, idx) => {
                    const isLast = idx === trail.length - 1;
                    const genLabel = node.Gen_Depth === 0 ? 'F0 Founder' : `F${node.Gen_Depth}`;
                    const lineCol = node.Line_Category === 'AB' ? 'text-amber-400' : (node.Line_Category === 'Casper' ? 'text-sky-400' : (node.Line_Category === 'Fli' ? 'text-green-400' : 'text-pink-400'));
                    const mixBadge = node.Is_Mix ? '<span class="text-[10px] px-1.5 py-0.2 bg-teal-900/60 text-teal-300 rounded ml-1">🔀 Mix</span>' : '';

                    trailHtml += `
                        <button onclick="changeFocalTank('${node.TUID}')" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg ${isLast ? 'bg-teal-600 text-white font-bold shadow-md' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'} transition">
                            <span>${node.Gen_Depth === 0 ? '🏠' : '🧬'}</span>
                            <span class="${isLast ? 'text-white' : lineCol}">${node.TUID}</span>
                            <span class="text-[10px] opacity-75">(${genLabel})</span>
                            ${mixBadge}
                        </button>
                    `;
                    if (!isLast) {
                        trailHtml += `<span class="text-slate-500">➔</span>`;
                    }
                });
                trailEl.innerHTML = trailHtml;
            }

            // Helper to render mini card
            function createMiniCard(t, relationLabel, isPink=false, isBlue=false) {
                if (!t) {
                    return `
                        <div class="p-3 rounded-lg border border-dashed border-slate-800 bg-slate-900/40 text-center text-slate-600">
                            <span class="text-[11px]">Unrecorded / External Stock</span>
                        </div>
                    `;
                }
                const isEuth = !t.Is_Active;
                const borderCol = isBlue ? 'border-sky-500/50' : (isPink ? 'border-pink-500/50' : (isEuth ? 'border-slate-700' : 'border-slate-700'));
                const bgGrad = isBlue ? 'bg-gradient-to-br from-sky-950/30 to-slate-900' : (isPink ? 'bg-gradient-to-br from-pink-950/30 to-slate-900' : 'bg-slate-900/80');

                return `
                    <div onclick="changeFocalTank('${t.TUID}')" class="cursor-pointer group p-2.5 rounded-xl border ${borderCol} ${bgGrad} hover:border-teal-400 transition hover:shadow-lg space-y-1.5">
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-bold uppercase tracking-wider ${isBlue ? 'text-sky-400' : (isPink ? 'text-pink-400' : 'text-slate-400')}">${relationLabel}</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded ${t.Is_Active ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/40' : 'bg-slate-800 text-slate-400'}">${t.Is_Active ? 'Active' : 'Euth'}</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <h4 class="text-sm font-black text-white group-hover:text-teal-300 transition">${t.TUID}</h4>
                            <span class="text-[11px] font-bold ${t.Line_Category === 'AB' ? 'text-amber-400' : (t.Line_Category === 'Casper' ? 'text-sky-400' : (t.Line_Category === 'Fli' ? 'text-green-400' : 'text-pink-400'))}">${t.Line_Category}</span>
                        </div>
                        <div class="flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/80 pt-1">
                            <span>Fish: <b class="text-slate-200">${t.Total_Count}</b></span>
                            <span>F: <b class="text-amber-400">${t.Inbreeding_F}</b></span>
                            <span>Gen: <b class="text-teal-400">F${t.Gen_Depth}</b></span>
                        </div>
                        ${t.Is_Mix ? '<div class="text-[10px] text-teal-300 bg-teal-950/60 px-1.5 py-0.5 rounded border border-teal-800/40">🔀 Mixed Larvae Batch</div>' : ''}
                    </div>
                `;
            }

            // 2. Col 1: Grandparents
            const sireObj = focal.Sire ? tanksMap[focal.Sire] : null;
            const damObj = focal.Dam ? tanksMap[focal.Dam] : null;

            const patSire = sireObj && sireObj.Sire ? tanksMap[sireObj.Sire] : null;
            const patDam = sireObj && sireObj.Dam ? tanksMap[sireObj.Dam] : null;
            const matSire = damObj && damObj.Sire ? tanksMap[damObj.Sire] : null;
            const matDam = damObj && damObj.Dam ? tanksMap[damObj.Dam] : null;

            let gpColHtml = '';
            if (focal.Gen_Depth === 0) {
                gpColHtml = `
                    <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-2">
                        <span class="text-2xl">🌱</span>
                        <p class="text-xs font-bold text-slate-300">F0 Founder Stock</p>
                        <p class="text-[11px] text-slate-500">No ancestor records preceding founder import.</p>
                    </div>
                `;
            } else {
                gpColHtml = `
                    <div class="space-y-2">
                        <span class="text-[10px] font-bold text-sky-400 uppercase">Paternal Ancestors</span>
                        ${createMiniCard(patSire, 'Paternal Grandfather ♂', false, true)}
                        ${createMiniCard(patDam, 'Paternal Grandmother ♀', true, false)}
                    </div>
                    <div class="space-y-2 pt-2 border-t border-slate-800">
                        <span class="text-[10px] font-bold text-pink-400 uppercase">Maternal Ancestors</span>
                        ${createMiniCard(matSire, 'Maternal Grandfather ♂', false, true)}
                        ${createMiniCard(matDam, 'Maternal Grandmother ♀', true, false)}
                    </div>
                `;
            }
            document.getElementById('treeColGrandparents').innerHTML = gpColHtml;

            // 3. Col 2: Parents
            let parentsColHtml = '';
            if (focal.Is_Mix && focal.Mix_Sources && focal.Mix_Sources.length > 0) {
                parentsColHtml = `
                    <div class="p-3 rounded-xl bg-gradient-to-br from-teal-950/50 to-slate-900 border border-teal-700/60 space-y-2.5">
                        <div class="flex items-center gap-1.5 text-teal-300 font-bold text-xs">
                            <span>🔀</span>
                            <span>Pooled Mating Setups</span>
                        </div>
                        <p class="text-[11px] text-slate-300 leading-relaxed">
                            Larvae from separate single crosses were combined into this communal cohort to maximize genetic vigor.
                        </p>
                        <div class="space-y-1.5 pt-1">
                            <span class="text-[10px] uppercase font-bold text-slate-400">Contributing Source Tanks:</span>
                            <div class="flex flex-wrap gap-1.5">
                                ${focal.Mix_Sources.map(s => `
                                    <button onclick="changeFocalTank('${s}')" class="px-2 py-1 rounded bg-slate-800 hover:bg-teal-700 text-teal-300 hover:text-white border border-slate-700 text-xs font-mono font-bold transition">
                                        ${s} ➔
                                    </button>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `;
            } else if (focal.Gen_Depth === 0) {
                parentsColHtml = `
                    <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-2">
                        <span class="text-2xl">🏛️</span>
                        <p class="text-xs font-bold text-slate-300">Baseline Founder</p>
                        <p class="text-[11px] text-slate-500">Serves as genetic origin ($F=0.0$).</p>
                    </div>
                `;
            } else {
                parentsColHtml = `
                    <div class="space-y-2">
                        ${createMiniCard(sireObj, 'Sire (Father ♂)', false, true)}
                        ${createMiniCard(damObj, 'Dam (Mother ♀)', true, false)}
                    </div>
                `;
            }
            document.getElementById('treeColParents').innerHTML = parentsColHtml;

            // 4. Col 3: Focal Hero Card
            const focalHero = document.getElementById('treeColFocal');
            const genBadge = document.getElementById('focalHeroGenBadge');
            if (genBadge) {
                genBadge.innerText = focal.Gen_Depth === 0 ? 'F0 Founder' : `Generation F${focal.Gen_Depth}`;
                genBadge.className = focal.Gen_Depth === 0 ? 'badge badge-optimal' : 'badge badge-good';
            }

            focalHero.innerHTML = `
                <div class="space-y-3">
                    <div class="flex items-center justify-between">
                        <div>
                            <span class="text-xs font-bold text-slate-400">TUID:</span>
                            <h3 class="text-3xl font-black text-white tracking-tight">${focal.TUID}</h3>
                        </div>
                        <div class="text-right">
                            <span class="text-xs font-bold px-2.5 py-1 rounded-lg ${focal.Line_Category === 'AB' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : (focal.Line_Category === 'Casper' ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30' : (focal.Line_Category === 'Fli' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-pink-500/20 text-pink-400 border border-pink-500/30'))}">
                                ${focal.Line_Category} Line
                            </span>
                            <div class="text-[10px] text-slate-400 mt-1">${focal.Status_Clean}</div>
                        </div>
                    </div>

                    <!-- Metrics Grid -->
                    <div class="grid grid-cols-2 gap-2 bg-slate-900/90 p-3 rounded-xl border border-slate-800 text-xs">
                        <div>
                            <span class="text-slate-400 text-[10px] uppercase">Total Biomass</span>
                            <p class="text-base font-black text-teal-300 mt-0.5">${focal.Total_Count} <span class="text-xs font-normal text-slate-400">fish</span></p>
                            <span class="text-[10px] text-slate-400">${focal.Female_Count} ♀ / ${focal.Male_Count} ♂</span>
                        </div>
                        <div>
                            <span class="text-slate-400 text-[10px] uppercase">Inbreeding Coeff (F)</span>
                            <p class="text-base font-black ${focal.Inbreeding_F >= 0.25 ? 'text-rose-400' : (focal.Inbreeding_F > 0 ? 'text-amber-400' : 'text-emerald-400')} mt-0.5">
                                F = ${focal.Inbreeding_F}
                            </p>
                            <span class="text-[10px] text-slate-400">${focal.Inbreeding_F === 0 ? 'Unrelated / Founder' : (focal.Inbreeding_F >= 0.25 ? 'High Consanguinity' : 'Moderate Inbreeding')}</span>
                        </div>
                        <div>
                            <span class="text-slate-400 text-[10px] uppercase">Age / Stage</span>
                            <p class="text-xs font-bold text-slate-200 mt-0.5">${focal.Age_Months ? focal.Age_Months + ' mo' : 'N/A'}</p>
                            <span class="text-[10px] text-slate-400">DOB: ${focal.DOB || 'N/A'}</span>
                        </div>
                        <div>
                            <span class="text-slate-400 text-[10px] uppercase">Turnover Status</span>
                            <p class="text-xs font-bold ${focal.Turnover_Urgency === 'OVERDUE' ? 'text-rose-400' : 'text-slate-200'} mt-0.5">${focal.Turnover_Urgency || 'N/A'}</p>
                            <span class="text-[10px] text-slate-400">${focal.Days_To_Turnover ? focal.Days_To_Turnover + 'd remaining' : 'No date'}</span>
                        </div>
                    </div>

                    <!-- Husbandry & Genetic Strategy Badge -->
                    <div class="p-2.5 rounded-xl ${focal.Is_Mix ? 'bg-teal-950/40 border border-teal-800/40' : 'bg-slate-900/60 border border-slate-800'} text-xs space-y-1">
                        <div class="flex items-center justify-between">
                            <span class="text-slate-400 text-[10px] uppercase font-bold">Genetic Structure:</span>
                            <span class="font-bold ${focal.Is_Mix ? 'text-teal-300' : 'text-slate-300'}">${focal.Genetic_Type || 'Single Cross'}</span>
                        </div>
                        <div class="text-[11px] text-slate-300">
                            <b>Notes:</b> ${focal.NOTES || 'None'}
                        </div>
                    </div>
                </div>
            `;

            // 5. Col 4: Direct Offspring (Children)
            const children = records.filter(r => r.Sire === focal.TUID || r.Dam === focal.TUID);
            document.getElementById('treeOffspringCountBadge').innerText = `${children.length} Tanks`;

            let offspringHtml = '';
            if (children.length === 0) {
                offspringHtml = `
                    <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-2">
                        <span class="text-2xl">🌱</span>
                        <p class="text-xs font-bold text-slate-300">No Direct Offspring</p>
                        <p class="text-[11px] text-slate-500">No tanks in the database have this tank recorded as Sire or Dam.</p>
                    </div>
                `;
            } else {
                children.forEach(ch => {
                    const isAsSire = ch.Sire === focal.TUID;
                    const isAsDam = ch.Dam === focal.TUID;
                    const roleLabel = (isAsSire && isAsDam) ? 'Selfed / Both' : (isAsSire ? 'Offspring via Sire ♂' : 'Offspring via Dam ♀');
                    offspringHtml += createMiniCard(ch, roleLabel);
                });
            }
            document.getElementById('treeColOffspring').innerHTML = offspringHtml;

            // 6. Col 5: Grandchildren
            const childIds = new Set(children.map(c => c.TUID));
            const grandchildren = records.filter(r => (r.Sire && childIds.has(r.Sire)) || (r.Dam && childIds.has(r.Dam)));
            document.getElementById('treeGrandchildrenCountBadge').innerText = `${grandchildren.length} Tanks`;

            let grandChildrenHtml = '';
            if (grandchildren.length === 0) {
                grandChildrenHtml = `
                    <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-2">
                        <span class="text-2xl">🌿</span>
                        <p class="text-xs font-bold text-slate-300">No Grandchildren</p>
                        <p class="text-[11px] text-slate-500">Terminal progeny branch.</p>
                    </div>
                `;
            } else {
                grandchildren.forEach(gc => {
                    grandChildrenHtml += createMiniCard(gc, `Grandchild (Gen F${gc.Gen_Depth})`);
                });
            }
            document.getElementById('treeColGrandchildren').innerHTML = grandChildrenHtml;
        }

        function copyLineageTrail() {
            if (!computedData) return;
            const records = computedData.records;
            const tanksMap = {};
            records.forEach(r => { tanksMap[r.TUID] = r; });
            const focal = tanksMap[currentFocalTUID];
            if (!focal) return;

            const trail = [];
            let curr = focal;
            const visited = new Set();
            while (curr && !visited.has(curr.TUID)) {
                visited.add(curr.TUID);
                trail.unshift(curr);
                const p = curr.Sire || curr.Dam;
                curr = p ? tanksMap[p] : null;
            }

            const pathStr = trail.map(n => `${n.TUID} (F${n.Gen_Depth}, ${n.Line_Category})`).join(' ➔ ');
            navigator.clipboard.writeText(pathStr).then(() => {
                alert(`📋 Copied Lineage Trail to Clipboard:\\n${pathStr}`);
            }).catch(() => {
                alert(`Lineage Path:\\n${pathStr}`);
            });
        }

        function printPedigreeCard() {
            if (!computedData) return;
            const records = computedData.records;
            const focal = records.find(r => r.TUID === currentFocalTUID);
            if (!focal) return;

            const printWin = window.open('', '_blank', 'width=800,height=600');
            printWin.document.write(`
                <html>
                <head>
                    <title>FishNET Pedigree Certificate - ${focal.TUID}</title>
                    <style>
                        body { font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; color: #0f172a; }
                        .card { border: 2px solid #0f172a; border-radius: 12px; padding: 24px; max-width: 650px; margin: 0 auto; }
                        h1 { margin: 0 0 8px 0; font-size: 24px; color: #0f766e; }
                        table { width: 100%; border-collapse: collapse; margin-top: 16px; }
                        th, td { border: 1px solid #cbd5e1; padding: 8px 12px; font-size: 13px; text-align: left; }
                        th { background: #f1f5f9; }
                    </style>
                </head>
                <body>
                    <div class="card">
                        <h1>🐟 Zebrafish Colony Pedigree Certificate</h1>
                        <p><b>Tank ID:</b> ${focal.TUID} | <b>Line:</b> ${focal.Line_Category} | <b>Generation:</b> F${focal.Gen_Depth}</p>
                        <table>
                            <tr><th>Status</th><td>${focal.STATUS || 'Active'}</td></tr>
                            <tr><th>Genotype / Notes</th><td>${focal.NOTES || 'N/A'}</td></tr>
                            <tr><th>Genetic Strategy</th><td>${focal.Genetic_Type || 'Single Cross'}</td></tr>
                            <tr><th>Inbreeding Coefficient (F)</th><td>${focal.Inbreeding_F}</td></tr>
                            <tr><th>Sire (Father ♂)</th><td>${focal.Sire || 'F0 Founder / External'}</td></tr>
                            <tr><th>Dam (Mother ♀)</th><td>${focal.Dam || 'F0 Founder / External'}</td></tr>
                            <tr><th>Fish Count</th><td>${focal.Total_Count} (${focal.Female_Count} Females / ${focal.Male_Count} Males)</td></tr>
                            <tr><th>Date of Birth (DOB)</th><td>${focal.DOB || 'N/A'}</td></tr>
                            <tr><th>Turnover Date</th><td>${focal.TURNOVER || 'N/A'}</td></tr>
                        </table>
                        <p style="margin-top: 24px; font-size: 11px; color: #64748b;">Generated from FishNET Colony Database on ${new Date().toLocaleDateString()}</p>
                    </div>
                </body>
                </html>
            `);
            printWin.document.close();
            printWin.print();
        }

        // ==================== SUB-VIEW 2: LINE-BY-LINE FLOWCHARTS ====================
        function selectLineTree(line) {
            currentLineTree = line;
            ['AB', 'Casper', 'Fli', 'Gata'].forEach(ln => {
                const btn = document.getElementById('line-tree-btn-' + ln);
                if (btn) {
                    if (ln === line) {
                        const col = ln === 'AB' ? 'bg-amber-500 text-slate-950' : (ln === 'Casper' ? 'bg-sky-500 text-slate-950' : (ln === 'Fli' ? 'bg-green-500 text-slate-950' : 'bg-pink-500 text-slate-950'));
                        btn.className = `line-tree-btn active px-3.5 py-1.5 rounded-lg text-xs font-bold ${col} transition`;
                    } else {
                        const textCol = ln === 'AB' ? 'text-amber-400' : (ln === 'Casper' ? 'text-sky-400' : (ln === 'Fli' ? 'text-green-400' : 'text-pink-400'));
                        btn.className = `line-tree-btn px-3.5 py-1.5 rounded-lg text-xs font-bold ${textCol} bg-slate-800 hover:bg-slate-700 transition`;
                    }
                }
            });
            renderLineTrees(line);
        }

        function renderLineTrees(line) {
            if (!computedData) return;
            const records = computedData.records;

            // Update counts in buttons
            ['AB', 'Casper', 'Fli', 'Gata'].forEach(ln => {
                const cnt = records.filter(r => r.Line_Category === ln).length;
                const el = document.getElementById('lineTreeCount' + ln);
                if (el) el.innerText = cnt;
            });

            const lineRecords = records.filter(r => r.Line_Category === line);
            const container = document.getElementById('lineTreeTiersContainer');
            if (!container) return;

            // Group by Gen_Depth
            const tiers = {};
            lineRecords.forEach(r => {
                const g = r.Gen_Depth;
                if (!tiers[g]) tiers[g] = [];
                tiers[g].push(r);
            });

            const sortedGens = Object.keys(tiers).map(Number).sort((a, b) => a - b);

            let html = '';
            sortedGens.forEach(gen => {
                const tanks = tiers[gen];
                const tierTitle = gen === 0 ? '🌱 Generation Tier 0: F0 Founders' : `🧬 Generation Tier ${gen}: F${gen} Offspring`;
                const tierDesc = gen === 0 ? 'Baseline founding stocks (no recorded internal ancestors)' : `Descendants with maximum lineage depth ${gen}`;

                html += `
                    <div class="glass-card p-4 rounded-xl space-y-3">
                        <div class="flex items-center justify-between border-b border-slate-700 pb-2">
                            <div>
                                <h3 class="text-sm font-bold text-white flex items-center gap-2">
                                    <span>${tierTitle}</span>
                                    <span class="px-2 py-0.5 rounded-full bg-slate-800 text-teal-400 text-xs font-mono">${tanks.length} Tanks</span>
                                </h3>
                                <p class="text-[11px] text-slate-400">${tierDesc}</p>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3 pt-2">
                            ${tanks.map(t => {
                                const isEuth = !t.Is_Active;
                                return `
                                    <div onclick="switchPedigreeMode('focal'); changeFocalTank('${t.TUID}');" class="cursor-pointer group p-3 rounded-xl border ${isEuth ? 'border-slate-800 bg-slate-900/40 opacity-75' : 'border-slate-700 bg-slate-900/90'} hover:border-teal-400 transition hover:shadow-md space-y-1.5">
                                        <div class="flex items-center justify-between">
                                            <span class="text-xs font-black text-white group-hover:text-teal-300 transition">${t.TUID}</span>
                                            <span class="text-[10px] px-1.5 py-0.2 rounded ${t.Is_Active ? 'bg-emerald-950 text-emerald-400' : 'bg-slate-800 text-slate-400'}">${t.Is_Active ? 'Active' : 'Euth'}</span>
                                        </div>
                                        <div class="text-[11px] text-slate-300">
                                            <span>Fish: <b>${t.Total_Count}</b></span> (${t.Female_Count}F / ${t.Male_Count}M)
                                        </div>
                                        <div class="text-[10px] text-slate-400 flex items-center justify-between border-t border-slate-800 pt-1">
                                            <span>F = <b class="text-amber-400">${t.Inbreeding_F}</b></span>
                                            <span>Prog: <b class="text-teal-400">${t.Progeny_Count}</b></span>
                                        </div>
                                        ${t.Is_Mix ? '<div class="text-[9px] font-bold text-teal-300 bg-teal-950/80 px-1 rounded border border-teal-800/40">🔀 Mix Cohort</div>' : ''}
                                        ${(t.Sire || t.Dam) ? `<div class="text-[9px] text-slate-400 truncate">P: ${t.Sire || '?' } × ${t.Dam || '?'}</div>` : ''}
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        }

        // ==================== SUB-VIEW 3: COLLAPSIBLE TREE TABLE ====================
        function renderTreeTable() {
            if (!computedData) return;
            const records = computedData.records;
            const tbody = document.getElementById('pedigreeTreeTableBody');
            if (!tbody) return;

            const q = (document.getElementById('treeTableSearchInput')?.value || '').toLowerCase().trim();
            const lineFilter = document.getElementById('treeTableLineFilter')?.value || 'ALL';
            const stFilter = document.getElementById('treeTableStatusFilter')?.value || 'ALL';

            let filtered = records.filter(r => {
                if (lineFilter !== 'ALL' && r.Line_Category !== lineFilter) return false;
                if (stFilter === 'ACTIVE' && !r.Is_Active) return false;
                if (stFilter === 'EUTH' && r.Is_Active) return false;
                if (q) {
                    const str = `${r.TUID} ${r.Line_Category} ${r.NOTES} ${r.STATUS} ${r.Sire} ${r.Dam} ${r.Genetic_Type}`.toLowerCase();
                    if (!str.includes(q)) return false;
                }
                return true;
            });

            // Sort hierarchically: Line -> Gen_Depth -> TUID
            filtered.sort((a, b) => {
                if (a.Line_Category !== b.Line_Category) return a.Line_Category.localeCompare(b.Line_Category);
                if (a.Gen_Depth !== b.Gen_Depth) return a.Gen_Depth - b.Gen_Depth;
                return a.TUID.localeCompare(b.TUID);
            });

            let html = '';
            filtered.forEach(r => {
                const isEuth = !r.Is_Active;
                const genBadge = r.Gen_Depth === 0 ? '<span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 text-[10px] font-bold">F0 Founder</span>' : `<span class="px-2 py-0.5 rounded bg-blue-950 text-blue-400 text-[10px] font-bold">Gen F${r.Gen_Depth}</span>`;
                const mixBadge = r.Is_Mix ? '<span class="px-1.5 py-0.5 rounded bg-teal-900/60 text-teal-300 text-[10px] border border-teal-700/50">🔀 Mix</span>' : '';
                const lineCol = r.Line_Category === 'AB' ? 'text-amber-400' : (r.Line_Category === 'Casper' ? 'text-sky-400' : (r.Line_Category === 'Fli' ? 'text-green-400' : 'text-pink-400'));

                html += `
                    <tr class="hover:bg-slate-800/60 transition ${isEuth ? 'opacity-60 bg-slate-900/40' : ''}">
                        <td class="p-3 font-mono font-bold flex items-center gap-1.5">
                            <span class="${lineCol}">${r.TUID}</span>
                            <span class="text-[10px] font-semibold text-slate-400">(${r.Line_Category})</span>
                        </td>
                        <td class="p-3">${genBadge}</td>
                        <td class="p-3">
                            <span class="badge ${r.Is_Active ? 'badge-optimal' : 'badge-archive'}">${r.Status_Clean}</span>
                        </td>
                        <td class="p-3">
                            <span class="font-bold text-white">${r.Total_Count}</span>
                            <span class="text-[11px] text-slate-400">(${r.Female_Count}♀ / ${r.Male_Count}♂)</span>
                        </td>
                        <td class="p-3 font-mono font-bold ${r.Inbreeding_F >= 0.25 ? 'text-rose-400' : (r.Inbreeding_F > 0 ? 'text-amber-400' : 'text-emerald-400')}">
                            ${r.Inbreeding_F}
                        </td>
                        <td class="p-3">
                            <div class="flex items-center gap-1.5">
                                ${mixBadge}
                                <span class="text-[11px] ${r.Is_Mix ? 'text-teal-300 font-semibold' : 'text-slate-300'}">${r.Genetic_Type || 'Single Cross'}</span>
                            </div>
                            ${r.Mix_Sources_Str ? `<div class="text-[10px] text-slate-400 mt-0.5">Pool: ${r.Mix_Sources_Str}</div>` : ''}
                        </td>
                        <td class="p-3 font-mono text-[11px] text-slate-300">
                            ${(r.Sire || r.Dam) ? `${r.Sire || '?'} × ${r.Dam || '?'}` : '<span class="text-slate-500">None (F0)</span>'}
                        </td>
                        <td class="p-3">
                            <span class="px-2 py-0.5 rounded bg-slate-800 text-teal-300 font-bold">${r.Progeny_Count}</span>
                        </td>
                        <td class="p-3 text-center">
                            <button onclick="switchPedigreeMode('focal'); changeFocalTank('${r.TUID}');" class="px-2.5 py-1 rounded bg-teal-600 hover:bg-teal-500 text-white text-[11px] font-semibold transition">
                                🎯 Focus
                            </button>
                        </td>
                    </tr>
                `;
            });

            tbody.innerHTML = html;
        }

        function filterTreeTable() {
            renderTreeTable();
        }

        function expandAllTreeRows() {
            renderTreeTable();
        }

        function collapseAllTreeRows() {
            renderTreeTable();
        }

        function exportTreeTableCSV() {
            if (!computedData) return;
            const headers = ['TUID', 'Line', 'Gen_Depth', 'Status', 'Total_Count', 'Female_Count', 'Male_Count', 'Inbreeding_F', 'Genetic_Type', 'Mix_Sources', 'Sire', 'Dam', 'Progeny_Count', 'DOB', 'TURNOVER'];
            let csvContent = 'data:text/csv;charset=utf-8,' + headers.join(',') + '\\n';

            computedData.records.forEach(r => {
                const row = [
                    r.TUID,
                    r.Line_Category,
                    r.Gen_Depth,
                    `"${r.STATUS || ''}"`,
                    r.Total_Count,
                    r.Female_Count,
                    r.Male_Count,
                    r.Inbreeding_F,
                    `"${r.Genetic_Type || ''}"`,
                    `"${r.Mix_Sources_Str || ''}"`,
                    r.Sire,
                    r.Dam,
                    r.Progeny_Count,
                    r.DOB || '',
                    r.TURNOVER || ''
                ];
                csvContent += row.join(',') + '\\n';
            });

            const encodedUri = encodeURI(csvContent);
            const link = document.createElement('a');
            link.setAttribute('href', encodedUri);
            link.setAttribute('download', `FishNET_Pedigree_Lineage_Matrix_${new Date().toISOString().slice(0,10)}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }


        // Pedigree Graph Rendering
        let networkNodesData = [];
        let networkEdgesData = [];

        function renderPedigreeNetwork() {
            if (!computedData) return;
            const records = computedData.records;
            const showEuth = document.getElementById('showEuthanizedToggle').checked;

            const visibleRecords = showEuth ? records : records.filter(r => r.Is_Active);
            const visibleIds = new Set(visibleRecords.map(r => r.TUID));

            networkNodesData = visibleRecords.map(r => {
                const isEuth = !r.Is_Active;
                const colDef = isEuth ? LINE_COLORS['Euthanized'] : (LINE_COLORS[r.Line_Category] || LINE_COLORS['Other']);

                return {
                    id: r.TUID,
                    label: `${r.TUID}\\n${r.Line_Category}`,
                    title: `<b>${r.TUID}</b> [${r.STATUS || 'Active'}]<br><b>Line:</b> ${r.Line_Category}<br><b>Notes:</b> ${r.NOTES || ''}<br><b>Fish:</b> ${r.Total_Count} (F:${r.Female_Count} / M:${r.Male_Count})<br><b>Inbreeding (F):</b> ${r.Inbreeding_F}<br><b>Parents:</b> ${r.Sire || '?'} x ${r.Dam || '?'}`,
                    group: r.Line_Category,
                    level: r.Gen_Depth,
                    color: {
                        background: colDef.bg,
                        border: colDef.border,
                        highlight: { background: '#f59e0b', border: '#b45309' }
                    },
                    shape: 'box',
                    font: { size: 11, face: 'Segoe UI', color: isEuth ? '#f8fafc' : '#0f172a' },
                    margin: 8,
                    opacity: isEuth ? 0.6 : 1.0,
                    recordData: r
                };
            });

            networkEdgesData = [];
            visibleRecords.forEach(r => {
                if (r.Sire && visibleIds.has(r.Sire)) {
                    networkEdgesData.push({
                        from: r.Sire,
                        to: r.TUID,
                        label: 'sire',
                        arrows: 'to',
                        color: { color: '#3b82f6', highlight: '#f59e0b' },
                        dashes: false
                    });
                }
                if (r.Dam && visibleIds.has(r.Dam) && r.Dam !== r.Sire) {
                    networkEdgesData.push({
                        from: r.Dam,
                        to: r.TUID,
                        label: 'dam',
                        arrows: 'to',
                        color: { color: '#ec4899', highlight: '#f59e0b' },
                        dashes: true
                    });
                }
            });

            const container = document.getElementById('pedigree-network');
            const data = {
                nodes: new vis.DataSet(networkNodesData),
                edges: new vis.DataSet(networkEdgesData)
            };

            const options = {
                layout: {
                    hierarchical: {
                        direction: 'UD',
                        sortMethod: 'directed',
                        nodeSpacing: 140,
                        levelSeparation: 130
                    }
                },
                physics: false,
                interaction: {
                    hover: true,
                    tooltipDelay: 100,
                    zoomView: true,
                    dragView: true
                },
                nodes: {
                    borderWidth: 2,
                    shadow: true
                },
                edges: {
                    smooth: { type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.4 },
                    width: 2
                }
            };

            network = new vis.Network(container, data, options);

            network.on('click', function(params) {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    selectedNodeId = nodeId;
                    displayNodeDetails(nodeId);
                }
            });
        }

        function displayNodeDetails(nodeId) {
            const n = networkNodesData.find(x => x.id === nodeId);
            if (!n) return;
            const r = n.recordData;

            document.getElementById('inspectTUID').innerText = r.TUID;
            document.getElementById('inspectLine').innerText = `Primary Line: ${r.Line_Category}`;
            document.getElementById('inspectStatusCol').innerText = r.STATUS || 'Active';
            document.getElementById('inspectNotes').innerText = r.NOTES || 'None';
            document.getElementById('inspectDOB').innerText = r.DOB || 'Unknown';
            document.getElementById('inspectTurnover').innerText = r.TURNOVER || 'Unknown';
            document.getElementById('inspectCounts').innerText = `${r.Female_Count} F / ${r.Male_Count} M (${r.Total_Count} Total)`;
            document.getElementById('inspectInbreeding').innerText = `F = ${r.Inbreeding_F}`;
            document.getElementById('inspectParents').innerText = (r.Sire || r.Dam) ? `${r.Sire || '?'} x ${r.Dam || '?'}` : 'F0 / Founder';
            document.getElementById('inspectCross').innerText = r['Derivative cross'] || 'Founder';

            const stBadge = document.getElementById('inspectStatus');
            stBadge.innerText = r.Status_Clean;
            stBadge.className = !r.Is_Active ? 'badge badge-archive' : 'badge badge-optimal';
        }

        function highlightAncestors() {
            if (!selectedNodeId || !network) return;
            const ancestors = new Set();
            function traceUp(id) {
                const incoming = networkEdgesData.filter(e => e.to === id);
                incoming.forEach(e => {
                    ancestors.add(e.from);
                    traceUp(e.from);
                });
            }
            traceUp(selectedNodeId);
            ancestors.add(selectedNodeId);
            network.selectNodes(Array.from(ancestors));
        }

        function highlightDescendants() {
            if (!selectedNodeId || !network) return;
            const progeny = new Set();
            function traceDown(id) {
                const outgoing = networkEdgesData.filter(e => e.from === id);
                outgoing.forEach(e => {
                    progeny.add(e.to);
                    traceDown(e.to);
                });
            }
            traceDown(selectedNodeId);
            progeny.add(selectedNodeId);
            network.selectNodes(Array.from(progeny));
        }

        function clearHighlights() {
            if (network) network.unselectAll();
        }

        function searchPedigreeNode() {
            const query = document.getElementById('pedigreeSearch').value.trim().toUpperCase();
            if (!query || !network) return;
            const target = networkNodesData.find(n => n.id.toUpperCase() === query);
            if (target) {
                network.focus(target.id, { scale: 1.2, animation: true });
                network.selectNodes([target.id]);
                displayNodeDetails(target.id);
            } else {
                alert('Tank ID not found in current pedigree graph: ' + query);
            }
        }

        function filterPedigreeByLine() {
            const filterVal = document.getElementById('lineFilter').value;
            if (filterVal === 'ALL') {
                renderPedigreeNetwork();
                return;
            }
            const filteredNodes = networkNodesData.filter(n => n.group === filterVal);
            const nodeIds = new Set(filteredNodes.map(n => n.id));
            const filteredEdges = networkEdgesData.filter(e => nodeIds.has(e.from) && nodeIds.has(e.to));

            const container = document.getElementById('pedigree-network');
            network = new vis.Network(container, {
                nodes: new vis.DataSet(filteredNodes),
                edges: new vis.DataSet(filteredEdges)
            }, {
                layout: { hierarchical: { direction: 'UD', sortMethod: 'directed', nodeSpacing: 140, levelSeparation: 130 } },
                physics: false
            });
        }

        function resetPedigreeView() {
            if (network) {
                network.fit({ animation: true });
                network.unselectAll();
            }
        }

        function toggleEuthanizedFilter() {
            renderPedigreeNetwork();
        }

        // Tabs switching
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

            document.getElementById('tab-' + tabId).classList.remove('hidden');
            document.getElementById('tab-btn-' + tabId).classList.add('active');

            if (tabId === 'pedigree') {
                setTimeout(renderPedigreeNetwork, 50);
            }
        }

        // Dynamic File Upload Handler (Parses .xlsx / .tab / .tsv / .csv)
        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            const fileName = file.name.toLowerCase();

            if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
                reader.onload = function(e) {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, { type: 'array' });
                    const firstSheetName = workbook.SheetNames[0];
                    const worksheet = workbook.Sheets[firstSheetName];
                    const jsonRows = XLSX.utils.sheet_to_json(worksheet, { defval: '' });
                    
                    processUploadedRows(jsonRows, file.name);
                };
                reader.readAsArrayBuffer(file);
            } else {
                // Text / Tab / CSV
                reader.onload = function(e) {
                    const text = e.target.result;
                    const delimiter = text.includes('\\t') ? '\\t' : ',';
                    const lines = text.split(/\\r?\\n/).filter(l => l.trim().length > 0);
                    if (lines.length < 2) {
                        alert('Uploaded file is empty or missing data rows.');
                        return;
                    }
                    const headers = lines[0].split(delimiter).map(h => h.trim());
                    const rows = [];
                    for (let i = 1; i < lines.length; i++) {
                        const cols = lines[i].split(delimiter);
                        const rowObj = {};
                        headers.forEach((h, idx) => {
                            rowObj[h] = cols[idx] ? cols[idx].trim() : '';
                        });
                        rows.push(rowObj);
                    }
                    processUploadedRows(rows, file.name);
                };
                reader.readAsText(file);
            }
        }

        function processUploadedRows(rows, fileName) {
            if (!rows || rows.length === 0) {
                alert('No valid records found in uploaded file.');
                return;
            }

            // Normalize column names
            const cleanRows = rows.map(r => {
                const cleanObj = {};
                Object.keys(r).forEach(k => {
                    const cleanK = k.trim();
                    cleanObj[cleanK] = String(r[k] || '').trim();
                });
                return cleanObj;
            });

            document.getElementById('currentDatasetLabel').innerText = fileName;
            const newAnalysis = runFullAnalysis(cleanRows);
            updateDashboardUI(newAnalysis);

            alert(`✅ Successfully loaded and analyzed ${cleanRows.length} records from ${fileName}!`);
        }

        function resetToDefaultData() {
            document.getElementById('currentDatasetLabel').innerText = 'Default FishNET.tab';
            const defaultAnalysis = runFullAnalysis(JSON.parse(JSON.stringify(DEFAULT_RECORDS)));
            updateDashboardUI(defaultAnalysis);
        }

        // Initialization
        window.addEventListener('load', function() {
            const initialAnalysis = runFullAnalysis(currentRecords);
            updateDashboardUI(initialAnalysis);
        });
    </script>
</body>
</html>
"""

html_content = html_template.replace('__RECORDS_JSON__', raw_records_json)

with open('FishNET_Interactive_Dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

with open(HTML_DASHBOARD_FILE, 'w', encoding='utf-8') as f:
    f.write(html_content)

print('HTML Dashboards generated: FishNET_Interactive_Dashboard.html and FishNET_Interactive_Dashboard_Standard_Backup.html')
