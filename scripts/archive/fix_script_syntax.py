import re
import subprocess
import os

print("Auditing and fixing JavaScript syntax in build_fishnet_analytics.py...")

with open('build_fishnet_analytics.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix literal broken string concatenation in JS
# e.g., headers.join(',') + '\n'
# In template strings, \n should be written as \\n or \n
code = code.replace("headers.join(',') + '\\n'", "headers.join(',') + '\\\\n'")
code = code.replace("row.join(',') + '\\n'", "row.join(',') + '\\\\n'")
code = code.replace("alert(`📋 Copied Lineage Trail to Clipboard:\\n${pathStr}`);", "alert(`📋 Copied Lineage Trail to Clipboard:\\\\n${pathStr}`);")
code = code.replace("alert(`Lineage Path:\\n${pathStr}`);", "alert(`Lineage Path:\\\\n${pathStr}`);")
code = code.replace("label: `${r.TUID}\\n${r.Line_Category}`", "label: `${r.TUID}\\\\n${r.Line_Category}`")
code = code.replace("split(/\\r?\\n/)", "split(/\\\\r?\\\\n/)")

with open('build_fishnet_analytics.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved fixed build_fishnet_analytics.py. Now generating dashboards...")
subprocess.run(['python', 'build_fishnet_analytics.py'], check=True)

# Now extract script from generated HTML and run node --check
with open('FishNET_Interactive_Dashboard_Standard_Backup.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

scripts = re.findall(r'<script(?![^>]*src)[^>]*>([\s\S]*?)</script>', html_content)
for i, s in enumerate(scripts):
    with open(f'temp_script_verify_{i}.js', 'w', encoding='utf-8') as js_f:
        js_f.write(s)
    res = subprocess.run(['node', '--check', f'temp_script_verify_{i}.js'], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✅ Script block {i+1} syntax is 100% VALID!")
    else:
        print(f"❌ Script block {i+1} has syntax error:")
        print(res.stderr)

# Clean up temp files
for f in os.listdir('.'):
    if f.startswith('temp_script_'):
        try:
            os.remove(f)
        except:
            pass

print("Done auditing!")
