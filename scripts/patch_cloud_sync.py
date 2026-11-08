import re
import os

print("=== Patching QU ZebraTrack Cloud Synchronization & Edit Persistence ===")

# -------------------------------------------------------------
# 1. Patch scripts/google_apps_script_backend.js
# -------------------------------------------------------------
gas_path = os.path.join(os.path.dirname(__file__), 'google_apps_script_backend.js')
if os.path.exists(gas_path):
    with open(gas_path, 'r', encoding='utf-8') as f:
        gas_text = f.read()

    old_update_pattern = r'\} else if \(action === "UPDATE_TANK"\) \{[\s\S]*?recordAudit\(ss, operator, "UPDATE_TANK_WARN", "Target tank " \+ tuidTarget \+ " not found on sheet"\);\s*\}\s*\}\s*\}'
    
    new_update_code = '''} else if (action === "UPDATE_TANK") {
      var sTanks = ss.getSheetByName("Tanks");
      if (sTanks) {
        var values = sTanks.getDataRange().getValues();
        var tuidTarget = String(data.tuid || "").trim().toUpperCase();
        var updated = false;
        for (var r = 1; r < values.length; r++) {
          if (String(values[r][0]).trim().toUpperCase() === tuidTarget) {
            // Actual sheet headers:
            // [1:TUID, 2:Derivative_Cross, 3:Locus 1, 4:Locus 1 Allele 1, 5:Notes, 6:Female, 7:Male, 8:Total_Fish, 9:Tank_Size, 10:Protocol, 11:DOB, 12:Turnover_Deadline, 13:Date Euthanized, 14:Status]
            if (data.notes !== undefined) sTanks.getRange(r + 1, 5).setValue(data.notes);
            if (data.female !== undefined) sTanks.getRange(r + 1, 6).setValue(Number(data.female) || 0);
            if (data.male !== undefined) sTanks.getRange(r + 1, 7).setValue(Number(data.male) || 0);
            if (data.total !== undefined) sTanks.getRange(r + 1, 8).setValue(Number(data.total) || 0);
            if (data.tank_size !== undefined) sTanks.getRange(r + 1, 9).setValue(data.tank_size);
            if (data.protocol !== undefined) sTanks.getRange(r + 1, 10).setValue(data.protocol);
            if (data.dob !== undefined) sTanks.getRange(r + 1, 11).setValue(data.dob);
            if (data.status !== undefined) {
              var formattedStatus = data.status;
              if (formattedStatus === "Active") formattedStatus = "Adult/Active";
              else if (formattedStatus === "Juvenile") formattedStatus = "Juvenile(<3 months old)";
              sTanks.getRange(r + 1, 14).setValue(formattedStatus);
              if (data.status === "Euthanized" && !values[r][12]) {
                sTanks.getRange(r + 1, 13).setValue(Utilities.formatDate(now, "GMT+3", "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"));
              }
            }
            if (sTanks.getLastColumn() >= 15) {
              sTanks.getRange(r + 1, 15).setValue((operator || "Staff") + " [Live Update]");
            }
            recordAudit(ss, operator, "UPDATE_TANK", "Updated " + tuidTarget + " -> Status: " + (data.status || "") + ", Total: " + (data.total || ""));
            updated = true;
            break;
          }
        }
        if (!updated) {
          recordAudit(ss, operator, "UPDATE_TANK_WARN", "Target tank " + tuidTarget + " not found on sheet");
        }
      }
    }'''

    if re.search(old_update_pattern, gas_text):
        gas_text = re.sub(old_update_pattern, new_update_code, gas_text)
        with open(gas_path, 'w', encoding='utf-8') as f:
            f.write(gas_text)
        print(" -> Patched google_apps_script_backend.js successfully.")
    else:
        print(" -> Pattern in google_apps_script_backend.js not matched or already patched.")

# -------------------------------------------------------------
# 2. Patch scripts/generate_integrated_dashboard.py
# -------------------------------------------------------------
gen_path = os.path.join(os.path.dirname(__file__), 'generate_integrated_dashboard.py')
with open(gen_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Update BUILD_VERSION to v9
code = re.sub(r"const BUILD_VERSION = '2026-11-08-ZebraTrack-v8';", "const BUILD_VERSION = '2026-11-08-ZebraTrack-v9';", code)

# Define cloudTankRawRecords cache and buildGoogleSheetsTankRows function
cloud_helper_defs = '''
        // Raw Cloud Sheet Records Cache (Preserves all non-editable facility columns)
        let cloudTankRawRecords = {};

        function buildGoogleSheetsTankRows() {
            const headers = ['TUID', 'Derivative_Cross', 'Locus 1', 'Locus 1 Allele 1', 'Notes', 'Female', 'Male', 'Total_Fish', 'Tank_Size', 'Protocol', 'DOB', 'Turnover_Deadline', 'Date Euthanized', 'Status'];
            const rows = [headers];
            const tuidList = Object.keys(currentTanks).sort((a,b) => {
                const na = parseInt(a.replace(/\\D/g, '')) || 0;
                const nb = parseInt(b.replace(/\\D/g, '')) || 0;
                return na - nb;
            });

            tuidList.forEach(id => {
                const t = currentTanks[id];
                const raw = cloudTankRawRecords[id] || {};
                const formattedStatus = t.status === 'Active' ? 'Adult/Active' : (t.status === 'Juvenile' ? 'Juvenile(<3 months old)' : 'Euthanized');
                const dateEuth = t.status === 'Euthanized' ? (raw['Date Euthanized'] || t.dod || new Date().toISOString().substring(0, 10)) : '';

                let locus = raw['Locus 1'] || '';
                let allele = raw['Locus 1 Allele 1'] || '';
                if (!locus && t.genotype) {
                    locus = t.genotype.startsWith('Mu') ? 'Mu' : (t.genotype.startsWith('Wt') ? 'Wt' : '');
                    allele = t.genotype.replace(/^(?:Mu|Wt)\\s*/, '');
                }

                rows.push([
                    t.tuid,
                    raw['Derivative_Cross'] || t.derivative_cross || '',
                    locus,
                    allele,
                    t.notes !== undefined ? t.notes : (raw['Notes'] || ''),
                    (t.female !== undefined && t.female !== '' && t.female !== null) ? String(t.female) : '',
                    (t.male !== undefined && t.male !== '' && t.male !== null) ? String(t.male) : '',
                    String(t.total !== undefined ? t.total : 0),
                    t.tank_size || raw['Tank_Size'] || '3.5L',
                    raw['Protocol'] || t.protocol || 'QU-IACUC 006/2023-AMM3',
                    raw['DOB'] || t.dob_iso || t.dob || '',
                    raw['Turnover_Deadline'] || t.turnover_date_resolved || t.turnover_date || '',
                    dateEuth,
                    formattedStatus
                ]);
            });
            return rows;
        }
'''

# New fetchLatestCloudData implementation that strictly protects local overrides
new_fetch_cloud = '''        // Live Cloud Data Fetching & Bidirectional Sync
        function fetchLatestCloudData(isSilent = false) {
            const badge = document.getElementById('cloudStatusBadge');
            if (badge && !isSilent) {
                badge.innerText = '🔄 Syncing Google Sheets...';
                badge.style.color = '#fbbf24';
            }

            // Check if there are unsynced local user modifications:
            const overrides = JSON.parse(localStorage.getItem('fishnet_user_tank_overrides') || '{}');
            const hasLocalModifications = Object.values(overrides).some(o => o.is_user_modified);

            // If user clicked Refresh Cloud and has local modifications, push them to cloud as part of the sync
            if (!isSilent && hasLocalModifications) {
                pushTankUpdateToCloud('BULK_SYNC', null);
            }

            fetch(CLOUD_API_URL)
                .then(res => res.json())
                .then(resp => {
                    if (resp.status === 'success' && resp.data) {
                        const cloudTanks = resp.data.tanks || [];
                        let updatedTanksCount = 0;
                        const currentOverrides = JSON.parse(localStorage.getItem('fishnet_user_tank_overrides') || '{}');

                        cloudTanks.forEach(ct => {
                            const tuid = ct.TUID;
                            if (!tuid || !currentTanks[tuid]) return;

                            // Cache the raw cloud record for perfect field preservation
                            cloudTankRawRecords[tuid] = ct;

                            // 🛡️ CRITICAL PERSISTENCE RULE:
                            // If this tank has an explicit manual user edit, NEVER overwrite it with stale cloud data!
                            if (currentOverrides[tuid] && currentOverrides[tuid].is_user_modified) {
                                Object.assign(currentTanks[tuid], currentOverrides[tuid]);
                                return; // Do not overwrite user edit!
                            }

                            // Otherwise, apply live cloud updates to unedited tanks
                            const target = currentTanks[tuid];
                            const rawStatus = ct.Status || ct.status;
                            const cloudStatus = normalizeStatus(rawStatus);
                            if (cloudStatus && cloudStatus !== target.status) {
                                target.status = cloudStatus;
                                updatedTanksCount++;
                                if (cloudStatus === 'Euthanized') {
                                    target.turnover_urgency = 'EUTHANIZED';
                                    target.days_to_turnover = null;
                                    currentAlerts = currentAlerts.filter(a => a.tuid !== tuid);
                                }
                            }
                            if (ct.Female !== undefined && ct.Female !== '') target.female = parseInt(ct.Female) || 0;
                            if (ct.Male !== undefined && ct.Male !== '') target.male = parseInt(ct.Male) || 0;
                            if (ct.Total_Fish !== undefined && ct.Total_Fish !== '') target.total = parseInt(ct.Total_Fish) || (target.female + target.male);
                        });

                        persistEdits();
                        recalculateAndRefreshAllTabs();

                        if (badge) {
                            badge.innerText = '☁️ Cloud: Google Sheets Live';
                            badge.style.color = '#34d399';
                        }

                        if (!isSilent) {
                            const userModCount = Object.values(currentOverrides).filter(o => o.is_user_modified).length;
                            alert(`✔ Cloud Sync Complete!

Successfully connected to Google Sheets.
• Tanks synced: ${cloudTanks.length}
• Remote updates applied: ${updatedTanksCount}
• User local modifications preserved: ${userModCount}

All dashboard KPIs, inventory, and alerts are synchronized!`);
                        }
                    } else {
                        throw new Error(resp.message || 'Malformed API response');
                    }
                })
                .catch(err => {
                    console.warn('Cloud sync error:', err);
                    if (badge && !isSilent) {
                        badge.innerText = '☁️ Cloud Ready (Offline Cache)';
                        badge.style.color = '#38bdf8';
                        alert(`⚠️ Cloud Sync Notice:\n\nCould not reach Google Sheets API directly (${err.message}). Local cached records and your edits remain active and preserved.`);
                    }
                });
        }'''

# Replace old fetchLatestCloudData block
old_fetch_pattern = r'// Live Cloud Data Fetching & Real-Time Sync\s*function fetchLatestCloudData\(isSilent = false\) \{[\s\S]*?alert\(`⚠️ Cloud Sync Notice:[\s\S]*?\}\);\s*\}'

if re.search(old_fetch_pattern, code):
    code = re.sub(old_fetch_pattern, lambda m: cloud_helper_defs + '\n' + new_fetch_cloud, code)
    print(" -> Replaced fetchLatestCloudData with protected bidirectional implementation.")
else:
    print(" -> Could not find old fetchLatestCloudData pattern in code.")

# Patch saveTankEdit to flag is_user_modified: true
old_save_override = r"overrides\[tuid\] = \{\s*status: t\.status,[\s\S]*?updated_at: new Date\(\)\.toISOString\(\)\s*\};"
new_save_override = """overrides[tuid] = {
                    status: t.status,
                    female: t.female,
                    male: t.male,
                    total: t.total,
                    line: t.line,
                    notes: t.notes,
                    tank_size: t.tank_size,
                    dob: t.dob,
                    turnover_urgency: t.turnover_urgency,
                    days_remaining: t.days_remaining,
                    is_user_modified: true,
                    updated_at: new Date().toISOString()
                };"""

if re.search(old_save_override, code):
    code = re.sub(old_save_override, lambda m: new_save_override, code)
    print(" -> Patched saveTankEdit to mark is_user_modified: true.")

# New pushTankUpdateToCloud implementation that builds full rows and posts SYNC_ALL_TANKS
new_push_cloud = '''        // Live Cloud Point Update Push (Google Sheets POST API via SYNC_ALL_TANKS)
        function pushTankUpdateToCloud(tuid, tankObj) {
            if (!CLOUD_API_URL) return;
            const badge = document.getElementById('cloudStatusBadge');
            if (badge) {
                badge.innerText = '☁️ Syncing Google Sheets...';
                badge.style.color = '#fbbf24';
            }

            try {
                const rows = buildGoogleSheetsTankRows();
                const payload = {
                    action: 'SYNC_ALL_TANKS',
                    operator: 'Staff (QU ZebraTrack Web App)',
                    target_tuid: tuid,
                    rows: rows
                };

                fetch(CLOUD_API_URL, {
                    method: 'POST',
                    mode: 'no-cors',
                    headers: { 'Content-Type': 'text/plain;charset=utf-8' },
                    body: JSON.stringify(payload)
                }).then(() => {
                    console.log('Live cloud sync push dispatched successfully for', tuid);
                    if (badge) {
                        badge.innerText = '☁️ Cloud: Google Sheets Live';
                        badge.style.color = '#34d399';
                    }
                }).catch(err => {
                    console.warn('Cloud sync error for', tuid, err);
                    if (badge) {
                        badge.innerText = '☁️ Cloud: Offline Cache Active';
                        badge.style.color = '#38bdf8';
                    }
                });
            } catch(err) {
                console.warn('Error constructing cloud sync payload:', err);
            }
        }'''

old_push_pattern = r'// Live Cloud Point Update Push \(Google Sheets POST API\)\s*function pushTankUpdateToCloud\(tuid, tankObj\) \{[\s\S]*?\}\);\s*\}'

if re.search(old_push_pattern, code):
    code = re.sub(old_push_pattern, lambda m: new_push_cloud, code)
    print(" -> Replaced pushTankUpdateToCloud with full SYNC_ALL_TANKS implementation.")
else:
    print(" -> Could not find old pushTankUpdateToCloud pattern in code.")

with open(gen_path, 'w', encoding='utf-8') as f:
    f.write(code)

print(" -> scripts/generate_integrated_dashboard.py updated.")
