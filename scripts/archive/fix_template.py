import os
import re

print("Fixing template brace handling in build_fishnet_analytics.py...")

# We will read build_fishnet_analytics.py up to html_content, and read the clean HTML template separately
with open('build_fishnet_analytics.py', 'r', encoding='utf-8') as f:
    full_code = f.read()

# Let's split at raw_records_json = json.dumps(records, default=str)
split_token = "raw_records_json = json.dumps(records, default=str)"
parts = full_code.split(split_token)

py_top = parts[0] + split_token + "\n\n"

# Let's extract the HTML part from after html_content = f\"\"\" to before the write statement
html_part = parts[1]
# Clean up f-string syntax
html_part = re.sub(r'html_content\s*=\s*f"""', 'html_template = """', html_part, 1)

# In the template, replace {raw_records_json} with __RECORDS_JSON__
html_part = re.sub(r'const DEFAULT_RECORDS = \{raw_records_json\};', 'const DEFAULT_RECORDS = __RECORDS_JSON__;', html_part)
html_part = re.sub(r'const DEFAULT_RECORDS = raw_records_json;', 'const DEFAULT_RECORDS = __RECORDS_JSON__;', html_part)

# Replace all {{ with { and }} with } in the HTML template
# But make sure __RECORDS_JSON__ remains
html_part = html_part.replace('{{', '{').replace('}}', '}')

# At the end of the script:
footer_code = """
html_content = html_template.replace('__RECORDS_JSON__', raw_records_json)

with open('FishNET_Interactive_Dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

with open(HTML_DASHBOARD_FILE, 'w', encoding='utf-8') as f:
    f.write(html_content)

print('HTML Dashboards generated: FishNET_Interactive_Dashboard.html and FishNET_Interactive_Dashboard_Standard_Backup.html')
"""

# Replace the end writing block
html_part = re.sub(r'"""\s*with open[\s\S]*', '"""\n' + footer_code, html_part)

clean_code = py_top + html_part

with open('build_fishnet_analytics.py', 'w', encoding='utf-8') as f:
    f.write(clean_code)

print("Saved clean build_fishnet_analytics.py.")
