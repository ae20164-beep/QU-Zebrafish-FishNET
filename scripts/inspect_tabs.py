"""
Inspect switchTab and tab div containers
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("scripts/generate_integrated_dashboard.py", "r", encoding="utf-8") as f:
    code = f.read()

# Look for switchTab function
m = re.search(r'function switchTab\([^)]*\)\s*\{[^}]*\}', code)
if m:
    print("switchTab definition:")
    print(m.group(0))

# Look for div with class tab-pane or tab-content or id="tab-
tab_divs = re.findall(r'<div[^>]+id=["\'](tab-[^"\']+)["\']', code)
print("\nTab div IDs found with 'tab-':", tab_divs)

# Look for all onclick="switchTab(...)
switch_calls = re.findall(r"switchTab\(['\"]([^'\"]+)['\"]\)", code)
print("\nswitchTab calls:", switch_calls)
