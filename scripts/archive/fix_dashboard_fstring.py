import os
import re

print("Converting generate_integrated_dashboard.py to safe template mode...")

with open('generate_integrated_dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Split at data_json_str = json.dumps(full_data)
split_token = "data_json_str = json.dumps(full_data)"
parts = code.split(split_token)

py_top = parts[0] + split_token + "\n\n"
html_part = parts[1]

# Convert html_content = f\"\"\" to html_template = \"\"\"
html_part = re.sub(r'html_content\s*=\s*f"""', 'html_template = """', html_part, 1)

# Replace {data_json_str} with __DATA_JSON__
html_part = re.sub(r'const MASTER_DATA\s*=\s*\{data_json_str\};', 'const MASTER_DATA = __DATA_JSON__;', html_part)
html_part = re.sub(r'const MASTER_DATA\s*=\s*data_json_str;', 'const MASTER_DATA = __DATA_JSON__;', html_part)

# Unescape all {{ and }} in HTML
html_part = html_part.replace('{{', '{').replace('}}', '}')

# At the end of function:
footer = """
    html_content = html_template.replace('__DATA_JSON__', data_json_str)

    out_path = os.path.join(labels_dir, 'FishNET_Interactive_Dashboard_With_Breeding.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Wrote {out_path}")

if __name__ == '__main__':
    generate_dashboard()
"""

# Replace the end writing block
html_part = re.sub(r'"""\s*out_path =[\s\S]*', '"""\n' + footer, html_part)

clean_code = py_top + html_part

with open('generate_integrated_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(clean_code)

print("Saved clean generate_integrated_dashboard.py.")
