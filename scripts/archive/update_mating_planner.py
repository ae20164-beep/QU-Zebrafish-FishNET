import re

print("Upgrading calculatePlanner in generate_integrated_dashboard.py...")

with open('generate_integrated_dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_planner_code = """        // Enhanced Intelligent Mating Planner Calculation
        function calculatePlanner() {
            const line = document.getElementById('plannerLine').value;
            const targetEmbryos = parseInt(document.getElementById('plannerTargetEmbryos').value) || 1000;
            const strategy = document.getElementById('plannerStrategy').value;

            const bm = calculateLineBenchmarks()[line] || { spawns: 10, eggs: 5000, validSpawns: 10, sr24Sum: 800 };
            const avgClutch = bm.spawns > 0 ? (bm.eggs / bm.spawns) : 500;
            const avgSR24 = bm.validSpawns > 0 ? (bm.sr24Sum / bm.validSpawns) / 100 : 0.75;
            const expectedViablePerSpawn = Math.max(50, avgClutch * avgSR24);

            const setupsNeeded = Math.ceil(targetEmbryos / expectedViablePerSpawn);
            let recommendationHTML = '';

            if (strategy === 'cross') {
                // Filter strictly for pure line crosses (Dam and Sire belong to the selected line, no outcrosses)
                const pureLinePairs = currentPairs.filter(p => {
                    const isPure = p.line === line && !p.line.includes('Outcross') && !p.is_outcross;
                    return isPure;
                });

                // Check active status of tanks in pair
                const activePairs = pureLinePairs.filter(p => {
                    const dam = currentTanks[p.dam || p.tank_a];
                    const sire = currentTanks[p.sire || p.tank_b];
                    return (dam && dam.status === 'Active') && (sire && sire.status === 'Active');
                });

                const displayPairs = activePairs.length > 0 ? activePairs : pureLinePairs;

                recommendationHTML = `
                    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 14px; margin-bottom: 16px;">
                        <h4 style="color: var(--accent-emerald); font-size: 15px; font-weight: bold; margin-bottom: 6px; display: flex; items-center; gap: 6px;">
                            <span>🎯</span> Recommended Cross-Pairing Plan (Dam ♀ × Sire ♂)
                        </h4>
                        <p style="font-size: 13px; color: var(--text-primary); margin-bottom: 8px;">
                            Target: <strong>${targetEmbryos.toLocaleString()} viable 24hpf embryos</strong> in line <strong>${line}</strong>
                        </p>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; font-size: 12px; margin-top: 10px;">
                            <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 6px;">
                                <span style="color: var(--text-secondary); font-size: 11px;">Breeding Setups:</span>
                                <p style="font-size: 16px; font-weight: bold; color: var(--accent-emerald);">${setupsNeeded} Pair Boxes</p>
                            </div>
                            <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 6px;">
                                <span style="color: var(--text-secondary); font-size: 11px;">Expected Total Eggs:</span>
                                <p style="font-size: 16px; font-weight: bold; color: var(--accent-blue);">~${Math.round(setupsNeeded * avgClutch).toLocaleString()}</p>
                            </div>
                            <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 6px;">
                                <span style="color: var(--text-secondary); font-size: 11px;">Expected 24hpf Viable:</span>
                                <p style="font-size: 16px; font-weight: bold; color: var(--accent-amber);">~${Math.round(setupsNeeded * expectedViablePerSpawn).toLocaleString()} (${(avgSR24 * 100).toFixed(1)}% SR)</p>
                            </div>
                        </div>
                    </div>

                    <div style="margin-top: 14px;">
                        <span style="font-size: 13px; font-weight: bold; color: var(--accent-blue); display: flex; items-center; gap: 6px;">
                            <span>🏆</span> Top Proven Active Cross Combinations in Facility:
                        </span>
                        <div style="margin-top: 8px; display: flex; flex-direction: column; gap: 8px;">
                            ${
                                displayPairs.slice(0, 4).map((p, idx) => {
                                    const damT = currentTanks[p.dam || p.tank_a] || {};
                                    const sireT = currentTanks[p.sire || p.tank_b] || {};
                                    const damActive = damT.status === 'Active';
                                    const sireActive = sireT.status === 'Active';

                                    return `
                                        <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); padding: 10px 14px; border-radius: 8px; font-size: 12px; display: flex; flex-direction: column; gap: 4px;">
                                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                                <strong style="color: #fff; font-size: 13px;">#${idx + 1}: ${p.pair_key}</strong>
                                                <span style="color: var(--accent-emerald); font-weight: bold;">${p.avg_sr24}% 24h SR</span>
                                            </div>
                                            <div style="display: flex; gap: 12px; font-size: 11px; color: var(--text-secondary);">
                                                <span>Dam: <b style="color: #f472b6;">${p.dam || p.tank_a}</b> (${damActive ? (damT.female || '?') + '♀ Active' : 'Archived'})</span>
                                                <span>Sire: <b style="color: #38bdf8;">${p.sire || p.tank_b}</b> (${sireActive ? (sireT.male || '?') + '♂ Active' : 'Archived'})</span>
                                                <span>Avg: <b style="color: #fff;">${p.avg_clutch}</b> eggs</span>
                                                <span>Spawns: <b style="color: #fff;">${p.spawns}</b></span>
                                            </div>
                                        </div>
                                    `;
                                }).join('') || '<div style="font-size: 12px; color: var(--text-muted); padding: 12px; background: rgba(255,255,255,0.02); border-radius: 6px;">No historical single-pair records found for pure ' + line + '. Recommend setting up crosses between active single-sex reservoirs in the rack.</div>'
                            }
                        </div>
                    </div>
                `;
            } else {
                // In-Tank Spawning Strategy: Find active mixed-sex / colony group tanks of this line
                const activeInTankCandidates = Object.values(currentTanks).filter(t => {
                    const isTargetLine = t.line === line;
                    const isActive = t.status === 'Active';
                    const isMixedOrInTank = (t.sex_type === 'Mixed-Sex' || t.can_in_tank || t.in_tank_spawns > 0 || (t.female > 0 && t.male > 0));
                    return isTargetLine && isActive && isMixedOrInTank;
                });

                // Rank by in-tank performance or overall fecundity
                activeInTankCandidates.sort((a, b) => {
                    const aSR = a.total_eggs_0h > 0 ? (a.total_live_24h / a.total_eggs_0h) : 0;
                    const bSR = b.total_eggs_0h > 0 ? (b.total_live_24h / b.total_eggs_0h) : 0;
                    return (b.in_tank_spawns - a.in_tank_spawns) || (bSR - aSR) || (b.total_eggs_0h - a.total_eggs_0h);
                });

                const inTankSetups = Math.ceil(targetEmbryos / (expectedViablePerSpawn * 1.2));

                recommendationHTML = `
                    <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 14px; margin-bottom: 16px;">
                        <h4 style="color: var(--accent-blue); font-size: 15px; font-weight: bold; margin-bottom: 6px; display: flex; items-center; gap: 6px;">
                            <span>📦</span> Recommended In-Tank / Colony Group Spawning Plan
                        </h4>
                        <p style="font-size: 13px; color: var(--text-primary); margin-bottom: 8px;">
                            Target: <strong>${targetEmbryos.toLocaleString()} viable embryos</strong> in line <strong>${line}</strong> using self-contained communal colony tanks.
                        </p>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; font-size: 12px; margin-top: 10px;">
                            <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 6px;">
                                <span style="color: var(--text-secondary); font-size: 11px;">Group Tanks Needed:</span>
                                <p style="font-size: 16px; font-weight: bold; color: var(--accent-blue);">${inTankSetups} Active Colony Tanks</p>
                            </div>
                            <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 6px;">
                                <span style="color: var(--text-secondary); font-size: 11px;">Expected Total Yield:</span>
                                <p style="font-size: 16px; font-weight: bold; color: var(--accent-emerald);">~${Math.round(inTankSetups * expectedViablePerSpawn * 1.2).toLocaleString()} viable embryos</p>
                            </div>
                            <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 6px;">
                                <span style="color: var(--text-secondary); font-size: 11px;">Husbandry Rest Period:</span>
                                <p style="font-size: 14px; font-weight: bold; color: var(--accent-amber);">≥14 Days Rest</p>
                            </div>
                        </div>
                    </div>

                    <div style="margin-top: 14px;">
                        <span style="font-size: 13px; font-weight: bold; color: var(--accent-emerald); display: flex; items-center; gap: 6px;">
                            <span>🏢</span> Active In-Tank Colony Tanks Available in Facility (${activeInTankCandidates.length} Tanks):
                        </span>
                        <div style="margin-top: 8px; display: flex; flex-direction: column; gap: 8px;">
                            ${
                                activeInTankCandidates.slice(0, 5).map((t, idx) => {
                                    const inTankSpawns = t.in_tank_spawns || 0;
                                    const avgLive = t.total_spawns > 0 ? Math.round(t.total_live_24h / t.total_spawns) : 'N/A';
                                    const mixTag = t.notes && t.notes.toLowerCase().includes('mix') ? '<span style="background: rgba(13,148,136,0.2); color: #2dd4bf; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 6px;">🔀 Mix Pool</span>' : '';

                                    return `
                                        <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); padding: 10px 14px; border-radius: 8px; font-size: 12px; display: flex; justify-content: space-between; align-items: center;">
                                            <div>
                                                <div style="display: flex; align-items: center; gap: 6px;">
                                                    <strong style="color: #fff; font-size: 13px;">${t.tuid}</strong>
                                                    <span style="color: var(--text-secondary); font-size: 11px;">(${t.notes || 'No notes'})</span>
                                                    ${mixTag}
                                                </div>
                                                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 3px;">
                                                    Fish: <b style="color: #fff;">${t.total}</b> (${t.female}♀ / ${t.male}♂) | In-Tank Spawns: <b style="color: var(--accent-blue);">${inTankSpawns}</b> | Avg Yield: <b style="color: var(--accent-emerald);">${avgLive}</b> viable/spawn
                                                </div>
                                            </div>
                                            <div>
                                                <button onclick="openTankModal('${t.tuid}')" style="background: var(--accent-blue); color: #000; border: none; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer;">
                                                    Inspect
                                                </button>
                                            </div>
                                        </div>
                                    `;
                                }).join('') || '<div style="font-size: 12px; color: var(--text-muted); padding: 12px; background: rgba(255,255,255,0.02); border-radius: 6px;">No active mixed-sex group colony tanks found for ' + line + '. Please use the Cross-Pairing strategy with single-sex tanks.</div>'
                            }
                        </div>
                    </div>
                `;
            }

            document.getElementById('plannerResultBox').innerHTML = recommendationHTML;
        }"""

# Replace the old calculatePlanner block
code = re.sub(r'// Planner Calculation\s*function calculatePlanner\(\) \{[\s\S]*?document\.getElementById\(\'plannerResultBox\'\)\.innerHTML = recommendationHTML;\s*\}', new_planner_code.strip(), code)

with open('generate_integrated_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved updated calculatePlanner in generate_integrated_dashboard.py.")
