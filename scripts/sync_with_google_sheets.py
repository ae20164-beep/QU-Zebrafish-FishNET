import os
import json
import urllib.request
import csv

def sync_from_google_sheets():
    labels_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels'
    api_url = 'https://script.google.com/macros/s/AKfycbyU-4YKpnXEp_CXI2mu2Xb-DFo1fcIbt_qk9AWtXoPsj5CnDYmJ1XiZni1jl2Tce3df/exec'
    
    print(f'Fetching latest cloud records from Google Sheets...')
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            res = json.loads(content)
            
            if res.get('status') != 'success' or 'data' not in res:
                print('Error response from Google Sheets API:', res)
                return
            
            cloud_data = res['data']
            cloud_tanks = cloud_data.get('tanks', [])
            cloud_events = cloud_data.get('events', [])
            
            print(f'Successfully pulled from Google Sheets:')
            print(f'  - Tanks: {len(cloud_tanks)} rows')
            print(f'  - Breeding Events: {len(cloud_events)} rows')
            
            # Save local backup copy of live cloud state
            cloud_backup_path = os.path.join(labels_dir, 'google_sheets_live_sync.json')
            with open(cloud_backup_path, 'w', encoding='utf-8') as f:
                json.dump(cloud_data, f, indent=2)
            print(f'[OK] Saved local cloud backup: {cloud_backup_path}')
            
    except Exception as e:
        print(f'Failed to sync from Google Sheets: {e}')

if __name__ == '__main__':
    sync_from_google_sheets()
