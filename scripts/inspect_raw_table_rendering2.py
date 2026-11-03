"""
Print the rest of renderRawEvents
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("scripts/generate_integrated_dashboard.py", "r", encoding="utf-8") as f:
    code = f.read()

idx = code.find("femaleTankHtml")
print(code[idx:idx+2500])
