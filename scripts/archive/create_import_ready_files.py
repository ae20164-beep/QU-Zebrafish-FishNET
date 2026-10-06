import csv
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

export_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels\FishNet Exported Data'
fishnet_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data'

def clean_val(v):
    if v is None:
        return ""
    # Replace FileMaker vertical tab \x0b and other illegal XML characters with standard newline/semicolon
    s = str(v).replace('\x0b', ' / ').replace('\x0c', ' ').replace('\x00', '')
    return s.strip()

# 1. Tanks
with open(os.path.join(export_dir, 'tanks.tab'), 'r', encoding='utf-8') as f:
    tanks_rows = list(csv.reader(f, delimiter='\t'))

tanks_headers = [
    'Date of Birth', 'Date of Death', 'Dervitive Cross', 'Species', 'Female',
    'Genotype', 'Lab Member', 'Male', 'Nick name', 'Number of Fish',
    'Protocol', 'Extra_1', 'Room', 'Extra_2', 'Extra_3',
    'Extra_4', 'Status', 'Extra_5', 'Tank Size', 'Position',
    'TUID', 'Turnover Date', 'Laboratories Name'
]

# Create Tanks Excel
wb_t = openpyxl.Workbook()
ws_t = wb_t.active
ws_t.title = 'Tanks'

header_fill = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')
header_font = Font(name='Segoe UI', size=11, bold=True, color='38BDF8')

ws_t.append(tanks_headers)
for cell in ws_t[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal='center', vertical='center')

for r in tanks_rows:
    ws_t.append([clean_val(x) for x in r])

# Auto column width
for col in ws_t.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws_t.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

wb_t.save(os.path.join(export_dir, 'Tanks_Import_Ready.xlsx'))
wb_t.save(os.path.join(fishnet_dir, 'Tanks_Import_Ready.xlsx'))

# Create Tanks Tab with headers & CSV with headers
with open(os.path.join(export_dir, 'tanks_with_headers.tab'), 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerow(tanks_headers)
    for r in tanks_rows:
        writer.writerow([clean_val(x) for x in r])

with open(os.path.join(export_dir, 'Tanks_Import_Ready.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, lineterminator='\n')
    writer.writerow(tanks_headers)
    for r in tanks_rows:
        writer.writerow([clean_val(x) for x in r])


# 2. Crosses
with open(os.path.join(export_dir, 'crosses.tab'), 'r', encoding='utf-8') as f:
    crosses_rows = list(csv.reader(f, delimiter='\t'))

crosses_headers = [
    'Unfertilized Count', 'Dead Larvae Count', 'Total Eggs Count', 'Viable Larvae Count',
    'Fertilization Rate', 'Viability Rate', 'Technician', 'CUID',
    'Date Logged', 'Cross Date', 'Setup Date', 'Maternal Tank TUID',
    'Larvae Transferred', 'Extra_1', 'Pairs Count', 'Paternal Tank TUID',
    'Protocol', 'Principal Investigator', 'Status', 'Facility',
    'Maternal Genotype', 'Maternal Nick Name', 'Paternal Genotype', 'Paternal Nick Name'
]

wb_c = openpyxl.Workbook()
ws_c = wb_c.active
ws_c.title = 'Crosses'

ws_c.append(crosses_headers)
for cell in ws_c[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal='center', vertical='center')

for r in crosses_rows:
    ws_c.append([clean_val(x) for x in r])

for col in ws_c.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws_c.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

wb_c.save(os.path.join(export_dir, 'Crosses_Import_Ready.xlsx'))
wb_c.save(os.path.join(fishnet_dir, 'Crosses_Import_Ready.xlsx'))

with open(os.path.join(export_dir, 'crosses_with_headers.tab'), 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerow(crosses_headers)
    for r in crosses_rows:
        writer.writerow([clean_val(x) for x in r])

with open(os.path.join(export_dir, 'Crosses_Import_Ready.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, lineterminator='\n')
    writer.writerow(crosses_headers)
    for r in crosses_rows:
        writer.writerow([clean_val(x) for x in r])


# 3. Nursery
with open(os.path.join(export_dir, 'nursery.tab'), 'r', encoding='utf-8') as f:
    nursery_rows = list(csv.reader(f, delimiter='\t'))

nursery_headers = [
    'NUID', 'Larvae Count', 'Status', 'Technician', 'CUID',
    'Graduation Date', 'Nursery Entry Date', 'Spawning Date', 'Setup Date',
    'Maternal Tank TUID', 'Paternal Tank TUID', 'Protocol', 'Principal Investigator',
    'Facility', 'Maternal Genotype', 'Maternal Nick Name', 'Paternal Genotype', 'Paternal Nick Name'
]

wb_n = openpyxl.Workbook()
ws_n = wb_n.active
ws_n.title = 'Nursery'

ws_n.append(nursery_headers)
for cell in ws_n[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal='center', vertical='center')

for r in nursery_rows:
    ws_n.append([clean_val(x) for x in r])

for col in ws_n.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws_n.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

wb_n.save(os.path.join(export_dir, 'Nursery_Import_Ready.xlsx'))
wb_n.save(os.path.join(fishnet_dir, 'Nursery_Import_Ready.xlsx'))

with open(os.path.join(export_dir, 'nursery_with_headers.tab'), 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerow(nursery_headers)
    for r in nursery_rows:
        writer.writerow([clean_val(x) for x in r])

with open(os.path.join(export_dir, 'Nursery_Import_Ready.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, lineterminator='\n')
    writer.writerow(nursery_headers)
    for r in nursery_rows:
        writer.writerow([clean_val(x) for x in r])

print("All import-ready files generated successfully!")
