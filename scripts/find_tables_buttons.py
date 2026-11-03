"""
Find all table IDs and buttons in the generator
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("scripts/generate_integrated_dashboard.py", "r", encoding="utf-8") as f:
    code = f.read()

tables = re.findall(r'<table[^>]+id=["\']([^"\']+)["\']', code)
print("Table IDs found:", tables)

onclicks = re.findall(r'onclick=["\']([^"\']+)["\']', code)
unique_onclicks = sorted(list(dict.fromkeys(onclicks)))
print(f"\nUnique onclick handlers found ({len(unique_onclicks)}):")
for oc in unique_onclicks:
    print(f"  • {oc}")
