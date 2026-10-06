import re
import subprocess

for fname in ['FishNET_Interactive_Dashboard_Standard_Backup.html', 'FishNET_Interactive_Dashboard.html', 'FishNET_Interactive_Dashboard_With_Breeding.html']:
    with open(fname, 'r', encoding='utf-8') as f:
        html = f.read()
    scripts = re.findall(r'<script(?![^>]*src)[^>]*>([\s\S]*?)</script>', html)
    for i, s in enumerate(scripts):
        with open('temp_check.js', 'w', encoding='utf-8') as js_f:
            js_f.write(s)
        res = subprocess.run(['node', '--check', 'temp_check.js'], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[OK] {fname} script #{i+1} is 100% syntactically valid!")
        else:
            print(f"[ERROR] {fname} script #{i+1} syntax error:")
            print(res.stderr)
