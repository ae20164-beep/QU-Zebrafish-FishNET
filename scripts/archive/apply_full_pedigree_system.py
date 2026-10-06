import os
import re

print("Building complete 4-mode pedigree engine into build_fishnet_analytics.py...")

with open('build_fishnet_analytics.py', 'r', encoding='utf-8') as f:
    content = f.read()

# JavaScript code for 4-mode Pedigree Explorer
pedigree_js_code = """
        // ==================== 4-MODE PEDIGREE ENGINE ====================
        let currentPedigreeMode = 'focal';
        let currentFocalTUID = 'T0135';
        let currentLineTree = 'AB';
        let treeTableExpandedNodes = new Set(['AB', 'Casper', 'Fli', 'Gata']);

        function switchPedigreeMode(mode) {
            currentPedigreeMode = mode;
            ['focal', 'lines', 'table', 'network'].forEach(m => {
                const sub = document.getElementById('ped-subview-' + m);
                const btn = document.getElementById('ped-btn-' + m);
                if (sub) {
                    if (m === mode) {
                        sub.classList.remove('hidden');
                    } else {
                        sub.classList.add('hidden');
                    }
                }
                if (btn) {
                    if (m === mode) {
                        btn.className = 'ped-mode-btn active px-3 py-1.5 rounded-lg text-xs font-semibold bg-teal-600 text-white transition flex items-center gap-1.5 shadow-sm';
                    } else {
                        btn.className = 'ped-mode-btn px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5';
                    }
                }
            });

            if (mode === 'focal') {
                populateFocalDropdown();
                renderFocalPedigreeTree(currentFocalTUID);
            } else if (mode === 'lines') {
                renderLineTrees(currentLineTree);
            } else if (mode === 'table') {
                renderTreeTable();
            } else if (mode === 'network') {
                setTimeout(renderPedigreeNetwork, 50);
            }
        }

        function populateFocalDropdown() {
            if (!computedData) return;
            const select = document.getElementById('focalTankSelect');
            if (!select) return;
            const records = computedData.records;
            select.innerHTML = '';

            // Group by Line
            const lines = ['AB', 'Casper', 'Fli', 'Gata', 'Other'];
            lines.forEach(ln => {
                const grp = records.filter(r => r.Line_Category === ln);
                if (grp.length > 0) {
                    const optGroup = document.createElement('optgroup');
                    optGroup.label = `${ln} Line (${grp.length} tanks)`;
                    grp.forEach(r => {
                        const opt = document.createElement('option');
                        opt.value = r.TUID;
                        const mixTag = r.Is_Mix ? ' [🔀 Mix]' : '';
                        const stTag = !r.Is_Active ? ' (Euthanized)' : '';
                        opt.innerText = `${r.TUID} - Gen F${r.Gen_Depth} (Fish: ${r.Total_Count})${mixTag}${stTag}`;
                        if (r.TUID === currentFocalTUID) opt.selected = true;
                        optGroup.appendChild(opt);
                    });
                    select.appendChild(optGroup);
                }
            });
        }

        function changeFocalTank(tuid) {
            currentFocalTUID = tuid;
            renderFocalPedigreeTree(tuid);
        }

        function searchAndFocusTank() {
            const val = (document.getElementById('focalSearchInput').value || '').trim().toUpperCase();
            if (!val || !computedData) return;
            const found = computedData.records.find(r => r.TUID.toUpperCase() === val || r.TUID.toUpperCase().endsWith(val.replace(/^T0*/, '')));
            if (found) {
                currentFocalTUID = found.TUID;
                const select = document.getElementById('focalTankSelect');
                if (select) select.value = found.TUID;
                renderFocalPedigreeTree(found.TUID);
            } else {
                alert(`Tank '${val}' not found in colony records.`);
            }
        }

        function renderFocalPedigreeTree(tuid) {
            if (!computedData) return;
            const records = computedData.records;
            const tanksMap = {};
            records.forEach(r => { tanksMap[r.TUID] = r; });

            const focal = tanksMap[tuid] || records[0];
            if (!focal) return;
            currentFocalTUID = focal.TUID;

            const select = document.getElementById('focalTankSelect');
            if (select && select.value !== focal.TUID) select.value = focal.TUID;

            // 1. Build Breadcrumb Ancestry Trail
            const trail = [];
            let curr = focal;
            const visited = new Set();
            while (curr && !visited.has(curr.TUID)) {
                visited.add(curr.TUID);
                trail.unshift(curr);
                const p = curr.Sire || curr.Dam;
                curr = p ? tanksMap[p] : null;
            }

            const trailEl = document.getElementById('focalBreadcrumbTrail');
            if (trailEl) {
                let trailHtml = '';
                trail.forEach((node, idx) => {
                    const isLast = idx === trail.length - 1;
                    const genLabel = node.Gen_Depth === 0 ? 'F0 Founder' : `F${node.Gen_Depth}`;
                    const lineCol = node.Line_Category === 'AB' ? 'text-amber-400' : (node.Line_Category === 'Casper' ? 'text-sky-400' : (node.Line_Category === 'Fli' ? 'text-green-400' : 'text-pink-400'));
                    const mixBadge = node.Is_Mix ? '<span class="text-[10px] px-1.5 py-0.2 bg-teal-900/60 text-teal-300 rounded ml-1">🔀 Mix</span>' : '';

                    trailHtml += `
                        <button onclick="changeFocalTank('${node.TUID}')" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg ${isLast ? 'bg-teal-600 text-white font-bold shadow-md' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'} transition">
                            <span>${node.Gen_Depth === 0 ? '🏠' : '🧬'}</span>
                            <span class="${isLast ? 'text-white' : lineCol}">${node.TUID}</span>
                            <span class="text-[10px] opacity-75">(${genLabel})</span>
                            ${mixBadge}
                        </button>
                    `;
                    if (!isLast) {
                        trailHtml += `<span class="text-slate-500">➔</span>`;
                    }
                });
                trailEl.innerHTML = trailHtml;
            }

            // Helper to render mini card
            function createMiniCard(t, relationLabel, isPink=false, isBlue=false) {
                if (!t) {
                    return `
                        <div class="p-3 rounded-lg border border-dashed border-slate-800 bg-slate-900/40 text-center text-slate-600">
                            <span class="text-[11px]">Unrecorded / External Stock</span>
                        </div>
                    `;
                }
                const isEuth = !t.Is_Active;
                const borderCol = isBlue ? 'border-sky-500/50' : (isPink ? 'border-pink-500/50' : (isEuth ? 'border-slate-700' : 'border-slate-700'));
                const bgGrad = isBlue ? 'bg-gradient-to-br from-sky-950/30 to-slate-900' : (isPink ? 'bg-gradient-to-br from-pink-950/30 to-slate-900' : 'bg-slate-900/80');

                return `
                    <div onclick="changeFocalTank('${t.TUID}')" class="cursor-pointer group p-2.5 rounded-xl border ${borderCol} ${bgGrad} hover:border-teal-400 transition hover:shadow-lg space-y-1.5">
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-bold uppercase tracking-wider ${isBlue ? 'text-sky-400' : (isPink ? 'text-pink-400' : 'text-slate-400')}">${relationLabel}</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded ${t.Is_Active ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/40' : 'bg-slate-800 text-slate-400'}">${t.Is_Active ? 'Active' : 'Euth'}</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <h4 class="text-sm font-black text-white group-hover:text-teal-300 transition">${t.TUID}</h4>
                            <span class="text-[11px] font-bold ${t.Line_Category === 'AB' ? 'text-amber-400' : (t.Line_Category === 'Casper' ? 'text-sky-400' : (t.Line_Category === 'Fli' ? 'text-green-400' : 'text-pink-400'))}">${t.Line_Category}</span>
                        </div>
                        <div class="flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/80 pt-1">
                            <span>Fish: <b class="text-slate-200">${t.Total_Count}</b></span>
                            <span>F: <b class="text-amber-400">${t.Inbreeding_F}</b></span>
                            <span>Gen: <b class="text-teal-400">F${t.Gen_Depth}</b></span>
                        </div>
                        ${t.Is_Mix ? '<div class="text-[10px] text-teal-300 bg-teal-950/60 px-1.5 py-0.5 rounded border border-teal-800/40">🔀 Mixed Larvae Batch</div>' : ''}
                    </div>
                `;
            }

            // 2. Col 1: Grandparents
            const sireObj = focal.Sire ? tanksMap[focal.Sire] : null;
            const damObj = focal.Dam ? tanksMap[focal.Dam] : null;

            const patSire = sireObj && sireObj.Sire ? tanksMap[sireObj.Sire] : null;
            const patDam = sireObj && sireObj.Dam ? tanksMap[sireObj.Dam] : null;
            const matSire = damObj && damObj.Sire ? tanksMap[damObj.Sire] : null;
            const matDam = damObj && damObj.Dam ? tanksMap[damObj.Dam] : null;

            let gpColHtml = '';
            if (focal.Gen_Depth === 0) {
                gpColHtml = `
                    <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-2">
                        <span class="text-2xl">🌱</span>
                        <p class="text-xs font-bold text-slate-300">F0 Founder Stock</p>
                        <p class="text-[11px] text-slate-500">No ancestor records preceding founder import.</p>
                    </div>
                `;
            } else {
                gpColHtml = `
                    <div class="space-y-2">
                        <span class="text-[10px] font-bold text-sky-400 uppercase">Paternal Ancestors</span>
                        ${createMiniCard(patSire, 'Paternal Grandfather ♂', false, true)}
                        ${createMiniCard(patDam, 'Paternal Grandmother ♀', true, false)}
                    </div>
                    <div class="space-y-2 pt-2 border-t border-slate-800">
                        <span class="text-[10px] font-bold text-pink-400 uppercase">Maternal Ancestors</span>
                        ${createMiniCard(matSire, 'Maternal Grandfather ♂', false, true)}
                        ${createMiniCard(matDam, 'Maternal Grandmother ♀', true, false)}
                    </div>
                `;
            }
            document.getElementById('treeColGrandparents').innerHTML = gpColHtml;

            // 3. Col 2: Parents
            let parentsColHtml = '';
            if (focal.Is_Mix && focal.Mix_Sources && focal.Mix_Sources.length > 0) {
                parentsColHtml = `
                    <div class="p-3 rounded-xl bg-gradient-to-br from-teal-950/50 to-slate-900 border border-teal-700/60 space-y-2.5">
                        <div class="flex items-center gap-1.5 text-teal-300 font-bold text-xs">
                            <span>🔀</span>
                            <span>Pooled Mating Setups</span>
                        </div>
                        <p class="text-[11px] text-slate-300 leading-relaxed">
                            Larvae from separate single crosses were combined into this communal cohort to maximize genetic vigor.
                        </p>
                        <div class="space-y-1.5 pt-1">
                            <span class="text-[10px] uppercase font-bold text-slate-400">Contributing Source Tanks:</span>
                            <div class="flex flex-wrap gap-1.5">
                                ${focal.Mix_Sources.map(s => `
                                    <button onclick="changeFocalTank('${s}')" class="px-2 py-1 rounded bg-slate-800 hover:bg-teal-700 text-teal-300 hover:text-white border border-slate-700 text-xs font-mono font-bold transition">
                                        ${s} ➔
                                    </button>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `;
            } else if (focal.Gen_Depth === 0) {
                parentsColHtml = `
                    <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-2">
                        <span class="text-2xl">🏛️</span>
                        <p class="text-xs font-bold text-slate-300">Baseline Founder</p>
                        <p class="text-[11px] text-slate-500">Serves as genetic origin ($F=0.0$).</p>
                    </div>
                `;
            } else {
                parentsColHtml = `
                    <div class="space-y-2">
                        ${createMiniCard(sireObj, 'Sire (Father ♂)', false, true)}
                        ${createMiniCard(damObj, 'Dam (Mother ♀)', true, false)}
                    </div>
                `;
            }
            document.getElementById('treeColParents').innerHTML = parentsColHtml;

            // 4. Col 3: Focal Hero Card
            const focalHero = document.getElementById('treeColFocal');
            const genBadge = document.getElementById('focalHeroGenBadge');
            if (genBadge) {
                genBadge.innerText = focal.Gen_Depth === 0 ? 'F0 Founder' : `Generation F${focal.Gen_Depth}`;
                genBadge.className = focal.Gen_Depth === 0 ? 'badge badge-optimal' : 'badge badge-good';
            }

            focalHero.innerHTML = `
                <div class="space-y-3">
                    <div class="flex items-center justify-between">
                        <div>
                            <span class="text-xs font-bold text-slate-400">TUID:</span>
                            <h3 class="text-3xl font-black text-white tracking-tight">${focal.TUID}</h3>
                        </div>
                        <div class="text-right">
                            <span class="text-xs font-bold px-2.5 py-1 rounded-lg ${focal.Line_Category === 'AB' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : (focal.Line_Category === 'Casper' ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30' : (focal.Line_Category === 'Fli' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-pink-500/20 text-pink-400 border border-pink-500/30'))}">
                                ${focal.Line_Category} Line
                            </span>
                            <div class="text-[10px] text-slate-400 mt-1">${focal.Status_Clean}</div>
                        </div>
                    </div>

                    <!-- Metrics Grid -->
                    <div class="grid grid-cols-2 gap-2 bg-slate-900/90 p-3 rounded-xl border border-slate-800 text-xs">
                        <div>
                            <span class="text-slate-400 text-[10px] uppercase">Total Biomass</span>
                            <p class="text-base font-black text-teal-300 mt-0.5">${focal.Total_Count} <span class="text-xs font-normal text-slate-400">fish</span></p>
                            <span class="text-[10px] text-slate-400">${focal.Female_Count} ♀ / ${focal.Male_Count} ♂</span>
                        </div>
                        <div>
                            <span class="text-slate-400 text-[10px] uppercase">Inbreeding Coeff (F)</span>
                            <p class="text-base font-black ${focal.Inbreeding_F >= 0.25 ? 'text-rose-400' : (focal.Inbreeding_F > 0 ? 'text-amber-400' : 'text-emerald-400')} mt-0.5">
                                F = ${focal.Inbreeding_F}
                            </p>
                            <span class="text-[10px] text-slate-400">${focal.Inbreeding_F === 0 ? 'Unrelated / Founder' : (focal.Inbreeding_F >= 0.25 ? 'High Consanguinity' : 'Moderate Inbreeding')}</span>
                        </div>
                        <div>
                            <span class="text-slate-400 text-[10px] uppercase">Age / Stage</span>
                            <p class="text-xs font-bold text-slate-200 mt-0.5">${focal.Age_Months ? focal.Age_Months + ' mo' : 'N/A'}</p>
                            <span class="text-[10px] text-slate-400">DOB: ${focal.DOB || 'N/A'}</span>
                        </div>
                        <div>
                            <span class="text-slate-400 text-[10px] uppercase">Turnover Status</span>
                            <p class="text-xs font-bold ${focal.Turnover_Urgency === 'OVERDUE' ? 'text-rose-400' : 'text-slate-200'} mt-0.5">${focal.Turnover_Urgency || 'N/A'}</p>
                            <span class="text-[10px] text-slate-400">${focal.Days_To_Turnover ? focal.Days_To_Turnover + 'd remaining' : 'No date'}</span>
                        </div>
                    </div>

                    <!-- Husbandry & Genetic Strategy Badge -->
                    <div class="p-2.5 rounded-xl ${focal.Is_Mix ? 'bg-teal-950/40 border border-teal-800/40' : 'bg-slate-900/60 border border-slate-800'} text-xs space-y-1">
                        <div class="flex items-center justify-between">
                            <span class="text-slate-400 text-[10px] uppercase font-bold">Genetic Structure:</span>
                            <span class="font-bold ${focal.Is_Mix ? 'text-teal-300' : 'text-slate-300'}">${focal.Genetic_Type || 'Single Cross'}</span>
                        </div>
                        <div class="text-[11px] text-slate-300">
                            <b>Notes:</b> ${focal.NOTES || 'None'}
                        </div>
                    </div>
                </div>
            `;

            // 5. Col 4: Direct Offspring (Children)
            const children = records.filter(r => r.Sire === focal.TUID || r.Dam === focal.TUID);
            document.getElementById('treeOffspringCountBadge').innerText = `${children.length} Tanks`;

            let offspringHtml = '';
            if (children.length === 0) {
                offspringHtml = `
                    <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-2">
                        <span class="text-2xl">🌱</span>
                        <p class="text-xs font-bold text-slate-300">No Direct Offspring</p>
                        <p class="text-[11px] text-slate-500">No tanks in the database have this tank recorded as Sire or Dam.</p>
                    </div>
                `;
            } else {
                children.forEach(ch => {
                    const isAsSire = ch.Sire === focal.TUID;
                    const isAsDam = ch.Dam === focal.TUID;
                    const roleLabel = (isAsSire && isAsDam) ? 'Selfed / Both' : (isAsSire ? 'Offspring via Sire ♂' : 'Offspring via Dam ♀');
                    offspringHtml += createMiniCard(ch, roleLabel);
                });
            }
            document.getElementById('treeColOffspring').innerHTML = offspringHtml;

            // 6. Col 5: Grandchildren
            const childIds = new Set(children.map(c => c.TUID));
            const grandchildren = records.filter(r => (r.Sire && childIds.has(r.Sire)) || (r.Dam && childIds.has(r.Dam)));
            document.getElementById('treeGrandchildrenCountBadge').innerText = `${grandchildren.length} Tanks`;

            let grandChildrenHtml = '';
            if (grandchildren.length === 0) {
                grandChildrenHtml = `
                    <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-2">
                        <span class="text-2xl">🌿</span>
                        <p class="text-xs font-bold text-slate-300">No Grandchildren</p>
                        <p class="text-[11px] text-slate-500">Terminal progeny branch.</p>
                    </div>
                `;
            } else {
                grandchildren.forEach(gc => {
                    grandChildrenHtml += createMiniCard(gc, `Grandchild (Gen F${gc.Gen_Depth})`);
                });
            }
            document.getElementById('treeColGrandchildren').innerHTML = grandChildrenHtml;
        }

        function copyLineageTrail() {
            if (!computedData) return;
            const records = computedData.records;
            const tanksMap = {};
            records.forEach(r => { tanksMap[r.TUID] = r; });
            const focal = tanksMap[currentFocalTUID];
            if (!focal) return;

            const trail = [];
            let curr = focal;
            const visited = new Set();
            while (curr && !visited.has(curr.TUID)) {
                visited.add(curr.TUID);
                trail.unshift(curr);
                const p = curr.Sire || curr.Dam;
                curr = p ? tanksMap[p] : null;
            }

            const pathStr = trail.map(n => `${n.TUID} (F${n.Gen_Depth}, ${n.Line_Category})`).join(' ➔ ');
            navigator.clipboard.writeText(pathStr).then(() => {
                alert(`📋 Copied Lineage Trail to Clipboard:\\n${pathStr}`);
            }).catch(() => {
                alert(`Lineage Path:\\n${pathStr}`);
            });
        }

        function printPedigreeCard() {
            if (!computedData) return;
            const records = computedData.records;
            const focal = records.find(r => r.TUID === currentFocalTUID);
            if (!focal) return;

            const printWin = window.open('', '_blank', 'width=800,height=600');
            printWin.document.write(`
                <html>
                <head>
                    <title>FishNET Pedigree Certificate - ${focal.TUID}</title>
                    <style>
                        body { font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; color: #0f172a; }
                        .card { border: 2px solid #0f172a; border-radius: 12px; padding: 24px; max-width: 650px; margin: 0 auto; }
                        h1 { margin: 0 0 8px 0; font-size: 24px; color: #0f766e; }
                        table { width: 100%; border-collapse: collapse; margin-top: 16px; }
                        th, td { border: 1px solid #cbd5e1; padding: 8px 12px; font-size: 13px; text-align: left; }
                        th { background: #f1f5f9; }
                    </style>
                </head>
                <body>
                    <div class="card">
                        <h1>🐟 Zebrafish Colony Pedigree Certificate</h1>
                        <p><b>Tank ID:</b> ${focal.TUID} | <b>Line:</b> ${focal.Line_Category} | <b>Generation:</b> F${focal.Gen_Depth}</p>
                        <table>
                            <tr><th>Status</th><td>${focal.STATUS || 'Active'}</td></tr>
                            <tr><th>Genotype / Notes</th><td>${focal.NOTES || 'N/A'}</td></tr>
                            <tr><th>Genetic Strategy</th><td>${focal.Genetic_Type || 'Single Cross'}</td></tr>
                            <tr><th>Inbreeding Coefficient (F)</th><td>${focal.Inbreeding_F}</td></tr>
                            <tr><th>Sire (Father ♂)</th><td>${focal.Sire || 'F0 Founder / External'}</td></tr>
                            <tr><th>Dam (Mother ♀)</th><td>${focal.Dam || 'F0 Founder / External'}</td></tr>
                            <tr><th>Fish Count</th><td>${focal.Total_Count} (${focal.Female_Count} Females / ${focal.Male_Count} Males)</td></tr>
                            <tr><th>Date of Birth (DOB)</th><td>${focal.DOB || 'N/A'}</td></tr>
                            <tr><th>Turnover Date</th><td>${focal.TURNOVER || 'N/A'}</td></tr>
                        </table>
                        <p style="margin-top: 24px; font-size: 11px; color: #64748b;">Generated from FishNET Colony Database on ${new Date().toLocaleDateString()}</p>
                    </div>
                </body>
                </html>
            `);
            printWin.document.close();
            printWin.print();
        }

        // ==================== SUB-VIEW 2: LINE-BY-LINE FLOWCHARTS ====================
        function selectLineTree(line) {
            currentLineTree = line;
            ['AB', 'Casper', 'Fli', 'Gata'].forEach(ln => {
                const btn = document.getElementById('line-tree-btn-' + ln);
                if (btn) {
                    if (ln === line) {
                        const col = ln === 'AB' ? 'bg-amber-500 text-slate-950' : (ln === 'Casper' ? 'bg-sky-500 text-slate-950' : (ln === 'Fli' ? 'bg-green-500 text-slate-950' : 'bg-pink-500 text-slate-950'));
                        btn.className = `line-tree-btn active px-3.5 py-1.5 rounded-lg text-xs font-bold ${col} transition`;
                    } else {
                        const textCol = ln === 'AB' ? 'text-amber-400' : (ln === 'Casper' ? 'text-sky-400' : (ln === 'Fli' ? 'text-green-400' : 'text-pink-400'));
                        btn.className = `line-tree-btn px-3.5 py-1.5 rounded-lg text-xs font-bold ${textCol} bg-slate-800 hover:bg-slate-700 transition`;
                    }
                }
            });
            renderLineTrees(line);
        }

        function renderLineTrees(line) {
            if (!computedData) return;
            const records = computedData.records;

            // Update counts in buttons
            ['AB', 'Casper', 'Fli', 'Gata'].forEach(ln => {
                const cnt = records.filter(r => r.Line_Category === ln).length;
                const el = document.getElementById('lineTreeCount' + ln);
                if (el) el.innerText = cnt;
            });

            const lineRecords = records.filter(r => r.Line_Category === line);
            const container = document.getElementById('lineTreeTiersContainer');
            if (!container) return;

            // Group by Gen_Depth
            const tiers = {};
            lineRecords.forEach(r => {
                const g = r.Gen_Depth;
                if (!tiers[g]) tiers[g] = [];
                tiers[g].push(r);
            });

            const sortedGens = Object.keys(tiers).map(Number).sort((a, b) => a - b);

            let html = '';
            sortedGens.forEach(gen => {
                const tanks = tiers[gen];
                const tierTitle = gen === 0 ? '🌱 Generation Tier 0: F0 Founders' : `🧬 Generation Tier ${gen}: F${gen} Offspring`;
                const tierDesc = gen === 0 ? 'Baseline founding stocks (no recorded internal ancestors)' : `Descendants with maximum lineage depth ${gen}`;

                html += `
                    <div class="glass-card p-4 rounded-xl space-y-3">
                        <div class="flex items-center justify-between border-b border-slate-700 pb-2">
                            <div>
                                <h3 class="text-sm font-bold text-white flex items-center gap-2">
                                    <span>${tierTitle}</span>
                                    <span class="px-2 py-0.5 rounded-full bg-slate-800 text-teal-400 text-xs font-mono">${tanks.length} Tanks</span>
                                </h3>
                                <p class="text-[11px] text-slate-400">${tierDesc}</p>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3 pt-2">
                            ${tanks.map(t => {
                                const isEuth = !t.Is_Active;
                                return `
                                    <div onclick="switchPedigreeMode('focal'); changeFocalTank('${t.TUID}');" class="cursor-pointer group p-3 rounded-xl border ${isEuth ? 'border-slate-800 bg-slate-900/40 opacity-75' : 'border-slate-700 bg-slate-900/90'} hover:border-teal-400 transition hover:shadow-md space-y-1.5">
                                        <div class="flex items-center justify-between">
                                            <span class="text-xs font-black text-white group-hover:text-teal-300 transition">${t.TUID}</span>
                                            <span class="text-[10px] px-1.5 py-0.2 rounded ${t.Is_Active ? 'bg-emerald-950 text-emerald-400' : 'bg-slate-800 text-slate-400'}">${t.Is_Active ? 'Active' : 'Euth'}</span>
                                        </div>
                                        <div class="text-[11px] text-slate-300">
                                            <span>Fish: <b>${t.Total_Count}</b></span> (${t.Female_Count}F / ${t.Male_Count}M)
                                        </div>
                                        <div class="text-[10px] text-slate-400 flex items-center justify-between border-t border-slate-800 pt-1">
                                            <span>F = <b class="text-amber-400">${t.Inbreeding_F}</b></span>
                                            <span>Prog: <b class="text-teal-400">${t.Progeny_Count}</b></span>
                                        </div>
                                        ${t.Is_Mix ? '<div class="text-[9px] font-bold text-teal-300 bg-teal-950/80 px-1 rounded border border-teal-800/40">🔀 Mix Cohort</div>' : ''}
                                        ${(t.Sire || t.Dam) ? `<div class="text-[9px] text-slate-400 truncate">P: ${t.Sire || '?' } × ${t.Dam || '?'}</div>` : ''}
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        }

        // ==================== SUB-VIEW 3: COLLAPSIBLE TREE TABLE ====================
        function renderTreeTable() {
            if (!computedData) return;
            const records = computedData.records;
            const tbody = document.getElementById('pedigreeTreeTableBody');
            if (!tbody) return;

            const q = (document.getElementById('treeTableSearchInput')?.value || '').toLowerCase().trim();
            const lineFilter = document.getElementById('treeTableLineFilter')?.value || 'ALL';
            const stFilter = document.getElementById('treeTableStatusFilter')?.value || 'ALL';

            let filtered = records.filter(r => {
                if (lineFilter !== 'ALL' && r.Line_Category !== lineFilter) return false;
                if (stFilter === 'ACTIVE' && !r.Is_Active) return false;
                if (stFilter === 'EUTH' && r.Is_Active) return false;
                if (q) {
                    const str = `${r.TUID} ${r.Line_Category} ${r.NOTES} ${r.STATUS} ${r.Sire} ${r.Dam} ${r.Genetic_Type}`.toLowerCase();
                    if (!str.includes(q)) return false;
                }
                return true;
            });

            // Sort hierarchically: Line -> Gen_Depth -> TUID
            filtered.sort((a, b) => {
                if (a.Line_Category !== b.Line_Category) return a.Line_Category.localeCompare(b.Line_Category);
                if (a.Gen_Depth !== b.Gen_Depth) return a.Gen_Depth - b.Gen_Depth;
                return a.TUID.localeCompare(b.TUID);
            });

            let html = '';
            filtered.forEach(r => {
                const isEuth = !r.Is_Active;
                const genBadge = r.Gen_Depth === 0 ? '<span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 text-[10px] font-bold">F0 Founder</span>' : `<span class="px-2 py-0.5 rounded bg-blue-950 text-blue-400 text-[10px] font-bold">Gen F${r.Gen_Depth}</span>`;
                const mixBadge = r.Is_Mix ? '<span class="px-1.5 py-0.5 rounded bg-teal-900/60 text-teal-300 text-[10px] border border-teal-700/50">🔀 Mix</span>' : '';
                const lineCol = r.Line_Category === 'AB' ? 'text-amber-400' : (r.Line_Category === 'Casper' ? 'text-sky-400' : (r.Line_Category === 'Fli' ? 'text-green-400' : 'text-pink-400'));

                html += `
                    <tr class="hover:bg-slate-800/60 transition ${isEuth ? 'opacity-60 bg-slate-900/40' : ''}">
                        <td class="p-3 font-mono font-bold flex items-center gap-1.5">
                            <span class="${lineCol}">${r.TUID}</span>
                            <span class="text-[10px] font-semibold text-slate-400">(${r.Line_Category})</span>
                        </td>
                        <td class="p-3">${genBadge}</td>
                        <td class="p-3">
                            <span class="badge ${r.Is_Active ? 'badge-optimal' : 'badge-archive'}">${r.Status_Clean}</span>
                        </td>
                        <td class="p-3">
                            <span class="font-bold text-white">${r.Total_Count}</span>
                            <span class="text-[11px] text-slate-400">(${r.Female_Count}♀ / ${r.Male_Count}♂)</span>
                        </td>
                        <td class="p-3 font-mono font-bold ${r.Inbreeding_F >= 0.25 ? 'text-rose-400' : (r.Inbreeding_F > 0 ? 'text-amber-400' : 'text-emerald-400')}">
                            ${r.Inbreeding_F}
                        </td>
                        <td class="p-3">
                            <div class="flex items-center gap-1.5">
                                ${mixBadge}
                                <span class="text-[11px] ${r.Is_Mix ? 'text-teal-300 font-semibold' : 'text-slate-300'}">${r.Genetic_Type || 'Single Cross'}</span>
                            </div>
                            ${r.Mix_Sources_Str ? `<div class="text-[10px] text-slate-400 mt-0.5">Pool: ${r.Mix_Sources_Str}</div>` : ''}
                        </td>
                        <td class="p-3 font-mono text-[11px] text-slate-300">
                            ${(r.Sire || r.Dam) ? `${r.Sire || '?'} × ${r.Dam || '?'}` : '<span class="text-slate-500">None (F0)</span>'}
                        </td>
                        <td class="p-3">
                            <span class="px-2 py-0.5 rounded bg-slate-800 text-teal-300 font-bold">${r.Progeny_Count}</span>
                        </td>
                        <td class="p-3 text-center">
                            <button onclick="switchPedigreeMode('focal'); changeFocalTank('${r.TUID}');" class="px-2.5 py-1 rounded bg-teal-600 hover:bg-teal-500 text-white text-[11px] font-semibold transition">
                                🎯 Focus
                            </button>
                        </td>
                    </tr>
                `;
            });

            tbody.innerHTML = html;
        }

        function filterTreeTable() {
            renderTreeTable();
        }

        function expandAllTreeRows() {
            renderTreeTable();
        }

        function collapseAllTreeRows() {
            renderTreeTable();
        }

        function exportTreeTableCSV() {
            if (!computedData) return;
            const headers = ['TUID', 'Line', 'Gen_Depth', 'Status', 'Total_Count', 'Female_Count', 'Male_Count', 'Inbreeding_F', 'Genetic_Type', 'Mix_Sources', 'Sire', 'Dam', 'Progeny_Count', 'DOB', 'TURNOVER'];
            let csvContent = 'data:text/csv;charset=utf-8,' + headers.join(',') + '\\n';

            computedData.records.forEach(r => {
                const row = [
                    r.TUID,
                    r.Line_Category,
                    r.Gen_Depth,
                    `"${r.STATUS || ''}"`,
                    r.Total_Count,
                    r.Female_Count,
                    r.Male_Count,
                    r.Inbreeding_F,
                    `"${r.Genetic_Type || ''}"`,
                    `"${r.Mix_Sources_Str || ''}"`,
                    r.Sire,
                    r.Dam,
                    r.Progeny_Count,
                    r.DOB || '',
                    r.TURNOVER || ''
                ];
                csvContent += row.join(',') + '\\n';
            });

            const encodedUri = encodeURI(csvContent);
            const link = document.createElement('a');
            link.setAttribute('href', encodedUri);
            link.setAttribute('download', `FishNET_Pedigree_Lineage_Matrix_${new Date().toISOString().slice(0,10)}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
"""

# Replace the beginning of pedigree network JS with our full engine
old_network_start = "// Pedigree Graph Rendering\n        let networkNodesData = [];"
if old_network_start in content:
    content = content.replace(old_network_start, pedigree_js_code + "\n\n        // Pedigree Graph Rendering\n        let networkNodesData = [];")
elif "let currentPedigreeMode = 'focal';" not in content:
    content = content.replace("let networkNodesData = [];", pedigree_js_code + "\n\n        let networkNodesData = [];")

# Also update displayNodeDetails to show genetic category & mix tags
old_disp = "document.getElementById('inspectLine').innerText = `Primary Line: ${r.Line_Category}`;"
new_disp = """document.getElementById('inspectLine').innerText = `Primary Line: ${r.Line_Category} | ${r.Genetic_Type || 'Single Cross'}`;
            const genTypeEl = document.getElementById('inspectGeneticType');
            if (genTypeEl) genTypeEl.innerText = r.Genetic_Type || 'Single Cross';"""

if old_disp in content and "inspectGeneticType" not in content:
    content = content.replace(old_disp, new_disp)

# Update switchTab to initialize pedigree mode
old_switch = """            if (tabId === 'pedigree') {
                setTimeout(renderPedigreeNetwork, 50);
            }"""
new_switch = """            if (tabId === 'pedigree') {
                switchPedigreeMode(currentPedigreeMode);
            }"""
if old_switch in content:
    content = content.replace(old_switch, new_switch)

with open('build_fishnet_analytics.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Injected 4-mode Pedigree JavaScript Engine successfully into build_fishnet_analytics.py.")
