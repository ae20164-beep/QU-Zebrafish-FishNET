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
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
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
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
            gap: 6px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 4px;
            overflow-x: auto;
        }
        
        .tab-btn {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 10px 14px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s ease;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 6px;
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
        .badge-larvae { background: rgba(192, 132, 252, 0.15); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3); }
        
        .badge-ab { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
        .badge-casper { background: rgba(192, 132, 252, 0.15); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3); }
        .badge-fli { background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); }
        .badge-gata { background: rgba(251, 191, 36, 0.15); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }
        
        .badge-female { background: rgba(244, 114, 182, 0.15); color: #f472b6; border: 1px solid rgba(244, 114, 182, 0.3); }
        .badge-male { background: rgba(96, 165, 250, 0.15); color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.3); }
        .badge-mixed { background: rgba(167, 139, 250, 0.15); color: #a78bfa; border: 1px solid rgba(167, 139, 250, 0.3); }

        .badge-critical { background: rgba(244, 63, 94, 0.2); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.4); }
        .badge-high { background: rgba(251, 146, 60, 0.2); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.4); }
        .badge-medium { background: rgba(250, 204, 21, 0.2); color: #facc15; border: 1px solid rgba(250, 204, 21, 0.4); }
        .badge-info { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
        
        /* Pedigree Subviews & Cards */
        .ped-mode-btn {
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 7px 12px;
            border-radius: var(--radius-sm);
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .ped-mode-btn.active {
            background: #0d9488;
            color: #fff;
            border-color: #0d9488;
        }
        .ped-mode-btn:hover:not(.active) {
            background: rgba(255,255,255,0.05);
            color: #fff;
        }

        .line-tree-btn {
            padding: 6px 12px;
            border-radius: var(--radius-sm);
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid var(--border-color);
            background: #1e293b;
            color: var(--text-secondary);
            transition: all 0.2s ease;
        }
        .line-tree-btn.active {
            background: #f59e0b;
            color: #000;
            border-color: #f59e0b;
            font-weight: 700;
        }

        .ped-card {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 12px;
            transition: all 0.2s ease;
            position: relative;
        }
        .ped-card:hover {
            border-color: var(--accent-blue);
            transform: translateY(-2px);
            background: rgba(30, 41, 59, 0.8);
        }
        .ped-card-hero {
            background: linear-gradient(135deg, rgba(13, 148, 136, 0.2) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 2px solid #14b8a6;
            box-shadow: 0 0 20px rgba(20, 184, 166, 0.2);
        }

        #pedigree-network {
            height: 520px;
            background: #090d16;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
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
        
        .modal-container {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            width: 100%;
            max-width: 900px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: var(--shadow-card);
            display: flex;
            flex-direction: column;
        }
        
        .modal-header {
            padding: 20px 24px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .modal-title {
            font-size: 18px;
            font-weight: 700;
            color: var(--text-primary);
        }
        
        .modal-body {
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .close-btn {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 20px;
            cursor: pointer;
        }
        
        .close-btn:hover {
            color: var(--text-primary);
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="header-title">
            <h1><span>🐠</span> FishNET Facility Reproductive & Colony Intelligence System</h1>
            <p>Unified Zebrafish Platform (2024–2026) | 183 Tanks • 2,233 Spawning Events • 1,252,045 Eggs • 72 Crosses • Full 5-Gen Pedigree</p>
        </div>
        <div class="header-controls">
            <button class="btn btn-outline" onclick="exportBreedingJSON()">💾 Export Database (JSON)</button>
            <button class="btn btn-emerald" onclick="exportBreedingCSV()">📥 Export Master CSV (2024–2026)</button>
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
        <div class="kpi-card kpi-purple">
            <span class="kpi-label">Crosses & Alerts</span>
            <span class="kpi-value" id="kpiCrossAlerts">72 / 120</span>
            <span class="kpi-subtext">72 Crosses | 120 Active Alerts</span>
        </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs-container">
        <button class="tab-btn active" onclick="switchTab('tab-benchmarks')">📊 4-Line Benchmarks</button>
        <button class="tab-btn" onclick="switchTab('tab-pedigree')">🌳 Pedigree Explorer</button>
        <button class="tab-btn" onclick="switchTab('tab-turnover')">⏳ Turnover & Colony Renewal</button>
        <button class="tab-btn" onclick="switchTab('tab-crosses-reg')">🧬 Crosses & Nursery Registry</button>
        <button class="tab-btn" onclick="switchTab('tab-alerts')">⚠️ Colony Alerts (<span id="tabBadgeAlerts">120</span>)</button>
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

    <!-- TAB 2: PEDIGREE EXPLORER -->
    <div id="tab-pedigree" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">🌳 Colony Lineage & 5-Generation Pedigree Architecture</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">4 Viewing Modes: 3-Gen Interactive Family Tree, 4-Line Trees, Collapsible Hierarchy Table, and Global Network Map</span>
                </div>
                <div class="card-header-actions" style="background: rgba(15,23,42,0.6); padding: 4px; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
                    <button onclick="switchPedigreeMode('focal')" id="ped-btn-focal" class="ped-mode-btn active">🎯 3-Gen Family Tree</button>
                    <button onclick="switchPedigreeMode('lines')" id="ped-btn-lines" class="ped-mode-btn">🌿 Line Trees (4 Lines)</button>
                    <button onclick="switchPedigreeMode('table')" id="ped-btn-table" class="ped-mode-btn">📑 Collapsible Table</button>
                    <button onclick="switchPedigreeMode('network')" id="ped-btn-network" class="ped-mode-btn">🕸️ Global Network Map</button>
                </div>
            </div>

            <!-- SUB-VIEW 1: FOCAL 3-GEN FAMILY TREE -->
            <div id="ped-subview-focal" class="ped-subview">
                <div class="filter-bar" style="margin-bottom: 16px;">
                    <div class="filter-group">
                        <span class="filter-label">Focal Tank:</span>
                        <select id="focalTankSelect" onchange="changeFocalTank(this.value)">
                            <!-- Populated dynamically -->
                        </select>
                    </div>
                    <div class="filter-group">
                        <input type="text" id="focalSearchInput" placeholder="Search Tank (e.g. T0135)..." style="width: 180px;">
                        <button class="btn btn-sm btn-emerald" onclick="searchAndFocusTank()">Focus</button>
                    </div>
                    <div class="filter-group" style="margin-left: auto;">
                        <button class="btn btn-sm btn-outline" onclick="copyLineageTrail()">📋 Copy Path</button>
                    </div>
                </div>

                <div id="focalBreadcrumbTrail" style="background: rgba(15,23,42,0.8); padding: 10px 14px; border-radius: var(--radius-sm); font-family: monospace; font-size: 12px; margin-bottom: 16px; border: 1px solid var(--border-color);">
                    <!-- Breadcrumbs -->
                </div>

                <!-- 5 Columns Tree -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px;">
                    <!-- Col 1: Grandparents -->
                    <div style="background: rgba(15,23,42,0.4); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px;">
                        <div style="font-size: 11px; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid var(--border-color); padding-bottom: 4px;">
                            👴👵 Grandparents (2-Gen)
                        </div>
                        <div id="treeColGrandparents" style="display: flex; flex-direction: column; gap: 8px;"></div>
                    </div>

                    <!-- Col 2: Parents -->
                    <div style="background: rgba(15,23,42,0.4); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px;">
                        <div style="font-size: 11px; font-weight: 700; color: var(--accent-blue); text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid var(--border-color); padding-bottom: 4px;">
                            👨👩 Parents (Sire x Dam)
                        </div>
                        <div id="treeColParents" style="display: flex; flex-direction: column; gap: 8px;"></div>
                    </div>

                    <!-- Col 3: Focal Tank -->
                    <div style="background: rgba(13, 148, 136, 0.15); border: 2px solid #14b8a6; border-radius: var(--radius-md); padding: 12px;">
                        <div style="font-size: 11px; font-weight: 700; color: #2dd4bf; text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid rgba(20, 184, 166, 0.4); padding-bottom: 4px; display: flex; justify-content: space-between;">
                            <span>🎯 Target Focal Tank</span>
                            <span id="focalHeroGenBadge" class="badge badge-active">Gen</span>
                        </div>
                        <div id="treeColFocal"></div>
                    </div>

                    <!-- Col 4: Offspring -->
                    <div style="background: rgba(15,23,42,0.4); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px;">
                        <div style="font-size: 11px; font-weight: 700; color: var(--accent-emerald); text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid var(--border-color); padding-bottom: 4px; display: flex; justify-content: space-between;">
                            <span>👶 Offspring (F1)</span>
                            <span id="treeOffspringCountBadge" style="color: var(--accent-emerald); font-size: 11px;">0 Tanks</span>
                        </div>
                        <div id="treeColOffspring" style="display: flex; flex-direction: column; gap: 8px; max-height: 400px; overflow-y: auto;"></div>
                    </div>

                    <!-- Col 5: Grandchildren -->
                    <div style="background: rgba(15,23,42,0.4); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px;">
                        <div style="font-size: 11px; font-weight: 700; color: var(--accent-purple); text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid var(--border-color); padding-bottom: 4px; display: flex; justify-content: space-between;">
                            <span>🌱 Grandchildren (F2)</span>
                            <span id="treeGrandchildrenCountBadge" style="color: var(--accent-purple); font-size: 11px;">0 Tanks</span>
                        </div>
                        <div id="treeColGrandchildren" style="display: flex; flex-direction: column; gap: 8px; max-height: 400px; overflow-y: auto;"></div>
                    </div>
                </div>
            </div>

            <!-- SUB-VIEW 2: LINE TREES -->
            <div id="ped-subview-lines" class="ped-subview" style="display: none;">
                <div class="filter-bar" style="margin-bottom: 16px;">
                    <div class="filter-group">
                        <button onclick="selectLineTree('AB')" id="line-tree-btn-AB" class="line-tree-btn active">🟡 AB Lineage Tree (<span id="lineTreeCountAB">0</span>)</button>
                        <button onclick="selectLineTree('Casper')" id="line-tree-btn-Casper" class="line-tree-btn">🔵 Casper Lineage Tree (<span id="lineTreeCountCasper">0</span>)</button>
                        <button onclick="selectLineTree('Fli')" id="line-tree-btn-Fli" class="line-tree-btn">🟢 Fli Lineage Tree (<span id="lineTreeCountFli">0</span>)</button>
                        <button onclick="selectLineTree('Gata')" id="line-tree-btn-Gata" class="line-tree-btn">🟣 Gata Lineage Tree (<span id="lineTreeCountGata">0</span>)</button>
                    </div>
                </div>
                <div id="lineTreeTiersContainer" style="display: flex; flex-direction: column; gap: 16px;">
                    <!-- Line Tree Tiers -->
                </div>
            </div>

            <!-- SUB-VIEW 3: COLLAPSIBLE TABLE -->
            <div id="ped-subview-table" class="ped-subview" style="display: none;">
                <div class="filter-bar" style="margin-bottom: 16px;">
                    <div class="filter-group">
                        <input type="text" id="treeTableSearchInput" onkeyup="filterTreeTable()" placeholder="Search Tank, Line, Parents..." style="width: 220px;">
                    </div>
                    <div class="filter-group">
                        <select id="treeTableLineFilter" onchange="filterTreeTable()">
                            <option value="ALL">All Lines</option>
                            <option value="AB">AB</option>
                            <option value="Casper">Casper</option>
                            <option value="Fli">Fli</option>
                            <option value="Gata">Gata</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <select id="treeTableStatusFilter" onchange="filterTreeTable()">
                            <option value="ALL">All Statuses</option>
                            <option value="ACTIVE" selected>Active / Adult Only</option>
                            <option value="EUTH">Euthanized Only</option>
                        </select>
                    </div>
                    <div class="filter-group" style="margin-left: auto;">
                        <button class="btn btn-sm btn-outline" onclick="exportTreeTableCSV()">📥 Export Table CSV</button>
                    </div>
                </div>
                <div class="table-responsive" style="max-height: 550px; overflow-y: auto;">
                    <table id="pedigreeTreeTable">
                        <thead>
                            <tr>
                                <th>Tank ID & Line</th>
                                <th>Generation</th>
                                <th>Status</th>
                                <th>Fish (F/M/Total)</th>
                                <th>Inbreeding (F)</th>
                                <th>Sire × Dam</th>
                                <th>Offspring</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="pedigreeTreeTableBody">
                            <!-- Populated dynamically -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- SUB-VIEW 4: GLOBAL NETWORK MAP -->
            <div id="ped-subview-network" class="ped-subview" style="display: none;">
                <div class="filter-bar" style="margin-bottom: 16px;">
                    <div class="filter-group">
                        <input type="text" id="pedigreeSearch" placeholder="Search Tank (e.g. T0135)..." style="width: 200px;">
                        <button class="btn btn-sm btn-emerald" onclick="searchPedigreeNode()">Locate</button>
                    </div>
                    <div class="filter-group">
                        <select id="lineFilter" onchange="filterPedigreeByLine()">
                            <option value="ALL">All 4 Lines</option>
                            <option value="AB">AB Lineage</option>
                            <option value="Casper">Casper Lineage</option>
                            <option value="Fli">Fli Lineage</option>
                            <option value="Gata">Gata Lineage</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <button class="btn btn-sm btn-outline" onclick="resetPedigreeView()">Reset View</button>
                    </div>
                </div>
                <div id="pedigree-network"></div>
            </div>
        </div>
    </div>

    <!-- TAB 3: TURNOVER & COLONY RENEWAL -->
    <div id="tab-turnover" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">⏳ Colony Turnover Schedule & 2-Year Lifespan Renewal Plan</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Zebrafish facility compliance: 540–730 days post-DOB lifecycle management</span>
                </div>
                <div class="card-header-actions">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('turnoverTable', 'colony_turnover_schedule')">📥 Export Schedule (CSV)</button>
                </div>
            </div>
            <div class="filter-bar" style="margin-bottom: 16px;">
                <div class="filter-group">
                    <span class="filter-label">Turnover Urgency:</span>
                    <select id="turnoverFilter" onchange="renderTurnoverTable()">
                        <option value="ALL">All Active Tanks (117)</option>
                        <option value="OVERDUE">🚨 Overdue Only (>2 Years)</option>
                        <option value="SOON">⚠️ Due Soon (<=30 Days)</option>
                        <option value="UPCOMING">Upcoming (31–90 Days)</option>
                        <option value="FUTURE">Future (>90 Days)</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Line:</span>
                    <select id="turnoverLineFilter" onchange="renderTurnoverTable()">
                        <option value="ALL">All Lines</option>
                        <option value="AB">AB</option>
                        <option value="Casper">Casper</option>
                        <option value="Fli">Fli</option>
                        <option value="Gata">Gata</option>
                    </select>
                </div>
            </div>
            <div class="table-responsive" style="max-height: 600px; overflow-y: auto;">
                <table id="turnoverTable">
                    <thead>
                        <tr>
                            <th>TUID</th>
                            <th>Status</th>
                            <th>Line</th>
                            <th>Sex (F/M/Tot)</th>
                            <th>DOB</th>
                            <th>Turnover Deadline</th>
                            <th>Days Remaining</th>
                            <th>Urgency</th>
                            <th>Recommended Colony Action</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody id="turnoverTableBody">
                        <!-- Populated dynamically -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 4: CROSSES & NURSERY PIPELINE -->
    <div id="tab-crosses-reg" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">🧬 72 Facility Crosses & Nursery Pipeline Registry</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Direct mapping from parental cross (Dam x Sire) to nursery clutch (NUID) and graduated tank offspring</span>
                </div>
                <div class="card-header-actions">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('crossesRegistryTable', 'fishnet_crosses_nursery_registry')">📥 Export Crosses (CSV)</button>
                </div>
            </div>
            <div class="filter-bar" style="margin-bottom: 16px;">
                <div class="filter-group">
                    <input type="text" id="crossRegSearch" placeholder="Search Cross (e.g. C0045, T0086)..." oninput="renderCrossesRegistry()" style="width: 240px;">
                </div>
            </div>
            <div class="table-responsive" style="max-height: 600px; overflow-y: auto;">
                <table id="crossesRegistryTable">
                    <thead>
                        <tr>
                            <th>Cross ID</th>
                            <th>Mating Date</th>
                            <th>Dam (♀ Female Tank)</th>
                            <th>Sire (♂ Male Tank)</th>
                            <th>Line Combination</th>
                            <th>Linked Nursery Clutches</th>
                            <th>Nursery Fish Yield</th>
                            <th>Graduation Date</th>
                            <th>Resulting Offspring Tanks</th>
                        </tr>
                    </thead>
                    <tbody id="crossesRegistryTableBody">
                        <!-- Populated dynamically -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 5: COLONY ALERTS & COMPLIANCE -->
    <div id="tab-alerts" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">⚠️ Active Colony Risk, Turnover & Genetic Compliance Alerts</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Automated monitoring for overdue lifecycles, elevated inbreeding (F >= 0.25), and depleted single-sex reservoirs</span>
                </div>
                <div class="card-header-actions">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('alertsTable', 'active_colony_alerts')">📥 Export Alerts (CSV)</button>
                </div>
            </div>
            <div class="filter-bar" style="margin-bottom: 16px;">
                <div class="filter-group">
                    <span class="filter-label">Severity:</span>
                    <select id="alertSeverityFilter" onchange="renderColonyAlerts()">
                        <option value="ALL">All Severities</option>
                        <option value="CRITICAL">🔴 Critical Only</option>
                        <option value="HIGH">🟠 High Only</option>
                        <option value="MEDIUM">🟡 Medium Only</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Category:</span>
                    <select id="alertCategoryFilter" onchange="renderColonyAlerts()">
                        <option value="ALL">All Categories</option>
                        <option value="Turnover Overdue">Turnover Overdue</option>
                        <option value="Turnover Due Soon">Turnover Due Soon</option>
                        <option value="Elevated Inbreeding">Elevated Inbreeding (F >= 0.25)</option>
                        <option value="Low Biomass Reservoir">Low Biomass Reservoir</option>
                    </select>
                </div>
            </div>
            <div id="alertsFeedContainer" style="display: flex; flex-direction: column; gap: 12px;">
                <!-- Populated dynamically -->
            </div>
        </div>
    </div>

    <!-- TAB 6: Cross-Pairing Synergies -->
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

    <!-- TAB 7: Longitudinal Trends -->
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

    <!-- TAB 8: Parental Age vs Fecundity Curves -->
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

    <!-- TAB 9: Breeder Scorecards -->
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

    <!-- TAB 10: Inventory & Sex Structure -->
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

    <!-- TAB 11: Data Audit & Sex Consistency -->
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

            <h4 style="font-size: 14px; margin-bottom: 12px; color: var(--accent-blue);">1. Single-Sex Reservoir Tanks (41 Tanks: 21 Female-Only, 20 Male-Only)</h4>
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
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 12: Intelligent Mating Planner -->
    <div id="tab-planner" class="tab-content">
        <div class="card planner-card">
            <div class="card-header">
                <div>
                    <span class="card-title">🎯 Intelligent Spawning Recommendation & Cross-Planner</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Algorithm recommending high-synergy parental combinations based on empirical survival data</span>
                </div>
            </div>
            <div class="filter-bar">
                <div class="filter-group">
                    <span class="filter-label">Target Line:</span>
                    <select id="planLine" onchange="calculatePlanner()">
                        <option value="AB">AB Line</option>
                        <option value="Casper">Casper Line</option>
                        <option value="Fli">Fli Line</option>
                        <option value="Gata">Gata Line</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Target Viable Yield:</span>
                    <input type="number" id="planEmbryoTarget" value="1000" min="100" max="10000" step="100" oninput="calculatePlanner()">
                </div>
            </div>
            
            <div id="plannerResultBox" class="planner-grid">
                <!-- Populated by JS -->
            </div>
        </div>
    </div>

    <!-- TAB 13: Master Breeding Log -->
    <div id="tab-raw-events" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">📋 Grand Master Spawning Event Log (2,233 Events, 2024-2026)</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Full individual spawning log history</span>
                </div>
                <div class="card-header-actions">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('rawEventsTable', 'grand_master_breeding_events_2024_2026')">📥 Export Full Log (CSV)</button>
                </div>
            </div>
            <div class="filter-bar" style="margin-bottom: 16px;">
                <div class="filter-group">
                    <span class="filter-label">Year:</span>
                    <select id="rawYearFilter" onchange="renderRawEvents()">
                        <option value="ALL">All Years (2024-2026)</option>
                        <option value="2026">2026 (544 events)</option>
                        <option value="2025">2025 (1,229 events)</option>
                        <option value="2024">2024 (460 events)</option>
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
                    <input type="text" id="rawSearch" placeholder="Search Tank, Date, Staff, Cross..." oninput="renderRawEvents()">
                </div>
            </div>
            
            <div class="table-responsive" style="max-height: 600px; overflow-y: auto;">
                <table id="rawEventsTable">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Line</th>
                            <th>Mating Type</th>
                            <th>Tanks Involved</th>
                            <th>Eggs (0hpf)</th>
                            <th>0hpf SR (%)</th>
                            <th>24hpf SR (%)</th>
                            <th>Viable Embryos (24h)</th>
                            <th>Staff</th>
                        </tr>
                    </thead>
                    <tbody id="rawEventsTableBody">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Tank Performance Modal -->
    <div id="tankModal" class="modal-overlay" onclick="closeModal(event)">
        <div class="modal-container" onclick="event.stopPropagation()">
            <div class="modal-header">
                <span class="modal-title" id="modalTitle">Tank Profile</span>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- Loaded Dynamically -->
            </div>
        </div>
    </div>

    <script>
        const MASTER_DATA = __DATA_JSON__;
        let currentEvents = MASTER_DATA.events || [];
        let currentTanks = MASTER_DATA.tank_stats || {};
        let currentPairs = MASTER_DATA.pair_synergies || [];
        let currentCrosses = MASTER_DATA.crosses_registry || [];
        let currentAlerts = MASTER_DATA.alerts || [];

        let currentFocalTank = 'T0135';
        let pedigreeNetworkInstance = null;

        // Export Utilities
        function exportChartAsPNG(canvasId, filename) {
            const chartCanvas = document.getElementById(canvasId);
            if (!chartCanvas) return;
            const link = document.createElement('a');
            link.download = (filename || 'chart') + '.png';
            link.href = chartCanvas.toDataURL('image/png');
            link.click();
        }

        function exportTableToCSV(tableId, fileName) {
            const table = document.getElementById(tableId);
            if (!table) return;
            let csv = [];
            const rows = table.querySelectorAll('tr');
            
            for (let i = 0; i < rows.length; i++) {
                if (rows[i].style.display === 'none') continue;
                const row = [], cols = rows[i].querySelectorAll('td, th');
                
                for (let j = 0; j < cols.length; j++) {
                    if (cols[j].classList.contains('no-export')) continue;
                    let data = cols[j].innerText.replace(/(\\r\\n|\\n|\\r)/gm, ' ').replace(/(\\s\\s+)/gm, ' ');
                    data = data.replace(/"/g, '""');
                    row.push('"' + data + '"');
                }
                csv.push(row.join(','));
            }
            
            const csvContent = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv.join('\\n'));
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

        function getStatusBadge(status) {
            if (status === 'Active') return '<span class="badge badge-active">Active</span>';
            if (status === 'Euthanized') return '<span class="badge badge-euthanized">Euthanized</span>';
            return '<span class="badge badge-larvae">Larvae</span>';
        }

        // TAB 1: Line Benchmarks
        function calculateLineBenchmarks() {
            const lines = ['AB', 'Casper', 'Fli', 'Gata'];
            const res = {};
            lines.forEach(l => {
                res[l] = { line: l, activeTanks: 0, spawns: 0, eggs: 0, live24h: 0, sr0Sum: 0, sr24Sum: 0, validSpawns: 0, inTankSpawns: 0 };
            });

            Object.values(currentTanks).forEach(t => {
                if (res[t.line] && t.status === 'Active') res[t.line].activeTanks++;
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

        function renderBenchmarks() {
            const bm = calculateLineBenchmarks();
            const tbody = document.getElementById('lineBenchmarkTableBody');
            if (!tbody) return;
            tbody.innerHTML = '';

            const lineLabels = ['AB', 'Casper', 'Fli', 'Gata'];
            const clutchData = [], sr0Data = [], sr24Data = [];

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
                        { label: 'Fertilization Rate (0hpf SR %)', data: sr0Data, backgroundColor: '#38bdf8', borderRadius: 6 },
                        { label: 'Viability Rate (24hpf SR %)', data: sr24Data, backgroundColor: '#34d399', borderRadius: 6 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#f8fafc' } } },
                    scales: {
                        y: { min: 0, max: 100, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#f8fafc' } }
                    }
                }
            });
        }

        // TAB 2: PEDIGREE EXPLORER JS
        function switchPedigreeMode(mode) {
            document.querySelectorAll('.ped-mode-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.ped-subview').forEach(v => v.style.display = 'none');
            
            const btn = document.getElementById(`ped-btn-${mode}`);
            if (btn) btn.classList.add('active');
            const sub = document.getElementById(`ped-subview-${mode}`);
            if (sub) sub.style.display = 'block';

            if (mode === 'focal') renderFocalPedigreeTree();
            else if (mode === 'lines') renderLineTrees();
            else if (mode === 'table') renderTreeTable();
            else if (mode === 'network') renderPedigreeNetwork();
        }

        function populateFocalDropdown() {
            const sel = document.getElementById('focalTankSelect');
            if (!sel) return;
            sel.innerHTML = '';
            
            const activeTanks = Object.values(currentTanks).filter(t => t.status === 'Active');
            activeTanks.sort((a, b) => a.tuid.localeCompare(b.tuid));

            activeTanks.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.tuid;
                opt.textContent = `${t.tuid} [${t.line}] - Gen ${t.generation || 0} (${t.female}F/${t.male}M)`;
                if (t.tuid === currentFocalTank) opt.selected = true;
                sel.appendChild(opt);
            });
        }

        function changeFocalTank(tuid) {
            if (!tuid || !currentTanks[tuid]) return;
            currentFocalTank = tuid;
            renderFocalPedigreeTree();
        }

        function searchAndFocusTank() {
            const q = document.getElementById('focalSearchInput').value.trim().toUpperCase();
            if (!q) return;
            let found = null;
            if (currentTanks[q]) found = q;
            else {
                const match = Object.keys(currentTanks).find(k => k.includes(q) || k.replace('T', '').includes(q));
                if (match) found = match;
            }
            if (found) {
                currentFocalTank = found;
                document.getElementById('focalTankSelect').value = found;
                renderFocalPedigreeTree();
            } else {
                alert(`Tank ID "${q}" not found in facility records.`);
            }
        }

        function createMiniCard(tuid, roleTitle, isHero = false) {
            if (!tuid || !currentTanks[tuid]) {
                return `<div class="ped-card" style="opacity: 0.5; text-align: center; padding: 10px; font-size: 11px; color: var(--text-muted);">
                    ${roleTitle || 'Founder'}<br><b>${tuid || 'Root Stock'}</b>
                </div>`;
            }
            const t = currentTanks[tuid];
            const badgeClass = `badge-${t.line.toLowerCase()}`;
            const inbr = t.inbreeding_f !== undefined ? t.inbreeding_f.toFixed(3) : '0.000';
            
            return `
                <div class="ped-card ${isHero ? 'ped-card-hero' : ''}" onclick="changeFocalTank('${t.tuid}')" style="cursor: pointer;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <strong style="color: #fff; font-size: 13px;">${t.tuid}</strong>
                        <span class="badge ${badgeClass}">${t.line}</span>
                    </div>
                    <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">
                        Gen: <b style="color: var(--accent-blue);">G${t.generation || 0}</b> | F: <b style="color: ${inbr >= 0.25 ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">${inbr}</b>
                    </div>
                    <div style="font-size: 11px; color: var(--text-secondary);">
                        Fish: <b style="color: #fff;">${t.total}</b> (${t.female}♀ / ${t.male}♂)
                    </div>
                    ${roleTitle ? `<div style="font-size: 10px; color: var(--accent-indigo); margin-top: 4px; font-weight: bold;">${roleTitle}</div>` : ''}
                </div>
            `;
        }

        function renderFocalPedigreeTree() {
            const focal = currentTanks[currentFocalTank];
            if (!focal) return;

            // Breadcrumb Trail
            let trail = `<span style="color: var(--accent-blue);">${focal.tuid} (${focal.line})</span>`;
            if (focal.dam_tuid || focal.sire_tuid) {
                trail = `<span style="color: var(--text-secondary);">${focal.sire_tuid || 'Sire'} &times; ${focal.dam_tuid || 'Dam'}</span> &rarr; ` + trail;
            }
            if (focal.derivative_cross) {
                trail += ` <span style="color: var(--accent-indigo);">[Cross ${focal.derivative_cross}]</span>`;
            }
            document.getElementById('focalBreadcrumbTrail').innerHTML = `<b>Lineage Trail:</b> ${trail}`;

            // Hero Card
            document.getElementById('focalHeroGenBadge').innerText = `Gen G${focal.generation || 0}`;
            document.getElementById('treeColFocal').innerHTML = createMiniCard(focal.tuid, 'Focal Target Tank', true);

            // Parents
            const parentsDiv = document.getElementById('treeColParents');
            parentsDiv.innerHTML = '';
            parentsDiv.innerHTML += createMiniCard(focal.sire_tuid, '♂ Sire (Paternal)');
            parentsDiv.innerHTML += createMiniCard(focal.dam_tuid, '♀ Dam (Maternal)');

            // Grandparents
            const gpDiv = document.getElementById('treeColGrandparents');
            gpDiv.innerHTML = '';
            const sire = currentTanks[focal.sire_tuid];
            const dam = currentTanks[focal.dam_tuid];
            gpDiv.innerHTML += createMiniCard(sire ? sire.sire_tuid : null, 'Paternal Grandfather');
            gpDiv.innerHTML += createMiniCard(sire ? sire.dam_tuid : null, 'Paternal Grandmother');
            gpDiv.innerHTML += createMiniCard(dam ? dam.sire_tuid : null, 'Maternal Grandfather');
            gpDiv.innerHTML += createMiniCard(dam ? dam.dam_tuid : null, 'Maternal Grandmother');

            // Offspring
            const offDiv = document.getElementById('treeColOffspring');
            offDiv.innerHTML = '';
            const offList = focal.children || [];
            document.getElementById('treeOffspringCountBadge').innerText = `${offList.length} Tanks`;
            if (offList.length === 0) {
                offDiv.innerHTML = '<div style="color: var(--text-muted); font-size: 11px; padding: 8px;">No direct offspring tanks spawned.</div>';
            } else {
                offList.forEach(ctuid => offDiv.innerHTML += createMiniCard(ctuid, 'F1 Offspring'));
            }

            // Grandchildren
            const gcDiv = document.getElementById('treeColGrandchildren');
            gcDiv.innerHTML = '';
            const gcList = focal.grandchildren || [];
            document.getElementById('treeGrandchildrenCountBadge').innerText = `${gcList.length} Tanks`;
            if (gcList.length === 0) {
                gcDiv.innerHTML = '<div style="color: var(--text-muted); font-size: 11px; padding: 8px;">No F2 grand-offspring.</div>';
            } else {
                gcList.forEach(gctuid => gcDiv.innerHTML += createMiniCard(gctuid, 'F2 Grandchild'));
            }
        }

        function copyLineageTrail() {
            const focal = currentTanks[currentFocalTank];
            if (!focal) return;
            const text = `${focal.tuid} (${focal.line}) | Gen: G${focal.generation || 0} | Sire: ${focal.sire_tuid || 'Root'} | Dam: ${focal.dam_tuid || 'Root'} | Cross: ${focal.derivative_cross || '-'}`;
            navigator.clipboard.writeText(text);
            alert('Lineage trail copied to clipboard:\n' + text);
        }

        // Line Trees
        let activeLineTree = 'AB';
        function selectLineTree(line) {
            activeLineTree = line;
            document.querySelectorAll('.line-tree-btn').forEach(b => b.classList.remove('active'));
            const btn = document.getElementById(`line-tree-btn-${line}`);
            if (btn) btn.classList.add('active');
            renderLineTrees();
        }

        function renderLineTrees() {
            const container = document.getElementById('lineTreeTiersContainer');
            if (!container) return;
            container.innerHTML = '';

            const lineTanks = Object.values(currentTanks).filter(t => t.line === activeLineTree);
            ['AB', 'Casper', 'Fli', 'Gata'].forEach(l => {
                const el = document.getElementById(`lineTreeCount${l}`);
                if (el) el.innerText = Object.values(currentTanks).filter(t => t.line === l).length;
            });

            // Group by generation
            const genMap = {};
            lineTanks.forEach(t => {
                const g = t.generation || 0;
                if (!genMap[g]) genMap[g] = [];
                genMap[g].push(t);
            });

            const sortedGens = Object.keys(genMap).map(Number).sort((a, b) => a - b);
            sortedGens.forEach(gen => {
                const list = genMap[gen];
                const tier = document.createElement('div');
                tier.style.background = 'rgba(15,23,42,0.4)';
                tier.style.border = '1px solid var(--border-color)';
                tier.style.borderRadius = 'var(--radius-md)';
                tier.style.padding = '14px';

                tier.innerHTML = `
                    <div style="font-size: 13px; font-weight: 700; color: var(--accent-blue); margin-bottom: 12px; display: flex; justify-content: space-between;">
                        <span>🧬 Generation G${gen} (${gen === 0 ? 'Founders / Root Stock' : 'Derived Lineage'})</span>
                        <span style="color: var(--text-secondary); font-size: 11px;">${list.length} Tanks</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px;">
                        ${list.map(t => createMiniCard(t.tuid, t.derivative_cross ? `Cross ${t.derivative_cross}` : 'Founder')).join('')}
                    </div>
                `;
                container.appendChild(tier);
            });
        }

        // Collapsible Tree Table
        function renderTreeTable() {
            const tbody = document.getElementById('pedigreeTreeTableBody');
            if (!tbody) return;
            tbody.innerHTML = '';

            const filterLine = document.getElementById('treeTableLineFilter') ? document.getElementById('treeTableLineFilter').value : 'ALL';
            const filterStat = document.getElementById('treeTableStatusFilter') ? document.getElementById('treeTableStatusFilter').value : 'ALL';
            const searchQ = document.getElementById('treeTableSearchInput') ? document.getElementById('treeTableSearchInput').value.trim().toUpperCase() : '';

            let tanks = Object.values(currentTanks);
            if (filterLine !== 'ALL') tanks = tanks.filter(t => t.line === filterLine);
            if (filterStat === 'ACTIVE') tanks = tanks.filter(t => t.status === 'Active');
            if (filterStat === 'EUTH') tanks = tanks.filter(t => t.status === 'Euthanized');
            if (searchQ) tanks = tanks.filter(t => t.tuid.includes(searchQ) || (t.notes && t.notes.toUpperCase().includes(searchQ)));

            tanks.sort((a, b) => a.tuid.localeCompare(b.tuid));

            tanks.forEach(t => {
                const badgeClass = `badge-${t.line.toLowerCase()}`;
                const inbr = t.inbreeding_f !== undefined ? t.inbreeding_f.toFixed(3) : '0.000';
                const parentsStr = (t.sire_tuid || t.dam_tuid) ? `${t.sire_tuid || 'Root'} &times; ${t.dam_tuid || 'Root'}` : 'Root Stock';
                const progenies = t.children ? t.children.join(', ') : '-';

                tbody.innerHTML += `
                    <tr>
                        <td><strong>${t.tuid}</strong> <span class="badge ${badgeClass}" style="margin-left: 6px;">${t.line}</span></td>
                        <td><span class="badge badge-active">G${t.generation || 0}</span></td>
                        <td>${getStatusBadge(t.status)}</td>
                        <td>${t.female}♀ / ${t.male}♂ (<b>${t.total}</b>)</td>
                        <td><b style="color: ${inbr >= 0.25 ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">${inbr}</b></td>
                        <td>${parentsStr}</td>
                        <td style="max-width: 150px; overflow: hidden; text-overflow: ellipsis;" title="${progenies}">${progenies}</td>
                        <td><button class="btn btn-sm btn-outline" onclick="changeFocalTank('${t.tuid}'); switchPedigreeMode('focal');">🎯 Inspect</button></td>
                    </tr>
                `;
            });
        }

        function filterTreeTable() {
            renderTreeTable();
        }

        function exportTreeTableCSV() {
            exportTableToCSV('pedigreeTreeTable', 'colony_pedigree_hierarchy_table');
        }

        // Global Vis.js Network Map
        function renderPedigreeNetwork() {
            const container = document.getElementById('pedigree-network');
            if (!container) return;

            const nodes = [];
            const edges = [];
            const lineFilter = document.getElementById('lineFilter') ? document.getElementById('lineFilter').value : 'ALL';

            const lineColors = {
                'AB': '#38bdf8',
                'Casper': '#c084fc',
                'Fli': '#34d399',
                'Gata': '#fbbf24',
                'DESMA': '#fb7185',
                'Other': '#94a3b8'
            };

            Object.values(currentTanks).forEach(t => {
                if (lineFilter !== 'ALL' && t.line !== lineFilter) return;

                nodes.push({
                    id: t.tuid,
                    label: `${t.tuid}\\n(${t.line})`,
                    color: {
                        background: t.status === 'Active' ? lineColors[t.line] || '#38bdf8' : '#475569',
                        border: '#1e293b'
                    },
                    font: { color: t.status === 'Active' ? '#000000' : '#ffffff', size: 11, face: 'Inter' },
                    shape: 'box',
                    margin: 8
                });

                if (t.sire_tuid && currentTanks[t.sire_tuid]) {
                    edges.push({ from: t.sire_tuid, to: t.tuid, color: { color: '#38bdf8' }, arrows: 'to' });
                }
                if (t.dam_tuid && currentTanks[t.dam_tuid]) {
                    edges.push({ from: t.dam_tuid, to: t.tuid, color: { color: '#f472b6' }, dashes: true, arrows: 'to' });
                }
            });

            const data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
            const options = {
                layout: { hierarchical: { direction: 'UD', sortMethod: 'directed', levelSeparation: 80, nodeSpacing: 120 } },
                physics: { hierarchicalRepulsion: { nodeDistance: 120 } },
                interaction: { hover: true, zoomView: true, dragView: true }
            };

            if (pedigreeNetworkInstance) pedigreeNetworkInstance.destroy();
            pedigreeNetworkInstance = new vis.Network(container, data, options);

            pedigreeNetworkInstance.on('click', function(params) {
                if (params.nodes.length > 0) {
                    const selectedTuid = params.nodes[0];
                    openTankModal(selectedTuid);
                }
            });
        }

        function filterPedigreeByLine() {
            renderPedigreeNetwork();
        }

        function searchPedigreeNode() {
            const q = document.getElementById('pedigreeSearch').value.trim().toUpperCase();
            if (!q || !pedigreeNetworkInstance) return;
            try {
                pedigreeNetworkInstance.focus(q, { scale: 1.2, animation: true });
                pedigreeNetworkInstance.selectNodes([q]);
            } catch(e) {
                alert(`Tank "${q}" not found in current network view.`);
            }
        }

        function resetPedigreeView() {
            if (pedigreeNetworkInstance) pedigreeNetworkInstance.fit({ animation: true });
        }

        // TAB 3: TURNOVER & COLONY RENEWAL JS
        function renderTurnoverTable() {
            const tbody = document.getElementById('turnoverTableBody');
            if (!tbody) return;
            tbody.innerHTML = '';

            const urgencyFilter = document.getElementById('turnoverFilter') ? document.getElementById('turnoverFilter').value : 'ALL';
            const lineFilter = document.getElementById('turnoverLineFilter') ? document.getElementById('turnoverLineFilter').value : 'ALL';

            let tanks = Object.values(currentTanks).filter(t => t.status === 'Active');
            if (lineFilter !== 'ALL') tanks = tanks.filter(t => t.line === lineFilter);

            tanks.forEach(t => {
                const days = t.days_to_turnover;
                const urg = t.turnover_urgency || 'N/A';

                if (urgencyFilter === 'OVERDUE' && urg !== 'OVERDUE') return;
                if (urgencyFilter === 'SOON' && !urg.includes('DUE SOON')) return;
                if (urgencyFilter === 'UPCOMING' && !urg.includes('UPCOMING')) return;
                if (urgencyFilter === 'FUTURE' && !urg.includes('FUTURE')) return;

                let badgeClass = 'badge-active';
                if (urg === 'OVERDUE') badgeClass = 'badge-critical';
                else if (urg.includes('DUE SOON')) badgeClass = 'badge-high';
                else if (urg.includes('UPCOMING')) badgeClass = 'badge-medium';

                const daysTxt = days !== null ? (days < 0 ? `<b style="color: var(--accent-rose);">${Math.abs(days)}d past</b>` : `<b>${days}d</b>`) : '-';
                const actionTxt = urg === 'OVERDUE' ? '🚨 Schedule replacement mating immediately' : (urg.includes('DUE SOON') ? '⚠️ Plan next-generation cross' : 'Routine husbandry');

                tbody.innerHTML += `
                    <tr>
                        <td><strong>${t.tuid}</strong></td>
                        <td>${getStatusBadge(t.status)}</td>
                        <td><span class="badge badge-${t.line.toLowerCase()}">${t.line}</span></td>
                        <td>${t.female}♀ / ${t.male}♂ (<b>${t.total}</b>)</td>
                        <td>${t.dob || '-'}</td>
                        <td>${t.turnover_date_resolved || t.turnover_date || '-'}</td>
                        <td>${daysTxt}</td>
                        <td><span class="badge ${badgeClass}">${urg}</span></td>
                        <td>${actionTxt}</td>
                        <td><button class="btn btn-sm btn-outline" onclick="openTankModal('${t.tuid}')">Inspect</button></td>
                    </tr>
                `;
            });
        }

        // TAB 4: CROSSES & NURSERY REGISTRY JS
        function renderCrossesRegistry() {
            const tbody = document.getElementById('crossesRegistryTableBody');
            if (!tbody) return;
            tbody.innerHTML = '';

            const q = document.getElementById('crossRegSearch') ? document.getElementById('crossRegSearch').value.trim().toUpperCase() : '';
            let list = currentCrosses;
            if (q) {
                list = list.filter(c => c.cuid.includes(q) || c.dam.includes(q) || c.sire.includes(q) || (c.offspring_tanks && c.offspring_tanks.join(',').includes(q)));
            }

            list.forEach(c => {
                const nClutches = c.nursery_clutches && c.nursery_clutches.length > 0 ? c.nursery_clutches.join(', ') : '-';
                const offTanks = c.offspring_tanks && c.offspring_tanks.length > 0 ? c.offspring_tanks.join(', ') : '-';

                tbody.innerHTML += `
                    <tr>
                        <td><strong style="color: var(--accent-indigo);">${c.cuid}</strong></td>
                        <td>${c.mating_date}</td>
                        <td><strong>${c.dam}</strong></td>
                        <td><strong>${c.sire}</strong></td>
                        <td><span class="badge" style="background: rgba(129, 140, 248, 0.15); color: #818cf8; border: 1px solid rgba(129, 140, 248, 0.3);">${c.line_pair}</span></td>
                        <td><span class="badge" style="background: rgba(192, 132, 252, 0.15); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3);">${nClutches}</span></td>
                        <td><b>${c.nursery_count || 0}</b> fish</td>
                        <td>${c.nursery_grad_date || '-'}</td>
                        <td style="color: var(--accent-emerald); font-weight: 600;">${offTanks}</td>
                    </tr>
                `;
            });
        }

        // TAB 5: COLONY ALERTS JS
        function renderColonyAlerts() {
            const container = document.getElementById('alertsFeedContainer');
            if (!container) return;
            container.innerHTML = '';

            const sevFilter = document.getElementById('alertSeverityFilter') ? document.getElementById('alertSeverityFilter').value : 'ALL';
            const catFilter = document.getElementById('alertCategoryFilter') ? document.getElementById('alertCategoryFilter').value : 'ALL';

            let list = currentAlerts;
            if (sevFilter !== 'ALL') list = list.filter(a => a.severity === sevFilter);
            if (catFilter !== 'ALL') list = list.filter(a => a.category === catFilter);

            document.getElementById('tabBadgeAlerts').innerText = currentAlerts.length;

            if (list.length === 0) {
                container.innerHTML = '<div style="color: var(--text-muted); font-size: 13px; padding: 20px; text-align: center;">No active colony alerts matching selected filter.</div>';
                return;
            }

            list.forEach(alt => {
                let borderCol = 'var(--accent-blue)';
                let badgeClass = 'badge-info';
                if (alt.severity === 'CRITICAL') { borderCol = 'var(--accent-rose)'; badgeClass = 'badge-critical'; }
                else if (alt.severity === 'HIGH') { borderCol = 'var(--accent-amber)'; badgeClass = 'badge-high'; }
                else if (alt.severity === 'MEDIUM') { borderCol = 'var(--accent-amber)'; badgeClass = 'badge-medium'; }

                const card = document.createElement('div');
                card.style.background = 'rgba(15, 23, 42, 0.6)';
                card.style.border = '1px solid var(--border-color)';
                card.style.borderLeft = `4px solid ${borderCol}`;
                card.style.borderRadius = 'var(--radius-md)';
                card.style.padding = '14px 18px';
                card.style.display = 'flex';
                card.style.justifyContent = 'space-between';
                card.style.alignItems = 'center';
                card.style.flexWrap = 'wrap';
                card.style.gap = '12px';

                card.innerHTML = `
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="badge ${badgeClass}">${alt.severity}</span>
                            <strong style="color: #fff; font-size: 14px;">${alt.tuid}</strong>
                            <span style="font-size: 12px; color: var(--text-secondary);">• ${alt.line} • <b>${alt.category}</b></span>
                        </div>
                        <p style="font-size: 13px; color: var(--text-primary); margin-top: 2px;">${alt.message}</p>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid var(--border-color); padding: 8px 12px; border-radius: 6px; font-size: 12px; color: var(--accent-emerald);">
                            <b>Action:</b> ${alt.action}
                        </div>
                        <button class="btn btn-sm btn-outline" onclick="openTankModal('${alt.tuid}')">Inspect</button>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        // TAB 6: Cross-Pairing Synergies
        function renderCrosses() {
            const tbody = document.getElementById('pairSynergyTableBody');
            if (!tbody) return;
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

        // TAB 7: Longitudinal Trends
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

            const sortedMonths = Object.keys(monthlyMap).sort();
            const eggData = [], liveData = [], srData = [];

            sortedMonths.forEach(m => {
                const st = monthlyMap[m];
                eggData.push(st.eggs);
                liveData.push(st.live);
                srData.push(st.validSpawns > 0 ? (st.sr24Sum / st.validSpawns).toFixed(1) : 0);
            });

            new Chart(document.getElementById('chartMonthlyEggs'), {
                type: 'line',
                data: {
                    labels: sortedMonths,
                    datasets: [
                        { label: 'Total Eggs Spawned (0hpf)', data: eggData, borderColor: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.1)', fill: true, tension: 0.3 },
                        { label: 'Viable Embryos (24hpf)', data: liveData, borderColor: '#34d399', backgroundColor: 'rgba(52, 211, 153, 0.1)', fill: true, tension: 0.3 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: { legend: { labels: { color: '#f8fafc' } } }
                }
            });

            new Chart(document.getElementById('chartMonthlySR'), {
                type: 'line',
                data: {
                    labels: sortedMonths,
                    datasets: [{ label: 'Monthly 24hpf Viability Rate (%)', data: srData, borderColor: '#fbbf24', tension: 0.3, pointRadius: 4, pointBackgroundColor: '#fbbf24' }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { min: 0, max: 100, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: { legend: { labels: { color: '#f8fafc' } } }
                }
            });
        }

        // TAB 8: Parental Age vs Fecundity Curves
        function renderAgeCurves() {
            const ageBuckets = {};
            currentEvents.forEach(ev => {
                if (ev.parent_age_months !== null && ev.parent_age_months >= 2 && ev.parent_age_months <= 30) {
                    const b = ev.parent_age_months;
                    if (!ageBuckets[b]) ageBuckets[b] = { eggs: 0, spawns: 0, live: 0, sr24Sum: 0, validSpawns: 0 };
                    ageBuckets[b].eggs += ev.eggs_0h;
                    ageBuckets[b].spawns++;
                    ageBuckets[b].live += ev.live_24h;
                    if (ev.eggs_0h > 0) {
                        ageBuckets[b].validSpawns++;
                        ageBuckets[b].sr24Sum += ev.sr_24h;
                    }
                }
            });

            const sortedAges = Object.keys(ageBuckets).map(Number).sort((a,b) => a - b);
            const clutchData = [], srData = [];

            sortedAges.forEach(age => {
                const b = ageBuckets[age];
                clutchData.push(b.spawns > 0 ? (b.eggs / b.spawns).toFixed(1) : 0);
                srData.push(b.validSpawns > 0 ? (b.sr24Sum / b.validSpawns).toFixed(1) : 0);
            });

            new Chart(document.getElementById('chartAgeFecundity'), {
                type: 'line',
                data: {
                    labels: sortedAges.map(a => a + ' mo'),
                    datasets: [{ label: 'Average Clutch Size (Eggs/Spawn)', data: clutchData, borderColor: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.15)', fill: true, tension: 0.3 }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: { legend: { labels: { color: '#f8fafc' } } }
                }
            });

            new Chart(document.getElementById('chartAgeViability'), {
                type: 'line',
                data: {
                    labels: sortedAges.map(a => a + ' mo'),
                    datasets: [{ label: '24hpf Survival Rate (%)', data: srData, borderColor: '#34d399', tension: 0.3, pointRadius: 4, pointBackgroundColor: '#34d399' }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { min: 0, max: 100, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: { legend: { labels: { color: '#f8fafc' } } }
                }
            });
        }

        // TAB 9: Scorecards
        function renderScorecards() {
            const tbody = document.getElementById('scorecardTableBody');
            if (!tbody) return;
            tbody.innerHTML = '';

            const lineFilter = document.getElementById('scorecardLineFilter').value;
            const sexFilter = document.getElementById('scorecardSexFilter').value;
            const statusFilter = document.getElementById('scorecardStatusFilter').value;
            const search = document.getElementById('scorecardSearch').value.trim().toUpperCase();

            let list = Object.values(currentTanks);
            if (lineFilter !== 'ALL') list = list.filter(t => t.line === lineFilter);
            if (sexFilter !== 'ALL') list = list.filter(t => t.sex_type === sexFilter);
            if (statusFilter !== 'ALL') list = list.filter(t => t.status === statusFilter);
            if (search) list = list.filter(t => t.tuid.includes(search));

            list.sort((a, b) => b.total_live_24h - a.total_live_24h);

            list.forEach((t, idx) => {
                const sexBadge = getSexBadge(t.sex_type);
                const statusBadge = getStatusBadge(t.status);
                const lineBadge = `<span class="badge badge-${t.line.toLowerCase()}">${t.line}</span>`;

                tbody.innerHTML += `
                    <tr>
                        <td><strong>#${idx + 1}</strong></td>
                        <td><strong>${t.tuid}</strong></td>
                        <td>${lineBadge}</td>
                        <td>${sexBadge}</td>
                        <td>${statusBadge}</td>
                        <td>${t.female}♀ / ${t.male}♂ (<b>${t.total}</b>)</td>
                        <td>${t.total_spawns}</td>
                        <td>${t.total_eggs_0h.toLocaleString()}</td>
                        <td><strong>${t.avg_clutch}</strong></td>
                        <td><span style="color: var(--accent-emerald); font-weight: bold;">${t.avg_sr_24h}%</span></td>
                        <td><strong>${t.total_live_24h.toLocaleString()}</strong></td>
                        <td>${t.last_spawn || '-'}</td>
                        <td class="no-export">
                            <button class="btn btn-sm btn-outline" onclick="openTankModal('${t.tuid}')">Inspect</button>
                        </td>
                    </tr>
                `;
            });
        }

        // TAB 10: Inventory
        function renderInventory() {
            const tbody = document.getElementById('inventoryTableBody');
            if (!tbody) return;
            tbody.innerHTML = '';

            const lineFilter = document.getElementById('invLineFilter').value;
            const sexFilter = document.getElementById('invSexFilter').value;
            const statusFilter = document.getElementById('invStatusFilter').value;
            const search = document.getElementById('invSearch').value.trim().toUpperCase();

            let list = Object.values(currentTanks);
            if (lineFilter !== 'ALL') list = list.filter(t => t.line === lineFilter);
            if (sexFilter !== 'ALL') list = list.filter(t => t.sex_type === sexFilter);
            if (statusFilter !== 'ALL') list = list.filter(t => t.status === statusFilter);
            if (search) list = list.filter(t => t.tuid.includes(search) || (t.notes && t.notes.toUpperCase().includes(search)) || (t.genotype && t.genotype.toUpperCase().includes(search)) || (t.derivative_cross && t.derivative_cross.toUpperCase().includes(search)));

            list.sort((a, b) => a.tuid.localeCompare(b.tuid));

            list.forEach(t => {
                const sexBadge = getSexBadge(t.sex_type);
                const statusBadge = getStatusBadge(t.status);
                const lineBadge = `<span class="badge badge-${t.line.toLowerCase()}">${t.line}</span>`;

                tbody.innerHTML += `
                    <tr>
                        <td><strong>${t.tuid}</strong></td>
                        <td><span style="color: var(--accent-indigo); font-weight: bold;">${t.derivative_cross || '-'}</span></td>
                        <td>${t.genotype || t.line}</td>
                        <td style="max-width: 150px; overflow: hidden; text-overflow: ellipsis;" title="${t.notes || ''}">${t.notes || '-'}</td>
                        <td>${lineBadge}</td>
                        <td>${sexBadge}</td>
                        <td>${t.female}</td>
                        <td>${t.male}</td>
                        <td><strong>${t.total}</strong></td>
                        <td>${t.tank_size || '-'}</td>
                        <td>${t.protocol || '-'}</td>
                        <td>${t.dob || '-'}</td>
                        <td>${t.turnover_date || '-'}</td>
                        <td>${t.age_months !== null ? t.age_months + ' mo' : '-'}</td>
                        <td>${statusBadge}</td>
                        <td>${t.total_spawns}</td>
                        <td>${t.total_eggs_0h.toLocaleString()}</td>
                        <td class="no-export">
                            <button class="btn btn-sm btn-outline" onclick="openTankModal('${t.tuid}')">Profile</button>
                        </td>
                    </tr>
                `;
            });
        }

        // TAB 11: Audit Tab
        function renderAuditTab() {
            const tbody = document.getElementById('auditReservoirTableBody');
            if (!tbody) return;
            tbody.innerHTML = '';

            const singleSex = Object.values(currentTanks).filter(t => t.sex_type === 'Female-Only' || t.sex_type === 'Male-Only');
            singleSex.sort((a, b) => a.tuid.localeCompare(b.tuid));

            singleSex.forEach(t => {
                const sexBadge = getSexBadge(t.sex_type);
                const statusBadge = getStatusBadge(t.status);
                const lineBadge = `<span class="badge badge-${t.line.toLowerCase()}">${t.line}</span>`;

                const partners = {};
                t.spawn_history.forEach(h => {
                    const mate = h.in_tank ? 'In-Tank' : 'Pair-Wise Cross';
                    partners[mate] = (partners[mate] || 0) + 1;
                });
                const pKeys = Object.keys(partners).slice(0, 3).join(', ') || 'None recorded';

                tbody.innerHTML += `
                    <tr>
                        <td><strong>${t.tuid}</strong></td>
                        <td>${lineBadge}</td>
                        <td>${sexBadge}</td>
                        <td>${t.female}♀ / ${t.male}♂ (<b>${t.total}</b>)</td>
                        <td>${statusBadge}</td>
                        <td style="max-width: 140px; overflow: hidden; text-overflow: ellipsis;" title="${t.notes || ''}">${t.notes || '-'}</td>
                        <td>${pKeys}</td>
                        <td><strong>${t.total_spawns}</strong></td>
                        <td>${t.total_eggs_0h.toLocaleString()}</td>
                    </tr>
                `;
            });
        }

        // TAB 12: Mating Planner
        function calculatePlanner() {
            const line = document.getElementById('planLine').value;
            const targetYield = parseInt(document.getElementById('planEmbryoTarget').value) || 1000;

            const relevantPairs = currentPairs.filter(p => p.line === line);
            const femaleReservoirs = Object.values(currentTanks).filter(t => t.line === line && t.status === 'Active' && t.sex_type === 'Female-Only' && t.female > 0);
            const maleReservoirs = Object.values(currentTanks).filter(t => t.line === line && t.status === 'Active' && t.sex_type === 'Male-Only' && t.male > 0);

            femaleReservoirs.sort((a, b) => b.female - a.female);
            maleReservoirs.sort((a, b) => b.male - a.male);

            let recommendationHTML = '';

            if (relevantPairs.length > 0) {
                const topPair = relevantPairs[0];
                const expectedPerSpawn = topPair.avg_clutch * (topPair.avg_sr24 / 100);
                const neededSpawns = Math.ceil(targetYield / Math.max(expectedPerSpawn, 1));

                recommendationHTML += `
                    <div class="recommendation-box">
                        <span style="font-size: 11px; font-weight: bold; color: var(--accent-emerald); text-transform: uppercase;">Top Cross Recommendation (Pair-Wise)</span>
                        <div style="font-size: 18px; font-weight: bold; color: #fff; margin-top: 4px;">${topPair.pair_key} (${line})</div>
                        <div style="font-size: 12px; color: var(--text-secondary); margin-top: 6px; line-height: 1.5;">
                            • Historical Fecundity: <b>${topPair.avg_clutch}</b> eggs/spawn | 24hpf Viability: <b style="color: var(--accent-emerald);">${topPair.avg_sr24}%</b><br>
                            • To reach target <b>${targetYield.toLocaleString()}</b> viable embryos, set up <strong>${neededSpawns}</strong> mating crossing tanks.
                        </div>
                    </div>
                `;
            }

            if (femaleReservoirs.length > 0 && maleReservoirs.length > 0) {
                recommendationHTML += `
                    <div class="recommendation-box" style="border-color: var(--accent-blue);">
                        <span style="font-size: 11px; font-weight: bold; color: var(--accent-blue); text-transform: uppercase;">Single-Sex Reservoir Setup</span>
                        <div style="font-size: 16px; font-weight: bold; color: #fff; margin-top: 4px;">
                            ♀ ${femaleReservoirs[0].tuid} (${femaleReservoirs[0].female} females) &times; ♂ ${maleReservoirs[0].tuid} (${maleReservoirs[0].male} males)
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary); margin-top: 6px;">
                            Dedicated single-sex separation ensures high egg yield and zero in-tank drop.
                        </div>
                    </div>
                `;
            }

            document.getElementById('plannerResultBox').innerHTML = recommendationHTML || '<div style="color: var(--text-muted); font-size: 13px;">No data available for this line combination.</div>';
        }

        // TAB 13: Raw Events
        function renderRawEvents() {
            const tbody = document.getElementById('rawEventsTableBody');
            if (!tbody) return;
            tbody.innerHTML = '';

            const year = document.getElementById('rawYearFilter').value;
            const line = document.getElementById('rawLineFilter').value;
            const search = document.getElementById('rawSearch').value.trim().toUpperCase();

            let list = currentEvents;
            if (year !== 'ALL') list = list.filter(e => e.year === parseInt(year));
            if (line !== 'ALL') list = list.filter(e => e.line === line);
            if (search) list = list.filter(e => (e.tank_id && e.tank_id.includes(search)) || (e.date && e.date.includes(search)) || (e.staff && e.staff.toUpperCase().includes(search)) || (e.notes && e.notes.toUpperCase().includes(search)));

            list.slice(0, 100).forEach(e => {
                const badgeClass = `badge-${e.line.toLowerCase()}`;
                tbody.innerHTML += `
                    <tr>
                        <td>${e.date}</td>
                        <td><span class="badge ${badgeClass}">${e.line}</span></td>
                        <td>${e.in_tank ? 'In-Tank' : 'Pair-Wise'}</td>
                        <td><strong>${e.tank_id}</strong></td>
                        <td>${e.eggs_0h}</td>
                        <td>${e.sr_0h}%</td>
                        <td>${e.sr_24h}%</td>
                        <td><strong>${e.live_24h}</strong></td>
                        <td>${e.staff || '-'}</td>
                    </tr>
                `;
            });
        }

        // Modal for Tank Profile
        function openTankModal(tuid) {
            const t = currentTanks[tuid];
            if (!t) return;

            document.getElementById('modalTitle').innerText = `${t.tuid} [${t.line}] — Facility Profile & Spawning History`;
            const mbody = document.getElementById('modalBody');

            let historyRows = '';
            t.spawn_history.forEach(h => {
                historyRows += `
                    <tr>
                        <td>${h.date}</td>
                        <td>${h.in_tank ? 'In-Tank' : 'Pair-Wise'}</td>
                        <td>${h.eggs_0h}</td>
                        <td>${h.sr_0h}%</td>
                        <td>${h.sr_24h}%</td>
                        <td><strong>${h.live_24h}</strong></td>
                        <td>${h.staff || '-'}</td>
                    </tr>
                `;
            });

            mbody.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Genotype / Strain</span>
                        <div style="font-weight: bold; margin-top: 4px; color: #fff;">${t.genotype || t.line}</div>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Derivative Cross</span>
                        <div style="font-weight: bold; margin-top: 4px; color: var(--accent-indigo);">${t.derivative_cross || 'Root Stock'}</div>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Sex Composition</span>
                        <div style="margin-top: 4px;">${getSexBadge(t.sex_type)}</div>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Adult Inventory</span>
                        <div style="font-weight: bold; margin-top: 4px;">${t.female}♀ / ${t.male}♂ (Total: ${t.total})</div>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">DOB</span>
                        <div style="font-weight: bold; margin-top: 4px;">${t.dob || '-'}</div>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Turnover Deadline</span>
                        <div style="font-weight: bold; margin-top: 4px;">${t.turnover_date_resolved || t.turnover_date || '-'}</div>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Generation & Inbreeding (F)</span>
                        <div style="font-weight: bold; margin-top: 4px; color: var(--accent-blue);">G${t.generation || 0} (F = ${t.inbreeding_f !== undefined ? t.inbreeding_f.toFixed(3) : '0.000'})</div>
                    </div>
                </div>

                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 12px; border-radius: 6px;">
                    <span style="font-size: 11px; color: var(--text-secondary);">FileMaker Lineage Notes:</span>
                    <p style="font-size: 13px; color: #fff; margin-top: 4px; font-family: monospace;">${t.notes || 'None recorded'}</p>
                </div>

                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                    <div style="background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.2); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Lifetime Spawns</span>
                        <div style="font-size: 18px; font-weight: bold; color: var(--accent-blue); margin-top: 2px;">${t.total_spawns}</div>
                    </div>
                    <div style="background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.2); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">Total Eggs</span>
                        <div style="font-size: 18px; font-weight: bold; color: var(--accent-amber); margin-top: 2px;">${t.total_eggs_0h.toLocaleString()}</div>
                    </div>
                    <div style="background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.2); padding: 12px; border-radius: 6px;">
                        <span style="font-size: 11px; color: var(--text-secondary);">24hpf Viability</span>
                        <div style="font-size: 18px; font-weight: bold; color: var(--accent-emerald); margin-top: 2px;">${t.avg_sr_24h}% (${t.total_live_24h.toLocaleString()})</div>
                    </div>
                </div>

                <h4 style="font-size: 14px; margin-bottom: 10px;">Individual Spawning History (${t.spawn_history.length} runs)</h4>
                <div class="table-responsive" style="max-height: 250px; overflow-y: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Type</th>
                                <th>Eggs (0H)</th>
                                <th>SR (0H)</th>
                                <th>SR (24H)</th>
                                <th>Viable (24H)</th>
                                <th>Staff</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${historyRows || '<tr><td colspan="7" style="text-align: center; color: var(--text-secondary);">No spawning events recorded.</td></tr>'}
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

            if (tabId === 'tab-pedigree') populateFocalDropdown(), renderFocalPedigreeTree();
            else if (tabId === 'tab-turnover') renderTurnoverTable();
            else if (tabId === 'tab-crosses-reg') renderCrossesRegistry();
            else if (tabId === 'tab-alerts') renderColonyAlerts();
            else if (tabId === 'tab-crosses') renderCrosses();
            else if (tabId === 'tab-trends') renderTrends();
            else if (tabId === 'tab-age-curves') renderAgeCurves();
            else if (tabId === 'tab-scorecards') renderScorecards();
            else if (tabId === 'tab-inventory') renderInventory();
            else if (tabId === 'tab-audit') renderAuditTab();
            else if (tabId === 'tab-planner') calculatePlanner();
            else if (tabId === 'tab-raw-events') renderRawEvents();
        }

        window.onload = function() {
            renderBenchmarks();
            populateFocalDropdown();
            renderFocalPedigreeTree();
            renderTurnoverTable();
            renderCrossesRegistry();
            renderColonyAlerts();
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

    out_colony = os.path.join(labels_dir, 'colony.html')
    with open(out_colony, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f'Wrote {out_colony}')

    out_breeding = os.path.join(labels_dir, 'breeding.html')
    with open(out_breeding, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f'Wrote {out_breeding}')

if __name__ == '__main__':
    generate_dashboard()
