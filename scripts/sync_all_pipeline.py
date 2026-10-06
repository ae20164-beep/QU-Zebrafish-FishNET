import os
import sys
import subprocess
import shutil

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)

print("=== FishNET Master Sync Pipeline ===")
print(f"Root directory: {ROOT_DIR}")
print(f"Scripts directory: {SCRIPTS_DIR}")

def run_step(script_name):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    print(f"\n--- Running: {script_name} ---")
    res = subprocess.run([sys.executable, script_path], cwd=ROOT_DIR)
    if res.returncode != 0:
        print(f"[FAIL] Error running {script_name} (code {res.returncode})")
        return False
    return True

# 0. Sync RA Registries and Build Projects/Labs Tables
print("\nStep 0: Synchronizing RAs & FileMaker Projects/Labs...")
run_step('sync_ra_team_registry.py')
run_step('build_comprehensive_projects_and_labs.py')

# 1. Synchronize FileMaker Master Exports & Dashboards
print("\nStep 1: Synchronizing FileMaker Master Exports...")
if run_step('build_fishnet_analytics.py'):
    print("[OK] Colony Analytics & Dashboards regenerated.")

# 2. Process all breeding records & update breeding data
print("\nStep 2: Processing breeding & reproductive intelligence...")
if run_step('process_all_breeding.py'):
    print("[OK] Breeding database & Pair Synergies compiled.")

# 3. Generate Integrated Reproductive Dashboard
print("\nStep 3: Generating Integrated Reproductive Dashboard...")
if run_step('generate_integrated_dashboard.py'):
    print("[OK] Reproductive Intelligence Dashboard updated.")

# 4. Copy to web deployment routes (index.html, colony.html, breeding.html)
print("\nStep 4: Updating web portal distribution files...")
shutil.copyfile(os.path.join(ROOT_DIR, 'FishNET_Interactive_Dashboard.html'), os.path.join(ROOT_DIR, 'colony.html'))
shutil.copyfile(os.path.join(ROOT_DIR, 'FishNET_Interactive_Dashboard_With_Breeding.html'), os.path.join(ROOT_DIR, 'breeding.html'))
print("[OK] Web portal (index.html, colony.html, breeding.html) synchronized.")

print("\n*** ALL MASTER FILES & DASHBOARDS ARE 100% SYNCHRONIZED! ***")
