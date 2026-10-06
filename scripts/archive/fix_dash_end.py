with open('generate_integrated_dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = '"""\n\n    out_integrated = os.path.join(labels_dir, \'FishNET_Interactive_Dashboard_With_Breeding.html\')'
replacement = '"""\n\n    html_content = html_template.replace(\'__DATA_JSON__\', data_json_str)\n\n    out_integrated = os.path.join(labels_dir, \'FishNET_Interactive_Dashboard_With_Breeding.html\')'

if target in code:
    code = code.replace(target, replacement)

with open('generate_integrated_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated generate_integrated_dashboard.py.")
