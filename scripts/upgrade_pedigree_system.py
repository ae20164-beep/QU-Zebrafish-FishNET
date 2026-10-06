import re

with open('build_fishnet_analytics.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure HTML_DASHBOARD_FILE writes to both FishNET_Interactive_Dashboard.html and FishNET_Interactive_Dashboard_Standard_Backup.html
output_write_code = """
with open('FishNET_Interactive_Dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

with open(HTML_DASHBOARD_FILE, 'w', encoding='utf-8') as f:
    f.write(html_content)

print('HTML Dashboards generated: FishNET_Interactive_Dashboard.html and FishNET_Interactive_Dashboard_Standard_Backup.html')
"""

# Let's replace the write block at the end
content = re.sub(r"with open\(HTML_DASHBOARD_FILE, 'w', encoding='utf-8'\) as f:\s+f\.write\(html_content\)\s+print\(f'HTML Dashboard generated: \{HTML_DASHBOARD_FILE\}'\)", output_write_code.strip(), content)

# 1. Update JS runFullAnalysis to include mix parsing
js_mix_parse = """
            // Parse Mix info in JS
            function parseJsMix(notes, status, tankStr) {
                const text = `${notes || ''} ${status || ''} ${tankStr || ''}`.toLowerCase();
                const isMix = text.includes('mix') || text.includes('pool');
                if (!isMix) return { isMix: false, sources: [], geneticType: 'Pedigreed / Single Cross' };

                const sources = [];
                const tMatches = (notes || '').match(/[tT](\\d{1,4})/g);
                if (tMatches) {
                    tMatches.forEach(m => {
                        const num = parseInt(m.replace(/[^0-9]/g, ''));
                        const cand = 'T' + String(num).padStart(4, '0');
                        if (!sources.includes(cand)) sources.push(cand);
                    });
                } else if (text.includes('95 x 93') || text.includes('95x93')) {
                    sources.push('T0095', 'T0093');
                }
                return { isMix: true, sources: sources, geneticType: 'Pooled Diverse Stock (Low Inbreeding Risk)' };
            }
"""

# Check if js_mix_parse needs to be injected into runFullAnalysis
if "parseJsMix" not in content:
    content = content.replace("function runFullAnalysis(records) {", "function runFullAnalysis(records) {\n" + js_mix_parse)

# In JS enrich:
old_js_enrich = "const line = categorizeLine(r['NOTES']);"
new_js_enrich = """const line = categorizeLine(r['NOTES']);
                const mixInfo = parseJsMix(r['NOTES'], r['STATUS'], r['TANK'] || r['TANK ']);
                const isMix = mixInfo.isMix;
                const mixSources = mixInfo.sources;
                const geneticType = genDepth[tuid] === 0 && !isMix ? 'Founder Stock (F0)' : mixInfo.geneticType;"""

if old_js_enrich in content and "const mixInfo = parseJsMix" not in content:
    content = content.replace(old_js_enrich, new_js_enrich)

old_js_obj = """Line_Category: line,
                    Gen_Depth: genDepth[tuid],"""
new_js_obj = """Line_Category: line,
                    Gen_Depth: genDepth[tuid],
                    Is_Mix: isMix,
                    Mix_Sources: mixSources,
                    Mix_Sources_Str: mixSources.join(', '),
                    Genetic_Type: geneticType,"""
if old_js_obj in content and "Is_Mix: isMix" not in content:
    content = content.replace(old_js_obj, new_js_obj)

# Now let's construct the 4-Mode Pedigree HTML Section
new_pedigree_section = """        <!-- ==================== TAB 2: PEDIGREE EXPLORER (4 INTERACTIVE MODES) ==================== -->
        <section id="tab-pedigree" class="tab-content hidden space-y-4">
            <div class="glass p-5 rounded-xl shadow-lg">
                <!-- Pedigree Header & Mode Selector -->
                <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-700">
                    <div>
                        <div class="flex items-center gap-2">
                            <h2 class="text-lg font-bold text-white flex items-center gap-2">
                                🌳 Colony Lineage & Pedigree Architecture
                            </h2>
                            <span class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-400 border border-teal-500/30">4 Visualization Modes</span>
                        </div>
                        <p class="text-xs text-slate-400 mt-0.5">Explore 3-gen family cards, clean line trees, collapsible table hierarchy, and the full colony network map.</p>
                    </div>

                    <!-- 4 Mode Sub-Tab Navigation -->
                    <div class="flex flex-wrap items-center gap-1.5 bg-slate-900/80 p-1.5 rounded-xl border border-slate-700">
                        <button onclick="switchPedigreeMode('focal')" id="ped-btn-focal" class="ped-mode-btn active px-3 py-1.5 rounded-lg text-xs font-semibold bg-teal-600 text-white transition flex items-center gap-1.5 shadow-sm">
                            <span>🎯 3-Gen Family Tree</span>
                        </button>
                        <button onclick="switchPedigreeMode('lines')" id="ped-btn-lines" class="ped-mode-btn px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5">
                            <span>🌿 Line Trees (4 Lines)</span>
                        </button>
                        <button onclick="switchPedigreeMode('table')" id="ped-btn-table" class="ped-mode-btn px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5">
                            <span>📑 Collapsible Tree Table</span>
                        </button>
                        <button onclick="switchPedigreeMode('network')" id="ped-btn-network" class="ped-mode-btn px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5">
                            <span>🕸️ Global Network Map</span>
                        </button>
                    </div>
                </div>

                <!-- Biological Husbandry Callout (Mixed Batches & Outcrosses) -->
                <div class="mt-4 p-3.5 rounded-xl bg-gradient-to-r from-teal-950/40 via-slate-900/60 to-indigo-950/40 border border-teal-800/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
                    <div class="flex items-center gap-2.5">
                        <span class="p-2 rounded-lg bg-teal-500/20 text-teal-300 text-sm">🔀</span>
                        <div>
                            <span class="font-bold text-teal-300">Husbandry Principle: Pooled Batches (...Mix Tanks):</span>
                            <p class="text-slate-300 text-[11px] mt-0.5">Tanks tagged with <b>🔀 Mix</b> contain larvae pooled from multiple separate single-pair matings. Inter-breeding these cohorts maintains high heterozygosity and actively suppresses inbreeding depression ($F \\to 0$).</p>
                        </div>
                    </div>
                    <span class="px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-teal-400 font-mono text-[11px] shrink-0">
                        33 Pooled Cohorts Identified
                    </span>
                </div>

                <!-- ==================== SUB-VIEW 1: FOCUSED 3-GEN FAMILY TREE ==================== -->
                <div id="ped-subview-focal" class="ped-subview mt-4 space-y-4">
                    <!-- Focal Controls & Search -->
                    <div class="glass-card p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-3">
                        <div class="flex flex-wrap items-center gap-2">
                            <label class="text-xs font-semibold text-slate-300">Select Focal Tank:</label>
                            <select id="focalTankSelect" onchange="changeFocalTank(this.value)" class="bg-slate-800 text-sm px-3 py-1.5 rounded-lg border border-slate-700 text-teal-300 font-bold focus:outline-none focus:border-teal-500">
                                <!-- Populated dynamically -->
                            </select>
                            <input type="text" id="focalSearchInput" placeholder="Quick search (e.g. T0135)..." class="bg-slate-800 text-xs px-3 py-1.5 rounded-lg border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 w-44">
                            <button onclick="searchAndFocusTank()" class="px-3 py-1.5 bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold rounded-lg transition">Focus</button>
                        </div>

                        <!-- Breadcrumb Trail & Action Buttons -->
                        <div class="flex flex-wrap items-center gap-2">
                            <button onclick="copyLineageTrail()" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition flex items-center gap-1">
                                <span>📋 Copy Lineage Path</span>
                            </button>
                            <button onclick="printPedigreeCard()" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition flex items-center gap-1 shadow-sm">
                                <span>🖨️ Export Pedigree Card</span>
                            </button>
                        </div>
                    </div>

                    <!-- Lineage Breadcrumb Trail Bar -->
                    <div class="p-3 bg-slate-900/90 rounded-xl border border-slate-800 flex items-center justify-between gap-2 overflow-x-auto text-xs font-mono">
                        <div class="flex items-center gap-2 text-slate-300" id="focalBreadcrumbTrail">
                            <!-- Populated dynamically -->
                        </div>
                    </div>

                    <!-- 5-Column Visual Family Tree Grid -->
                    <div class="grid grid-cols-1 md:grid-cols-5 gap-3.5 min-h-[460px]">
                        <!-- Column 1: Grandparents -->
                        <div class="glass-card p-3 rounded-xl space-y-3">
                            <div class="border-b border-slate-700 pb-1.5 flex items-center justify-between">
                                <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">👴👵 Grandparents</span>
                                <span class="text-[10px] text-slate-500">Ancestors (2-gen)</span>
                            </div>
                            <div id="treeColGrandparents" class="space-y-2 text-xs">
                                <!-- Populated dynamically -->
                            </div>
                        </div>

                        <!-- Column 2: Parents -->
                        <div class="glass-card p-3 rounded-xl space-y-3">
                            <div class="border-b border-slate-700 pb-1.5 flex items-center justify-between">
                                <span class="text-xs font-bold text-sky-400 uppercase tracking-wider">👨👩 Parents</span>
                                <span class="text-[10px] text-slate-500">Direct Sire & Dam</span>
                            </div>
                            <div id="treeColParents" class="space-y-2 text-xs">
                                <!-- Populated dynamically -->
                            </div>
                        </div>

                        <!-- Column 3: Focal Tank (Hero Card) -->
                        <div class="glass-card p-3.5 rounded-xl space-y-3 border-2 border-teal-500/60 shadow-xl shadow-teal-950/40 bg-gradient-to-b from-slate-900 via-slate-900/90 to-teal-950/20">
                            <div class="border-b border-teal-500/40 pb-1.5 flex items-center justify-between">
                                <span class="text-xs font-bold text-teal-300 uppercase tracking-wider flex items-center gap-1">
                                    <span>🎯 Target Focus Tank</span>
                                </span>
                                <span id="focalHeroGenBadge" class="badge badge-optimal">F0 Founder</span>
                            </div>
                            <div id="treeColFocal" class="space-y-2">
                                <!-- Populated dynamically -->
                            </div>
                        </div>

                        <!-- Column 4: Direct Offspring (Children) -->
                        <div class="glass-card p-3 rounded-xl space-y-3">
                            <div class="border-b border-slate-700 pb-1.5 flex items-center justify-between">
                                <span class="text-xs font-bold text-emerald-400 uppercase tracking-wider">👶 Offspring (F1)</span>
                                <span id="treeOffspringCountBadge" class="text-[10px] text-emerald-400 font-bold">0 Tanks</span>
                            </div>
                            <div id="treeColOffspring" class="space-y-2 max-h-[460px] overflow-y-auto pr-1 text-xs">
                                <!-- Populated dynamically -->
                            </div>
                        </div>

                        <!-- Column 5: Grandchildren -->
                        <div class="glass-card p-3 rounded-xl space-y-3">
                            <div class="border-b border-slate-700 pb-1.5 flex items-center justify-between">
                                <span class="text-xs font-bold text-purple-400 uppercase tracking-wider">🌱 Grandchildren</span>
                                <span id="treeGrandchildrenCountBadge" class="text-[10px] text-purple-400 font-bold">0 Tanks</span>
                            </div>
                            <div id="treeColGrandchildren" class="space-y-2 max-h-[460px] overflow-y-auto pr-1 text-xs">
                                <!-- Populated dynamically -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ==================== SUB-VIEW 2: LINE-BY-LINE HIERARCHICAL TREES ==================== -->
                <div id="ped-subview-lines" class="ped-subview hidden mt-4 space-y-4">
                    <!-- Line Selector Tabs -->
                    <div class="flex flex-wrap items-center justify-between gap-3 bg-slate-900/80 p-3 rounded-xl border border-slate-700">
                        <div class="flex flex-wrap items-center gap-2">
                            <button onclick="selectLineTree('AB')" id="line-tree-btn-AB" class="line-tree-btn active px-3.5 py-1.5 rounded-lg text-xs font-bold bg-amber-500 text-slate-950 transition">
                                🟡 AB Lineage Tree (<span id="lineTreeCountAB">0</span>)
                            </button>
                            <button onclick="selectLineTree('Casper')" id="line-tree-btn-Casper" class="line-tree-btn px-3.5 py-1.5 rounded-lg text-xs font-bold text-sky-400 bg-slate-800 hover:bg-slate-700 transition">
                                🔵 Casper Lineage Tree (<span id="lineTreeCountCasper">0</span>)
                            </button>
                            <button onclick="selectLineTree('Fli')" id="line-tree-btn-Fli" class="line-tree-btn px-3.5 py-1.5 rounded-lg text-xs font-bold text-green-400 bg-slate-800 hover:bg-slate-700 transition">
                                🟢 Fli Lineage Tree (<span id="lineTreeCountFli">0</span>)
                            </button>
                            <button onclick="selectLineTree('Gata')" id="line-tree-btn-Gata" class="line-tree-btn px-3.5 py-1.5 rounded-lg text-xs font-bold text-pink-400 bg-slate-800 hover:bg-slate-700 transition">
                                🟣 Gata Lineage Tree (<span id="lineTreeCountGata">0</span>)
                            </button>
                        </div>
                        <div class="text-xs text-slate-400">
                            Showing generation depth from top founders downward.
                        </div>
                    </div>

                    <!-- Line Tiers Container -->
                    <div id="lineTreeTiersContainer" class="space-y-6">
                        <!-- Populated dynamically: Generation Tiers -->
                    </div>
                </div>

                <!-- ==================== SUB-VIEW 3: COLLAPSIBLE TREE TABLE ==================== -->
                <div id="ped-subview-table" class="ped-subview hidden mt-4 space-y-4">
                    <div class="glass-card p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-3">
                        <div class="flex flex-wrap items-center gap-2">
                            <input type="text" id="treeTableSearchInput" onkeyup="filterTreeTable()" placeholder="Search Tank, Line, Parents..." class="bg-slate-800 text-xs px-3 py-1.5 rounded-lg border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 w-56">
                            <select id="treeTableLineFilter" onchange="filterTreeTable()" class="bg-slate-800 text-xs px-3 py-1.5 rounded-lg border border-slate-700 text-slate-200">
                                <option value="ALL">All Lines</option>
                                <option value="AB">AB</option>
                                <option value="Casper">Casper</option>
                                <option value="Fli">Fli</option>
                                <option value="Gata">Gata</option>
                            </select>
                            <select id="treeTableStatusFilter" onchange="filterTreeTable()" class="bg-slate-800 text-xs px-3 py-1.5 rounded-lg border border-slate-700 text-slate-200">
                                <option value="ALL">All Statuses</option>
                                <option value="ACTIVE">Adult / Active Only</option>
                                <option value="EUTH">Euthanized Only</option>
                            </select>
                        </div>

                        <div class="flex items-center gap-2">
                            <button onclick="expandAllTreeRows()" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-lg border border-slate-700 transition">Expand All</button>
                            <button onclick="collapseAllTreeRows()" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-lg border border-slate-700 transition">Collapse All</button>
                            <button onclick="exportTreeTableCSV()" class="px-3 py-1.5 bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold rounded-lg transition flex items-center gap-1">
                                <span>📥 Export CSV</span>
                            </button>
                        </div>
                    </div>

                    <div class="table-container max-h-[550px] overflow-y-auto">
                        <table class="w-full text-left text-xs" id="pedigreeTreeTable">
                            <thead class="bg-slate-900/90 text-slate-400 sticky top-0 uppercase tracking-wider text-[11px] border-b border-slate-700">
                                <tr>
                                    <th class="p-3">Tank ID & Line</th>
                                    <th class="p-3">Generation</th>
                                    <th class="p-3">Status</th>
                                    <th class="p-3">Fish (F/M/Total)</th>
                                    <th class="p-3">Inbreeding (F)</th>
                                    <th class="p-3">Genetic Category / Mix Pool</th>
                                    <th class="p-3">Sire × Dam</th>
                                    <th class="p-3">Progeny</th>
                                    <th class="p-3 text-center">Action</th>
                                </tr>
                            </thead>
                            <tbody id="pedigreeTreeTableBody" class="divide-y divide-slate-800 text-slate-200">
                                <!-- Populated dynamically -->
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- ==================== SUB-VIEW 4: GLOBAL NETWORK MAP (VIS.JS) ==================== -->
                <div id="ped-subview-network" class="ped-subview hidden mt-4 space-y-4">
                    <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-700">
                        <div class="flex flex-wrap items-center gap-2">
                            <div class="relative">
                                <input type="text" id="pedigreeSearch" placeholder="Search Tank (e.g. T0135)..." 
                                    class="bg-slate-800 text-sm px-3 py-1.5 rounded-lg border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-teal-500">
                                <button onclick="searchPedigreeNode()" class="px-3 py-1.5 bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold rounded-lg transition ml-1">Locate</button>
                            </div>

                            <select id="lineFilter" onchange="filterPedigreeByLine()" class="bg-slate-800 text-sm px-3 py-1.5 rounded-lg border border-slate-700 text-slate-200 focus:outline-none focus:border-teal-500">
                                <option value="ALL">All 4 Lines</option>
                                <option value="AB">AB Lineage</option>
                                <option value="Casper">Casper Lineage</option>
                                <option value="Fli">Fli Lineage</option>
                                <option value="Gata">Gata Lineage</option>
                            </select>

                            <button onclick="resetPedigreeView()" class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-medium rounded-lg transition">Reset View</button>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
                        <!-- Network Canvas -->
                        <div class="lg:col-span-3">
                            <div id="pedigree-network"></div>
                            <div class="flex flex-wrap items-center gap-4 mt-2 text-xs text-slate-400">
                                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-amber-400 inline-block"></span> <b>AB</b></span>
                                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-sky-400 inline-block"></span> <b>Casper</b></span>
                                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-green-400 inline-block"></span> <b>Fli</b></span>
                                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-pink-400 inline-block"></span> <b>Gata</b></span>
                                <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-slate-500 inline-block"></span> <b>Euthanized/Archived</b></span>
                                <span class="flex items-center gap-1.5"><span class="w-4 h-0.5 bg-blue-500 inline-block"></span> Paternal (Sire)</span>
                                <span class="flex items-center gap-1.5"><span class="w-4 h-0.5 border-t border-dashed border-pink-500 inline-block"></span> Maternal (Dam)</span>
                            </div>
                        </div>

                        <!-- Node Inspector Card -->
                        <div class="glass-card p-4 rounded-xl space-y-4">
                            <div class="border-b border-slate-700 pb-2">
                                <span id="inspectStatus" class="badge badge-optimal">Active Tank</span>
                                <h3 id="inspectTUID" class="text-2xl font-black text-teal-400 mt-1">Select a Tank</h3>
                                <p id="inspectLine" class="text-xs font-semibold text-slate-300">Click any tank node to inspect</p>
                            </div>

                            <div class="space-y-2 text-xs">
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Status:</span>
                                    <span id="inspectStatusCol" class="font-bold text-slate-200">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Genotype / Notes:</span>
                                    <span id="inspectNotes" class="font-medium text-slate-200 text-right max-w-[160px]">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Genetic Category:</span>
                                    <span id="inspectGeneticType" class="font-semibold text-teal-300 text-right max-w-[160px]">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">DOB:</span>
                                    <span id="inspectDOB" class="font-medium text-slate-200">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Turnover Date:</span>
                                    <span id="inspectTurnover" class="font-medium text-slate-200">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Fish Count:</span>
                                    <span id="inspectCounts" class="font-bold text-teal-300">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Inbreeding (F):</span>
                                    <span id="inspectInbreeding" class="font-bold text-amber-400">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Parents (Sire x Dam):</span>
                                    <span id="inspectParents" class="font-semibold text-sky-400">-</span>
                                </div>
                                <div class="flex justify-between py-1 border-b border-slate-800">
                                    <span class="text-slate-400">Cross ID:</span>
                                    <span id="inspectCross" class="font-semibold text-purple-400">-</span>
                                </div>
                            </div>

                            <!-- Action Buttons -->
                            <div class="space-y-2 pt-2">
                                <button onclick="highlightAncestors()" class="w-full py-2 bg-blue-600/80 hover:bg-blue-600 text-white rounded-lg text-xs font-semibold transition flex items-center justify-center gap-1.5">
                                    ⬆️ Trace Ancestors (Parents & Grandparents)
                                </button>
                                <button onclick="highlightDescendants()" class="w-full py-2 bg-purple-600/80 hover:bg-purple-600 text-white rounded-lg text-xs font-semibold transition flex items-center justify-center gap-1.5">
                                    ⬇️ Trace Progeny & Descendants
                                </button>
                                <button onclick="clearHighlights()" class="w-full py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white rounded-lg text-xs transition">
                                    Clear Highlight
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>"""

# Replace the old section
content = re.sub(r'<!-- ==================== TAB 2: PEDIGREE EXPLORER ==================== -->[\s\S]*?<!-- ==================== TAB 3: TURNOVER ACTION PLAN ==================== -->', new_pedigree_section + "\n\n        <!-- ==================== TAB 3: TURNOVER ACTION PLAN ==================== -->", content)

with open('build_fishnet_analytics.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated HTML structure in build_fishnet_analytics.py.")
