import csv
import os
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from collections import defaultdict

def excel_date_to_str(val):
    try:
        f = float(val)
        dt = datetime(1899, 12, 30) + timedelta(days=f)
        return dt.strftime('%Y-%m-%d')
    except:
        return str(val)

def parse_date(d_str, default_year=2026):
    if not d_str:
        return ''
    d_str = str(d_str).strip()
    if re.match(r'^[0-9]{5}(\.[0-9]+)?$', d_str):
        return excel_date_to_str(d_str)
    
    m = re.match(r'^(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})$', d_str)
    if m:
        d, mth, y = m.groups()
        if len(y) == 2:
            y = '20' + y
        return f'{int(y):04d}-{int(mth):02d}-{int(d):02d}'
    
    for fmt in ['%b %d, %Y', '%B %d, %Y', '%b-%d', '%d-%b', '%d-%b-%y', '%d-%b-%Y']:
        try:
            dt = datetime.strptime(d_str, fmt)
            if dt.year == 1900:
                dt = dt.replace(year=default_year)
            return dt.strftime('%Y-%m-%d')
        except:
            pass
    return d_str

def parse_clean_float(val):
    if val is None:
        return 0.0
    val_str = str(val).strip().replace('%', '')
    m = re.search(r'([0-9]+(?:\.[0-9]+)?)', val_str)
    if m:
        try:
            return float(m.group(1))
        except:
            return 0.0
    return 0.0

def parse_clean_int(val):
    if val is None:
        return 0
    val_str = str(val).strip()
    m = re.search(r'([0-9]+)', val_str)
    if m:
        try:
            return int(m.group(1))
        except:
            return 0
    return 0

def extract_line_and_tanks(fishline_str):
    s = str(fishline_str).strip()
    # Correct common OCR/typos like A13 -> AB
    s_clean = re.sub(r'\bA13\b', 'AB', s)
    s_upper = s_clean.upper()
    
    line = 'Other'
    if 'AB' in s_upper or 'WILD' in s_upper:
        line = 'AB'
    elif 'CASP' in s_upper or 'CAS' in s_upper:
        line = 'Casper'
    elif 'FLI' in s_upper:
        line = 'Fli'
    elif 'GATA' in s_upper:
        line = 'Gata'
    
    # Extract tank numbers matching T123, T-123, T.123, AB106, Gata101, Fli19, Tank 95, etc.
    res = []
    # Pattern 1: Tank/T prefix followed by digits
    for m in re.finditer(r'(?:Tank|T|T\.|T\-)\s*0*([0-9]{1,4})\b', s_clean, re.IGNORECASE):
        res.append(int(m.group(1)))
    # Pattern 2: Strain prefix directly followed by digits (e.g. AB106, Gata101, Cas114)
    for m in re.finditer(r'(?:AB|Fli|Gata|Casper|Casp|Cas)\s*0*([0-9]{1,4})\b', s_clean, re.IGNORECASE):
        val = int(m.group(1))
        if val not in res and val < 300:  # avoid years like 2025/2026
            res.append(val)
    
    # Preserve order while making unique
    seen = set()
    tank_ids = []
    for v in res:
        tid = f'T{v:04d}'
        if tid not in seen:
            seen.add(tid)
            tank_ids.append(tid)
            
    return line, tank_ids


def read_xlsx_rows(path):
    z = zipfile.ZipFile(path)
    strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
            t = si.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
            strings.append(t.text if t is not None else '')
    
    sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    rows = []
    for row in sheet.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
        row_vals = []
        for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            val = v.text if v is not None else ''
            t = c.attrib.get('t')
            if t == 's' and val != '':
                val = strings[int(val)]
            row_vals.append(val)
        rows.append(row_vals)
    return rows

def process():
    labels_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels'
    done_dir = os.path.join(labels_dir, 'DONE')
    if not os.path.exists(os.path.join(done_dir, '24-including intank.csv')):
        done_dir = os.path.join(labels_dir, 'archive', 'DONE')
    breeding_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\breeding'
    
    # 1. Load Crosses Mapping for Cross-Checking DOB
    crosses_map = {}
    crosses_tab_path = os.path.join(labels_dir, 'FishNet Exported Data', 'Crosses.tab')
    if os.path.exists(crosses_tab_path):
        with open(crosses_tab_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for r in csv.reader(f, delimiter='\t'):
                if len(r) >= 10:
                    cuid = r[7].strip().upper()
                    mating_date = r[9].strip()
                    origin = r[11].strip() if len(r) > 11 else ''
                    crosses_map[cuid] = {'date': mating_date, 'origin': origin}

    def parse_cross_date_dt(cd):
        if not cd:
            return None
        m = re.match(r'^(\d{1,2})-(\w{3})-(\d{2,4})$', cd)
        if m:
            d, mon, y = m.groups()
            months = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
            m_num = months.get(mon.capitalize(), 1)
            yr = int(y)
            if yr < 100: yr += 2000
            return datetime(yr, m_num, int(d))
        m2 = re.match(r'^(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})$', cd)
        if m2:
            d, mth, y = m2.groups()
            yr = int(y)
            if yr < 100: yr += 2000
            return datetime(yr, int(mth), int(d))
        return None

    def resolve_dob(raw_dob, d_cross):
        c_info = crosses_map.get(d_cross.upper(), {})
        cross_dt = parse_cross_date_dt(c_info.get('date', ''))
        
        if not raw_dob:
            if cross_dt:
                return cross_dt, cross_dt.strftime('%d-%m-%Y'), cross_dt.strftime('%Y-%m-%d')
            return None, '', ''
        
        parts = re.split(r'[-/]', str(raw_dob).strip())
        if len(parts) == 3:
            try:
                p1, p2, p3 = int(parts[0]), int(parts[1]), int(parts[2])
                if p3 < 100: p3 += 2000
                
                if cross_dt:
                    # If US format (month=p1, day=p2) matches cross date
                    if cross_dt.year == p3 and cross_dt.month == p1 and cross_dt.day == p2:
                        dt = datetime(p3, p1, p2)
                        return dt, dt.strftime('%d-%m-%Y'), dt.strftime('%Y-%m-%d')
                    # If Euro format (day=p1, month=p2) matches cross date
                    elif cross_dt.year == p3 and cross_dt.month == p2 and cross_dt.day == p1:
                        dt = datetime(p3, p2, p1)
                        return dt, dt.strftime('%d-%m-%Y'), dt.strftime('%Y-%m-%d')
                    else:
                        # Ground directly to cross date if available
                        return cross_dt, cross_dt.strftime('%d-%m-%Y'), cross_dt.strftime('%Y-%m-%d')
                else:
                    # Fallback heuristic
                    if p1 <= 12 and p2 > 12:
                        dt = datetime(p3, p1, p2)
                        return dt, dt.strftime('%d-%m-%Y'), dt.strftime('%Y-%m-%d')
                    elif p2 <= 12 and p1 <= 31:
                        dt = datetime(p3, p2, p1)
                        return dt, dt.strftime('%d-%m-%Y'), dt.strftime('%Y-%m-%d')
            except:
                pass
        
        for fmt in ['%d-%b-%y', '%d-%m-%y', '%d-%b-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
            try:
                dt = datetime.strptime(raw_dob, fmt)
                if dt.year > 2030:
                    dt = dt.replace(year=dt.year - 100)
                return dt, dt.strftime('%d-%m-%Y'), dt.strftime('%Y-%m-%d')
            except:
                pass
        return None, str(raw_dob), ''

    # 1. Load FishNET Tanks with Sex Structure Analysis
    fishnet_tanks = {}
    tanks_tab_path = os.path.join(labels_dir, 'FishNet Exported Data', 'Tanks.tab')
    if not os.path.exists(tanks_tab_path):
        tanks_tab_path = os.path.join(labels_dir, 'FishNET.tab')

    with open(tanks_tab_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        reader = list(csv.reader(f, delimiter='\t'))
        for row in reader:
            if not row or len(row) < 21:
                continue
            # Col 21 (index 20): TUID
            tuid = row[20].strip().upper()
            if not tuid or not tuid.startswith('T'):
                continue
            
            dob = row[0].strip()
            dod = row[1].strip() if len(row) > 1 else ''
            derivative_cross = row[2].strip() if len(row) > 2 else ''
            facility = row[3].strip() if len(row) > 3 else ''
            female = int(row[4].strip()) if len(row) > 4 and row[4].strip().isdigit() else 0
            genotype = row[5].strip() if len(row) > 5 else ''
            lab_member = row[6].strip() if len(row) > 6 else ''
            male = int(row[7].strip()) if len(row) > 7 and row[7].strip().isdigit() else 0
            notes = row[8].strip() if len(row) > 8 else ''
            total = int(row[9].strip()) if len(row) > 9 and row[9].strip().isdigit() else (female + male)
            protocol = row[10].strip() if len(row) > 10 else ''
            room = row[12].strip() if len(row) > 12 else ''
            status_raw = row[16].strip() if len(row) > 16 else 'Adult/Active'
            tank_size = row[18].strip() if len(row) > 18 else ''
            turnover_date = row[21].strip() if len(row) > 21 else ''
            lab_name = row[22].strip() if len(row) > 22 else ''
            
            # Accurate Line categorization
            g_upper = genotype.upper()
            n_upper = notes.upper()
            combined = f"{g_upper} {n_upper}"
            if 'CASPER' in combined or 'MITFA' in combined or 'MPV17' in combined or re.search(r'\bCAS\b', combined):
                line = 'Casper'
            elif 'FLI' in combined or 'EGFP' in combined:
                line = 'Fli'
            elif 'GATA' in combined or 'DSRED' in combined:
                line = 'Gata'
            elif 'DESMA' in combined or 'DESM' in combined:
                line = 'DESMA'
            elif 'AB' in combined or 'WILD' in combined or 'WT' in combined:
                line = 'AB'
            else:
                line = 'Other'
            
            # Resolve DOB with cross-grounding
            dob_dt, dob_display, dob_iso = resolve_dob(dob, derivative_cross)

            # Determine Biological / Operational Status
            # Check age relative to present (Oct 2026):
            is_mature = False
            if dob_dt:
                age_days = (datetime(2026, 10, 6) - dob_dt).days
                if age_days > 90:  # > 3 months
                    is_mature = True

            if 'EUTH' in status_raw.upper() or 'DEAD' in status_raw.upper():
                status_clean = 'Euthanized'
            elif 'LARVAE' in status_raw.upper():
                # If tank is already mature (>3 months) or actively breeding, graduate to Active
                status_clean = 'Active' if is_mature else 'Larvae'
            elif 'ACTIVE' in status_raw.upper() or 'ADULT' in status_raw.upper():
                status_clean = 'Active'
            else:
                status_clean = status_raw

            # Determine Sex Structure
            if female > 0 and male == 0:
                sex_type = 'Female-Only'
                can_in_tank = False
            elif male > 0 and female == 0:
                sex_type = 'Male-Only'
                can_in_tank = False
            elif female > 0 and male > 0:
                sex_type = 'Mixed Colony'
                can_in_tank = True
            else:
                sex_type = 'Unsexed / Juvenile'
                can_in_tank = False

            num_id = int(re.sub(r'\D', '', tuid)) if re.search(r'\d', tuid) else 0
            std_tuid = f'T{num_id:04d}'
            tank_obj = {
                'tuid': std_tuid,
                'raw_tuid': tuid,
                'num_id': num_id,
                'derivative_cross': derivative_cross,
                'genotype': genotype,
                'notes': notes,
                'line': line,
                'female': female,
                'male': male,
                'total': total,
                'sex_type': sex_type,
                'can_in_tank': can_in_tank,
                'dob': dob_display or dob,
                'raw_dob': dob,
                'dob_iso': dob_iso,
                'dob_dt': dob_dt,
                'turnover_date': turnover_date,
                'tank_size': tank_size,
                'protocol': protocol,
                'room': room,
                'lab_member': lab_member,
                'lab_name': lab_name,
                'status': status_clean,
                'raw_status': status_raw
            }
            fishnet_tanks[std_tuid] = tank_obj

    unique_tanks = {t['tuid']: t for t in fishnet_tanks.values()}
    n_active = sum(1 for t in unique_tanks.values() if t['status'] == 'Active')
    n_euth = sum(1 for t in unique_tanks.values() if t['status'] == 'Euthanized')
    n_larvae = sum(1 for t in unique_tanks.values() if t['status'] == 'Larvae')
    n_f_only = sum(1 for t in unique_tanks.values() if t['sex_type'] == 'Female-Only')
    n_m_only = sum(1 for t in unique_tanks.values() if t['sex_type'] == 'Male-Only')
    n_mixed = sum(1 for t in unique_tanks.values() if t['sex_type'] == 'Mixed Colony')

    print(f'Loaded {len(unique_tanks)} unique tanks ({n_active} Active, {n_euth} Euthanized, {n_larvae} Larvae).')
    print(f'Sex Structure: {n_f_only} Female-Only, {n_m_only} Male-Only, {n_mixed} Mixed Colony.')

    # 2. Transcribe & Parse 2026 Data
    p26_events = []
    p26_csv_path = os.path.join(breeding_dir, '26.csv')
    with open(p26_csv_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        reader = list(csv.reader(f))
        for r in reader[1:]:
            if not r or len(r) < 3 or not r[0].strip():
                continue
            date_iso = parse_date(r[0], 2026)
            fishline = r[1].strip()
            line, tanks = extract_line_and_tanks(fishline)
            in_tank = True if len(r) > 7 and 'YES' in r[7].strip().upper() else ('intank' in fishline.lower())
            eggs_0h = parse_clean_int(r[2])
            sr_0h = parse_clean_float(r[3])
            sr_24h = parse_clean_float(r[4])
            staff_initials = r[6].strip() if len(r) > 6 else ''
            
            live_0h = int(round(eggs_0h * (sr_0h / 100.0))) if sr_0h > 0 else 0
            live_24h = int(round(live_0h * (sr_24h / 100.0))) if sr_24h > 0 else 0

            p26_events.append({
                'year': 2026,
                'date': date_iso,
                'fishline': fishline,
                'line': line,
                'tanks': tanks,
                'primary_tank': tanks[0] if tanks else '',
                'in_tank': in_tank,
                'setup_staff': staff_initials,
                'collection_staff': staff_initials,
                'scoring_24h_staff': staff_initials,
                'staff_summary': staff_initials,
                'eggs_0h': eggs_0h,
                'sr_0h': sr_0h,
                'live_0h': live_0h,
                'sr_24h': sr_24h,
                'live_24h': live_24h,
                'source': '2026_log_sheet_part1'
            })

    # Part 2: 26-1.csv
    p26_1_path = os.path.join(breeding_dir, '26-1.csv')
    with open(p26_1_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        reader = list(csv.reader(f))
        for r in reader[1:]:
            if not r or len(r) < 2 or not r[0].strip():
                continue
            date_iso = parse_date(r[0], 2026)
            fishline = r[1].strip()
            line, tanks = extract_line_and_tanks(fishline)
            in_tank = True if len(r) > 2 and 'YES' in r[2].strip().upper() else ('intank' in fishline.lower())
            setup_staff = r[3].strip() if len(r) > 3 else ''
            
            raw_0h = r[4].strip() if len(r) > 4 else ''
            eggs_0h = 0
            sr_0h = 100.0
            if '/' in raw_0h:
                parts = raw_0h.split('/')
                eggs_0h = parse_clean_int(parts[0])
                sr_0h = parse_clean_float(parts[1])
            else:
                eggs_0h = parse_clean_int(raw_0h)
            
            raw_24h = r[5].strip() if len(r) > 5 else ''
            sr_24h = 0.0
            if 'SR%' in raw_24h or 'SR=' in raw_24h or 'SR%=' in raw_24h or 'SR' in raw_24h:
                m = re.search(r'SR%?\s*=?\s*([0-9]+(?:\.[0-9]+)?)', raw_24h)
                if m:
                    sr_24h = float(m.group(1))
            elif '%' in raw_24h:
                sr_24h = parse_clean_float(raw_24h)
            
            staff_combined = r[6].strip() if len(r) > 6 else ''
            col_staff = staff_combined
            score_staff = staff_combined
            if '/' in staff_combined:
                sp_parts = [p.strip() for p in staff_combined.split('/')]
                if len(sp_parts) >= 2:
                    col_staff = sp_parts[0]
                    score_staff = sp_parts[-1]

            live_0h = int(round(eggs_0h * (sr_0h / 100.0))) if sr_0h > 0 else 0
            live_24h = int(round(live_0h * (sr_24h / 100.0))) if sr_24h > 0 else 0

            p26_events.append({
                'year': 2026,
                'date': date_iso,
                'fishline': fishline,
                'line': line,
                'tanks': tanks,
                'primary_tank': tanks[0] if tanks else '',
                'in_tank': in_tank,
                'setup_staff': setup_staff,
                'collection_staff': col_staff,
                'scoring_24h_staff': score_staff,
                'staff_summary': f"{setup_staff} / {staff_combined}" if setup_staff else staff_combined,
                'eggs_0h': eggs_0h,
                'sr_0h': sr_0h,
                'live_0h': live_0h,
                'sr_24h': sr_24h,
                'live_24h': live_24h,
                'source': '2026_log_sheet_part2'
            })

    # Part 3: Newly transcribed pages 1-10
    p3_transcriptions = [
        ['29/06/2026', 'AB T99(F) x AB T130(M)', 'No', 'AE', '330', '100', 'AE', '89', 'AE'],
        ['29/06/2026', 'Gata T110 (intank)', 'Yes', 'AG', '368', '100', 'AE', '95', 'AG'],
        ['29/06/2026', 'Gata T111 (intank)', 'Yes', 'AG', '102', '100', 'AE', '63', 'AG'],
        ['29/06/2026', 'Gata T120 (intank)', 'Yes', 'AG', '131', '100', 'AE', '78', 'AG'],
        ['29/06/2026', 'Gata T113 (intank)', 'Yes', 'AG', '306', '100', 'AE', '23', 'AG'],
        ['30/06/2026', 'Gata T73', 'No', 'AG', '0', '0', '', '0', ''],
        ['30/06/2026', 'Gata T127', 'No', 'AG', '48', '100', 'AG', '75', 'AG'],
        ['30/06/2026', 'Gata T111 (intank)', 'Yes', 'AG', '101', '100', 'AE', '92', 'AE'],
        ['30/06/2026', 'Gata T49(M) x Gata T73(F)', 'No', 'AE', '911', '100', 'AE', '86', 'AG'],
        ['04/07/2026', 'Casp T121 intank', 'Yes', 'AE', '0', '0', '', '0', ''],
        ['04/07/2026', 'Casp T108 F,1 T77 M,1', 'No', 'AG', '0', '0', '', '0', ''],
        ['04/07/2026', 'Casp T124 1F,1M', 'No', 'AG', '0', '0', '', '0', ''],
        ['04/07/2026', 'Casp T109,F,1 T122,M,1', 'No', 'AG', '175', '99.4', 'AE', '33', 'AE'],
        ['04/07/2026', 'Casp T109 1F,1M', 'No', 'AG', '0', '0', '', '0', ''],
        ['04/07/2026', 'Casp T122 1F,1M', 'No', 'AG', '0', '0', '', '0', ''],
        ['04/07/2026', 'Casp T131 1F,1M', 'No', 'AG', '0', '0', '', '0', ''],
        ['04/07/2026', 'Casp T114,F,1 T77,M,1', 'No', 'AG', '0', '0', '', '0', ''],
        ['04/07/2026', 'Casp T108 1F,1M', 'No', 'AG', '134', '96', 'AE', '91.66', 'AE'],
        ['04/07/2026', 'Casp T126 In tank', 'Yes', 'AG', '226', '100', 'AE', '90.5', 'AE'],
        ['04/07/2026', 'Casp T125 In tank', 'Yes', 'AG', '231', '100', 'AE', '79.2', 'AE'],
        ['04/07/2026', 'Casp T115 intank', 'Yes', 'AG', '737', '100', 'AE', '84.12', 'AE'],
        ['05/07/2026', 'AB T86', 'No', 'AE', '955', '100', 'AE', '93', 'AE'],
        ['05/07/2026', 'AB T96', 'No', 'AE', '744', '100', 'AE', '82', 'AE'],
        ['05/07/2026', 'AB T99(F) x AB T130(M)', 'No', 'AE', '411', '100', 'AE', '92', 'AE'],
        ['05/07/2026', 'AB T76(F) x AB T130(M)', 'No', 'AE', '487', '100', 'AE', '94', 'AE'],
        ['06/07/2026', 'Gata T49(M) x Gata T73(F)', 'No', 'AE', '546', '100', 'AE', '94', 'AE'],
        ['06/07/2026', 'Gata T127', 'No', 'AE', '0', '0', '', '0', ''],
        ['07/07/2026', 'Gata T127', 'No', 'AE', '471', '100', 'AE', '72', 'AE'],
        ['11/07/2026', 'AB T87', 'No', 'AE', '0', '0', '', '0', ''],
        ['11/07/2026', 'AB T86', 'No', 'AE', '228', '100', 'AG', '73', 'AG'],
        ['18/07/2026', 'AB T86 intank', 'Yes', 'AG', '391', '100', 'AE', '84', 'AG'],
        ['18/07/2026', 'AB T129 intank', 'Yes', 'AG', '421', '100', 'AE', '75', 'AG'],
        ['18/07/2026', 'AB T96 intank', 'Yes', 'AG', '387', '100', 'AE', '74', 'AG'],
        ['19/07/2026', 'AB T106 intank', 'Yes', 'AG', '333', '100', 'AE', '90', 'AG'],
        ['19/07/2026', 'AB T81 intank', 'Yes', 'AG', '598', '100', 'AE', '83', 'AG'],
        ['19/07/2026', 'AB T80 intank', 'Yes', 'AG', '331', '100', 'AE', '61', 'AG'],
        ['19/07/2026', 'Gata T110 intank', 'Yes', 'AG', '76', '100', 'AE', '94', 'AG'],
        ['19/07/2026', 'Gata T120 intank', 'Yes', 'AG', '32', '100', 'AE', '62', 'AG'],
        ['20/07/2026', 'Fli T98 intank', 'Yes', 'AG', '274', '100', 'AE', '34.3', 'AG'],
        ['20/07/2026', 'Fli T83 intank', 'Yes', 'AG', '624', '100', 'AE', '77.8', 'AG'],
        ['20/07/2026', 'Fli T133 intank', 'Yes', 'AG', '747', '93', 'AE', '76.7', 'AG'],
        ['20/07/2026', 'Fli T119 intank', 'Yes', 'AG', '345', '100', 'AE', '95.9', 'AE'],
        ['20/07/2026', 'Fli T132 intank', 'Yes', 'AG', '163', '58', 'AE', '84.2', 'AE'],
        ['25/07/2026', 'Gata T110', 'No', 'AE', '0', '0', '', '0', ''],
        ['25/07/2026', 'Gata T120', 'No', 'AG', '71', '100', 'AE', '60', 'AG'],
        ['26/07/2026', 'Gata T111', 'No', 'AE', '897', '100', 'AG', '22', 'AG'],
        ['26/07/2026', 'Gata T113', 'No', 'AE', '138', '100', 'AE', '0', 'AE'],
        ['26/07/2026', 'Gata T113(F) x Gata T112(M)', 'No', 'AE', '349', '100', 'AE', '22', 'AG'],
        ['26/07/2026', 'Gata T112(M) x Gata T101(F)', 'No', 'AE', '666', '100', 'AE', '44', 'AE'],
        ['26/07/2026', 'Gata T101(M) x Gata T113(F)', 'No', 'AE', '268', '100', 'AG', '84', 'AG'],
        ['27/07/2026', 'AB T87', 'No', 'AE', '768', '97', 'AG', '93', 'AE'],
        ['27/07/2026', 'AB T83', 'No', 'AG', '634', '100', 'AE', '78', 'AE'],
        ['27/07/2026', 'AB T106', 'No', 'AE', '906', '100', 'AG', '66', 'AG'],
        ['27/07/2026', 'AB T86', 'No', 'AE', '931', '100', 'AG', '89', 'AE'],
        ['28/07/2026', 'AB T99(F) x AB T130(M)', 'No', 'AE', '947', '100', 'AE', '76', 'AE'],
        ['28/07/2026', 'AB T79(F) x AB T130(M)', 'No', 'AE', '2080', '100', 'AE', '79', 'AG'],
        ['28/07/2026', 'AB T93(M) x AB T95(F)', 'No', 'AE', '681', '100', 'AG', '73', 'AG'],
        ['28/07/2026', 'AB T97', 'No', 'AE', '159', '100', 'AE', '81', 'AE'],
        ['28/07/2026', 'AB T87', 'No', 'AE', '760', '100', 'AE', '83', 'AE'],
        ['28/07/2026', 'AB T128', 'No', 'AE', '317', '100', 'AG', '68', 'AG'],
        ['03/08/2026', 'AB T129', 'No', 'AG', '625', '100', 'AE', '95.2', 'AE'],
        ['03/08/2026', 'AB T96', 'No', 'AE', '774', '100', 'AE', '81', 'AG'],
        ['03/08/2026', 'AB T86', 'No', 'AE', '1007', '100', 'AG', '87.6', 'AE'],
        ['03/08/2026', 'AB T80', 'No', 'AE', '387', '100', 'AE', '78', 'AE'],
        ['03/08/2026', 'AB T106', 'No', 'AG', '1722', '100', 'AG', '71', 'AE'],
        ['04/08/2026', 'AB T128', 'No', 'AE', '528', '100', 'AE', '82.9', 'AG'],
        ['04/08/2026', 'AB T93(M) x AB T95(F)', 'No', 'AE', '1017', '100', 'AE', '91', 'AE'],
        ['04/08/2026', 'AB T99(F) x AB T130(M)', 'No', 'AE', '409', '100', 'AG', '79', 'AE'],
        ['04/08/2026', 'AB T97', 'No', 'AE', '502', '100', 'AE', '91', 'AG'],
        ['04/08/2026', 'AB T87', 'No', 'AE', '298', '100', 'AG', '68', 'AG'],
        ['04/08/2026', 'AB T129', 'No', 'AE', '147', '100', 'AG', '97', 'AG'],
        ['04/08/2026', 'AB T76(F) x AB T130(M)', 'No', 'AG', '210', '100', 'AE', '96', 'AE'],
        ['08/08/2026', 'AB T129', 'No', 'AG', '61', '100', 'AE', '78', 'AE'],
        ['08/08/2026', 'AB T128', 'No', 'AE', '374', '100', 'AG', '95.1', 'AG'],
        ['10/08/2026', 'AB T97', 'No', 'AE', '201', '100', 'AE', '73', 'AE'],
        ['11/08/2026', 'Fli T98', 'No', 'AE', '60', '100', 'AE', '10', 'AE'],
        ['11/08/2026', 'Fli T82', 'No', 'AG', '466', '100', 'AE', '96.5', 'AE'],
        ['11/08/2026', 'Fli T133', 'No', 'AE', '177', '100', 'AE', '87.5', 'AE'],
        ['11/08/2026', 'Fli T119', 'No', 'AG', '516', '100', 'AE', '88', 'AE'],
        ['11/08/2026', 'Fli T70', 'No', 'AE', '355', '100', 'AE', '7', 'AE'],
        ['11/08/2026', 'AB T80 intank', 'Yes', 'AE', '211', '100', 'AE', '72.9', 'AE'],
        ['11/08/2026', 'Fli T133(F) x Fli T98(M)', 'No', 'AG', '71', '100', 'AG', '73', 'AG'],
        ['11/08/2026', 'AB T81 intank', 'Yes', 'AG', '597', '100', 'AG', '87', 'AE'],
        ['11/08/2026', 'AB T86 intank', 'Yes', 'AG', '567', '100', 'AG', '89.9', 'AE'],
        ['15/08/2026', 'Fli T82', 'No', 'AG', '506', '100', 'AG', '91', 'AE'],
        ['15/08/2026', 'Fli T119', 'No', 'AG', '872', '100', 'AE', '95', 'AG'],
        ['16/08/2026', 'Fli T133', 'No', 'AE', '306', '100', 'AE', '77', 'AG'],
        ['16/08/2026', 'Fli T133(F) x Fli T98(M)', 'No', 'AG', '282', '100', 'AE', '83', 'AE'],
        ['16/08/2026', 'Fli T132', 'No', 'AE', '237', '100', 'AE', '91', 'AE'],
        ['16/08/2026', 'Fli T70', 'No', 'AE', '350', '100', 'AE', '14', 'AE'],
        ['16/08/2026', 'Fli T98', 'No', 'AE', '57', '100', 'AG', '0', 'AE'],
        ['22/08/2026', 'AB T129 In tank', 'Yes', 'EA', '122', '100', 'AE', '81.9', 'AE'],
        ['22/08/2026', 'AB T87', 'No', 'EA', '699', '100', 'AG', '86', 'AE'],
        ['23/08/2026', 'AB T99(F) x AB T130(M)', 'No', 'EA', '361', '100', 'AG', '96', 'EA'],
        ['23/08/2026', 'AB T80', 'No', 'EA', '392', '100', 'AG', '67', 'EA'],
        ['24/08/2026', 'AB T128', 'No', 'EA', '303', '100', 'AE', '92', 'AF'],
        ['24/08/2026', 'AB T95(F) x AB T93(M)', 'No', 'AE', '1312', '100', 'AE', '74.92', 'AF'],
        ['25/08/2026', 'AB T97', 'No', 'AE', '0', '0', '', '0', ''],
        ['25/08/2026', 'AB T81', 'No', 'AE', '759', '100', 'AG', '69.2', 'EA'],
        ['25/08/2026', 'AB T106', 'No', 'AE', '2252', '74', 'AG', '84.6', 'EA'],
        ['26/08/2026', 'Fli T119', 'No', 'AE', '467', '100', 'AE+AF', '93.61', 'MF'],
        ['28/08/2026', 'Fli T119', 'No', '', '508', '100', 'MF', '88.6', 'MF'],
        ['29/08/2026', 'AB T129', 'No', 'AF', '320', '100', 'AE+AF', '97.8', 'AF'],
        ['29/08/2026', 'AB T128', 'No', 'AE', '185', '100', '', '70.27', 'AF'],
        ['29/08/2026', 'AB T87', 'No', 'AF', '0', '0', 'AE+AF', '0', ''],
        ['29/08/2026', 'AB T86', 'No', 'AF', '1244', '100', 'AE+AF', '86.2', 'AF'],
        ['29/08/2026', 'AB T86 + AB T93(F)(M)', 'No', 'AF', '98', '100', 'AF', '94.8', 'AF']
    ]

    for p3 in p3_transcriptions:
        date_iso = parse_date(p3[0], 2026)
        fishline = p3[1]
        line, tanks = extract_line_and_tanks(fishline)
        in_tank = (p3[2].lower() == 'yes') or ('intank' in fishline.lower())
        setup_staff = p3[3]
        eggs_0h = parse_clean_int(p3[4])
        sr_0h = parse_clean_float(p3[5])
        col_staff = p3[6]
        sr_24h = parse_clean_float(p3[7])
        score_staff = p3[8]
        
        live_0h = int(round(eggs_0h * (sr_0h / 100.0))) if sr_0h > 0 else 0
        live_24h = int(round(live_0h * (sr_24h / 100.0))) if sr_24h > 0 else 0

        p26_events.append({
            'year': 2026,
            'date': date_iso,
            'fishline': fishline,
            'line': line,
            'tanks': tanks,
            'primary_tank': tanks[0] if tanks else '',
            'in_tank': in_tank,
            'setup_staff': setup_staff,
            'collection_staff': col_staff,
            'scoring_24h_staff': score_staff,
            'staff_summary': f"Setup: {setup_staff} | Col: {col_staff} | 24H: {score_staff}",
            'eggs_0h': eggs_0h,
            'sr_0h': sr_0h,
            'live_0h': live_0h,
            'sr_24h': sr_24h,
            'live_24h': live_24h,
            'source': '2026_log_sheet_part3'
        })

    # Sort 2026 events by date
    p26_events.sort(key=lambda x: x['date'] or '')
    print(f'Total 2026 breeding events compiled: {len(p26_events)}')

    # 3. Compile Master 2024 - 2026 Dataset
    all_events = []

    # 2024
    p24_path = os.path.join(done_dir, '24-including intank.csv')
    with open(p24_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        reader = list(csv.reader(f))
        for r in reader[1:]:
            if not r or not r[0].strip():
                continue
            date_iso = parse_date(r[0], 2024)
            fishline = r[1].strip()
            line, tanks = extract_line_and_tanks(fishline)
            in_tank = (r[2].strip().upper() == 'TRUE') or ('intank' in fishline.lower())
            eggs_0h = parse_clean_int(r[3])
            sr_0h = parse_clean_float(r[4])
            live_0h = parse_clean_int(r[5]) if len(r) > 5 else int(round(eggs_0h * (sr_0h / 100.0)))
            sr_24h = parse_clean_float(r[6]) if len(r) > 6 else 0.0
            live_24h = parse_clean_int(r[7]) if len(r) > 7 else int(round(live_0h * (sr_24h / 100.0)))
            
            all_events.append({
                'year': 2024,
                'date': date_iso,
                'fishline': fishline,
                'line': line,
                'tanks': tanks,
                'primary_tank': tanks[0] if tanks else '',
                'in_tank': in_tank,
                'setup_staff': '',
                'collection_staff': '',
                'scoring_24h_staff': '',
                'staff_summary': '',
                'eggs_0h': eggs_0h,
                'sr_0h': sr_0h,
                'live_0h': live_0h,
                'sr_24h': sr_24h,
                'live_24h': live_24h,
                'source': '2024_master'
            })

    # 2025
    p25_path = os.path.join(done_dir, '25-including intank.xlsx')
    r25 = read_xlsx_rows(p25_path)
    for r in r25[1:]:
        if not r or not r[0].strip():
            continue
        date_iso = parse_date(r[0], 2025)
        fishline = r[1].strip() if len(r) > 1 else ''
        line, tanks = extract_line_and_tanks(fishline)
        in_tank = (r[2].strip() == '1' or r[2].strip().upper() == 'TRUE') if len(r) > 2 else False
        eggs_0h = parse_clean_int(r[3]) if len(r) > 3 else 0
        sr_0h = parse_clean_float(r[4]) if len(r) > 4 else 0.0
        live_0h = parse_clean_int(r[5]) if len(r) > 5 else int(round(eggs_0h * (sr_0h / 100.0)))
        sr_24h = parse_clean_float(r[6]) if len(r) > 6 else 0.0
        live_24h = int(round(live_0h * (sr_24h / 100.0))) if sr_24h > 0 else 0

        all_events.append({
            'year': 2025,
            'date': date_iso,
            'fishline': fishline,
            'line': line,
            'tanks': tanks,
            'primary_tank': tanks[0] if tanks else '',
            'in_tank': in_tank,
            'setup_staff': '',
            'collection_staff': '',
            'scoring_24h_staff': '',
            'staff_summary': '',
            'eggs_0h': eggs_0h,
            'sr_0h': sr_0h,
            'live_0h': live_0h,
            'sr_24h': sr_24h,
            'live_24h': live_24h,
            'source': '2025_master'
        })

    all_events.extend(p26_events)
    all_events.sort(key=lambda x: x['date'] or '')
    print(f'Total Grand Combined Events (2024-2026): {len(all_events)}')

    # 4. Compute Tank Breeding Metrics joined with FishNET.tab
    tank_stats = {}
    for tuid, tinfo in unique_tanks.items():
        tank_stats[tuid] = {
            **tinfo,
            'total_spawns': 0,
            'successful_spawns': 0,
            'total_eggs_0h': 0,
            'total_live_24h': 0,
            'avg_eggs_per_spawn': 0.0,
            'avg_sr_0h': 0.0,
            'avg_sr_24h': 0.0,
            'in_tank_spawns': 0,
            'pairwise_spawns': 0,
            'cross_partners': {},
            'first_spawn': '',
            'last_spawn': '',
            'spawns_by_year': {2024: 0, 2025: 0, 2026: 0},
            'eggs_by_year': {2024: 0, 2025: 0, 2026: 0},
            'spawn_history': []
        }

    # Canonical Cross-Pairing Synergy (interchangeable setups unified)
    def get_canonical_pair(t1, t2):
        obj1 = unique_tanks.get(t1, {})
        obj2 = unique_tanks.get(t2, {})
        s1 = obj1.get('sex_type', '')
        s2 = obj2.get('sex_type', '')
        
        if s1 == 'Female-Only' and s2 == 'Male-Only':
            dam, sire = t1, t2
        elif s2 == 'Female-Only' and s1 == 'Male-Only':
            dam, sire = t2, t1
        elif obj1.get('female', 0) > 0 and obj2.get('male', 0) > 0 and obj1.get('male', 0) == 0:
            dam, sire = t1, t2
        elif obj2.get('female', 0) > 0 and obj1.get('male', 0) > 0 and obj2.get('male', 0) == 0:
            dam, sire = t2, t1
        else:
            psort = sorted([t1, t2])
            dam, sire = psort[0], psort[1]
            
        p_key = f"{dam} x {sire}"
        return p_key, dam, sire

    pair_synergies = defaultdict(lambda: {
        'tank_a': '', 'tank_b': '', 'dam': '', 'sire': '', 'line': '', 'dam_line': '', 'sire_line': '', 'is_outcross': False,
        'spawns': 0, 'eggs': 0, 'live24h': 0, 'sr0_sum': 0, 'sr24_sum': 0
    })

    for ev in all_events:
        t_list = ev['tanks']
        if len(t_list) >= 2:
            t1, t2 = t_list[0], t_list[1]
            p_key, dam, sire = get_canonical_pair(t1, t2)
            ps = pair_synergies[p_key]
            ps['tank_a'] = dam
            ps['tank_b'] = sire
            ps['dam'] = dam
            ps['sire'] = sire
            line_dam = unique_tanks.get(dam, {}).get('line', 'Other')
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
            ps['sire_line'] = line_sire
            ps['spawns'] += 1
            ps['eggs'] += ev['eggs_0h']
            ps['live24h'] += ev['live_24h']
            if ev['eggs_0h'] > 0:
                ps['sr0_sum'] += ev['sr_0h']
                ps['sr24_sum'] += ev['sr_24h']


        for t in t_list:
            if t in tank_stats:
                st = tank_stats[t]
                st['total_spawns'] += 1
                if ev['eggs_0h'] > 0 and ev['sr_24h'] > 0:
                    st['successful_spawns'] += 1
                st['total_eggs_0h'] += ev['eggs_0h']
                st['total_live_24h'] += ev['live_24h']
                if ev['in_tank']:
                    st['in_tank_spawns'] += 1
                else:
                    st['pairwise_spawns'] += 1
                
                # Track partners
                for p in t_list:
                    if p != t:
                        st['cross_partners'][p] = st['cross_partners'].get(p, 0) + 1

                yr = ev['year']
                if yr in st['spawns_by_year']:
                    st['spawns_by_year'][yr] += 1
                    st['eggs_by_year'][yr] += ev['eggs_0h']
                if not st['first_spawn'] or (ev['date'] and ev['date'] < st['first_spawn']):
                    st['first_spawn'] = ev['date']
                if not st['last_spawn'] or (ev['date'] and ev['date'] > st['last_spawn']):
                    st['last_spawn'] = ev['date']
                
                # Age calculation
                age_months = None
                if st['dob_dt'] and ev['date']:
                    try:
                        sp_dt = datetime.strptime(ev['date'], '%Y-%m-%d')
                        diff_days = (sp_dt - st['dob_dt']).days
                        age_months = round(diff_days / 30.4375, 1)
                    except:
                        pass
                
                st['spawn_history'].append({
                    'date': ev['date'],
                    'year': ev['year'],
                    'eggs_0h': ev['eggs_0h'],
                    'sr_0h': ev['sr_0h'],
                    'sr_24h': ev['sr_24h'],
                    'live_24h': ev['live_24h'],
                    'in_tank': ev['in_tank'],
                    'age_months': age_months,
                    'staff': ev.get('staff_summary', '')
                })

    for tuid, st in tank_stats.items():
        if st['total_spawns'] > 0:
            st['avg_eggs_per_spawn'] = round(st['total_eggs_0h'] / st['total_spawns'], 1)
            valid_sr0 = [h['sr_0h'] for h in st['spawn_history'] if h['eggs_0h'] > 0]
            valid_sr24 = [h['sr_24h'] for h in st['spawn_history'] if h['eggs_0h'] > 0]
            st['avg_sr_0h'] = round(sum(valid_sr0) / len(valid_sr0), 1) if valid_sr0 else 0.0
            st['avg_sr_24h'] = round(sum(valid_sr24) / len(valid_sr24), 1) if valid_sr24 else 0.0

    # Format pair synergies list
    pair_list = []
    for k, v in pair_synergies.items():
        if v['spawns'] > 0:
            avg_c = round(v['eggs'] / v['spawns'], 1)
            avg_sr24 = round(v['sr24_sum'] / v['spawns'], 1)
            pair_list.append({
                'pair_key': k,
                'tank_a': v['tank_a'],
                'tank_b': v['tank_b'],
                'line': v['line'],
                'spawns': v['spawns'],
                'total_eggs': v['eggs'],
                'avg_clutch': avg_c,
                'avg_sr24': avg_sr24,
                'total_live24h': v['live24h']
            })
    pair_list.sort(key=lambda x: x['total_eggs'], reverse=True)

    summary_data = {
        'events': all_events,
        'tank_stats': {k: {k2: v2 for k2, v2 in v.items() if k2 != 'dob_dt'} for k, v in tank_stats.items()},
        'pair_synergies': pair_list,
        'metadata': {
            'total_events': len(all_events),
            'events_2024': sum(1 for e in all_events if e['year'] == 2024),
            'events_2025': sum(1 for e in all_events if e['year'] == 2025),
            'events_2026': sum(1 for e in all_events if e['year'] == 2026),
            'total_eggs_spawned': sum(e['eggs_0h'] for e in all_events),
            'total_live_24h': sum(e['live_24h'] for e in all_events),
            'total_tanks': len(unique_tanks),
            'active_tanks': sum(1 for t in unique_tanks.values() if t['status'] == 'Active'),
            'euthanized_tanks': sum(1 for t in unique_tanks.values() if t['status'] == 'Euthanized'),
            'female_only_tanks': n_f_only,
            'male_only_tanks': n_m_only,
            'mixed_colony_tanks': n_mixed
        }
    }
    
    with open(os.path.join(labels_dir, 'breeding_dashboard_data.json'), 'w', encoding='utf-8') as f:
        json.dump(summary_data, f)
    print(f'Saved breeding_dashboard_data.json with sex awareness and {len(pair_list)} cross-pair records.')

if __name__ == '__main__':
    process()
