import os
import csv
import re
from datetime import datetime, date
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter

def clean_val(v):
    if v is None:
        return ""
    if isinstance(v, str):
        # Remove Excel illegal control characters
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', v).strip()
    return v

def generate_color_coded_excel():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(scripts_dir)
    tanks_tab_path = os.path.join(root_dir, 'FishNet Exported Data', 'Tanks.tab')
    if not os.path.exists(tanks_tab_path):
        tanks_tab_path = os.path.join(root_dir, 'FishNet Exported Data', 'tanks.tab')

    print(f"Reading tanks from: {tanks_tab_path}")
    with open(tanks_tab_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        reader = list(csv.reader(f, delimiter='\t'))

    if not reader:
        print("Error: Tanks.tab is empty!")
        return False

    header_row = reader[0]
    has_header = ('TUID' in [c.strip().upper() for c in header_row] or 'STATUS' in [c.strip().upper() for c in header_row])
    col_map = {col.strip().upper(): idx for idx, col in enumerate(header_row)} if has_header else {}
    data_rows = reader[1:] if has_header else reader

    def parse_d(d_str):
        if not d_str or not isinstance(d_str, str): return None
        d_str = clean_val(d_str)
        for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%d-%m-%Y', '%d-%b-%y', '%d-%b-%Y', '%d-%m-%y', '%Y-%m-%d', '%m/%d/%y', '%d/%m/%y']:
            try:
                dt = datetime.strptime(d_str, fmt)
                if dt.year > 2030: dt = dt.replace(year=dt.year - 100)
                return dt.date()
            except ValueError:
                pass
        return None

    tanks = []
    for r in data_rows:
        if not r or not any(r): continue
        if has_header:
            def get_val(name):
                idx = col_map.get(name.upper())
                return clean_val(r[idx]) if idx is not None and idx < len(r) else ''
            tuid = get_val('TUID')
            if not tuid or not tuid.upper().startswith('T'): continue
            notes = get_val('NOTES')
            genotype = get_val('GENOTYPE')
            dob_raw = get_val('DOB') or get_val('DATE OF BIRTH')
            dod_raw = get_val('DATE OF DEATH') or get_val('DATE_OF_DEATH')
            turnover_raw = get_val('TURNOVER_DEADLINE') or get_val('TURNOVER DATE')
            cross = get_val('DERIVATIVE_CROSS') or get_val('DERVITIVE CROSS')
            female_raw = get_val('FEMALE') or get_val('FEMALES')
            male_raw = get_val('MALE') or get_val('MALES')
            total_raw = get_val('TOTAL_FISH') or get_val('NUMBER OF FISH') or get_val('TOTAL')
            tank_size = get_val('TANK_SIZE') or get_val('TANK SIZE')
            status = get_val('STATUS')
            protocol = get_val('PROTOCOL')
        else:
            if len(r) >= 15:
                tuid = clean_val(r[0])
                notes = clean_val(r[1])
                genotype = clean_val(r[2])
                dob_raw = clean_val(r[5])
                dod_raw = clean_val(r[6])
                turnover_raw = clean_val(r[7])
                cross = clean_val(r[8])
                female_raw = clean_val(r[9])
                male_raw = clean_val(r[10])
                total_raw = clean_val(r[11])
                tank_size = clean_val(r[12])
                status = clean_val(r[13])
                protocol = clean_val(r[14])
            else:
                continue

        tanks.append({
            'tuid': tuid.upper(),
            'notes': notes,
            'genotype': genotype,
            'dob': parse_d(dob_raw),
            'dod': parse_d(dod_raw),
            'turnover': parse_d(turnover_raw),
            'cross': cross,
            'female': int(female_raw) if female_raw.isdigit() else ('-' if female_raw == '' else female_raw),
            'male': int(male_raw) if male_raw.isdigit() else ('-' if male_raw == '' else male_raw),
            'total': int(total_raw) if total_raw.isdigit() else 0,
            'size': tank_size or '1.8L',
            'status': status or 'Adult/Active',
            'protocol': protocol
        })

    print(f"Parsed {len(tanks)} tanks for color-coded Excel.")

    # Create Workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "FishNET Tanks"
    ws.views.sheetView[0].showGridLines = True

    # Styling Palette
    COLOR_HEADER_BG = "0F172A"       # Slate 900
    COLOR_HEADER_TXT = "FFFFFF"      # White
    COLOR_RED_BG = "FEE2E2"          # Rose 100
    COLOR_RED_TXT = "991B1B"         # Rose 800
    COLOR_YELLOW_BG = "FEF9C3"       # Amber 100
    COLOR_YELLOW_TXT = "854D0E"      # Amber 800
    COLOR_GREEN_BG = "DCFCE7"        # Emerald 100
    COLOR_GREEN_TXT = "166534"       # Emerald 800
    COLOR_GRAY_BG = "F1F5F9"         # Slate 100
    COLOR_GRAY_TXT = "64748B"        # Slate 500

    thin_border_side = Side(border_style="thin", color="CBD5E1")
    border_standard = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

    headers = [
        'TUID', 'Notes', 'Genotype', 'DOB', 'Date of death',
        'Turnover_Deadline', 'Derivative_Cross', 'Female', 'Male',
        'Total_Fish', 'Tank_Size', 'Status', 'Protocol',
        'Current Age (Months)', 'Colony Status Classification'
    ]

    # Write Headers
    for c_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=c_idx, value=h)
        cell.font = Font(name="Segoe UI", size=10, bold=True, color=COLOR_HEADER_TXT)
        cell.fill = PatternFill(start_color=COLOR_HEADER_BG, end_color=COLOR_HEADER_BG, fill_type="solid")
        cell.alignment = Alignment(horizontal="center" if c_idx not in [2, 3, 13] else "left", vertical="center")
        cell.border = border_standard
    ws.row_dimensions[1].height = 26

    today = date.today()

    for idx, t in enumerate(tanks, start=2):
        ws.row_dimensions[idx].height = 20

        # Compute static classification for base styling
        is_euth = 'euth' in t['status'].lower() or 'dead' in t['status'].lower()
        dob = t['dob']
        dod = t['dod']
        
        if dob:
            ref_date = dod if (is_euth and dod) else today
            age_months_calc = round(max(0, (ref_date - dob).days) / 30.4375, 1)
        else:
            age_months_calc = 0.0

        if is_euth:
            class_str = "⚪ Euthanized / Retired"
            base_bg = COLOR_GRAY_BG
            base_txt = COLOR_GRAY_TXT
        elif age_months_calc >= 18.0:
            class_str = "🔴 Overdue (> 18 Mo / Due for Euthanasia)"
            base_bg = COLOR_RED_BG
            base_txt = COLOR_RED_TXT
        elif age_months_calc < 3.0:
            class_str = "🟡 Juvenile (< 3 Mo)"
            base_bg = COLOR_YELLOW_BG
            base_txt = COLOR_YELLOW_TXT
        else:
            class_str = "🟢 Prime Adult Breeder (3 - 18 Mo)"
            base_bg = COLOR_GREEN_BG
            base_txt = COLOR_GREEN_TXT

        row_fill = PatternFill(start_color=base_bg, end_color=base_bg, fill_type="solid")
        row_font = Font(name="Segoe UI", size=9.5, color=base_txt, bold=(base_bg in [COLOR_RED_BG, COLOR_YELLOW_BG]))

        age_formula = f'=IF(ISBLANK(D{idx}), "", IF(ISNUMBER(SEARCH("euth", LOWER(L{idx}))), IF(ISBLANK(E{idx}), ROUND((TODAY()-D{idx})/30.4375, 1), ROUND((E{idx}-D{idx})/30.4375, 1)), ROUND((TODAY()-D{idx})/30.4375, 1)))'
        class_formula = f'=IF(ISNUMBER(SEARCH("euth", LOWER(L{idx}))), "⚪ Euthanized / Retired", IF(N{idx}>=18, "🔴 Overdue (> 18 Mo / Due for Euthanasia)", IF(N{idx}<3, "🟡 Juvenile (< 3 Mo)", "🟢 Prime Adult Breeder (3 - 18 Mo)")))'

        values = [
            clean_val(t['tuid']),
            clean_val(t['notes']),
            clean_val(t['genotype']),
            t['dob'],
            t['dod'],
            t['turnover'],
            clean_val(t['cross']),
            clean_val(t['female']),
            clean_val(t['male']),
            t['total'],
            clean_val(t['size']),
            clean_val(t['status']),
            clean_val(t['protocol']),
            age_formula,
            class_formula
        ]

        for c_idx, val in enumerate(values, start=1):
            cell = ws.cell(row=idx, column=c_idx, value=val)
            cell.font = row_font
            cell.fill = row_fill
            cell.border = border_standard

            # Formatting
            if c_idx in [4, 5, 6]: # Dates
                if val:
                    cell.number_format = 'yyyy-mm-dd'
                    cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx in [1, 8, 9, 10, 11]: # IDs, Counts
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx == 14: # Age
                cell.number_format = '0.0 "mo"'
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx in [12, 15]: # Status
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # Add Dynamic Excel Conditional Formatting Rules (evaluated by Excel on open!)
    last_row = len(tanks) + 1
    cf_range = f"A2:O{last_row}"

    cf_euth_fill = PatternFill(start_color=COLOR_GRAY_BG, end_color=COLOR_GRAY_BG, fill_type="solid")
    cf_euth_font = Font(name="Segoe UI", size=9.5, color=COLOR_GRAY_TXT)
    rule_euth = FormulaRule(formula=[f'ISNUMBER(SEARCH("euth", LOWER($L2)))'], fill=cf_euth_fill, font=cf_euth_font)

    cf_red_fill = PatternFill(start_color=COLOR_RED_BG, end_color=COLOR_RED_BG, fill_type="solid")
    cf_red_font = Font(name="Segoe UI", size=9.5, color=COLOR_RED_TXT, bold=True)
    rule_red = FormulaRule(formula=[f'AND(NOT(ISNUMBER(SEARCH("euth", LOWER($L2)))), $N2>=18)'], fill=cf_red_fill, font=cf_red_font)

    cf_yellow_fill = PatternFill(start_color=COLOR_YELLOW_BG, end_color=COLOR_YELLOW_BG, fill_type="solid")
    cf_yellow_font = Font(name="Segoe UI", size=9.5, color=COLOR_YELLOW_TXT, bold=True)
    rule_yellow = FormulaRule(formula=[f'AND(NOT(ISNUMBER(SEARCH("euth", LOWER($L2)))), $N2<3)'], fill=cf_yellow_fill, font=cf_yellow_font)

    cf_green_fill = PatternFill(start_color=COLOR_GREEN_BG, end_color=COLOR_GREEN_BG, fill_type="solid")
    cf_green_font = Font(name="Segoe UI", size=9.5, color=COLOR_GREEN_TXT)
    rule_green = FormulaRule(formula=[f'AND(NOT(ISNUMBER(SEARCH("euth", LOWER($L2)))), $N2>=3, $N2<18)'], fill=cf_green_fill, font=cf_green_font)

    # Add in priority order: Euthanized first, then Red (>18m), then Yellow (<3m), then Green (3-18m)
    ws.conditional_formatting.add(cf_range, rule_euth)
    ws.conditional_formatting.add(cf_range, rule_red)
    ws.conditional_formatting.add(cf_range, rule_yellow)
    ws.conditional_formatting.add(cf_range, rule_green)

    # Auto-adjust column widths
    col_widths = {
        1: 10,   # TUID
        2: 24,   # Notes
        3: 36,   # Genotype
        4: 13,   # DOB
        5: 14,   # Date of death
        6: 18,   # Turnover_Deadline
        7: 16,   # Derivative_Cross
        8: 10,   # Female
        9: 10,   # Male
        10: 12,  # Total_Fish
        11: 12,  # Tank_Size
        12: 16,  # Status
        13: 25,  # Protocol
        14: 22,  # Current Age (Months)
        15: 38   # Colony Status Classification
    }
    for col_idx, width in col_widths.items():
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width

    # Freeze header and first column
    ws.freeze_panes = "B2"

    target_path_1 = os.path.join(root_dir, 'FishNet Exported Data', 'tanks_color_coded.xlsx')
    target_path_2 = os.path.join(root_dir, 'tanks_color_coded.xlsx')
    
    wb.save(target_path_1)
    wb.save(target_path_2)
    print(f"[OK] Generated color-coded Excel: {target_path_1}")
    print(f"[OK] Generated color-coded Excel: {target_path_2}")
    return True

if __name__ == '__main__':
    generate_color_coded_excel()
