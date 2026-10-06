with open('build_fishnet_analytics.py', 'r', encoding='utf-8') as f:
    code = f.read()

safe_save = """try:
    wb.save(EXCEL_REPORT_FILE)
    print(f'Excel Report written successfully: {EXCEL_REPORT_FILE}')
except PermissionError:
    alt_file = 'FishNET_Colony_Analytics_Report_v2.xlsx'
    wb.save(alt_file)
    print(f'Excel file locked; saved to: {alt_file}')"""

target = "wb.save(EXCEL_REPORT_FILE)\nprint(f'Excel Report written successfully: {EXCEL_REPORT_FILE}')"
if target in code:
    code = code.replace(target, safe_save)

with open('build_fishnet_analytics.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated safe excel save.")
