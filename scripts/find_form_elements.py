"""
Find all input and select IDs in the generator
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("scripts/generate_integrated_dashboard.py", "r", encoding="utf-8") as f:
    code = f.read()

inputs = re.findall(r'<input[^>]+id=["\']([^"\']+)["\']', code)
selects = re.findall(r'<select[^>]+id=["\']([^"\']+)["\']', code)

print("Input IDs found:", inputs)
print("\nSelect IDs found:", selects)
