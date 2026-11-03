"""
Inspect renderRawEvents row template and columns
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("scripts/generate_integrated_dashboard.py", "r", encoding="utf-8") as f:
    code = f.read()

idx = code.find("function renderRawEvents")
print(code[idx:idx+3500])
