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
    # Correct common OCR/typos like A13 -> AB, A1B -> AB
    s_clean = re.sub(r'\bA13\b', 'AB', s, flags=re.IGNORECASE)
    s_clean = re.sub(r'\bA1B\b', 'AB', s_clean, flags=re.IGNORECASE)
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
    
    # Extract tank numbers matching T123, T-123, T.123, AB106, Gata101, Fli19, Tank 95, Cas.126, etc.
    res = []
    # Pattern 1: Tank/T prefix followed by digits
    for m in re.finditer(r'(?:Tank|T|T\.|T\-)\s*0*([0-9]{1,4})\b', s_clean, re.IGNORECASE):
        res.append(int(m.group(1)))
    # Pattern 2: Strain prefix directly followed by digits (e.g. AB106, Gata101, Cas114, Cas.126)
    for m in re.finditer(r'(?:AB|Fli|Gata|Casper|Casp|Cas)[\s\.\-]*0*([0-9]{1,4})\b', s_clean, re.IGNORECASE):
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
    
    # 1. Load Nursery Mapping
    nursery_map = {}
    nursery_by_cross = {}
    nursery_tab_path = os.path.join(labels_dir, 'FishNet Exported Data', 'Nursery.tab')
    if os.path.exists(nursery_tab_path):
        with open(nursery_tab_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for r in csv.reader(f, delimiter='\t'):
                if len(r) >= 8:
                    nuid = r[0].strip().upper()
                    count = r[1].strip()
                    action = r[2].strip()
                    cuid = r[4].strip().upper()
                    grad_date = r[6].strip()
                    mating_date = r[7].strip()
                    set_date = r[8].strip() if len(r) > 8 else ''
                    dam = r[9].strip() if len(r) > 9 else ''
                    sire = r[10].strip() if len(r) > 10 else ''
                    n_rec = {
                        'nuid': nuid, 'count': count, 'action': action, 'cuid': cuid,
                        'grad_date': grad_date, 'mating_date': mating_date, 'set_date': set_date,
                        'dam': dam, 'sire': sire
                    }
                    nursery_map[nuid] = n_rec
                    if cuid:
                        if cuid not in nursery_by_cross:
                            nursery_by_cross[cuid] = []
                        nursery_by_cross[cuid].append(n_rec)

    # 2. Load Crosses Mapping for Cross-Checking DOB (with dynamic column extraction)
    crosses_map = {}
    crosses_tab_path = os.path.join(labels_dir, 'FishNet Exported Data', 'Crosses.tab')
    if os.path.exists(crosses_tab_path):
        with open(crosses_tab_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for r in csv.reader(f, delimiter='\t'):
                if not r: continue
                cuid = None
                for col in r:
                    c_m = re.search(r'\b(C\d{4})\b', col.strip().upper())
                    if c_m:
                        cuid = c_m.group(1)
                        break
                if not cuid: continue
                
                dates = []
                for col in r:
                    c_str = col.strip()
                    if re.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$', c_str) or re.match(r'^\d{1,2}-[A-Za-z]{3}-\d{2,4}$', c_str):
                        dates.append(c_str)
                mating_date = dates[0] if dates else ''
                
                tanks_in_row = []
                for col in r:
                    for tm in re.findall(r'\bT\d{4}\b', col.strip().upper()):
                        if tm not in tanks_in_row:
                            tanks_in_row.append(tm)
                
                crosses_map[cuid] = {
                    'cuid': cuid,
                    'date': mating_date,
                    'dam': tanks_in_row[0] if len(tanks_in_row) > 0 else '',
                    'sire': tanks_in_row[1] if len(tanks_in_row) > 1 else (tanks_in_row[0] if tanks_in_row else '')
                }

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
        
        # Check nursery date if cross date missing
        if not cross_dt and d_cross:
            n_list = nursery_by_cross.get(d_cross.upper(), [])
            if n_list:
                cross_dt = parse_cross_date_dt(n_list[0].get('mating_date', ''))
        
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

    # 3. Load FishNET Tanks with Sex Structure Analysis
    # 3. Load FishNET Tanks with Sex Structure Analysis
    fishnet_tanks = {}
    tanks_tab_path = os.path.join(labels_dir, 'FishNet Exported Data', 'Tanks.tab')
    if not os.path.exists(tanks_tab_path):
        tanks_tab_path = os.path.join(labels_dir, 'FishNET.tab')

    with open(tanks_tab_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        reader = list(csv.reader(f, delimiter='\t'))
        
    if reader:
        header_row = reader[0]
        has_header = ('TUID' in [c.strip().upper() for c in header_row] or 'STATUS' in [c.strip().upper() for c in header_row])
        col_map = {col.strip().upper(): idx for idx, col in enumerate(header_row)} if has_header else {}
        data_rows = reader[1:] if has_header else reader
        
        for row in data_rows:
            if not row:
                continue
                
            if has_header:
                def get_val(col_name, default=''):
                    idx = col_map.get(col_name.upper())
                    if idx is not None and idx < len(row):
                        return row[idx].strip()
                    return default
                    
                tuid = get_val('TUID')
                if not tuid or not tuid.upper().startswith('T'):
                    continue
                tuid = tuid.upper()
                
                dob = get_val('DOB') or get_val('DATE OF BIRTH')
                dod = get_val('DATE OF DEATH') or get_val('DATE_OF_DEATH')
                derivative_cross = get_val('DERIVATIVE_CROSS') or get_val('DERVITIVE CROSS')
                facility = get_val('FACILITY', 'Zebrafish')
                female_str = get_val('FEMALE') or get_val('FEMALES')
                male_str = get_val('MALE') or get_val('MALES')
                total_str = get_val('TOTAL_FISH') or get_val('NUMBER OF FISH') or get_val('TOTAL')
                genotype = get_val('GENOTYPE')
                notes = get_val('NOTES')
                protocol = get_val('PROTOCOL')
                status_raw = get_val('STATUS', 'Adult/Active')
                tank_size = get_val('TANK_SIZE') or get_val('TANK SIZE')
                turnover_date = get_val('TURNOVER_DEADLINE') or get_val('TURNOVER DATE')
                lab_name = get_val('LABORATORIES::LAB NAME') or get_val('LAB NAME')
                lab_member = get_val('LAB MEMBER')
                room = get_val('ROOM', 'D126')
            else:
                if len(row) < 21:
                    continue
                tuid = row[20].strip().upper()
                if not tuid or not tuid.startswith('T'):
                    continue
                dob = row[0].strip()
                dod = row[1].strip() if len(row) > 1 else ''
                derivative_cross = row[2].strip() if len(row) > 2 else ''
                facility = row[3].strip() if len(row) > 3 else ''
                female_str = row[4].strip() if len(row) > 4 else ''
                genotype = row[5].strip() if len(row) > 5 else ''
                lab_member = row[6].strip() if len(row) > 6 else ''
                male_str = row[7].strip() if len(row) > 7 else ''
                notes = row[8].strip() if len(row) > 8 else ''
                total_str = row[9].strip() if len(row) > 9 else ''
                protocol = row[10].strip() if len(row) > 10 else ''
                room = row[12].strip() if len(row) > 12 else ''
                status_raw = row[16].strip() if len(row) > 16 else 'Adult/Active'
                tank_size = row[18].strip() if len(row) > 18 else ''
                turnover_date = row[21].strip() if len(row) > 21 else ''
                lab_name = row[22].strip() if len(row) > 22 else ''

            female = int(female_str) if female_str.isdigit() else 0
            male = int(male_str) if male_str.isdigit() else 0
            total = int(total_str) if total_str.isdigit() else (female + male)
            
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

            # Link derivative nursery records
            n_records = nursery_by_cross.get(derivative_cross.upper(), [])
            derivative_nursery = ', '.join([n['nuid'] for n in n_records]) if n_records else ''
            nursery_grad_date = n_records[0]['grad_date'] if n_records else ''
            nursery_count = sum(int(n['count']) for n in n_records if n['count'].isdigit()) if n_records else 0

            tank_obj = {
                'tuid': std_tuid,
                'raw_tuid': tuid,
                'num_id': num_id,
                'derivative_cross': derivative_cross,
                'derivative_nursery': derivative_nursery,
                'nursery_grad_date': nursery_grad_date,
                'nursery_count': nursery_count,
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

    # 2. Parse 2026 Data from verified 2026_Updated.xlsx
    p26_events = []
    p26_updated_xlsx = os.path.join(done_dir, '2026_Updated.xlsx')
    p26_csv_path = os.path.join(done_dir, '2026_breeding_complete.csv')
    
    if os.path.exists(p26_updated_xlsx):
        print(f"Loading 2026 data directly from verified update: {p26_updated_xlsx}")
        import openpyxl
        wb26 = openpyxl.load_workbook(p26_updated_xlsx, data_only=True)
        ws26 = wb26.active
        
        csv_rows_to_save = [['Date', 'Fishline', 'In_Tank', 'Total_Eggs_0H', 'Survival_Rate_0H', 'Live_Embryos_0H', 'Survival_Rate_24H']]
        
        for r in range(2, ws26.max_row + 1):
            d_val = ws26.cell(r, 1).value
            fl = str(ws26.cell(r, 2).value or '').strip()
            in_tank_val = ws26.cell(r, 3).value
            eggs = ws26.cell(r, 4).value or 0
            sr0 = ws26.cell(r, 5).value or 0.0
            live0 = ws26.cell(r, 6).value or 0
            sr24 = ws26.cell(r, 7).value or 0.0
            
            if not fl and not d_val:
                continue
                
            if isinstance(d_val, datetime):
                date_iso = d_val.strftime('%Y-%m-%d')
            else:
                date_iso = parse_date(d_val, 2026)
                
            in_tank = bool(in_tank_val)
            if isinstance(in_tank_val, str):
                in_tank = in_tank_val.strip().upper() in ['TRUE', 'YES', '1']
                
            line, tanks = extract_line_and_tanks(fl)
            eggs_0h = parse_clean_int(eggs)
            sr_0h = parse_clean_float(sr0)
            live_0h = parse_clean_int(live0) if live0 else int(round(eggs_0h * (sr_0h / 100.0)))
            sr_24h = parse_clean_float(sr24)
            live_24h = int(round(live_0h * (sr_24h / 100.0))) if sr_24h > 0 else 0
            
            csv_rows_to_save.append([date_iso, fl, in_tank, eggs_0h, sr_0h, live_0h, sr_24h])
            
            p26_events.append({
                'year': 2026,
                'date': date_iso,
                'fishline': fl,
                'line': line,
                'tanks': tanks,
                'primary_tank': tanks[0] if tanks else '',
                'in_tank': in_tank,
                'setup_staff': 'Lab Staff',
                'collection_staff': 'Lab Staff',
                'scoring_24h_staff': 'Lab Staff',
                'staff_summary': 'Lab Staff',
                'eggs_0h': eggs_0h,
                'sr_0h': sr_0h,
                'live_0h': live_0h,
                'sr_24h': sr_24h,
                'live_24h': live_24h,
                'source': '2026_Updated'
            })
            
        with open(p26_csv_path, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows(csv_rows_to_save)
        print(f"Synchronized {p26_csv_path} with {len(p26_events)} rows.")
    elif os.path.exists(p26_csv_path):
        print(f"Loading 2026 data from {p26_csv_path}...")
        with open(p26_csv_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = list(csv.reader(f))
            for r in reader[1:]:
                if not r or len(r) < 2 or not r[0].strip():
                    continue
                date_iso = parse_date(r[0], 2026)
                fishline = r[1].strip()
                line, tanks = extract_line_and_tanks(fishline)
                in_tank = r[2].strip().upper() in ['TRUE', 'YES', '1'] if len(r) > 2 else ('intank' in fishline.lower())
                eggs_0h = parse_clean_int(r[3]) if len(r) > 3 else 0
                sr_0h = parse_clean_float(r[4]) if len(r) > 4 else 0.0
                live_0h = parse_clean_int(r[5]) if len(r) > 5 else int(round(eggs_0h * (sr_0h / 100.0)))
                sr_24h = parse_clean_float(r[6]) if len(r) > 6 else 0.0
                live_24h = int(round(live_0h * (sr_24h / 100.0))) if sr_24h > 0 else 0
                
                p26_events.append({
                    'year': 2026,
                    'date': date_iso,
                    'fishline': fishline,
                    'line': line,
                    'tanks': tanks,
                    'primary_tank': tanks[0] if tanks else '',
                    'in_tank': in_tank,
                    'setup_staff': 'Lab Staff',
                    'collection_staff': 'Lab Staff',
                    'scoring_24h_staff': 'Lab Staff',
                    'staff_summary': 'Lab Staff',
                    'eggs_0h': eggs_0h,
                    'sr_0h': sr_0h,
                    'live_0h': live_0h,
                    'sr_24h': sr_24h,
                    'live_24h': live_24h,
                    'source': '2026_Updated'
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

    # 5. Compute Pedigree, Kinship Matrix & Inbreeding (F)
    parents_map = {}
    explicit_gen = {}
    children_map = defaultdict(list)
    for tuid, st in tank_stats.items():
        d_cross = st.get('derivative_cross', '').upper()
        notes = st.get('notes', '')
        genotype = st.get('genotype', '')
        combined = f"{notes} {genotype}"

        # Extract explicit generation tag (e.g. G1, G2, F1, F2)
        m_gen = re.search(r'\b[GF](\d+)\b', combined, re.I)
        explicit_gen[tuid] = int(m_gen.group(1)) if m_gen else 0

        dam, sire = '', ''
        if d_cross in crosses_map:
            dam = crosses_map[d_cross].get('dam', '')
            sire = crosses_map[d_cross].get('sire', '')
        if not dam and not sire:
            m_tanks = re.findall(r'\bT\s*0*(\d{1,4})\b', notes, re.I)
            if len(m_tanks) >= 2:
                dam = f'T{int(m_tanks[0]):04d}'
                sire = f'T{int(m_tanks[1]):04d}'
            elif len(m_tanks) == 1:
                dam = f'T{int(m_tanks[0]):04d}'
                sire = dam
        parents_map[tuid] = (sire, dam)
        st['sire'] = sire
        st['dam'] = dam
        st['sire_tuid'] = sire
        st['dam_tuid'] = dam

    for tuid, (sire, dam) in parents_map.items():
        if sire and sire in tank_stats:
            children_map[sire].append(tuid)
        if dam and dam in tank_stats and dam != sire:
            children_map[dam].append(tuid)

    for tuid, st in tank_stats.items():
        st['progeny'] = children_map[tuid]
        st['progeny_count'] = len(children_map[tuid])
        st['children'] = children_map[tuid]
        gc = []
        for child_id in children_map[tuid]:
            for gc_id in children_map.get(child_id, []):
                if gc_id not in gc:
                    gc.append(gc_id)
        st['grandchildren'] = gc
    # Tabular Kinship & Inbreeding (Henderson's Numerator Relationship Matrix A)
    all_ids = sorted(list(tank_stats.keys()))
    A = defaultdict(lambda: defaultdict(float))
    for i in all_ids:
        si, di = parents_map.get(i, ('', ''))
        if si and di and si in tank_stats and di in tank_stats:
            A[i][i] = 1.0 + 0.5 * A[si][di]
        else:
            A[i][i] = 1.0
        for j in all_ids:
            if i == j: continue
            sj, dj = parents_map.get(j, ('', ''))
            if sj and dj and sj in tank_stats and dj in tank_stats:
                val = 0.5 * (A[i][sj] + A[i][dj])
            elif sj and sj in tank_stats:
                val = 0.5 * A[i][sj]
            elif dj and dj in tank_stats:
                val = 0.5 * A[i][dj]
            else:
                val = 0.0
            A[i][j] = val
            A[j][i] = val

    inbreeding_coeffs = {}
    for i in all_ids:
        si, di = parents_map.get(i, ('', ''))
        if si and di and si in tank_stats and di in tank_stats:
            inbreeding_coeffs[i] = round(0.5 * A[si][di], 4)
        else:
            inbreeding_coeffs[i] = 0.0
        tank_stats[i]['inbreeding_f'] = inbreeding_coeffs[i]

    # Scientifically Documented Filial Inbreeding Generation (F_n)
    # Rules (Standardized Genetic Nomenclature / The Zebrafish Book / Falconer & Mackay):
    # 1. Founder / Unknown Parents: F0
    # 2. Inter-line Outcross (e.g. Casper x AB): Resets to F1 (inbreeding broken)
    # 3. Within-line Outcross (Unrelated families / distant cousins, Kinship A[si][di] < 0.0625): Resets to F1
    # 4. Sibling / Sibling-intercross Inbreeding (A[si][di] >= 0.0625 or si == di): 1 + max(F(si), F(di))
    filial_gen = {}
    def calc_filial(t, visited=None):
        if visited is None: visited = set()
        if t in filial_gen: return filial_gen[t]
        if t in visited: return 0
        visited.add(t)

        s, d = parents_map.get(t, ('', ''))
        if not s and not d:
            filial_gen[t] = 0
            return 0

        fs = calc_filial(s, visited.copy()) if s and s in tank_stats else 0
        fd = calc_filial(d, visited.copy()) if d and d in tank_stats else 0

        line_s = tank_stats.get(s, {}).get('line', '')
        line_d = tank_stats.get(d, {}).get('line', '')
        is_diff_line = (line_s and line_d and line_s != line_d)

        kinship = A[s][d] if (s and d and s in tank_stats and d in tank_stats) else 0.0
        is_unrelated_within_line = (not is_diff_line and s != d and kinship < 0.0625)

        if is_diff_line or is_unrelated_within_line:
            filial_gen[t] = 1
        else:
            filial_gen[t] = 1 + max(fs, fd)

        return filial_gen[t]

    for t in tank_stats:
        calc_filial(t)
        tank_stats[t]['gen_depth'] = filial_gen[t]
        tank_stats[t]['generation'] = filial_gen[t]
        tank_stats[t]['filial_generation'] = filial_gen[t]
        tank_stats[t]['gen'] = filial_gen[t]

    # 6. Compute Turnover Countdown, Aging Lifecycle & Compliance Alerts
    NOW = datetime(2026, 10, 6)
    alerts = []
    turnover_overdue = []
    turnover_due30 = []
    turnover_due60 = []
    turnover_due90 = []
    turnover_future = []

    for tuid, st in tank_stats.items():
        # Lifecycle stage
        dob_dt = st.get('dob_dt')
        age_months = None
        if dob_dt:
            diff_days = (NOW - dob_dt).days
            age_months = round(diff_days / 30.4375, 1)
        st['age_months_now'] = age_months

        if st['status'] != 'Active':
            st['lifecycle_stage'] = 'Euthanized / Inactive'
        elif age_months is not None:
            if age_months < 3:
                st['lifecycle_stage'] = 'Juvenile (<3m)'
            elif age_months <= 6:
                st['lifecycle_stage'] = 'Young Adult (3-6m)'
            elif age_months <= 12:
                st['lifecycle_stage'] = 'Prime Breeding (6-12m)'
            elif age_months <= 18:
                st['lifecycle_stage'] = 'Mature Stock (12-18m)'
            else:
                st['lifecycle_stage'] = 'Geriatric (>18m)'
        else:
            st['lifecycle_stage'] = 'Active (Unknown Age)'

        # Turnover date parsing
        turn_str = st.get('turnover_date', '')
        turn_dt = None
        for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%d-%b-%y', '%d-%b-%Y', '%d-%m-%y']:
            try:
                turn_dt = datetime.strptime(turn_str, fmt)
                if turn_dt.year > 2030: turn_dt = turn_dt.replace(year=turn_dt.year - 100)
                break
            except:
                pass
        
        # Fallback 18 months (548 days / 1.5 years) from DOB
        if not turn_dt and dob_dt:
            turn_dt = dob_dt + timedelta(days=548)

        if turn_dt and st['status'] == 'Active':
            days_left = (turn_dt - NOW).days
            st['days_to_turnover'] = days_left
            st['turnover_date_resolved'] = turn_dt.strftime('%d-%m-%Y')
            
            if days_left < 0:
                st['turnover_urgency'] = 'OVERDUE'
                turnover_overdue.append(tuid)
                alerts.append({
                    'tuid': tuid, 'line': st['line'], 'severity': 'CRITICAL',
                    'category': 'Turnover Overdue',
                    'message': f"Tank is {abs(days_left)} days past 18-month colony turnover limit (Turnover: {st['turnover_date_resolved']}).",
                    'action': 'Schedule immediate renewal cross or colony retirement.'
                })
            elif days_left <= 30:
                st['turnover_urgency'] = 'DUE SOON (<=30d)'
                turnover_due30.append(tuid)
                alerts.append({
                    'tuid': tuid, 'line': st['line'], 'severity': 'HIGH',
                    'category': 'Turnover Due Soon',
                    'message': f"Reaches 18-month turnover deadline in {days_left} days.",
                    'action': 'Set up next-generation replacement pairings in breeding room.'
                })
            elif days_left <= 60:
                st['turnover_urgency'] = 'UPCOMING (31-60d)'
                turnover_due60.append(tuid)
            elif days_left <= 90:
                st['turnover_urgency'] = 'UPCOMING (61-90d)'
                turnover_due90.append(tuid)
            else:
                st['turnover_urgency'] = 'FUTURE (>90d)'
                turnover_future.append(tuid)
        else:
            st['days_to_turnover'] = None
            st['turnover_urgency'] = 'N/A'
            st['turnover_date_resolved'] = turn_str or '-'

        # Inbreeding alerts
        if st['status'] == 'Active' and st['inbreeding_f'] >= 0.25:
            alerts.append({
                'tuid': tuid, 'line': st['line'], 'severity': 'HIGH',
                'category': 'Elevated Inbreeding',
                'message': f"Inbreeding coefficient F = {st['inbreeding_f']} (Full-sib / Parent-Offspring level).",
                'action': 'Outcross with unrelated stock in next generation.'
            })

        # Single-Sex Stock Depletion Alerts
        if st['status'] == 'Active' and st['total'] < 5 and (st['sex_type'] == 'Female-Only' or st['sex_type'] == 'Male-Only'):
            alerts.append({
                'tuid': tuid, 'line': st['line'], 'severity': 'MEDIUM',
                'category': 'Low Biomass Reservoir',
                'message': f"Single-sex reservoir has only {st['total']} fish remaining ({st['female']}F / {st['male']}M).",
                'action': 'Replenish reservoir from upcoming nursery graduation batches.'
            })

    # 7. Compile Complete Crosses Registry
    crosses_registry = []
    # Map tank offspring
    cross_offspring = defaultdict(list)
    for tuid, st in tank_stats.items():
        if st.get('derivative_cross'):
            cross_offspring[st['derivative_cross'].upper()].append(tuid)

    for cuid, c_data in sorted(crosses_map.items()):
        n_clutches = nursery_by_cross.get(cuid, [])
        off_tanks = cross_offspring.get(cuid, [])
        n_count = sum(int(n['count']) for n in n_clutches if n['count'].isdigit()) if n_clutches else 0
        n_grad = n_clutches[0]['grad_date'] if n_clutches else ''
        
        dam_t = tank_stats.get(c_data.get('dam', ''), {})
        sire_t = tank_stats.get(c_data.get('sire', ''), {})
        line_str = f"{dam_t.get('line', 'AB')} x {sire_t.get('line', 'AB')}" if dam_t or sire_t else 'AB x AB'
        
        crosses_registry.append({
            'cuid': cuid,
            'mating_date': c_data.get('date', '-'),
            'dam': c_data.get('dam', '-'),
            'sire': c_data.get('sire', '-'),
            'line_pair': line_str,
            'nursery_clutches': [n['nuid'] for n in n_clutches],
            'nursery_count': n_count,
            'nursery_grad_date': n_grad,
            'offspring_tanks': off_tanks,
            'offspring_count': len(off_tanks)
        })

    summary_data = {
        'events': all_events,
        'tank_stats': {k: {k2: v2 for k2, v2 in v.items() if k2 != 'dob_dt'} for k, v in tank_stats.items()},
        'pair_synergies': pair_list,
        'crosses_registry': crosses_registry,
        'alerts': alerts,
        'turnover_summary': {
            'overdue_count': len(turnover_overdue),
            'due30_count': len(turnover_due30),
            'due60_count': len(turnover_due60),
            'due90_count': len(turnover_due90),
            'future_count': len(turnover_future)
        },
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
            'larvae_tanks': sum(1 for t in unique_tanks.values() if t['status'] == 'Larvae'),
            'female_only_tanks': n_f_only,
            'male_only_tanks': n_m_only,
            'mixed_colony_tanks': n_mixed,
            'total_crosses': len(crosses_registry),
            'total_alerts': len(alerts)
        }
    }
    
    with open(os.path.join(labels_dir, 'breeding_dashboard_data.json'), 'w', encoding='utf-8') as f:
        json.dump(summary_data, f)
    print(f'Saved breeding_dashboard_data.json with pedigree, turnover, crosses, and {len(alerts)} alerts.')

    # Synchronize grand master CSV
    master_csv_path = os.path.join(labels_dir, 'archive', 'DONE', 'fishnet_master_breeding_2024_2026.csv')
    try:
        with open(master_csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow([
                'Event_ID', 'Year', 'Spawn_Date', 'Fishline_Raw', 'Standard_Line',
                'Tanks_Involved', 'Primary_Tank', 'In_Tank', 'Setup_Staff_Initial',
                'Collection_0H_Staff_Initial', 'Scoring_24H_Staff_Initial',
                'Total_Eggs_0H', 'Survival_Rate_0H', 'Live_Embryos_0H',
                'Survival_Rate_24H', 'Live_Embryos_24H', 'Fertility_Success', 'Source'
            ])
            for i, ev in enumerate(all_events, 1):
                t_str = ';'.join(ev['tanks'])
                p_tank = ev['primary_tank'] if ev['primary_tank'] else (ev['tanks'][0] if ev['tanks'] else '')
                w.writerow([
                    f"EV-{i:05d}",
                    str(ev['year']),
                    ev['date'],
                    ev['fishline'],
                    ev['line'],
                    t_str,
                    p_tank,
                    'Yes' if ev['in_tank'] else 'No',
                    ev.get('setup_staff', ''),
                    ev.get('collection_staff', ''),
                    ev.get('scoring_24h_staff', ''),
                    ev['eggs_0h'],
                    ev['sr_0h'],
                    ev.get('live_0h', int(round(ev['eggs_0h'] * ev['sr_0h'] / 100.0))),
                    ev['sr_24h'],
                    ev['live_24h'],
                    'Yes' if ev['live_24h'] > 0 else 'No',
                    ev.get('source', '')
                ])
        print(f"Synchronized {master_csv_path} with {len(all_events)} master events.")
    except Exception as e:
        print(f"Warning: could not write {master_csv_path}: {e}")

if __name__ == '__main__':
    process()
