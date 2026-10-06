import os
import re
import json

booking_script = r'C:\Users\ae20164\OneDrive - Jordan University of Science and Technology (JUST)\zebrafish-booking-portal\scripts\sync-registry.js'

with open(booking_script, 'r', encoding='utf-8') as f:
    code = f.read()

# Extract array elements with regex
matches = re.findall(r'\{\s*num:\s*"(.*?)",\s*base:\s*"(.*?)",\s*ver:\s*"(.*?)",\s*exp:\s*"(.*?)",\s*pi:\s*"(.*?)",\s*email:\s*"(.*?)",\s*status:\s*"(.*?)"\s*\}', code)

print(f"Extracted {len(matches)} protocols from booking portal registry:")
active_protocols = []
for m in matches:
    num, base, ver, exp, pi, email, status = m
    obj = {
        'protocol_num': num,
        'base': base,
        'version': ver,
        'expiry_date': exp,
        'pi': pi,
        'email': email,
        'status': status
    }
    active_protocols.append(obj)
    if status == 'ACTIVE':
        print(f"[{status}] {num} | PI: {pi} | Exp: {exp}")

# Also inspect Google Sheets integration in booking portal if possible
print(f"\nTotal Active Protocols in Registry: {len([p for p in active_protocols if p['status'] == 'ACTIVE'])}")
