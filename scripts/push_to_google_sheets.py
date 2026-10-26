import os
import csv
import json
import urllib.request
import urllib.error

API_URL = 'https://script.google.com/macros/s/AKfycbyU-4YKpnXEp_CXI2mu2Xb-DFo1fcIbt_qk9AWtXoPsj5CnDYmJ1XiZni1jl2Tce3df/exec'

def push_data():
    labels_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    events_csv = os.path.join(labels_dir, 'google_sheets_import', '2_Breeding_Events.csv')
    tanks_csv = os.path.join(labels_dir, 'google_sheets_import', '1_Tanks.csv')

    print("=== Pushing Master Clean Data to Google Sheets ===")
    
    # 1. Push Tanks
    if os.path.exists(tanks_csv):
        with open(tanks_csv, 'r', encoding='utf-8') as f:
            tank_rows = list(csv.reader(f))
        print(f"Uploading {len(tank_rows)-1} tanks to Google Sheets...")
        payload_tanks = {
            'action': 'SYNC_ALL_TANKS',
            'operator': 'Automated Pipeline Sync',
            'rows': tank_rows
        }
        try:
            req = urllib.request.Request(
                API_URL,
                data=json.dumps(payload_tanks).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                print("  Tanks Push Response:", res)
        except Exception as e:
            print("  [ERROR] Failed to push tanks:", e)

    # 2. Push Breeding Events
    if os.path.exists(events_csv):
        with open(events_csv, 'r', encoding='utf-8') as f:
            event_rows = list(csv.reader(f))
        print(f"Uploading {len(event_rows)-1} breeding events to Google Sheets...")
        payload_events = {
            'action': 'SYNC_ALL_BREEDING_EVENTS',
            'operator': 'Automated Pipeline Sync',
            'rows': event_rows
        }
        try:
            req = urllib.request.Request(
                API_URL,
                data=json.dumps(payload_events).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                print("  Events Push Response:", res)
        except Exception as e:
            print("  [ERROR] Failed to push breeding events:", e)

if __name__ == '__main__':
    push_data()
