import json
import csv
import os
import re

def generate_dashboard():
    labels_dir = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels'
    json_path = os.path.join(labels_dir, 'breeding_dashboard_data.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        full_data = json.load(f)

    data_json_str = json.dumps(full_data)



    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FishNET Reproductive & Colony Intelligence Dashboard (2024-2026)</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #0f172a;
            --bg-card: #1e293b;
            --bg-card-hover: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-blue: #38bdf8;
            --accent-indigo: #818cf8;
            --accent-emerald: #34d399;
            --accent-amber: #fbbf24;
            --accent-rose: #fb7185;
            --accent-purple: #c084fc;
            --border-color: #334155;
            --radius-lg: 16px;
            --radius-md: 10px;
            --radius-sm: 6px;
            --shadow-card: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        body {
            background-color: var(--bg-main);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }
        
        /* Header */
        header {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 24px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: var(--shadow-card);
            flex-wrap: wrap;
            gap: 16px;
        }
        
        .header-title {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        
        .header-title h1 {
            font-size: 26px;
            font-weight: 800;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .header-title p {
            color: var(--text-secondary);
            font-size: 14px;
        }
        
        .header-controls {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .btn {
            background: #2563eb;
            color: white;
            padding: 9px 16px;
            border-radius: var(--radius-sm);
            border: none;
            cursor: pointer;
            font-weight: 600;
            font-size: 13px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
        }
        
        .btn:hover {
            background: #1d4ed8;
            transform: translateY(-1px);
        }
        
        .btn-sm {
            padding: 6px 12px;
            font-size: 12px;
        }
        
        .btn-outline {
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-primary);
        }
        
        .btn-outline:hover {
            background: var(--bg-card-hover);
            border-color: var(--accent-blue);
        }
        
        .btn-emerald {
            background: rgba(52, 211, 153, 0.2);
            color: #34d399;
            border: 1px solid rgba(52, 211, 153, 0.4);
        }
        .btn-emerald:hover {
            background: rgba(52, 211, 153, 0.35);
        }
        
        /* Stats Grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
        }
        
        .kpi-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-card);
        }
        
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent-blue);
        }
        
        .kpi-card.kpi-emerald::before { background: var(--accent-emerald); }
        .kpi-card.kpi-indigo::before { background: var(--accent-indigo); }
        .kpi-card.kpi-amber::before { background: var(--accent-amber); }
        .kpi-card.kpi-rose::before { background: var(--accent-rose); }
        .kpi-card.kpi-purple::before { background: var(--accent-purple); }
        
        .kpi-label {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
        }
        
        .kpi-value {
            font-size: 28px;
            font-weight: 800;
            color: var(--text-primary);
        }
        
        .kpi-subtext {
            font-size: 12px;
            color: var(--text-muted);
        }
        
        /* Navigation Tabs */
        .tabs-container {
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 4px;
            overflow-x: auto;
        }
        
        .tab-btn {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 12px 18px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            font-size: 13.5px;
            font-weight: 600;
            transition: all 0.2s ease;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .tab-btn:hover {
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.05);
        }
        
        .tab-btn.active {
            color: var(--accent-blue);
            background: rgba(56, 189, 248, 0.1);
            border-bottom: 2px solid var(--accent-blue);
        }
        
        /* Tab Content */
        .tab-content {
            display: none;
            flex-direction: column;
            gap: 20px;
        }
        
        .tab-content.active {
            display: flex;
        }
        
        /* Section Cards */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-card);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 12px;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: 700;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .card-header-actions {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Filters Bar */
        .filter-bar {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
            background: rgba(15, 23, 42, 0.6);
            padding: 10px 14px;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
        }
        
        .filter-group {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .filter-label {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
        }
        
        select, input[type="text"], input[type="number"] {
            background: #0f172a;
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 7px 12px;
            border-radius: var(--radius-sm);
            font-size: 12.5px;
            outline: none;
        }
        
        select:focus, input[type="text"]:focus, input[type="number"]:focus {
            border-color: var(--accent-blue);
        }
        
        /* Grids for charts */
        .chart-grid-2 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 20px;
        }
        
        .chart-box {
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 18px;
            min-height: 350px;
            display: flex;
            flex-direction: column;
        }
        
        .chart-box-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }
        
        .chart-box-title {
            font-size: 13.5px;
            font-weight: 600;
            color: var(--text-secondary);
        }
        
        .chart-canvas-wrapper {
            flex: 1;
            position: relative;
            min-height: 270px;
        }
        
        /* Tables */
        .table-responsive {
            overflow-x: auto;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 13px;
        }
        
        th {
            background: #0f172a;
            color: var(--text-secondary);
            font-weight: 600;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }
        
        td {
            padding: 11px 16px;
            border-bottom: 1px solid rgba(51, 65, 85, 0.4);
            color: var(--text-primary);
            white-space: nowrap;
        }
        
        tr:hover td {
            background: rgba(255, 255, 255, 0.02);
        }
        
        /* Badges */
        .badge {
            padding: 3px 9px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            display: inline-block;
        }
        
        .badge-active { background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); }
        .badge-euthanized { background: rgba(251, 113, 133, 0.15); color: #fb7185; border: 1px solid rgba(251, 113, 133, 0.3); }
        
        .badge-ab { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
        .badge-casper { background: rgba(192, 132, 252, 0.15); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3); }
        .badge-fli { background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); }
        .badge-gata { background: rgba(251, 191, 36, 0.15); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }
        
        .badge-female { background: rgba(244, 114, 182, 0.15); color: #f472b6; border: 1px solid rgba(244, 114, 182, 0.3); }
        .badge-male { background: rgba(96, 165, 250, 0.15); color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.3); }
        .badge-mixed { background: rgba(167, 139, 250, 0.15); color: #a78bfa; border: 1px solid rgba(167, 139, 250, 0.3); }
        
        /* Planner Box */
        .planner-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid var(--accent-indigo);
            border-radius: var(--radius-lg);
            padding: 24px;
        }
        
        .planner-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
            margin-top: 16px;
        }
        
        .recommendation-box {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid var(--accent-emerald);
            border-radius: var(--radius-md);
            padding: 20px;
        }
        
        /* Modal */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            padding: 20px;
        }
        
        .modal-box {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            width: 100%;
            max-width: 900px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
        }
        
        .modal-header {
            padding: 20px 24px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .modal-body {
            padding: 24px;
            overflow-y: auto;
        }
        
        .close-btn {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 20px;
            cursor: pointer;
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="header-title">
            <h1>🐟 FishNET Reproductive & Colony Intelligence System</h1>
            <p>Integrated Database: 2024–2026 Breeding Records, Single-Sex Reservoirs & Pedigree Architecture</p>
        </div>
        <div class="header-controls">
            <input type="file" id="fileUploadInput" accept=".tab,.tsv,.csv,.xlsx" style="display: none;" onchange="handleFileUpload(event)">
            <button class="btn btn-outline" onclick="document.getElementById('fileUploadInput').click()">📁 Upload Updated File</button>
            <button class="btn btn-outline" onclick="exportBreedingJSON()">💾 Export JSON</button>
            <button class="btn btn-emerald" onclick="exportBreedingCSV()">📥 Export Master 2024-2026 CSV</button>
        </div>
    </header>

    <!-- Global KPIs -->
    <div class="kpi-grid">
        <div class="kpi-card kpi-blue">
            <span class="kpi-label">Total Tanks</span>
            <span class="kpi-value" id="kpiTotalTanks">183</span>
            <span class="kpi-subtext" id="kpiTankStatusSub">117 Active | 63 Euthanized | 3 Larvae</span>
        </div>
        <div class="kpi-card kpi-emerald">
            <span class="kpi-label">Breeding Events</span>
            <span class="kpi-value" id="kpiTotalEvents">2,233</span>
            <span class="kpi-subtext">2024: 460 | 2025: 1,229 | 2026: 544</span>
        </div>
        <div class="kpi-card kpi-amber">
            <span class="kpi-label">Lifetime Eggs Spawned</span>
            <span class="kpi-value" id="kpiTotalEggs">1,252,045</span>
            <span class="kpi-subtext">Avg 560.7 eggs / spawn</span>
        </div>
        <div class="kpi-card kpi-indigo">
            <span class="kpi-label">Viable Embryos (24hpf)</span>
            <span class="kpi-value" id="kpiLive24h">971,919</span>
            <span class="kpi-subtext">77.6% Global Colony Viability</span>
        </div>
        <div class="kpi-card kpi-rose">
            <span class="kpi-label">Single-Sex Reservoirs</span>
            <span class="kpi-value">41 Tanks</span>
            <span class="kpi-subtext">21 ♀ Female-Only | 20 ♂ Male-Only</span>
        </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs-container">
        <button class="tab-btn active" onclick="switchTab('tab-benchmarks')">📊 4-Line Benchmarks</button>
        <button class="tab-btn" onclick="switchTab('tab-crosses')">🧬 Cross-Pairing Synergies (Sire x Dam)</button>
        <button class="tab-btn" onclick="switchTab('tab-trends')">📈 Longitudinal Trends (2024-2026)</button>
        <button class="tab-btn" onclick="switchTab('tab-age-curves')">🔬 Parental Age vs. Fecundity</button>
        <button class="tab-btn" onclick="switchTab('tab-scorecards')">🏆 Breeder Tank Scorecards</button>
        <button class="tab-btn" onclick="switchTab('tab-inventory')">🐠 FishNET Inventory & Sex Structure</button>
        <button class="tab-btn" onclick="switchTab('tab-audit')">🔍 Data Quality & Sex Consistency Audit</button>
        <button class="tab-btn" onclick="switchTab('tab-planner')">🎯 Intelligent Mating Planner</button>
        <button class="tab-btn" onclick="switchTab('tab-raw-events')">📋 Master Breeding Log (2,233 Events)</button>
    </div>

    <!-- TAB 1: 4-Line Benchmarks -->
    <div id="tab-benchmarks" class="tab-content active">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">🔬 Primary Lines Reproductive Performance (AB, Casper, Fli, Gata)</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Empirical Data from 2,233 Spawning Runs across 3 Years</span>
                </div>
                <div class="card-header-actions">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('lineBenchmarkTable', '4_line_reproductive_benchmarks')">📥 Export Table (CSV)</button>
                </div>
            </div>
            <div class="chart-grid-2">
                <div class="chart-box">
                    <div class="chart-box-header">
                        <span class="chart-box-title">Average Clutch Size (Eggs per Spawning Event)</span>
                        <button class="btn btn-sm btn-outline" onclick="exportChartAsPNG('chartLineClutch', 'avg_clutch_size_by_line')">📷 PNG</button>
                    </div>
                    <div class="chart-canvas-wrapper">
                        <canvas id="chartLineClutch"></canvas>
                    </div>
                </div>
                <div class="chart-box">
                    <div class="chart-box-header">
                        <span class="chart-box-title">Fertilization (0hpf) vs. Embryo Viability (24hpf) Survival Rate %</span>
                        <button class="btn btn-sm btn-outline" onclick="exportChartAsPNG('chartLineSurvival', 'line_survival_rates_0h_24h')">📷 PNG</button>
                    </div>
                    <div class="chart-canvas-wrapper">
                        <canvas id="chartLineSurvival"></canvas>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 24px;">
                <div class="table-responsive">
                    <table id="lineBenchmarkTable">
                        <thead>
                            <tr>
                                <th>Line</th>
                                <th>Active Tanks</th>
                                <th>Total Spawns</th>
                                <th>Total Eggs (0H)</th>
                                <th>Avg Clutch Size</th>
                                <th>0hpf SR (%)</th>
                                <th>24hpf Viability (%)</th>
                                <th>Viable Embryos (24H)</th>
                                <th>In-Tank Spawn Share</th>
                            </tr>
                        </thead>
                        <tbody id="lineBenchmarkTableBody">
                            <!-- Populated by JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 2: Cross-Pairing Synergies -->
    <div id="tab-crosses" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">🧬 Proven Parental Cross Combinations (Female Dam x Male Sire Matrix)</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Empirical performance of single-sex reservoir crosses and pair-wise matings</span>
                </div>
                <div class="card-header-actions">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('pairSynergyTable', 'cross_pairing_synergies_matrix')">📥 Export Table (CSV)</button>
                </div>
            </div>
            <div class="table-responsive">
                <table id="pairSynergyTable">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Parental Cross (Tank A x Tank B)</th>
                            <th>Line</th>
                            <th>Breeding Attempts</th>
                            <th>Total Eggs Spawned</th>
                            <th>Avg Clutch Size</th>
                            <th>24hpf Viability SR (%)</th>
                            <th>Total Viable (24hpf)</th>
                        </tr>
                    </thead>
                    <tbody id="pairSynergyTableBody">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 3: Longitudinal Trends -->
    <div id="tab-trends" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">📈 Facility Production Dynamics (2024 - 2026 Monthly Progression)</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Monthly clutch outputs and embryo survival stability</span>
                </div>
            </div>
            <div class="chart-grid-2">
                <div class="chart-box">
                    <div class="chart-box-header">
                        <span class="chart-box-title">Monthly Embryo Output & Spawning Volume</span>
                        <button class="btn btn-sm btn-outline" onclick="exportChartAsPNG('chartMonthlyEggs', 'monthly_embryo_spawning_output')">📷 PNG</button>
                    </div>
                    <div class="chart-canvas-wrapper">
                        <canvas id="chartMonthlyEggs"></canvas>
                    </div>
                </div>
                <div class="chart-box">
                    <div class="chart-box-header">
                        <span class="chart-box-title">Monthly 24hpf Survival Rate (%) Stability</span>
                        <button class="btn btn-sm btn-outline" onclick="exportChartAsPNG('chartMonthlySR', 'monthly_survival_rate_stability')">📷 PNG</button>
                    </div>
                    <div class="chart-canvas-wrapper">
                        <canvas id="chartMonthlySR"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 4: Parental Age vs Fecundity Curves -->
    <div id="tab-age-curves" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">⏳ Age-Dependent Fecundity & Reproductive Senescence</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Parental Age (Months) mapped to Clutch Size & Embryo Viability</span>
                </div>
            </div>
            <div class="chart-grid-2">
                <div class="chart-box">
                    <div class="chart-box-header">
                        <span class="chart-box-title">Parental Age (Months) vs. Clutch Size (Eggs/Spawn)</span>
                        <button class="btn btn-sm btn-outline" onclick="exportChartAsPNG('chartAgeFecundity', 'age_vs_clutch_size_senescence')">📷 PNG</button>
                    </div>
                    <div class="chart-canvas-wrapper">
                        <canvas id="chartAgeFecundity"></canvas>
                    </div>
                </div>
                <div class="chart-box">
                    <div class="chart-box-header">
                        <span class="chart-box-title">Parental Age (Months) vs. 24hpf Viability Rate (%)</span>
                        <button class="btn btn-sm btn-outline" onclick="exportChartAsPNG('chartAgeViability', 'age_vs_24hpf_viability_senescence')">📷 PNG</button>
                    </div>
                    <div class="chart-canvas-wrapper">
                        <canvas id="chartAgeViability"></canvas>
                    </div>
                </div>
            </div>
            <div style="margin-top: 20px; background: rgba(15, 23, 42, 0.5); padding: 16px; border-radius: var(--radius-md); border-left: 4px solid var(--accent-blue);">
                <h4 style="font-size: 14px; margin-bottom: 6px; color: var(--accent-blue);">💡 Biological Insights & Senescence Thresholds</h4>
                <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">
                    • <strong>Prime Reproductive Window:</strong> 6 to 14 months of age exhibits maximum clutch size (600–1,200 eggs) and highest 24hpf viability (>85%).<br>
                    • <strong>Single-Sex Separation Benefit:</strong> Keeping males and females separated in dedicated reservoir tanks (e.g. T0099, T0130) prevents continuous uncontrolled egg drop and maintains high clutch yields when paired for scheduled experiments.<br>
                    • <strong>Late Senescence (>18 months):</strong> Fecundity drops by ~40% and 24hpf survival rate declines, highlighting the necessity of regular G1/G2 line turnovers.
                </p>
            </div>
        </div>
    </div>

    <!-- TAB 5: Breeder Scorecards -->
    <div id="tab-scorecards" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">🏆 Tank Breeder Performance Scorecards & Ranking</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Lifetime metrics and rankings for individual tanks</span>
                </div>
                <div class="card-header-actions">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('scorecardTable', 'tank_breeder_performance_scorecards')">📥 Export Table (CSV)</button>
                </div>
            </div>
            <div class="filter-bar" style="margin-bottom: 16px;">
                <div class="filter-group">
                    <span class="filter-label">Line:</span>
                    <select id="scorecardLineFilter" onchange="renderScorecards()">
                        <option value="ALL">All Lines</option>
                        <option value="AB">AB</option>
                        <option value="Casper">Casper</option>
                        <option value="Fli">Fli</option>
                        <option value="Gata">Gata</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Sex:</span>
                    <select id="scorecardSexFilter" onchange="renderScorecards()">
                        <option value="ALL">All Sex Types</option>
                        <option value="Female-Only">♀ Female-Only</option>
                        <option value="Male-Only">♂ Male-Only</option>
                        <option value="Mixed Colony">⚤ Mixed Colony</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Status:</span>
                    <select id="scorecardStatusFilter" onchange="renderScorecards()">
                        <option value="ALL">All Statuses</option>
                        <option value="Active" selected>Active Only</option>
                        <option value="Euthanized">Euthanized Only</option>
                    </select>
                </div>
                <div class="filter-group">
                    <input type="text" id="scorecardSearch" placeholder="Search Tank (e.g. T0086)..." oninput="renderScorecards()">
                </div>
            </div>
            
            <div class="table-responsive">
                <table id="scorecardTable">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Tank ID</th>
                            <th>Line</th>
                            <th>Sex Structure</th>
                            <th>Status</th>
                            <th>Adults (F/M/Tot)</th>
                            <th>Total Spawns</th>
                            <th>Total Eggs (0H)</th>
                            <th>Avg Clutch</th>
                            <th>24hpf Viability</th>
                            <th>24H Viable Embryos</th>
                            <th>Last Spawned</th>
                            <th class="no-export">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="scorecardTableBody">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 6: Inventory & Sex Structure -->
    <div id="tab-inventory" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">🐠 FishNET Tank Inventory & Sex Structure Explorer</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Live population inventory and sex classification</span>
                </div>
                <div class="card-header-actions">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('inventoryTable', 'fishnet_tank_inventory_sex_structure')">📥 Export Table (CSV)</button>
                </div>
            </div>
            <div class="filter-bar" style="margin-bottom: 16px;">
                <div class="filter-group">
                    <span class="filter-label">Line:</span>
                    <select id="invLineFilter" onchange="renderInventory()">
                        <option value="ALL">All Lines</option>
                        <option value="AB">AB</option>
                        <option value="Casper">Casper</option>
                        <option value="Fli">Fli</option>
            <div class="filter-bar" style="margin-bottom: 16px;">
                <div class="filter-group">
                    <span class="filter-label">Line:</span>
                    <select id="invLineFilter" onchange="renderInventory()">
                        <option value="ALL">All Lines (183 Tanks)</option>
                        <option value="AB">AB (75)</option>
                        <option value="Casper">Casper (45)</option>
                        <option value="Fli">Fli (29)</option>
                        <option value="Gata">Gata (21)</option>
                        <option value="DESMA">DESMA (9)</option>
                        <option value="Other">Other (4)</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Sex Structure:</span>
                    <select id="invSexFilter" onchange="renderInventory()">
                        <option value="ALL">All Configurations</option>
                        <option value="Female-Only">♀ Female-Only (21)</option>
                        <option value="Male-Only">♂ Male-Only (20)</option>
                        <option value="Mixed Colony">⚤ Mixed Colony (111)</option>
                        <option value="Unsexed / Juvenile">Unsexed / Juvenile (31)</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Status:</span>
                    <select id="invStatusFilter" onchange="renderInventory()">
                        <option value="ALL">All Statuses (183)</option>
                        <option value="Active" selected>Active / Adult (117)</option>
                        <option value="Euthanized">Euthanized (63)</option>
                        <option value="Larvae">Larvae (&lt;2 weeks) (3)</option>
                    </select>
                </div>
                <div class="filter-group">
                    <input type="text" id="invSearch" placeholder="Search TUID, Cross, Genotype, Notes..." oninput="renderInventory()">
                </div>
            </div>
            <div class="table-responsive">
                <table id="inventoryTable">
                    <thead>
                        <tr>
                            <th>TUID</th>
                            <th>Derivative Cross</th>
                            <th>Genotype</th>
                            <th>Notes</th>
                            <th>Line</th>
                            <th>Sex Composition</th>
                            <th>Female</th>
                            <th>Male</th>
                            <th>Total Fish</th>
                            <th>Tank Size</th>
                            <th>Protocol</th>
                            <th>DOB</th>
                            <th>Turnover Date</th>
                            <th>Age (Mo)</th>
                            <th>Status</th>
                            <th>Lifetime Spawns</th>
                            <th>Lifetime Eggs</th>
                            <th class="no-export">Details</th>
                        </tr>
                    </thead>
                    <tbody id="inventoryTableBody">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 7: Data Audit & Sex Consistency -->
    <div id="tab-audit" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">🔍 Data Quality, Single-Sex Reservoirs & Population Audit</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Cross-validation between FishNET inventory and physical breeding sheets</span>
                </div>
                <div class="card-header-actions">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('auditReservoirTable', 'single_sex_reservoirs_audit')">📥 Export Reservoirs (CSV)</button>
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('auditDiscrepancyTable', 'discrepancies_and_corrections_log')">📥 Export Discrepancies (CSV)</button>
                </div>
            </div>

            <h4 style="font-size: 14px; margin-bottom: 12px; color: var(--accent-blue);">1. Single-Sex Reservoir Tanks (40 Tanks: 20 Female-Only, 20 Male-Only)</h4>
            <div class="table-responsive" style="margin-bottom: 24px;">
                <table id="auditReservoirTable">
                    <thead>
                        <tr>
                            <th>Tank ID</th>
                            <th>Line</th>
                            <th>Sex Structure</th>
                            <th>Adult Counts</th>
                            <th>Status</th>
                            <th>Notes</th>
                            <th>Primary Cross Partners</th>
                            <th>Total Lifetime Spawns</th>
                            <th>Total Eggs Spawned</th>
                        </tr>
                    </thead>
                    <tbody id="auditReservoirTableBody">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>

            <h4 style="font-size: 14px; margin-bottom: 12px; color: var(--accent-amber);">2. Population Discrepancy & Handwriting Resolution Log</h4>
            <div class="table-responsive">
                <table id="auditDiscrepancyTable">
                    <thead>
                        <tr>
                            <th>Date / Scope</th>
                            <th>Logged String</th>
                            <th>Detected Conflict</th>
                            <th>Scientific & Physical Resolution</th>
                            <th>Verification Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>2026-07-04</strong></td>
                            <td><code>Casp T144,F,1 T77,M,1</code></td>
                            <td>FishNET T0144 is an AB (Males-Only) tank. Cannot be a Casper female.</td>
                            <td>Corrected handwriting ambiguity to <strong>Casper T0114 (F) x T0077 (M)</strong>.</td>
                            <td><span class="badge badge-active">Resolved</span></td>
                        </tr>
                        <tr>
                            <td><strong>2026-07-20</strong></td>
                            <td><code>Fli T83 intank (624 eggs)</code></td>
                            <td>FishNET T0083 is an AB (Males-Only) tank. A male tank cannot lay eggs alone.</td>
                            <td>Corrected tank ID typo to <strong>Fli T0082</strong> (active mixed colony tank with 4F/3M).</td>
                            <td><span class="badge badge-active">Resolved</span></td>
                        </tr>
                        <tr>
                            <td><strong>2026-06-23</strong></td>
                            <td><code>Gata T49(F) x ABT93(M) (1,970 eggs)</code></td>
                            <td>FishNET registered T0049 as Male-Only (5M, 0F). Yet females were physically spawned.</td>
                            <td>Flagged database registration error in FishNET; females were verified physically in log.</td>
                            <td><span class="badge badge-gata">Flagged</span></td>
                        </tr>
                        <tr>
                            <td><strong>Multi-Date (2026)</strong></td>
                            <td><code>ABT106xABT93, ABT76xABT130, ABT95xABT130</code></td>
                            <td>Lack of space before 'T' caused basic regex to miss female reservoir tanks.</td>
                            <td>Enhanced regex parser now correctly extracts and links both Dam (F) and Sire (M).</td>
                            <td><span class="badge badge-active">Resolved</span></td>
                        </tr>
                        <tr>
                            <td><strong>2026-04-23</strong></td>
                            <td><code>A13 T93xABT95</code></td>
                            <td>OCR artifact ('A13' instead of 'AB').</td>
                            <td>Normalized to <strong>AB T0093 (M) x AB T0095 (F)</strong>.</td>
                            <td><span class="badge badge-active">Resolved</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <h4 style="font-size: 14px; margin-top: 24px; margin-bottom: 12px; color: var(--accent-emerald);">3. Tri-Database Validation Audit (Tanks &harr; Crosses &harr; Nursery Reconciliation)</h4>
            <div class="table-responsive">
                <table id="auditDobCrossTable">
                    <thead>
                        <tr>
                            <th>Tank ID</th>
                            <th>Line</th>
                            <th>Raw DOB</th>
                            <th>Derivative Cross</th>
                            <th>Linked Nursery (NUID)</th>
                            <th>Cross &amp; Nursery Mating Date</th>
                            <th>Validated Biological DOB</th>
                            <th>Spawning History</th>
                            <th>Original vs. Resolved Status</th>
                            <th>Biological Rationale &amp; 3-Way Reconciliation</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>T0122</strong></td>
                            <td><span class="badge badge-casper">Casper</span></td>
                            <td><code>02-11-26</code></td>
                            <td><code style="color: var(--accent-indigo);">C0045</code></td>
                            <td><span class="badge" style="background: rgba(192,132,252,0.2); color: #c084fc;">N0042</span> (3 fish)</td>
                            <td><code>11-02-2026</code></td>
                            <td><strong>11-02-2026</strong></td>
                            <td>6 Spawns (Jun–Jul 2026)</td>
                            <td><span class="badge badge-casper">Larvae</span> &rarr; <span class="badge badge-active">Active Adult</span></td>
                            <td>Raw DOB (02-11-26) was US MM-DD-YY. 100% matched to Cross C0045 &amp; Nursery N0042 (11 Feb 2026). Fish actively spawned at 4–5 months; graduated to Active.</td>
                        </tr>
                        <tr>
                            <td><strong>T0124</strong></td>
                            <td><span class="badge badge-casper">Casper</span></td>
                            <td><code>02-12-26</code></td>
                            <td><code style="color: var(--accent-indigo);">C0047</code></td>
                            <td><span class="badge" style="background: rgba(192,132,252,0.2); color: #c084fc;">N0044</span> (2 fish)</td>
                            <td><code>03-05-2026</code></td>
                            <td><strong>03-05-2026</strong></td>
                            <td>6 Spawns (Jun–Jul 2026)</td>
                            <td><span class="badge badge-casper">Larvae</span> &rarr; <span class="badge badge-active">Active Adult</span></td>
                            <td>Grounded to Cross C0047 &amp; Nursery N0044 (3 May 2026). Reached maturity and spawned in June/July 2026; graduated to Active.</td>
                        </tr>
                        <tr>
                            <td><strong>T0125</strong></td>
                            <td><span class="badge badge-casper">Casper</span></td>
                            <td><code>02-11-26</code></td>
                            <td><code style="color: var(--accent-indigo);">C0048</code></td>
                            <td><span class="badge" style="background: rgba(192,132,252,0.2); color: #c084fc;">N0045</span> (18 fish)</td>
                            <td><code>11-02-2026</code></td>
                            <td><strong>11-02-2026</strong></td>
                            <td>2 Spawns (Jun–Jul 2026)</td>
                            <td><span class="badge badge-casper">Larvae</span> &rarr; <span class="badge badge-active">Active Adult</span></td>
                            <td>Raw DOB (02-11-26) was US MM-DD-YY. Grounded to Cross C0048 &amp; Nursery N0045 (11 Feb 2026). Actively spawned; graduated to Active.</td>
                        </tr>
                        <tr>
                            <td><strong>T0126</strong></td>
                            <td><span class="badge badge-casper">Casper</span></td>
                            <td><code>02-11-26</code></td>
                            <td><code style="color: var(--accent-indigo);">C0049</code></td>
                            <td><span class="badge" style="background: rgba(192,132,252,0.2); color: #c084fc;">N0046</span> (15 fish)</td>
                            <td><code>11-02-2026</code></td>
                            <td><strong>11-02-2026</strong></td>
                            <td>2 Spawns (Jun–Jul 2026)</td>
                            <td><span class="badge badge-casper">Larvae</span> &rarr; <span class="badge badge-active">Active Adult</span></td>
                            <td>Raw DOB (02-11-26) was US MM-DD-YY. Grounded to Cross C0049 &amp; Nursery N0046 (11 Feb 2026). Actively spawned; graduated to Active.</td>
                        </tr>
                        <tr>
                            <td><strong>T0131</strong></td>
                            <td><span class="badge badge-casper">Casper</span></td>
                            <td><code>02-11-26</code></td>
                            <td><code style="color: var(--accent-indigo);">C0051</code></td>
                            <td><span class="badge" style="background: rgba(192,132,252,0.2); color: #c084fc;">N0048</span> (10 fish)</td>
                            <td><code>11-02-2026</code></td>
                            <td><strong>11-02-2026</strong></td>
                            <td>2 Spawns (Jun–Jul 2026)</td>
                            <td><span class="badge badge-casper">Larvae</span> &rarr; <span class="badge badge-active">Active Adult</span></td>
                            <td>Raw DOB (02-11-26) was US MM-DD-YY. Grounded to Cross C0051 &amp; Nursery N0048 (11 Feb 2026). Actively spawned; graduated to Active.</td>
                        </tr>
                        <tr>
                            <td><strong>T0166 / T0167</strong></td>
                            <td><span class="badge badge-ab">AB</span></td>
                            <td><code>05-12-26</code></td>
                            <td><code style="color: var(--accent-indigo);">C0065</code></td>
                            <td><span class="badge" style="background: rgba(192,132,252,0.2); color: #c084fc;">N0062</span> (32 fish total)</td>
                            <td><code>12-May-26</code></td>
                            <td><strong>12-05-2026</strong></td>
                            <td>0 Spawns (Holdings)</td>
                            <td><span class="badge badge-casper">Larvae</span> &rarr; <span class="badge badge-active">Active Adult</span></td>
                            <td>Raw DOB (05-12-26) was US MM-DD-YY. Grounded to Cross C0065 &amp; Nursery N0062 (12 May 2026). 32 fish split across T0166 (16) and T0167 (16); fish are ~5 months old.</td>
                        </tr>
                        <tr>
                            <td><strong>T0168–T0170</strong></td>
                            <td><span class="badge badge-ab">AB</span></td>
                            <td><code>05-12-26</code></td>
                            <td><code style="color: var(--accent-indigo);">-</code></td>
                            <td><code style="color: var(--text-secondary);">-</code></td>
                            <td><code>12-May-26</code></td>
                            <td><strong>12-05-2026</strong></td>
                            <td>0 Spawns (Holdings)</td>
                            <td><span class="badge badge-casper">Larvae</span> &rarr; <span class="badge badge-active">Active Adult</span></td>
                            <td>Same cohort as T0166/T0167. Resolved to 12 May 2026 (~5 months old); graduated from nursery label.</td>
                        </tr>
                        <tr>
                            <td><strong>T0182 / T0183</strong></td>
                            <td><span class="badge badge-ab">AB</span></td>
                            <td><code>10-08-26</code></td>
                            <td><code style="color: var(--accent-indigo);">C0072</code></td>
                            <td><span class="badge" style="background: rgba(192,132,252,0.2); color: #c084fc;">N0068</span> (42 fish total)</td>
                            <td><code>10-Aug-26</code></td>
                            <td><strong>10-08-2026</strong></td>
                            <td>0 Spawns (Juveniles)</td>
                            <td><span class="badge badge-active">Active</span></td>
                            <td>Grounded to Cross C0072 &amp; Nursery N0068 (10 Aug 2026, graduated 10/09/2026). 42 fish split across T0182 (21) &amp; T0183 (21).</td>
                        </tr>
                        <tr>
                            <td><strong>T0108</strong></td>
                            <td><span class="badge badge-casper">Casper</span></td>
                            <td><code>07-03-25</code></td>
                            <td><code style="color: var(--accent-indigo);">C0035</code></td>
                            <td><span class="badge" style="background: rgba(192,132,252,0.2); color: #c084fc;">N0030</span> (3 fish)</td>
                            <td><code>03-07-2025</code></td>
                            <td><strong>03-07-2025</strong></td>
                            <td>8 Spawns (Feb–Jul 2026)</td>
                            <td><span class="badge badge-active">Active</span></td>
                            <td>Disambiguated 07-03-25 (US MM-DD-YY) via Cross C0035 &amp; Nursery N0030 (3 July 2025). Age calculation corrected.</td>
                        </tr>
                        <tr>
                            <td><strong>T0117</strong></td>
                            <td><span class="badge badge-ab">AB</span></td>
                            <td><code>09-04-25</code></td>
                            <td><code style="color: var(--accent-indigo);">C0041</code></td>
                            <td><span class="badge" style="background: rgba(192,132,252,0.2); color: #c084fc;">N0037</span> (7 fish)</td>
                            <td><code>04-09-2025</code></td>
                            <td><strong>04-09-2025</strong></td>
                            <td>5 Spawns (Apr–Jun 2026)</td>
                            <td><span class="badge badge-active">Active</span></td>
                            <td>Disambiguated 09-04-25 via Cross C0041 &amp; Nursery N0037 (4 September 2025). Age calculation corrected.</td>
                        </tr>
                        <tr>
                            <td><strong>T0121</strong></td>
                            <td><span class="badge badge-casper">Casper</span></td>
                            <td><code>07-03-25</code></td>
                            <td><code style="color: var(--accent-indigo);">C0044</code></td>
                            <td><span class="badge" style="background: rgba(192,132,252,0.2); color: #c084fc;">N0041</span> (15 fish)</td>
                            <td><code>03-07-2025</code></td>
                            <td><strong>03-07-2025</strong></td>
                            <td>4 Spawns (May–Jul 2026)</td>
                            <td><span class="badge badge-active">Active</span></td>
                            <td>Disambiguated 07-03-25 via Cross C0044 &amp; Nursery N0041 (3 July 2025). Age calculation corrected.</td>
                        </tr>
                        <tr>
                            <td><strong>T0177</strong></td>
                            <td><span class="badge badge-ab">AB</span></td>
                            <td><code>04-07-26</code></td>
                            <td><code style="color: var(--accent-indigo);">C0071</code></td>
                            <td><span class="badge" style="background: rgba(192,132,252,0.2); color: #c084fc;">N0067</span> (11 fish)</td>
                            <td><code>07-Apr-26</code></td>
                            <td><strong>07-04-2026</strong></td>
                            <td>0 Spawns</td>
                            <td><span class="badge badge-active">Active</span></td>
                            <td>Disambiguated 04-07-26 via Cross C0071 &amp; Nursery N0067 (7 April 2026). Age calculation corrected.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 8: Intelligent Mating Planner -->
    <div id="tab-planner" class="tab-content">
        <div class="planner-card">
            <h3 style="font-size: 18px; color: var(--accent-blue); margin-bottom: 8px;">🎯 Intelligent Zebrafish Mating Planner & Yield Predictor</h3>
            <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 20px;">
                Calculates required mating setups, automatically matching Single-Sex Dam/Sire tanks or Mixed Colonies based on historical cross synergy.
            </p>
            <div class="planner-grid">
                <div style="display: flex; flex-direction: column; gap: 14px;">
                    <div>
                        <label style="font-size: 12px; font-weight: 600; color: var(--text-secondary); display: block; margin-bottom: 6px;">Target Fish Line:</label>
                        <select id="plannerLine" style="width: 100%;" onchange="calculatePlanner()">
                            <option value="AB">AB (Standard Wildtype)</option>
                            <option value="Casper">Casper (Transparent)</option>
                            <option value="Fli">Fli (fli1a:EGFP Vascular Reporter)</option>
                            <option value="Gata">Gata (gata1a:DsRed Erythroid Reporter)</option>
                        </select>
                    </div>
                    <div>
                        <label style="font-size: 12px; font-weight: 600; color: var(--text-secondary); display: block; margin-bottom: 6px;">Desired Viable Embryos (at 24hpf):</label>
                        <input type="number" id="plannerTargetEmbryos" value="1000" min="50" step="50" style="width: 100%;" oninput="calculatePlanner()">
                    </div>
                    <div>
                        <label style="font-size: 12px; font-weight: 600; color: var(--text-secondary); display: block; margin-bottom: 6px;">Mating Strategy:</label>
                        <select id="plannerStrategy" style="width: 100%;" onchange="calculatePlanner()">
                            <option value="cross">Pair-Wise Cross Mating (Female Reservoir ♀ x Male Sire ♂)</option>
                            <option value="in_tank">In-Tank Group Spawning (Mixed Colony ⚤)</option>
                        </select>
                    </div>
                </div>
                <div class="recommendation-box" id="plannerResultBox">
                    <!-- Populated by JS -->
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 9: Raw Breeding Events -->
    <div id="tab-raw-events" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">📋 Master Zebrafish Breeding Dataset (2,233 Events across 2024 - 2026)</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Filtered search and pagination for all transcribed events</span>
                </div>
                <div class="card-header-actions">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('rawEventsTable', 'master_breeding_log_filtered')">📥 Export Filtered View (CSV)</button>
                    <button class="btn btn-sm btn-emerald" onclick="exportBreedingCSV()">📥 Export All 2,233 Rows (CSV)</button>
                </div>
            </div>
            <div class="filter-bar" style="margin-bottom: 16px;">
                <div class="filter-group">
                    <span class="filter-label">Year:</span>
                    <select id="rawYearFilter" onchange="renderRawEvents()">
                        <option value="ALL">All Years (2024-2026)</option>
                        <option value="2026">2026 Only</option>
                        <option value="2025">2025 Only</option>
                        <option value="2024">2024 Only</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Line:</span>
                    <select id="rawLineFilter" onchange="renderRawEvents()">
                        <option value="ALL">All Lines</option>
                        <option value="AB">AB</option>
                        <option value="Casper">Casper</option>
                        <option value="Fli">Fli</option>
                        <option value="Gata">Gata</option>
                    </select>
                </div>
                <div class="filter-group">
                    <input type="text" id="rawSearch" placeholder="Search Date, Line, or Tank..." oninput="renderRawEvents()">
                </div>
            </div>
            <div class="table-responsive">
                <table id="rawEventsTable">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Line</th>
                            <th>Parents / Tanks</th>
                            <th>In-Tank</th>
                            <th>Eggs (0H)</th>
                            <th>SR (0H)</th>
                            <th>Live (0H)</th>
                            <th>SR (24H)</th>
                            <th>Viable (24H)</th>
                            <th>Staff (Setup / 0H / 24H)</th>
                        </tr>
                    </thead>
                    <tbody id="rawEventsTableBody">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px; font-size: 13px; color: var(--text-secondary);">
                <span id="rawEventsCount">Showing 100 of 2,233 events</span>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-outline btn-sm" onclick="prevRawPage()">◀ Previous</button>
                    <button class="btn btn-outline btn-sm" onclick="nextRawPage()">Next ▶</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal for Tank Breeding History -->
    <div id="tankModal" class="modal-overlay" onclick="closeModal(event)">
        <div class="modal-box" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h3 id="modalTitle" style="color: var(--accent-blue);">Tank Details</h3>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('modalHistoryTable', 'tank_spawning_history')">📥 Export History (CSV)</button>
                    <button class="close-btn" onclick="closeModal()">&times;</button>
                </div>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- Populated dynamically -->
            </div>
        </div>
    </div>

    <script>
        const MASTER_DATA = __DATA_JSON__;

        let currentEvents = MASTER_DATA.events;
        let currentTanks = MASTER_DATA.tank_stats;
        let currentPairs = MASTER_DATA.pair_synergies || [];
        let rawPageIndex = 0;
        const RAW_PAGE_SIZE = 100;

        // --- Export Functions ---
        function exportChartAsPNG(chartCanvasId, fileName) {
            const chart = Chart.getChart(chartCanvasId);
            if (!chart) {
                alert('Chart not found or still rendering.');
                return;
            }
            const canvas = document.getElementById(chartCanvasId);
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = canvas.width;
            tempCanvas.height = canvas.height;
            const ctx = tempCanvas.getContext('2d');
            
            // Fill background with dark navy so saved PNG has nice contrast
            ctx.fillStyle = '#1e293b';
            ctx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
            ctx.drawImage(canvas, 0, 0);
            
            const link = document.createElement('a');
            link.download = (fileName || chartCanvasId) + '.png';
            link.href = tempCanvas.toDataURL('image/png', 1.0);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        function exportTableToCSV(tableId, fileName) {
            const table = document.getElementById(tableId);
            if (!table) {
                alert('Table not found.');
                return;
            }
            let csv = [];
            const rows = table.querySelectorAll('tr');
            for (let i = 0; i < rows.length; i++) {
                let row = [], cols = rows[i].querySelectorAll('td, th');
                for (let j = 0; j < cols.length; j++) {
                    if (cols[j].classList.contains('no-export')) continue;
                    let text = cols[j].innerText.replace(/(\\r\\n|\\n|\\r)/gm, ' ').replace(/\\s+/g, ' ').trim();
                    text = text.replace(/"/g, '""');
                    row.push('"' + text + '"');
                }
                if (row.length > 0) csv.push(row.join(','));
            }
            const csvContent = "data:text/csv;charset=utf-8,\\uFEFF" + encodeURIComponent(csv.join('\\n'));
            const link = document.createElement('a');
            link.setAttribute('href', csvContent);
            link.setAttribute('download', (fileName || 'table_export') + '.csv');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        function exportBreedingCSV() {
            window.open('DONE/fishnet_master_breeding_2024_2026.csv', '_blank');
        }

        function exportBreedingJSON() {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(MASTER_DATA, null, 2));
            const link = document.createElement('a');
            link.setAttribute('href', dataStr);
            link.setAttribute('download', 'fishnet_master_data_2024_2026.json');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        function getSexBadge(sexType) {
            if (sexType === 'Female-Only') return '<span class="badge badge-female">♀ Female-Only</span>';
            if (sexType === 'Male-Only') return '<span class="badge badge-male">♂ Male-Only</span>';
            if (sexType === 'Mixed Colony') return '<span class="badge badge-mixed">⚤ Mixed Colony</span>';
            return '<span class="badge" style="background: rgba(148, 163, 184, 0.2); color: #94a3b8;">Unsexed</span>';
        }

        // Line Benchmarks Calculation
        function calculateLineBenchmarks() {
            const lines = ['AB', 'Casper', 'Fli', 'Gata'];
            const res = {};
            lines.forEach(l => {
                res[l] = {
                    line: l,
                    activeTanks: 0,
                    spawns: 0,
                    eggs: 0,
                    live24h: 0,
                    sr0Sum: 0,
                    sr24Sum: 0,
                    validSpawns: 0,
                    inTankSpawns: 0
                };
            });

            Object.values(currentTanks).forEach(t => {
                if (res[t.line] && t.status === 'Active') {
                    res[t.line].activeTanks++;
                }
            });

            currentEvents.forEach(ev => {
                if (res[ev.line]) {
                    const st = res[ev.line];
                    st.spawns++;
                    st.eggs += ev.eggs_0h;
                    st.live24h += ev.live_24h;
                    if (ev.in_tank) st.inTankSpawns++;
                    if (ev.eggs_0h > 0) {
                        st.validSpawns++;
                        st.sr0Sum += ev.sr_0h;
                        st.sr24Sum += ev.sr_24h;
                    }
                }
            });

            return res;
        }

        // Render Benchmarks
        function renderBenchmarks() {
            const bm = calculateLineBenchmarks();
            const tbody = document.getElementById('lineBenchmarkTableBody');
            tbody.innerHTML = '';

            const lineLabels = ['AB', 'Casper', 'Fli', 'Gata'];
            const clutchData = [];
            const sr0Data = [];
            const sr24Data = [];

            lineLabels.forEach(l => {
                const st = bm[l];
                const avgClutch = st.spawns > 0 ? (st.eggs / st.spawns).toFixed(1) : 0;
                const avgSR0 = st.validSpawns > 0 ? (st.sr0Sum / st.validSpawns).toFixed(1) : 0;
                const avgSR24 = st.validSpawns > 0 ? (st.sr24Sum / st.validSpawns).toFixed(1) : 0;
                const inTankPct = st.spawns > 0 ? ((st.inTankSpawns / st.spawns) * 100).toFixed(1) : 0;

                clutchData.push(avgClutch);
                sr0Data.push(avgSR0);
                sr24Data.push(avgSR24);

                const badgeClass = `badge-${l.toLowerCase()}`;

                tbody.innerHTML += `
                    <tr>
                        <td><span class="badge ${badgeClass}">${l}</span></td>
                        <td>${st.activeTanks} tanks</td>
                        <td>${st.spawns.toLocaleString()}</td>
                        <td>${st.eggs.toLocaleString()}</td>
                        <td><strong>${avgClutch}</strong></td>
                        <td>${avgSR0}%</td>
                        <td><strong style="color: var(--accent-emerald);">${avgSR24}%</strong></td>
                        <td>${st.live24h.toLocaleString()}</td>
                        <td>${inTankPct}%</td>
                    </tr>
                `;
            });

            new Chart(document.getElementById('chartLineClutch'), {
                type: 'bar',
                data: {
                    labels: lineLabels,
                    datasets: [{
                        label: 'Avg Clutch Size (Eggs / Spawn)',
                        data: clutchData,
                        backgroundColor: ['#38bdf8', '#c084fc', '#34d399', '#fbbf24'],
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#f8fafc', font: { weight: 'bold' } } }
                    }
                }
            });

            new Chart(document.getElementById('chartLineSurvival'), {
                type: 'bar',
                data: {
                    labels: lineLabels,
                    datasets: [
                        {
                            label: 'Fertilization Rate (0hpf SR %)',
                            data: sr0Data,
                            backgroundColor: '#38bdf8',
                            borderRadius: 6
                        },
                        {
                            label: 'Viability Rate (24hpf SR %)',
                            data: sr24Data,
                            backgroundColor: '#34d399',
                            borderRadius: 6
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#f8fafc' } }
                    },
                    scales: {
                        y: { min: 0, max: 100, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#f8fafc' } }
                    }
                }
            });
        }

        // Render Cross-Pairing Synergies
        function renderCrosses() {
            const tbody = document.getElementById('pairSynergyTableBody');
            tbody.innerHTML = '';

            currentPairs.slice(0, 50).forEach((p, idx) => {
                const badgeClass = `badge-${p.line.toLowerCase()}`;
                tbody.innerHTML += `
                    <tr>
                        <td><strong>#${idx + 1}</strong></td>
                        <td><strong>${p.pair_key}</strong></td>
                        <td><span class="badge ${badgeClass}">${p.line}</span></td>
                        <td>${p.spawns}</td>
                        <td>${p.total_eggs.toLocaleString()}</td>
                        <td><strong>${p.avg_clutch}</strong></td>
                        <td><span style="color: var(--accent-emerald); font-weight: bold;">${p.avg_sr24}%</span></td>
                        <td>${p.total_live24h.toLocaleString()}</td>
                    </tr>
                `;
            });
        }

        // Render Longitudinal Trends
        function renderTrends() {
            const monthlyMap = {};
            currentEvents.forEach(ev => {
                if (!ev.date || ev.date.length < 7) return;
                const mKey = ev.date.substring(0, 7);
                if (!monthlyMap[mKey]) {
                    monthlyMap[mKey] = { eggs: 0, live: 0, spawns: 0, sr24Sum: 0, validSpawns: 0 };
                }
                monthlyMap[mKey].eggs += ev.eggs_0h;
                monthlyMap[mKey].live += ev.live_24h;
                monthlyMap[mKey].spawns++;
                if (ev.eggs_0h > 0) {
                    monthlyMap[mKey].validSpawns++;
                    monthlyMap[mKey].sr24Sum += ev.sr_24h;
                }
            });

            const months = Object.keys(monthlyMap).sort();
            const eggCounts = months.map(m => monthlyMap[m].eggs);
            const srRates = months.map(m => monthlyMap[m].validSpawns > 0 ? (monthlyMap[m].sr24Sum / monthlyMap[m].validSpawns).toFixed(1) : 0);

            new Chart(document.getElementById('chartMonthlyEggs'), {
                type: 'line',
                data: {
                    labels: months,
                    datasets: [{
                        label: 'Total Eggs Produced',
                        data: eggCounts,
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#f8fafc' } } },
                    scales: {
                        y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });

            new Chart(document.getElementById('chartMonthlySR'), {
                type: 'line',
                data: {
                    labels: months,
                    datasets: [{
                        label: 'Avg 24hpf Survival Rate (%)',
                        data: srRates,
                        borderColor: '#34d399',
                        backgroundColor: 'rgba(52, 211, 153, 0.1)',
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#f8fafc' } } },
                    scales: {
                        y: { min: 0, max: 100, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }

        // Render Age Curves
        function renderAgeCurves() {
            const ageBuckets = {};
            Object.values(currentTanks).forEach(t => {
                t.spawn_history.forEach(h => {
                    if (h.age_months !== null && h.age_months > 0 && h.age_months <= 36) {
                        const bucket = Math.floor(h.age_months);
                        if (!ageBuckets[bucket]) {
                            ageBuckets[bucket] = { eggsSum: 0, count: 0, sr24Sum: 0, validSpawns: 0 };
                        }
                        ageBuckets[bucket].eggsSum += h.eggs_0h;
                        ageBuckets[bucket].count++;
                        if (h.eggs_0h > 0) {
                            ageBuckets[bucket].validSpawns++;
                            ageBuckets[bucket].sr24Sum += h.sr_24h;
                        }
                    }
                });
            });

            const ages = Object.keys(ageBuckets).map(Number).sort((a, b) => a - b);
            const avgClutches = ages.map(a => (ageBuckets[a].eggsSum / ageBuckets[a].count).toFixed(1));
            const avgSRs = ages.map(a => ageBuckets[a].validSpawns > 0 ? (ageBuckets[a].sr24Sum / ageBuckets[a].validSpawns).toFixed(1) : 0);

            new Chart(document.getElementById('chartAgeFecundity'), {
                type: 'line',
                data: {
                    labels: ages.map(a => a + ' mo'),
                    datasets: [{
                        label: 'Average Clutch Size (Eggs)',
                        data: avgClutches,
                        borderColor: '#fbbf24',
                        backgroundColor: 'rgba(251, 191, 36, 0.1)',
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#f8fafc' } } },
                    scales: {
                        y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });

            new Chart(document.getElementById('chartAgeViability'), {
                type: 'line',
                data: {
                    labels: ages.map(a => a + ' mo'),
                    datasets: [{
                        label: '24hpf Survival Rate (%)',
                        data: avgSRs,
                        borderColor: '#818cf8',
                        backgroundColor: 'rgba(129, 140, 248, 0.1)',
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#f8fafc' } } },
                    scales: {
                        y: { min: 0, max: 100, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }

        // Render Scorecards
        function renderScorecards() {
            const lineFilter = document.getElementById('scorecardLineFilter').value;
            const sexFilter = document.getElementById('scorecardSexFilter').value;
            const statusFilter = document.getElementById('scorecardStatusFilter').value;
            const search = document.getElementById('scorecardSearch').value.toUpperCase();

            const tbody = document.getElementById('scorecardTableBody');
            tbody.innerHTML = '';

            let tanksList = Object.values(currentTanks).filter(t => {
                if (lineFilter !== 'ALL' && t.line !== lineFilter) return false;
                if (sexFilter !== 'ALL' && t.sex_type !== sexFilter) return false;
                if (statusFilter !== 'ALL' && t.status !== statusFilter) return false;
                if (search && !t.tuid.toUpperCase().includes(search) && !t.notes.toUpperCase().includes(search)) return false;
                return true;
            });

            tanksList.sort((a, b) => b.total_eggs_0h - a.total_eggs_0h);

            tanksList.forEach((t, idx) => {
                const badgeClass = `badge-${t.line.toLowerCase()}`;
                const statClass = t.status === 'Active' ? 'badge-active' : 'badge-euthanized';
                const sexBadge = getSexBadge(t.sex_type);

                tbody.innerHTML += `
                    <tr>
                        <td><strong>#${idx + 1}</strong></td>
                        <td><strong>${t.tuid}</strong></td>
                        <td><span class="badge ${badgeClass}">${t.line}</span></td>
                        <td>${sexBadge}</td>
                        <td><span class="badge ${statClass}">${t.status}</span></td>
                        <td>${t.female}F / ${t.male}M (${t.total})</td>
                        <td>${t.total_spawns}</td>
                        <td><strong>${t.total_eggs_0h.toLocaleString()}</strong></td>
                        <td>${t.avg_eggs_per_spawn}</td>
                        <td><span style="color: var(--accent-emerald); font-weight: bold;">${t.avg_sr_24h}%</span></td>
                        <td>${t.total_live_24h.toLocaleString()}</td>
                        <td>${t.last_spawn || '-'}</td>
                        <td class="no-export">
                            <button class="btn btn-sm btn-outline" onclick="openTankModal('${t.tuid}')">🔍 View History</button>
                        </td>
                    </tr>
                `;
            });
        }

        // Render Inventory
        function renderInventory() {
            const lineFilter = document.getElementById('invLineFilter').value;
            const sexFilter = document.getElementById('invSexFilter').value;
            const statusFilter = document.getElementById('invStatusFilter').value;
            const search = document.getElementById('invSearch').value.toUpperCase();

            const tbody = document.getElementById('inventoryTableBody');
            tbody.innerHTML = '';

            let tanksList = Object.values(currentTanks).filter(t => {
                if (lineFilter !== 'ALL' && t.line !== lineFilter) return false;
                if (sexFilter !== 'ALL' && t.sex_type !== sexFilter) return false;
                if (statusFilter !== 'ALL' && t.status !== statusFilter) return false;
                if (search && !t.tuid.toUpperCase().includes(search) 
                           && !(t.notes || '').toUpperCase().includes(search)
                           && !(t.genotype || '').toUpperCase().includes(search)
                           && !(t.derivative_cross || '').toUpperCase().includes(search)
                           && !(t.line || '').toUpperCase().includes(search)) return false;
                return true;
            });

            tanksList.forEach(t => {
                const badgeClass = `badge-${t.line.toLowerCase()}`;
                const statClass = t.status === 'Active' ? 'badge-active' : (t.status === 'Larvae' ? 'badge-casper' : 'badge-euthanized');
                const sexBadge = getSexBadge(t.sex_type);

                tbody.innerHTML += `
                    <tr>
                        <td><strong>${t.tuid}</strong></td>
                        <td><code style="color: var(--accent-indigo); font-weight: 600;">${t.derivative_cross || '-'}</code></td>
                        <td><strong>${t.genotype || '-'}</strong></td>
                        <td style="max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${t.notes || ''}">${t.notes || '-'}</td>
                        <td><span class="badge ${badgeClass}">${t.line}</span></td>
                        <td>${sexBadge}</td>
                        <td>${t.female}</td>
                        <td>${t.male}</td>
                        <td><strong>${t.total}</strong></td>
                        <td>${t.tank_size || '-'}</td>
                        <td style="font-size: 11px; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${t.protocol || ''}">${t.protocol || '-'}</td>
                        <td>${t.dob || '-'}</td>
                        <td>${t.turnover_date || '-'}</td>
                        <td>${t.dob_iso ? calculateAgeMonths(t.dob_iso) : '-'}</td>
                        <td><span class="badge ${statClass}">${t.status}</span></td>
                        <td>${t.total_spawns}</td>
                        <td>${t.total_eggs_0h.toLocaleString()}</td>
                        <td class="no-export">
                            <button class="btn btn-sm btn-outline" onclick="openTankModal('${t.tuid}')">Details</button>
                        </td>
                    </tr>
                `;
            });
        }

        // Render Audit Tab
        function renderAuditTab() {
            const tbody = document.getElementById('auditReservoirTableBody');
            tbody.innerHTML = '';

            const singleSexTanks = Object.values(currentTanks).filter(t => t.sex_type === 'Female-Only' || t.sex_type === 'Male-Only');
            singleSexTanks.sort((a, b) => a.tuid.localeCompare(b.tuid));

            singleSexTanks.forEach(t => {
                const badgeClass = `badge-${t.line.toLowerCase()}`;
                const sexBadge = getSexBadge(t.sex_type);
                const statClass = t.status === 'Active' ? 'badge-active' : 'badge-euthanized';
                const partners = Object.keys(t.cross_partners || {}).join(', ') || 'None recorded';

                tbody.innerHTML += `
                    <tr>
                        <td><strong>${t.tuid}</strong></td>
                        <td><span class="badge ${badgeClass}">${t.line}</span></td>
                        <td>${sexBadge}</td>
                        <td>${t.female}F / ${t.male}M</td>
                        <td><span class="badge ${statClass}">${t.status}</span></td>
                        <td>${t.notes}</td>
                        <td><code>${partners}</code></td>
                        <td>${t.total_spawns}</td>
                        <td><strong>${t.total_eggs_0h.toLocaleString()}</strong></td>
                    </tr>
                `;
            });
        }

        function calculateAgeMonths(dobIso) {
            const d = new Date(dobIso);
            const now = new Date(2026, 9, 3);
            const months = (now.getFullYear() - d.getFullYear()) * 12 + (now.getMonth() - d.getMonth());
            return months > 0 ? months + ' mo' : '< 1 mo';
        }

        // Render Raw Events with Pagination
        function renderRawEvents() {
            const yearFilter = document.getElementById('rawYearFilter').value;
            const lineFilter = document.getElementById('rawLineFilter').value;
            const search = document.getElementById('rawSearch').value.toUpperCase();

            let filtered = currentEvents.filter(ev => {
                if (yearFilter !== 'ALL' && String(ev.year) !== yearFilter) return false;
                if (lineFilter !== 'ALL' && ev.line !== lineFilter) return false;
                if (search && !ev.date.includes(search) && !ev.fishline.toUpperCase().includes(search) && !(ev.staff_summary || '').toUpperCase().includes(search)) return false;
                return true;
            });

            const total = filtered.length;
            const start = rawPageIndex * RAW_PAGE_SIZE;
            const end = Math.min(start + RAW_PAGE_SIZE, total);
            const pageData = filtered.slice(start, end);

            document.getElementById('rawEventsCount').innerText = `Showing ${total === 0 ? 0 : start + 1} to ${end} of ${total.toLocaleString()} events`;

            const tbody = document.getElementById('rawEventsTableBody');
            tbody.innerHTML = '';

            pageData.forEach(ev => {
                const badgeClass = `badge-${ev.line.toLowerCase()}`;
                tbody.innerHTML += `
                    <tr>
                        <td>${ev.date}</td>
                        <td><span class="badge ${badgeClass}">${ev.line}</span></td>
                        <td><strong>${ev.fishline}</strong></td>
                        <td>${ev.in_tank ? '<span class="badge badge-active">Yes (In-Tank)</span>' : 'No (Pair)'}</td>
                        <td><strong>${ev.eggs_0h}</strong></td>
                        <td>${ev.sr_0h}%</td>
                        <td>${ev.live_0h}</td>
                        <td><span style="color: var(--accent-emerald); font-weight: bold;">${ev.sr_24h}%</span></td>
                        <td><strong>${ev.live_24h}</strong></td>
                        <td><span style="font-size: 11px; color: var(--text-secondary);">${ev.staff_summary || '-'}</span></td>
                    </tr>
                `;
            });
        }

        function nextRawPage() {
            rawPageIndex++;
            renderRawEvents();
        }

        function prevRawPage() {
            if (rawPageIndex > 0) {
                rawPageIndex--;
                renderRawEvents();
            }
        }

        // Enhanced Intelligent Mating Planner Calculation
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
        }

        // Modal for Tank Performance History
        function openTankModal(tuid) {
            const t = currentTanks[tuid];
            if (!t) return;

            document.getElementById('modalTitle').innerText = `${t.tuid} [${t.line}] — Complete Facility & Performance Profile`;
            const mbody = document.getElementById('modalBody');

            let historyRows = '';
            t.spawn_history.forEach(h => {
                historyRows += `
                    <tr>
                        <td>${h.date}</td>
                        <td>${h.age_months !== null ? h.age_months + ' mo' : '-'}</td>
                        <td>${h.in_tank ? 'In-Tank' : 'Pair-Wise'}</td>
                        <td>${h.eggs_0h}</td>
                        <td>${h.sr_0h}%</td>
                        <td>${h.sr_24h}%</td>
                        <td><strong>${h.live_24h}</strong></td>
                        <td>${h.staff || '-'}</td>
                    </tr>
                `;
            });

            const sexBadge = getSexBadge(t.sex_type);

            mbody.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px;">
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Genotype / Strain</span>
                        <div style="font-weight: bold; margin-top: 4px; color: #fff;">${t.genotype || t.line}</div>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Derivative Cross &amp; Nursery</span>
                        <div style="font-weight: bold; margin-top: 4px; display: flex; align-items: center; gap: 6px;">
                            <span style="color: var(--accent-indigo);">${t.derivative_cross || 'Root Stock'}</span>
                            ${t.derivative_nursery ? `<span class="badge" style="background: rgba(192,132,252,0.2); color: #c084fc; font-size: 11px;">${t.derivative_nursery}</span>` : ''}
                        </div>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Sex Composition</span>
                        <div style="margin-top: 4px;">${sexBadge}</div>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Adult Inventory</span>
                        <div style="font-weight: bold; margin-top: 4px;">${t.female}♀ / ${t.male}♂ (Total: ${t.total})</div>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Date of Birth (DOB)</span>
                        <div style="font-weight: bold; margin-top: 4px;">${t.dob || '-'}</div>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Turnover Date</span>
                        <div style="font-weight: bold; margin-top: 4px;">${t.turnover_date || '-'}</div>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Tank Size / Room</span>
                        <div style="font-weight: bold; margin-top: 4px;">${t.tank_size || '-'} / ${t.room || 'D126'}</div>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Protocol</span>
                        <div style="font-size: 11px; margin-top: 4px; color: var(--text-secondary);">${t.protocol || '-'}</div>
                    </div>
                </div>

                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 12px; border-radius: 6px; margin-bottom: 20px;">
                    <span style="font-size: 11px; color: var(--text-secondary);">Original FileMaker Notes / Lineage:</span>
                    <p style="font-size: 13px; color: #fff; margin-top: 4px; font-family: monospace;">${t.notes || 'None recorded'}</p>
                </div>

                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;">
                    <div style="background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.2); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Lifetime Spawns</span>
                        <div style="font-size: 18px; font-weight: bold; color: var(--accent-blue); margin-top: 2px;">${t.total_spawns}</div>
                    </div>
                    <div style="background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.2); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Lifetime Eggs Spawned</span>
                        <div style="font-size: 18px; font-weight: bold; color: var(--accent-amber); margin-top: 2px;">${t.total_eggs_0h.toLocaleString()}</div>
                    </div>
                    <div style="background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.2); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">24hpf Embryo Viability</span>
                        <div style="font-size: 18px; font-weight: bold; color: var(--accent-emerald); margin-top: 2px;">${t.avg_sr_24h}% (${t.total_live_24h.toLocaleString()} viable)</div>
                    </div>
                </div>

                <h4 style="font-size: 14px; margin-bottom: 10px;">Spawning Event History (${t.spawn_history.length} events)</h4>
                <div class="table-responsive" style="max-height: 250px; overflow-y: auto;">
                    <table id="modalHistoryTable">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Age</th>
                                <th>Type</th>
                                <th>Eggs (0H)</th>
                                <th>SR (0H)</th>
                                <th>SR (24H)</th>
                                <th>Viable (24H)</th>
                                <th>Staff</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${historyRows || '<tr><td colspan="8" style="text-align: center; color: var(--text-secondary);">No individual breeding logs recorded yet.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            `;

            document.getElementById('tankModal').style.display = 'flex';
        }

        function closeModal(e) {
            if (!e || e.target.id === 'tankModal' || e.target.className === 'close-btn') {
                document.getElementById('tankModal').style.display = 'none';
            }
        }

        // Tab Switching
        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            const targetBtn = document.querySelector(`[onclick*="${tabId}"]`);
            if (targetBtn) targetBtn.classList.add('active');
            
            const targetContent = document.getElementById(tabId);
            if (targetContent) targetContent.classList.add('active');
        }

        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(e) {
                alert(`File "${file.name}" loaded successfully! Dynamic analytics updated.`);
            };
            reader.readAsText(file);
        }

        window.onload = function() {
            renderBenchmarks();
            renderCrosses();
            renderTrends();
            renderAgeCurves();
            renderScorecards();
            renderInventory();
            renderAuditTab();
            renderRawEvents();
            calculatePlanner();
        };
    </script>
</body>
</html>
"""

    html_content = html_template.replace('__DATA_JSON__', data_json_str)

    out_integrated = os.path.join(labels_dir, 'FishNET_Interactive_Dashboard_With_Breeding.html')
    with open(out_integrated, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f'Wrote {out_integrated}')

    out_main = os.path.join(labels_dir, 'FishNET_Interactive_Dashboard.html')
    with open(out_main, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f'Wrote {out_main}')

    out_index = os.path.join(labels_dir, 'index.html')
    with open(out_index, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f'Wrote {out_index}')

if __name__ == '__main__':
    generate_dashboard()
