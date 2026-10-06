import os
import sys
import re
import csv
import json
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
EXPORTED_DIR = os.path.join(ROOT_DIR, 'FishNet Exported Data')

print("=== FishNET AI Vision Paper Log Digitizer ===")

def process_log_entries(entries, log_image_name="Paper Log"):
    """
    entries: list of dicts with keys:
    ['date', 'fishline', 'in_tank', 'eggs_0h', 'sr_0h', 'sr_24h', 'live_24h', 'staff']
    """
    if not entries:
        print("No valid breeding entries to add.")
        return False

    print(f"\nProcessing {len(entries)} digitized breeding records from {log_image_name}...")
    
    # 1. Append to Breeding Database / JSON
    json_path = os.path.join(ROOT_DIR, 'breeding_dashboard_data.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            b_data = json.load(f)
    else:
        b_data = {'events': [], 'tank_stats': {}, 'pair_synergies': []}

    for e in entries:
        ev_obj = {
            'year': int(e['date'][:4]) if len(e.get('date', '')) >= 4 else 2026,
            'date': e.get('date', ''),
            'fishline': e.get('fishline', ''),
            'line': e.get('line', 'AB'),
            'tanks': e.get('tanks', []),
            'primary_tank': e.get('tanks', [''])[0] if e.get('tanks') else '',
            'in_tank': e.get('in_tank', False),
            'eggs_0h': int(e.get('eggs_0h', 0)),
            'sr_0h': float(e.get('sr_0h', 100.0)),
            'live_0h': int(e.get('live_0h', e.get('eggs_0h', 0))),
            'sr_24h': float(e.get('sr_24h', 85.0)),
            'live_24h': int(e.get('live_24h', 0)),
            'setup_staff': e.get('staff', ''),
            'collection_staff': e.get('staff', ''),
            'staff_summary': e.get('staff', '')
        }
        b_data['events'].append(ev_obj)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(b_data, f, indent=2)

    print(f"[OK] Appended {len(entries)} events to breeding_dashboard_data.json.")

    # 2. Re-run master pipeline to synchronize dashboards and reports
    import subprocess
    sync_script = os.path.join(SCRIPTS_DIR, 'sync_all_pipeline.py')
    subprocess.run([sys.executable, sync_script], cwd=ROOT_DIR)
    
    print(f"\n🎉 Successfully digitized and synchronized {len(entries)} records into all master files and web dashboards!")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        print(f"Target log image: {img_path}")
        print("Ready for AI Vision parsing.")
    else:
        print("Usage: python digitize_paper_log.py [path_to_log_image.jpg/png]")
