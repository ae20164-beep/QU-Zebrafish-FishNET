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
    <title>FishNET Facility Reproductive & Colony Intelligence System</title>
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
        
        .btn-blue {
            background: rgba(56, 189, 248, 0.2);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.4);
        }
        .btn-blue:hover {
            background: rgba(56, 189, 248, 0.35);
        }

        .btn-emerald {
            background: rgba(52, 211, 153, 0.2);
            color: #34d399;
            border: 1px solid rgba(52, 211, 153, 0.4);
        }
        .btn-emerald:hover {
            background: rgba(52, 211, 153, 0.35);
        }

        .btn-purple {
            background: rgba(192, 132, 252, 0.2);
            color: #c084fc;
            border: 1px solid rgba(192, 132, 252, 0.4);
        }
        .btn-purple:hover {
            background: rgba(192, 132, 252, 0.35);
        }

        .ocr-dropzone {
            border: 2px dashed rgba(56, 189, 248, 0.4);
            background: rgba(56, 189, 248, 0.04);
            border-radius: var(--radius-md);
            padding: 24px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .ocr-dropzone:hover {
            border-color: var(--accent-blue);
            background: rgba(56, 189, 248, 0.08);
        }

        .cloud-badge {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 6px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 6px;
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
        
        select, input[type="text"], input[type="number"], input[type="date"], textarea {
            background: #0f172a;
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            font-size: 12.5px;
            outline: none;
        }
        
        select:focus, input[type="text"]:focus, input[type="number"]:focus, input[type="date"]:focus, textarea:focus {
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
            cursor: pointer;
            user-select: none;
            position: relative;
            transition: all 0.15s ease;
        }
        
        th:not(.no-sort):not(.no-export):hover {
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
        }
        
        th.no-sort, th.no-export {
            cursor: default;
        }
        
        th:not(.no-sort):not(.no-export)::after {
            content: " ⇅";
            opacity: 0.35;
            font-size: 11px;
            margin-left: 6px;
            display: inline-block;
            transition: opacity 0.15s ease, color 0.15s ease;
        }
        
        th:not(.no-sort):not(.no-export):hover::after {
            opacity: 0.9;
            color: #38bdf8;
        }
        
        th.sorted-asc::after {
            content: " ▲" !important;
            opacity: 1 !important;
            color: #38bdf8 !important;
        }
        
        th.sorted-desc::after {
            content: " ▼" !important;
            opacity: 1 !important;
            color: #38bdf8 !important;
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
        
        .badge-ab { background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); }
        .badge-casper { background: rgba(251, 191, 36, 0.15); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }
        .badge-fli { background: rgba(244, 114, 182, 0.15); color: #f472b6; border: 1px solid rgba(244, 114, 182, 0.3); }
        .badge-gata { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
        
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

        /* Intelligent Mating Planner Modern Styles */
        .planner-kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        .planner-kpi-box {
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            position: relative;
        }
        .planner-kpi-box.emerald {
            border-color: rgba(16, 185, 129, 0.4);
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(15, 23, 42, 0.7) 100%);
        }
        .planner-kpi-box.blue {
            border-color: rgba(56, 189, 248, 0.4);
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(15, 23, 42, 0.7) 100%);
        }
        .planner-kpi-box.purple {
            border-color: rgba(168, 85, 247, 0.4);
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(15, 23, 42, 0.7) 100%);
        }
        .planner-options-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }
        .planner-plan-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            box-shadow: var(--shadow-card);
            transition: all 0.2s ease;
        }
        .planner-plan-card:hover {
            border-color: var(--accent-blue);
            box-shadow: 0 4px 20px rgba(56, 189, 248, 0.15);
        }
        .planner-plan-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .planner-match-box {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: var(--radius-md);
            padding: 16px;
            gap: 12px;
        }
        .planner-fish-entity {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .planner-protocol-box {
            background: rgba(255, 255, 255, 0.02);
            border-left: 3px solid var(--accent-blue);
            padding: 12px 14px;
            border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
            font-size: 12px;
            color: var(--text-secondary);
            line-height: 1.6;
        }

        /* Form Grid */
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .form-group label {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
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
            <p>Unified Zebrafish Platform (2024–2026) | 183 Tanks • 2,233 Spawning Events • 1,252,045 Eggs • 72 Crosses • Live Cloud Database</p>
        </div>
        <div class="header-controls">
            <span class="cloud-badge" id="cloudStatusBadge">🟢 Cloud: Google Sheets Live</span>
            <button class="btn btn-outline" onclick="fetchLatestCloudData()">🔄 Refresh Cloud</button>
            <button class="btn btn-outline" onclick="exportBreedingJSON()">💾 Export JSON</button>
            <button class="btn btn-outline" onclick="exportBreedingCSV()">📥 Export Master CSV</button>
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
        <button class="tab-btn" onclick="switchTab('tab-trends')">📈 Longitudinal Trends & Climate Seasonality</button>
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
                        <button onclick="selectLineTree('AB')" id="line-tree-btn-AB" class="line-tree-btn active">🟢 AB Lineage Tree (<span id="lineTreeCountAB">0</span>)</button>
                        <button onclick="selectLineTree('Casper')" id="line-tree-btn-Casper" class="line-tree-btn">🟡 Casper Lineage Tree (<span id="lineTreeCountCasper">0</span>)</button>
                        <button onclick="selectLineTree('Fli')" id="line-tree-btn-Fli" class="line-tree-btn">🌸 Fli Lineage Tree (<span id="lineTreeCountFli">0</span>)</button>
                        <button onclick="selectLineTree('Gata')" id="line-tree-btn-Gata" class="line-tree-btn">🔵 Gata Lineage Tree (<span id="lineTreeCountGata">0</span>)</button>
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
                    <span class="card-title">⏳ Colony Turnover Schedule & 18-Month Lifespan Renewal Plan</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Zebrafish facility compliance: 18-month (540 days) post-DOB lifecycle management & renewal</span>
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
                        <option value="OVERDUE">🚨 Overdue Only (>18 Months)</option>
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
                            <th>Action</th>
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
                    <span style="font-size: 12px; color: var(--text-secondary);">Empirical performance of single-sex reservoir crosses and pair-wise matings (135 total historical pairs)</span>
                </div>
                <div class="card-header-actions">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('pairSynergyTable', 'cross_pairing_synergies_matrix')">📥 Export Table (CSV)</button>
                </div>
            </div>
            <div class="filter-bar" style="margin-bottom: 16px;">
                <div class="filter-group">
                    <input type="text" id="crossPairSearch" placeholder="Search Pair (e.g. T0135, Casper)..." oninput="renderCrosses()" style="width: 240px;">
                </div>
                <div class="filter-group">
                    <span class="filter-label">Line:</span>
                    <select id="crossPairLineFilter" onchange="renderCrosses()">
                        <option value="ALL">All Lines</option>
                        <option value="AB">AB</option>
                        <option value="Casper">Casper</option>
                        <option value="Fli">Fli</option>
                        <option value="Gata">Gata</option>
                        <option value="Outcross">Outcrosses</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Display Rows:</span>
                    <select id="crossPairPageSize" onchange="renderCrosses()">
                        <option value="ALL">All 135 Pairs</option>
                        <option value="50">Top 50 Pairs</option>
                        <option value="100">Top 100 Pairs</option>
                    </select>
                </div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-left: auto;" id="crossPairCountBadge">
                    Showing 135 pairs
                </div>
            </div>
            <div class="table-responsive" style="max-height: 650px; overflow-y: auto;">
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

            <!-- Seasonal & Qatar Climate Dynamics (Paper 2 Q7) -->
            <div style="margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border-color);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <h3 style="font-size: 16px; font-weight: 700; color: var(--text-primary);">☀️ Seasonal & Qatar Climate Dynamics (Harmonic Fourier Analysis - Paper 2 Q7)</h3>
                        <p style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">Empirical Investigation of Indoor RAS Embryo Viability across Doha Climate Cycles (2,198 Validated Spawns)</p>
                    </div>
                    <span class="badge" style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); font-size: 12px; padding: 4px 10px;">ANOVA F = 21.601 (p &lt; 0.0001)</span>
                </div>
                
                <!-- 4-Season Metric Cards -->
                <div class="planner-kpi-grid">
                    <div class="planner-kpi-box blue">
                        <span class="planner-kpi-label">❄️ Winter (Dec – Feb)</span>
                        <span class="planner-kpi-val" style="color: #38bdf8; font-size: 20px; font-weight: 700;">62.9% SR</span>
                        <span class="planner-kpi-sub" style="font-size: 11px; color: var(--text-secondary);">488 Spawns • Trough Period (Feb: 59.0%)</span>
                    </div>
                    <div class="planner-kpi-box emerald">
                        <span class="planner-kpi-label">🌱 Spring (Mar – May)</span>
                        <span class="planner-kpi-val" style="color: #34d399; font-size: 20px; font-weight: 700;">65.4% SR</span>
                        <span class="planner-kpi-sub" style="font-size: 11px; color: var(--text-secondary);">511 Spawns • Rebound Window</span>
                    </div>
                    <div class="planner-kpi-box amber">
                        <span class="planner-kpi-label">☀️ Summer (Jun – Aug)</span>
                        <span class="planner-kpi-val" style="color: #fbbf24; font-size: 20px; font-weight: 700;">69.9% SR</span>
                        <span class="planner-kpi-sub" style="font-size: 11px; color: var(--text-secondary);">640 Spawns • High Viability</span>
                    </div>
                    <div class="planner-kpi-box purple">
                        <span class="planner-kpi-label">🍂 Autumn (Sep – Nov)</span>
                        <span class="planner-kpi-val" style="color: #c084fc; font-size: 20px; font-weight: 700;">72.4% SR</span>
                        <span class="planner-kpi-sub" style="font-size: 11px; color: var(--text-secondary);">559 Spawns • Peak Period (Aug/Sep: 76.0%)</span>
                    </div>
                </div>

                <!-- Mathematical Harmonic Model & Operational Guide -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-top: 16px;">
                    <div style="background: rgba(15, 23, 42, 0.7); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
                        <h4 style="font-size: 14px; margin-bottom: 8px; color: #38bdf8;">📐 Harmonic Sinusoidal Fourier Equation</h4>
                        <div style="font-family: monospace; font-size: 12px; color: #f8fafc; background: rgba(0,0,0,0.4); padding: 10px 12px; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #38bdf8;">
                            SR%(m) = 67.88% - 6.28·sin(2π·m/12) - 0.84·cos(2π·m/12)
                        </div>
                        <ul style="font-size: 12px; color: var(--text-secondary); line-height: 1.6; padding-left: 18px; margin: 0;">
                            <li><strong>Baseline Facility Mean:</strong> 67.88% 24hpf viability</li>
                            <li><strong>Harmonic Amplitude (A):</strong> ±6.33% (Total 12.67% Peak-to-Trough Delta)</li>
                            <li><strong>Inflection Peak:</strong> Late August / Early September (Month 8.7)</li>
                            <li><strong>Inflection Trough:</strong> Late February / Early March (Month 2.7)</li>
                            <li><strong>Clutch Size Correlation:</strong> r = +0.0039 (Mating fecundity is constant across seasons)</li>
                        </ul>
                    </div>

                    <div style="background: rgba(15, 23, 42, 0.7); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
                        <h4 style="font-size: 14px; margin-bottom: 8px; color: #34d399;">💡 3Rs Operational Protocols & Seasonality Mitigation</h4>
                        <ul style="font-size: 12px; color: var(--text-secondary); line-height: 1.6; padding-left: 18px; margin: 0;">
                            <li><strong>Winter Trough Compensation (Feb–Mar):</strong> Increase breeding setup volume by <strong>+15% to +20%</strong> to absorb seasonal embryo survival dips and ensure experimental quotas are met.</li>
                            <li><strong>Autumn High Efficiency (Aug–Nov):</strong> High baseline viability (72–76%) allows a <strong>15% reduction in breeder pairs</strong>, cutting animal use and technician sorting labor.</li>
                            <li><strong>HVAC & RO Water Monitoring:</strong> Subtle shifts in municipal top-up water temperature during winter months drive thermal cycling in heaters, causing micro-variations in embryonic viability.</li>
                        </ul>
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
                            <td><span class="badge badge-medium">Flagged</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TAB 12: Intelligent Mating Planner -->
    <div id="tab-planner" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">🎯 Intelligent Spawning Recommendation & Cross-Planner</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Automated mating setup calculator matching live active inventory with 2-year empirical breeding benchmarks</span>
                </div>
            </div>
            
            <div class="filter-bar" style="background: rgba(15, 23, 42, 0.5); padding: 16px; border-radius: var(--radius-md); margin-bottom: 20px; flex-wrap: wrap; gap: 14px;">
                <div class="filter-group">
                    <span class="filter-label">Genetic Line:</span>
                    <select id="planLine" onchange="calculatePlanner()" style="font-weight: 700; font-size: 14px; min-width: 140px;">
                        <option value="AB">AB Line</option>
                        <option value="Casper">Casper Line</option>
                        <option value="Fli">Fli Line</option>
                        <option value="Gata">Gata Line</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Mating Setup Ratio (1.7L Tank):</span>
                    <select id="planRatio" onchange="calculatePlanner()" style="font-weight: 700; font-size: 14px; min-width: 190px;">
                        <option value="2:1" selected>2♀ : 1♂ (Standard Trio - 3 Fish)</option>
                        <option value="1:1">1♀ : 1♂ (Pair Mating - 2 Fish)</option>
                        <option value="6:3">6♀ : 3♂ (Group Spawning - 9 Fish Max)</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Desired Viable Embryos (24hpf):</span>
                    <input type="number" id="planEmbryoTarget" value="1000" min="50" max="10000" step="50" oninput="calculatePlanner()" style="width: 120px; font-weight: 700; font-size: 14px;">
                </div>
                <div class="filter-group" style="display: flex; align-items: flex-end; gap: 6px;">
                    <button class="btn btn-sm btn-outline" onclick="setQuickEmbryoTarget(300)">300</button>
                    <button class="btn btn-sm btn-outline" onclick="setQuickEmbryoTarget(500)">500</button>
                    <button class="btn btn-sm btn-outline" onclick="setQuickEmbryoTarget(1000)">1,000</button>
                    <button class="btn btn-sm btn-outline" onclick="setQuickEmbryoTarget(2000)">2,000</button>
                </div>
                <div style="margin-left: auto; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 11px; color: var(--text-secondary); background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.25); padding: 6px 10px; border-radius: 6px;">
                        🐟 <strong>Breeding Tank:</strong> 1.7L (Max Capacity: 9 Fish)
                    </span>
                </div>
            </div>
            
            <div id="plannerResultBox">
                <!-- Populated dynamically by JS -->
            </div>
        </div>
    </div>

    <!-- TAB 13: Master Breeding Log -->
    <div id="tab-raw-events" class="tab-content">
        <div class="card">
            <div class="card-header">
                <div>
                    <span class="card-title">📋 Grand Master Spawning Event Log (<span id="rawHeaderCount">2,233</span> Events)</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">Full individual spawning log history with multi-page navigation</span>
                </div>
                <div class="card-header-actions">
                    <button class="btn btn-sm btn-outline" onclick="exportTableToCSV('rawEventsTable', 'grand_master_breeding_events_2024_2026')">📥 Export Filtered Log (CSV)</button>
                </div>
            </div>
            <div class="filter-bar" style="margin-bottom: 16px;">
                <div class="filter-group">
                    <span class="filter-label">Year:</span>
                    <select id="rawYearFilter" onchange="renderRawEvents(true)">
                        <option value="ALL">All Years (2024-2026)</option>
                        <option value="2026">2026 (544 events)</option>
                        <option value="2025">2025 (1,229 events)</option>
                        <option value="2024">2024 (460 events)</option>
                    </select>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Line:</span>
                    <select id="rawLineFilter" onchange="renderRawEvents(true)">
                        <option value="ALL">All Lines</option>
                        <option value="AB">AB</option>
                        <option value="Casper">Casper</option>
                        <option value="Fli">Fli</option>
                        <option value="Gata">Gata</option>
                        <option value="DESMA">DESMA</option>
                    </select>
                </div>
                <div class="filter-group">
                    <input type="text" id="rawSearch" placeholder="Search Tank, Date, Staff, Cross..." oninput="renderRawEvents(true)">
                </div>
            </div>
            
            <div class="table-responsive" style="max-height: 620px; overflow-y: auto;">
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
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody id="rawEventsTableBody">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>

            <!-- Pagination & Rows-Per-Page Toolbar -->
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-top: 1px solid var(--border-color); flex-wrap: wrap; gap: 12px; background: rgba(15,23,42,0.3); margin-top: 8px; border-radius: 0 0 var(--radius-md) var(--radius-md);">
                <div style="display: flex; align-items: center; gap: 14px; font-size: 12px; color: var(--text-secondary); flex-wrap: wrap;">
                    <span>Showing <b id="rawPageRange" style="color: #fff;">1 - 50</b> of <b id="rawTotalCount" style="color: #fff;">2,233</b> events</span>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span>Rows per page:</span>
                        <select id="rawPageSize" onchange="changeRawPageSize(this.value)" style="background: var(--bg-card); color: #fff; border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 4px 8px; font-size: 12px; cursor: pointer;">
                            <option value="50" selected>50 rows</option>
                            <option value="100">100 rows</option>
                            <option value="200">200 rows</option>
                            <option value="500">500 rows</option>
                            <option value="ALL">All rows (2,233)</option>
                        </select>
                    </div>
                </div>
                <div id="rawPaginationControls" style="display: flex; align-items: center; gap: 4px; flex-wrap: wrap;">
                    <!-- Dynamically rendered: First, Prev, Page numbers, Next, Last -->
                </div>
            </div>
        </div>
    </div>

    <!-- MODAL: UNIVERSAL ROW EDITOR WITH BIOLOGICAL CONFLICT VALIDATION -->
    <div id="modalEditRow" class="modal-overlay" onclick="closeModal(event)">
        <div class="modal-container" onclick="event.stopPropagation()" style="max-width: 680px;">
            <div class="modal-header">
                <div>
                    <span class="modal-title" id="editModalTitle">✏️ Edit Facility Record</span>
                    <p style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;" id="editModalSubtitle">Relational updates will automatically cascade and validate against biological rules.</p>
                </div>
                <button class="close-btn" onclick="closeEditModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div id="editValidationAlert" style="display: none; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); color: #fca5a5; padding: 12px 16px; border-radius: 6px; font-size: 13px; line-height: 1.5; margin-bottom: 16px;">
                    <!-- Conflict message shown here -->
                </div>
                
                <form id="formEditRecord" onsubmit="submitRowEdit(event)">
                    <div id="editFormContent">
                        <!-- Dynamically Populated based on Record Type: Tank, Cross, or Event -->
                    </div>
                    <div style="margin-top: 20px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-color); padding-top: 16px;">
                        <span style="font-size: 11px; color: var(--text-muted);">Validated & synced across all 13 modules</span>
                        <div style="display: flex; gap: 10px;">
                            <button type="button" class="btn btn-outline" onclick="closeEditModal()">Cancel</button>
                            <button type="submit" class="btn btn-blue" id="btnSaveRowEdit">💾 Validate & Save Changes</button>
                        </div>
                    </div>
                </form>
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
        const CLOUD_API_URL = 'https://script.google.com/macros/s/AKfycbyU-4YKpnXEp_CXI2mu2Xb-DFo1fcIbt_qk9AWtXoPsj5CnDYmJ1XiZni1jl2Tce3df/exec';
        
        let MASTER_DATA = __DATA_JSON__;
        let currentEvents = MASTER_DATA.events || [];
        let currentTanks = MASTER_DATA.tank_stats || {};
        let currentPairs = MASTER_DATA.pair_synergies || [];
        let currentCrosses = MASTER_DATA.crosses_registry || [];
        let currentAlerts = MASTER_DATA.alerts || [];

        let currentFocalTank = 'T0135';
        let pedigreeNetworkInstance = null;

        // ==========================================
        // 🔄 UNIVERSAL TABLE COLUMN SORTING ENGINE
        // ==========================================
        document.addEventListener('click', function (e) {
            const th = e.target.closest('table thead th');
            if (!th) return;
            if (th.classList.contains('no-sort') || th.classList.contains('no-export')) return;

            const table = th.closest('table');
            if (!table) return;
            const tbody = table.querySelector('tbody');
            if (!tbody) return;

            const rows = Array.from(tbody.querySelectorAll('tr'));
            if (rows.length <= 1) return;

            const thIndex = Array.from(th.parentNode.children).indexOf(th);
            const isCurrentAsc = th.classList.contains('sorted-asc');
            const newDirection = isCurrentAsc ? 'desc' : 'asc';

            // Clear sort classes from sibling th elements
            th.parentNode.querySelectorAll('th').forEach(sibling => {
                sibling.classList.remove('sorted-asc', 'sorted-desc');
            });
            th.classList.add(newDirection === 'asc' ? 'sorted-asc' : 'sorted-desc');

            function getCellValue(tr, idx) {
                const cell = tr.children[idx];
                if (!cell) return '';
                const input = cell.querySelector('input, select');
                if (input) return input.value || '';
                return cell.innerText || cell.textContent || '';
            }

            function parseSortVal(val) {
                if (val === null || val === undefined) return { type: 'str', val: '' };
                val = String(val).trim();

                // Clean numbers with commas, percentage signs, unit suffixes
                const cleanNum = val.replace(/,/g, '').replace(/%/g, '').replace(/eggs?/i, '').replace(/fish/i, '').replace(/days?/i, '').trim();
                if (cleanNum !== '' && !isNaN(cleanNum) && !isNaN(parseFloat(cleanNum))) {
                    return { type: 'num', val: parseFloat(cleanNum) };
                }

                // Parse dates (e.g. YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY, Month D, Yr)
                const dateParsed = Date.parse(val);
                if (isNaN(cleanNum) && !isNaN(dateParsed) && (val.includes('-') || val.includes('/') || val.includes('.'))) {
                    return { type: 'date', val: dateParsed };
                }

                return { type: 'str', val: val.toLowerCase() };
            }

            rows.sort((rowA, rowB) => {
                const rawA = getCellValue(rowA, thIndex);
                const rawB = getCellValue(rowB, thIndex);

                const itemA = parseSortVal(rawA);
                const itemB = parseSortVal(rawB);

                let cmp = 0;
                if (itemA.type === 'num' && itemB.type === 'num') {
                    cmp = itemA.val - itemB.val;
                } else if (itemA.type === 'date' && itemB.type === 'date') {
                    cmp = itemA.val - itemB.val;
                } else {
                    cmp = String(itemA.val).localeCompare(String(itemB.val), undefined, { numeric: true, sensitivity: 'base' });
                }

                return newDirection === 'asc' ? cmp : -cmp;
            });

            rows.forEach(r => tbody.appendChild(r));
        });

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

        // Live Cloud Data Fetching
        function fetchLatestCloudData() {
            const badge = document.getElementById('cloudStatusBadge');
            badge.innerText = '🔄 Syncing Google Sheets...';
            badge.style.color = '#fbbf24';

            fetch(CLOUD_API_URL)
                .then(res => res.json())
                .then(resp => {
                    if (resp.status === 'success' && resp.data) {
                        badge.innerText = '🟢 Cloud: Google Sheets Live';
                        badge.style.color = '#34d399';
                        alert('Successfully synced live records with Master Google Sheet!');
                    }
                })
                .catch(err => {
                    badge.innerText = '🟢 Cloud Ready (Offline Cache)';
                    badge.style.color = '#38bdf8';
                });
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
                        backgroundColor: ['#34d399', '#fbbf24', '#f472b6', '#38bdf8'],
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
                opt.textContent = `${t.tuid} [${t.line}] - Gen ${t.generation > 0 ? 'F' + t.generation : 'F0'} (${t.female}F/${t.male}M)`;
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
                        Gen: <b style="color: var(--accent-blue);">${t.generation > 0 ? 'F' + t.generation : 'F0'}</b> | Inbreeding: <b style="color: ${inbr >= 0.25 ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">${inbr}</b>
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

            let trail = `<span style="color: var(--accent-blue);">${focal.tuid} (${focal.line})</span>`;
            if (focal.dam_tuid || focal.sire_tuid) {
                trail = `<span style="color: var(--text-secondary);">${focal.sire_tuid || 'Sire'} &times; ${focal.dam_tuid || 'Dam'}</span> &rarr; ` + trail;
            }
            if (focal.derivative_cross) {
                trail += ` <span style="color: var(--accent-indigo);">[Cross ${focal.derivative_cross}]</span>`;
            }
            document.getElementById('focalBreadcrumbTrail').innerHTML = `<b>Lineage Trail:</b> ${trail}`;

            document.getElementById('focalHeroGenBadge').innerText = focal.generation > 0 ? `Gen F${focal.generation}` : 'Gen F0 (Founder)';
            document.getElementById('treeColFocal').innerHTML = createMiniCard(focal.tuid, 'Focal Target Tank', true);

            const parentsDiv = document.getElementById('treeColParents');
            parentsDiv.innerHTML = '';
            parentsDiv.innerHTML += createMiniCard(focal.sire_tuid, '♂ Sire (Paternal)');
            parentsDiv.innerHTML += createMiniCard(focal.dam_tuid, '♀ Dam (Maternal)');

            const gpDiv = document.getElementById('treeColGrandparents');
            gpDiv.innerHTML = '';
            const sire = currentTanks[focal.sire_tuid];
            const dam = currentTanks[focal.dam_tuid];
            gpDiv.innerHTML += createMiniCard(sire ? sire.sire_tuid : null, 'Paternal Grandfather');
            gpDiv.innerHTML += createMiniCard(sire ? sire.dam_tuid : null, 'Paternal Grandmother');
            gpDiv.innerHTML += createMiniCard(dam ? dam.sire_tuid : null, 'Maternal Grandfather');
            gpDiv.innerHTML += createMiniCard(dam ? dam.dam_tuid : null, 'Maternal Grandmother');

            const offDiv = document.getElementById('treeColOffspring');
            offDiv.innerHTML = '';
            const offList = focal.children || [];
            document.getElementById('treeOffspringCountBadge').innerText = `${offList.length} Tanks`;
            if (offList.length === 0) {
                offDiv.innerHTML = '<div style="color: var(--text-muted); font-size: 11px; padding: 8px;">No direct offspring tanks spawned.</div>';
            } else {
                offList.forEach(ctuid => offDiv.innerHTML += createMiniCard(ctuid, 'F1 Offspring'));
            }

            const gcDiv = document.getElementById('treeColGrandgrandchildren');
            if (gcDiv) {
                gcDiv.innerHTML = '';
                const gcList = focal.grandchildren || [];
                document.getElementById('treeGrandchildrenCountBadge').innerText = `${gcList.length} Tanks`;
                if (gcList.length === 0) {
                    gcDiv.innerHTML = '<div style="color: var(--text-muted); font-size: 11px; padding: 8px;">No F2 grand-offspring.</div>';
                } else {
                    gcList.forEach(gctuid => gcDiv.innerHTML += createMiniCard(gctuid, 'F2 Grandchild'));
                }
            }
        }

        function copyLineageTrail() {
            const focal = currentTanks[currentFocalTank];
            if (!focal) return;
            const text = `${focal.tuid} (${focal.line}) | Gen: G${focal.generation || 0} | Sire: ${focal.sire_tuid || 'Root'} | Dam: ${focal.dam_tuid || 'Root'} | Cross: ${focal.derivative_cross || '-'}`;
            navigator.clipboard.writeText(text);
            alert(`Lineage trail copied to clipboard:\\n${text}`);
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
                        <td><span class="badge badge-active">${t.generation > 0 ? 'F' + t.generation : 'F0'}</span></td>
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
                'AB': '#34d399',
                'Casper': '#fbbf24',
                'Fli': '#f472b6',
                'Gata': '#38bdf8',
                'DESMA': '#a855f7',
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
                        <td class="no-export">
                            <div style="display: flex; gap: 4px;">
                                <button class="btn btn-sm btn-outline" onclick="openTankModal('${t.tuid}')">Inspect</button>
                                <button class="btn btn-sm btn-blue" style="padding: 2px 6px; font-size: 11px;" onclick="openEditTankModal('${t.tuid}')">✏️ Edit</button>
                            </div>
                        </td>
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
                        <td class="no-export">
                            <button class="btn btn-sm btn-blue" style="padding: 2px 6px; font-size: 11px;" onclick="openEditCrossModal('${c.cuid}')">✏️ Edit</button>
                        </td>
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

            const searchVal = (document.getElementById('crossPairSearch')?.value || '').toLowerCase().trim();
            const lineVal = document.getElementById('crossPairLineFilter')?.value || 'ALL';
            const pageSizeVal = document.getElementById('crossPairPageSize')?.value || 'ALL';
            const limit = pageSizeVal === 'ALL' ? Infinity : parseInt(pageSizeVal);

            let filtered = currentPairs.filter(p => {
                if (lineVal !== 'ALL') {
                    if (lineVal === 'Outcross' && !p.line.includes('Outcross')) return false;
                    if (lineVal !== 'Outcross' && p.line !== lineVal) return false;
                }
                if (searchVal) {
                    const matchKey = (p.pair_key || '').toLowerCase().includes(searchVal);
                    const matchLine = (p.line || '').toLowerCase().includes(searchVal);
                    if (!matchKey && !matchLine) return false;
                }
                return true;
            });

            const countBadge = document.getElementById('crossPairCountBadge');
            if (countBadge) {
                countBadge.textContent = `Showing ${Math.min(filtered.length, limit)} of ${filtered.length} pairs (${currentPairs.length} total in dataset)`;
            }

            filtered.slice(0, limit).forEach((p, idx) => {
                const badgeClass = p.line.startsWith('Outcross') ? 'badge-other' : `badge-${p.line.toLowerCase()}`;
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

            Object.values(currentTanks).forEach(t => {
                if (!t.spawn_history) return;
                t.spawn_history.forEach(h => {
                    if (h.age_months !== undefined && h.age_months !== null) {
                        const age = Math.round(h.age_months);
                        if (age >= 3 && age <= 30 && h.eggs_0h > 0) {
                            if (!ageBuckets[age]) ageBuckets[age] = { eggs: 0, spawns: 0, live: 0, sr24Sum: 0, validSpawns: 0 };
                            ageBuckets[age].eggs += h.eggs_0h;
                            ageBuckets[age].spawns++;
                            ageBuckets[age].live += (h.live_24h || 0);
                            if (h.sr_24h !== undefined && h.sr_24h !== null && h.sr_24h > 0) {
                                ageBuckets[age].validSpawns++;
                                ageBuckets[age].sr24Sum += h.sr_24h;
                            }
                        }
                    }
                });
            });

            const sortedAges = Object.keys(ageBuckets).map(Number).sort((a,b) => a - b);
            const clutchData = [], srData = [];

            sortedAges.forEach(age => {
                const b = ageBuckets[age];
                clutchData.push(b.spawns > 0 ? (b.eggs / b.spawns).toFixed(1) : 0);
                srData.push(b.validSpawns > 0 ? (b.sr24Sum / b.validSpawns).toFixed(1) : 0);
            });

            const canvasClutch = document.getElementById('chartAgeFecundity');
            if (canvasClutch) {
                const existing = Chart.getChart(canvasClutch);
                if (existing) existing.destroy();
                new Chart(canvasClutch, {
                    type: 'line',
                    data: {
                        labels: sortedAges.map(a => a + ' mo'),
                        datasets: [{ 
                            label: 'Average Clutch Size (Eggs/Spawn)', 
                            data: clutchData, 
                            borderColor: '#38bdf8', 
                            backgroundColor: 'rgba(56, 189, 248, 0.15)', 
                            fill: true, 
                            tension: 0.3,
                            pointRadius: 4,
                            pointBackgroundColor: '#38bdf8'
                        }]
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
            }

            const canvasViability = document.getElementById('chartAgeViability');
            if (canvasViability) {
                const existing2 = Chart.getChart(canvasViability);
                if (existing2) existing2.destroy();
                new Chart(canvasViability, {
                    type: 'line',
                    data: {
                        labels: sortedAges.map(a => a + ' mo'),
                        datasets: [{ 
                            label: '24hpf Survival Rate (%)', 
                            data: srData, 
                            borderColor: '#34d399', 
                            backgroundColor: 'rgba(52, 211, 153, 0.15)',
                            fill: true,
                            tension: 0.3, 
                            pointRadius: 4, 
                            pointBackgroundColor: '#34d399' 
                        }]
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
                            <div style="display: flex; gap: 4px;">
                                <button class="btn btn-sm btn-outline" onclick="openTankModal('${t.tuid}')">Inspect</button>
                                <button class="btn btn-sm btn-blue" style="padding: 2px 6px; font-size: 11px;" onclick="openEditTankModal('${t.tuid}')">✏️ Edit</button>
                            </div>
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
                            <div style="display: flex; gap: 4px;">
                                <button class="btn btn-sm btn-outline" onclick="openTankModal('${t.tuid}')">Profile</button>
                                <button class="btn btn-sm btn-blue" style="padding: 2px 6px; font-size: 11px;" onclick="openEditTankModal('${t.tuid}')">✏️ Edit</button>
                            </div>
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
        function setQuickEmbryoTarget(target) {
            const input = document.getElementById('planEmbryoTarget');
            if (input) {
                input.value = target;
                calculatePlanner();
            }
        }

        function calculatePlanner() {
            const line = document.getElementById('planLine').value;
            const targetYield = parseInt(document.getElementById('planEmbryoTarget').value) || 1000;
            const ratioVal = document.getElementById('planRatio')?.value || '2:1';

            let femalesPerBox = 2;
            let malesPerBox = 1;
            let ratioMultiplier = 1.5;
            let ratioLabel = '2♀ : 1♂ (Standard Trio)';
            let fishPerBox = 3;

            if (ratioVal === '1:1') {
                femalesPerBox = 1;
                malesPerBox = 1;
                ratioMultiplier = 1.0;
                ratioLabel = '1♀ : 1♂ (Pair Mating)';
                fishPerBox = 2;
            } else if (ratioVal === '6:3') {
                femalesPerBox = 6;
                malesPerBox = 3;
                ratioMultiplier = 4.0;
                ratioLabel = '6♀ : 3♂ (Group Spawning - 9 Fish Max)';
                fishPerBox = 9;
            }

            const relevantPairs = currentPairs.filter(p => p.line === line);
            const lineTanks = Object.values(currentTanks).filter(t => t.line === line && t.status === 'Active');

            // All candidate female & male sources
            const femaleTanks = lineTanks.filter(t => t.female > 0).sort((a, b) => (b.breeder_score || b.avg_clutch || 0) - (a.breeder_score || a.avg_clutch || 0));
            const maleTanks = lineTanks.filter(t => t.male > 0).sort((a, b) => (b.breeder_score || b.avg_clutch || 0) - (a.breeder_score || a.avg_clutch || 0));
            const mixedTanks = lineTanks.filter(t => t.female > 0 && t.male > 0).sort((a, b) => (b.breeder_score || b.avg_clutch || 0) - (a.breeder_score || a.avg_clutch || 0));

            // Benchmark metrics for line
            let avgClutch = 350;
            let avgSr24 = 92.0;
            let benchmarkPairName = `${line} Standard Baseline`;
            if (relevantPairs.length > 0) {
                avgClutch = relevantPairs[0].avg_clutch;
                avgSr24 = relevantPairs[0].avg_sr24;
                benchmarkPairName = relevantPairs[0].pair_key;
            }

            const expectedPerCage = Math.max(1, Math.round(avgClutch * ratioMultiplier * (avgSr24 / 100)));
            const neededCages = Math.max(1, Math.ceil(targetYield / expectedPerCage));
            const totalEstimatedEmbryos = neededCages * expectedPerCage;
            const totalFemalesNeeded = neededCages * femalesPerBox;
            const totalMalesNeeded = neededCages * malesPerBox;
            const totalFishNeeded = totalFemalesNeeded + totalMalesNeeded;

            // Pick Best Female and Male Tanks
            const bestFemale = femaleTanks.length > 0 ? femaleTanks[0] : null;
            let bestMale = maleTanks.length > 0 ? maleTanks[0] : null;
            if (bestFemale && bestMale && bestFemale.tuid === bestMale.tuid && maleTanks.length > 1) {
                bestMale = maleTanks[1];
            }

            // Top Mixed Tank
            const bestMixed = mixedTanks.length > 0 ? mixedTanks[0] : null;

            let html = `
                <!-- 1. HERO PRESCRIPTION CARD -->
                <div class="planner-kpi-grid">
                    <div class="planner-kpi-box emerald">
                        <span class="kpi-label">🎯 Target Viable Embryos</span>
                        <div class="kpi-value" style="color: var(--accent-emerald); font-size: 26px;">${targetYield.toLocaleString()} <span style="font-size: 13px; font-weight: normal; color: var(--text-secondary);">@ 24hpf</span></div>
                        <span class="kpi-subtext">Selected Line: <strong>${line}</strong></span>
                    </div>
                    <div class="planner-kpi-box blue">
                        <span class="kpi-label">📦 1.7L Breeding Tanks Needed</span>
                        <div class="kpi-value" style="color: var(--accent-blue); font-size: 26px;">${neededCages} <span style="font-size: 13px; font-weight: normal; color: var(--text-secondary);">Tanks (${ratioLabel})</span></div>
                        <span class="kpi-subtext">Expected output: <strong>~${totalEstimatedEmbryos.toLocaleString()} embryos</strong></span>
                    </div>
                    <div class="planner-kpi-box purple">
                        <span class="kpi-label">🐟 Total Fish Required</span>
                        <div class="kpi-value" style="font-size: 22px; color: #fff;">${totalFemalesNeeded}♀ + ${totalMalesNeeded}♂ <span style="font-size: 13px; color: var(--text-secondary);">(${totalFishNeeded} fish)</span></div>
                        <span class="kpi-subtext">${fishPerBox} fish/tank (Max 9 in 1.7L tank)</span>
                    </div>
                    <div class="planner-kpi-box">
                        <span class="kpi-label">🧬 Historical Benchmark</span>
                        <div class="kpi-value" style="font-size: 22px; color: #fff;">${avgClutch} <span style="font-size: 13px; color: var(--text-secondary);">eggs/spawn</span></div>
                        <span class="kpi-subtext">Mean 24h survival: <strong style="color: var(--accent-emerald);">${avgSr24}%</strong></span>
                    </div>
                </div>

                <!-- 2. TWO CLEAR SETUP OPTIONS -->
                <div style="margin-bottom: 12px; font-size: 14px; font-weight: 700; color: var(--text-primary); display: flex; align-items: center; gap: 8px;">
                    <span>⚡ Choose Your Setup Strategy:</span>
                </div>

                <div class="planner-options-grid">
                    <!-- OPTION A: PAIR-WISE CROSS -->
                    <div class="planner-plan-card" style="border-left: 4px solid var(--accent-blue);">
                        <div class="planner-plan-header">
                            <div>
                                <span class="planner-plan-badge" style="background: rgba(56, 189, 248, 0.15); color: var(--accent-blue);">Option A &bull; Standard Inter-Tank Cross</span>
                                <h3 style="margin: 6px 0 2px 0; font-size: 16px; color: #fff;">1.7L Tank Setup (${ratioLabel})</h3>
                            </div>
                            <span style="font-size: 11px; background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); padding: 4px 8px; border-radius: 4px; font-weight: 700;">Optimal Quality</span>
                        </div>

                        ${bestFemale && bestMale ? `
                        <div class="planner-match-box">
                            <div class="planner-fish-entity">
                                <span style="font-size: 11px; color: #f472b6; font-weight: 700;">♀ FEMALE DAM TANK</span>
                                <strong style="font-size: 18px; color: #fff;">${bestFemale.tuid}</strong>
                                <span style="font-size: 12px; color: var(--text-secondary);">${bestFemale.female}♀ available &bull; Score: <b>${bestFemale.breeder_score || 85}/100</b></span>
                                <button class="btn btn-sm btn-outline" style="margin-top: 6px; padding: 4px 8px; font-size: 11px;" onclick="openTankModal('${bestFemale.tuid}')">Inspect ${bestFemale.tuid}</button>
                            </div>
                            <div style="font-size: 20px; font-weight: 800; color: var(--accent-blue);">&times;</div>
                            <div class="planner-fish-entity" style="text-align: right;">
                                <span style="font-size: 11px; color: #60a5fa; font-weight: 700;">♂ MALE SIRE TANK</span>
                                <strong style="font-size: 18px; color: #fff;">${bestMale.tuid}</strong>
                                <span style="font-size: 12px; color: var(--text-secondary);">${bestMale.male}♂ available &bull; Score: <b>${bestMale.breeder_score || 85}/100</b></span>
                                <button class="btn btn-sm btn-outline" style="margin-top: 6px; padding: 4px 8px; font-size: 11px; align-self: flex-end;" onclick="openTankModal('${bestMale.tuid}')">Inspect ${bestMale.tuid}</button>
                            </div>
                        </div>

                        <div class="planner-protocol-box">
                            <strong>📋 Setup Instructions for Tonight:</strong><br>
                            1. Prepare <strong>${neededCages} standard 1.7L breeding tank(s)</strong> with slotted insert and dividers.<br>
                            2. Transfer <strong>${femalesPerBox} female(s)</strong> from <code>${bestFemale.tuid}</code> (pull ${totalFemalesNeeded}♀ total) and <strong>${malesPerBox} male(s)</strong> from <code>${bestMale.tuid}</code> (pull ${totalMalesNeeded}♂ total) into each 1.7L box.<br>
                            3. Total load is <strong>${fishPerBox} fish per 1.7L tank</strong> (well within the 9-fish limit).<br>
                            4. Keep divided overnight &rarr; pull divider at morning light onset (8:00 AM) &rarr; collect embryos at ~10:00 AM.
                        </div>
                        ` : `
                        <div style="color: var(--text-muted); font-size: 13px; padding: 16px;">Insufficient active male/female tanks for cross pairing in this line.</div>
                        `}
                    </div>

                    <!-- OPTION B: DIRECT IN-TANK SPAWNING -->
                    <div class="planner-plan-card" style="border-left: 4px solid var(--accent-purple);">
                        <div class="planner-plan-header">
                            <div>
                                <span class="planner-plan-badge" style="background: rgba(168, 85, 247, 0.15); color: var(--accent-purple);">Option B &bull; In-Tank Spawning</span>
                                <h3 style="margin: 6px 0 2px 0; font-size: 16px; color: #fff;">Mixed Colony Internal Spawning</h3>
                            </div>
                            <span style="font-size: 11px; background: rgba(255, 255, 255, 0.1); color: var(--text-secondary); padding: 4px 8px; border-radius: 4px; font-weight: 600;">Zero Handling Stress</span>
                        </div>

                        ${bestMixed ? `
                        <div class="planner-match-box" style="flex-direction: column; align-items: flex-start; gap: 8px;">
                            <div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">
                                <div>
                                    <span style="font-size: 11px; color: var(--accent-purple); font-weight: 700;">ACTIVE MIXED TANK CANDIDATE</span>
                                    <div style="font-size: 18px; font-weight: 800; color: #fff;">${bestMixed.tuid} (${line})</div>
                                </div>
                                <button class="btn btn-sm btn-outline" style="padding: 4px 8px; font-size: 11px;" onclick="openTankModal('${bestMixed.tuid}')">Inspect ${bestMixed.tuid}</button>
                            </div>
                            <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.5;">
                                • Current Biomass: <b>${bestMixed.female} Females</b> & <b>${bestMixed.male} Males</b> (Total: ${bestMixed.total} fish)<br>
                                • Historical Breeder Score: <strong style="color: var(--accent-emerald);">${bestMixed.breeder_score || 85}/100</strong> (${bestMixed.total_spawns} lifetime spawns)
                            </div>
                        </div>

                        <div class="planner-protocol-box" style="border-left-color: var(--accent-purple);">
                            <strong>📋 Setup Instructions for Tonight:</strong><br>
                            1. Place <strong>${Math.min(neededCages, 2)} collection slotted inserts</strong> directly inside tank <code>${bestMixed.tuid}</code> before lights off.<br>
                            2. No fish handling or netting between tanks required.<br>
                            3. Remove egg collection trays at ~10:00 AM next morning.
                        </div>
                        ` : `
                        <div style="color: var(--text-muted); font-size: 13px; padding: 16px;">No mixed colony tanks with both sexes currently active in ${line} line.</div>
                        `}
                    </div>
                </div>

                <!-- 3. ACTIVE CANDIDATE TANKS INVENTORY -->
                <div style="margin-top: 10px;">
                    <div style="font-size: 14px; font-weight: 700; color: var(--text-primary); margin-bottom: 12px;">
                        📋 All Active Candidate Breeder Tanks (${line} Line &bull; ${lineTanks.length} Tanks)
                    </div>
                    <div class="table-responsive" style="max-height: 320px; overflow-y: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>TUID</th>
                                    <th>Sex Breakdown</th>
                                    <th>Sex Type</th>
                                    <th>Breeder Score</th>
                                    <th>Age (Months)</th>
                                    <th>Turnover Status</th>
                                    <th>Past Spawns</th>
                                    <th>Avg Clutch</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${lineTanks.map(t => {
                                    const sexBadge = getSexBadge(t.sex_type);
                                    const ageMonths = t.age_days ? (t.age_days / 30.4).toFixed(1) : '-';
                                    const scoreColor = (t.breeder_score || 0) >= 80 ? 'var(--accent-emerald)' : (t.breeder_score || 0) >= 60 ? '#eab308' : 'var(--text-muted)';
                                    return `
                                        <tr>
                                            <td><strong>${t.tuid}</strong></td>
                                            <td><strong>${t.female}♀ / ${t.male}♂</strong> (${t.total} tot)</td>
                                            <td>${sexBadge}</td>
                                            <td><span style="color: ${scoreColor}; font-weight: 800;">${t.breeder_score ? t.breeder_score + '/100' : 'N/A'}</span></td>
                                            <td>${ageMonths} mo</td>
                                            <td><span class="badge badge-active">${t.turnover_urgency || 'Active'}</span></td>
                                            <td>${t.total_spawns}</td>
                                            <td>${t.avg_clutch || '-'}</td>
                                            <td>
                                                <button class="btn btn-sm btn-outline" style="padding: 2px 8px; font-size: 11px;" onclick="openTankModal('${t.tuid}')">Inspect</button>
                                            </td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;

            document.getElementById('plannerResultBox').innerHTML = html;
        }

        // TAB 13: Raw Events State & Pagination
        let rawCurrentPage = 1;
        let rawPageSize = 50;

        function changeRawPageSize(val) {
            rawPageSize = val === 'ALL' ? Infinity : parseInt(val);
            rawCurrentPage = 1;
            renderRawEvents(false);
        }

        function goToRawPage(page) {
            rawCurrentPage = page;
            renderRawEvents(false);
        }

        function renderRawEvents(resetPage = false) {
            const tbody = document.getElementById('rawEventsTableBody');
            if (!tbody) return;
            tbody.innerHTML = '';

            if (resetPage) rawCurrentPage = 1;

            const year = document.getElementById('rawYearFilter') ? document.getElementById('rawYearFilter').value : 'ALL';
            const line = document.getElementById('rawLineFilter') ? document.getElementById('rawLineFilter').value : 'ALL';
            const search = document.getElementById('rawSearch') ? document.getElementById('rawSearch').value.trim().toUpperCase() : '';

            let list = currentEvents;
            if (year !== 'ALL') list = list.filter(e => e.year === parseInt(year));
            if (line !== 'ALL') list = list.filter(e => e.line === line);
            if (search) list = list.filter(e => (e.tank_id && e.tank_id.toUpperCase().includes(search)) || (e.date && e.date.includes(search)) || (e.staff && e.staff.toUpperCase().includes(search)) || (e.notes && e.notes.toUpperCase().includes(search)));

            const totalFiltered = list.length;
            const pageSizeNum = rawPageSize === Infinity ? totalFiltered : rawPageSize;
            const totalPages = Math.max(1, Math.ceil(totalFiltered / (pageSizeNum || 1)));
            
            if (rawCurrentPage > totalPages) rawCurrentPage = totalPages;
            if (rawCurrentPage < 1) rawCurrentPage = 1;

            const startIdx = (rawCurrentPage - 1) * pageSizeNum;
            const endIdx = rawPageSize === Infinity ? totalFiltered : Math.min(startIdx + pageSizeNum, totalFiltered);
            const pageItems = list.slice(startIdx, endIdx);

            let htmlRows = '';
            pageItems.forEach(e => {
                const badgeClass = `badge-${(e.line || 'other').toLowerCase()}`;
                htmlRows += `
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
                        <td class="no-export">
                            <button class="btn btn-sm btn-blue" style="padding: 2px 6px; font-size: 11px;" onclick="openEditEventModal(${currentEvents.indexOf(e)})">✏️ Edit</button>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = htmlRows || '<tr><td colspan="10" style="text-align: center; color: var(--text-muted); padding: 20px;">No matching breeding records found.</td></tr>';

            // Update Counts & Labels
            const headerCount = document.getElementById('rawHeaderCount');
            if (headerCount) headerCount.innerText = totalFiltered.toLocaleString();

            const rangeLabel = document.getElementById('rawPageRange');
            if (rangeLabel) {
                rangeLabel.innerText = totalFiltered === 0 ? '0' : `${(startIdx + 1).toLocaleString()} - ${endIdx.toLocaleString()}`;
            }
            const totalLabel = document.getElementById('rawTotalCount');
            if (totalLabel) totalLabel.innerText = totalFiltered.toLocaleString();

            // Render Pagination Controls
            const pagBox = document.getElementById('rawPaginationControls');
            if (!pagBox) return;
            pagBox.innerHTML = '';

            if (totalPages <= 1) return;

            // First & Prev buttons
            const prevDisabled = rawCurrentPage <= 1 ? 'disabled style="opacity: 0.4; cursor: not-allowed;"' : '';
            pagBox.innerHTML += `<button type="button" class="btn btn-sm btn-outline" ${prevDisabled} onclick="goToRawPage(1)" title="First Page">«</button>`;
            pagBox.innerHTML += `<button type="button" class="btn btn-sm btn-outline" ${prevDisabled} onclick="goToRawPage(${rawCurrentPage - 1})" title="Previous Page">‹ Prev</button>`;

            // Page Numbers (sliding window around current page)
            let startPage = Math.max(1, rawCurrentPage - 2);
            let endPage = Math.min(totalPages, rawCurrentPage + 2);
            if (startPage > 1) {
                pagBox.innerHTML += `<button type="button" class="btn btn-sm btn-outline" onclick="goToRawPage(1)">1</button>`;
                if (startPage > 2) pagBox.innerHTML += `<span style="color: var(--text-muted); padding: 0 4px; font-size: 11px;">...</span>`;
            }
            for (let p = startPage; p <= endPage; p++) {
                const isActive = p === rawCurrentPage;
                pagBox.innerHTML += `<button type="button" class="btn btn-sm ${isActive ? 'btn-blue' : 'btn-outline'}" onclick="goToRawPage(${p})">${p}</button>`;
            }
            if (endPage < totalPages) {
                if (endPage < totalPages - 1) pagBox.innerHTML += `<span style="color: var(--text-muted); padding: 0 4px; font-size: 11px;">...</span>`;
                pagBox.innerHTML += `<button type="button" class="btn btn-sm btn-outline" onclick="goToRawPage(${totalPages})">${totalPages}</button>`;
            }

            // Next & Last buttons
            const nextDisabled = rawCurrentPage >= totalPages ? 'disabled style="opacity: 0.4; cursor: not-allowed;"' : '';
            pagBox.innerHTML += `<button type="button" class="btn btn-sm btn-outline" ${nextDisabled} onclick="goToRawPage(${rawCurrentPage + 1})" title="Next Page">Next ›</button>`;
            pagBox.innerHTML += `<button type="button" class="btn btn-sm btn-outline" ${nextDisabled} onclick="goToRawPage(${totalPages})" title="Last Page">»</button>`;
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
                <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
                    <button class="btn btn-sm btn-blue" onclick="openEditTankModal('${t.tuid}')">✏️ Edit Tank Details & Biometrics</button>
                </div>
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
                        <span style="font-size: 11px; color: var(--text-secondary);">Filial Generation & Inbreeding</span>
                        <div style="font-weight: bold; margin-top: 4px; color: var(--accent-blue);">${t.generation > 0 ? 'F' + t.generation : 'F0 (Founder)'} (Inbreeding F = ${t.inbreeding_f !== undefined ? t.inbreeding_f.toFixed(3) : '0.000'})</div>
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

        // ==========================================
        // ✏️ UNIVERSAL ROW EDITING & VALIDATION ENGINE
        // ==========================================
        let currentEditMode = null; // 'tank', 'cross', or 'event'
        let currentEditTargetId = null;

        function showValidationAlert(msg) {
            const alertBox = document.getElementById('editValidationAlert');
            if (alertBox) {
                alertBox.innerHTML = `<strong>⚠️ Biological Conflict / Validation Error:</strong><br>${msg}`;
                alertBox.style.display = 'block';
            }
        }

        function clearValidationAlert() {
            const alertBox = document.getElementById('editValidationAlert');
            if (alertBox) {
                alertBox.innerHTML = '';
                alertBox.style.display = 'none';
            }
        }

        function closeEditModal() {
            document.getElementById('modalEditRow').style.display = 'none';
            clearValidationAlert();
            currentEditMode = null;
            currentEditTargetId = null;
        }

        function openEditTankModal(tuid) {
            const t = currentTanks[tuid];
            if (!t) return;
            currentEditMode = 'tank';
            currentEditTargetId = tuid;
            clearValidationAlert();

            document.getElementById('editModalTitle').innerText = `✏️ Edit Tank ${tuid} [${t.line}]`;
            document.getElementById('editModalSubtitle').innerText = `Update line, sex distribution, DOB, or tank size. Validation rules enforce welfare and breeding compatibility.`;

            const formContent = document.getElementById('editFormContent');
            formContent.innerHTML = `
                <div class="form-grid">
                    <div class="form-group">
                        <label>Tank ID (Read-Only):</label>
                        <input type="text" id="editTankId" value="${t.tuid}" readonly style="background: rgba(255,255,255,0.05); color: var(--text-muted);">
                    </div>
                    <div class="form-group">
                        <label>Line / Strain:</label>
                        <select id="editTankLine" required>
                            <option value="AB" ${t.line === 'AB' ? 'selected' : ''}>AB</option>
                            <option value="Casper" ${t.line === 'Casper' ? 'selected' : ''}>Casper</option>
                            <option value="Fli" ${t.line === 'Fli' ? 'selected' : ''}>Fli</option>
                            <option value="Gata" ${t.line === 'Gata' ? 'selected' : ''}>Gata</option>
                            <option value="DESMA" ${t.line === 'DESMA' ? 'selected' : ''}>DESMA</option>
                            <option value="Other" ${t.line === 'Other' ? 'selected' : ''}>Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Status:</label>
                        <select id="editTankStatus" required>
                            <option value="Active" ${t.status === 'Active' ? 'selected' : ''}>Active</option>
                            <option value="Terminated" ${t.status === 'Terminated' ? 'selected' : ''}>Terminated</option>
                            <option value="Retired" ${t.status === 'Retired' ? 'selected' : ''}>Retired</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Female Count (♀):</label>
                        <input type="number" id="editTankFemale" min="0" value="${t.female}" required oninput="recalcEditTankTotal()">
                    </div>
                    <div class="form-group">
                        <label>Male Count (♂):</label>
                        <input type="number" id="editTankMale" min="0" value="${t.male}" required oninput="recalcEditTankTotal()">
                    </div>
                    <div class="form-group">
                        <label>Total Fish:</label>
                        <input type="number" id="editTankTotal" min="0" value="${t.total}" readonly style="background: rgba(255,255,255,0.05); font-weight: bold;">
                    </div>
                    <div class="form-group">
                        <label>Date of Birth (DOB):</label>
                        <input type="date" id="editTankDob" value="${t.dob || ''}">
                    </div>
                    <div class="form-group">
                        <label>Tank Size:</label>
                        <select id="editTankSize">
                            <option value="1.5L" ${t.tank_size === '1.5L' ? 'selected' : ''}>1.5L</option>
                            <option value="1.8L" ${t.tank_size === '1.8L' ? 'selected' : ''}>1.8L</option>
                            <option value="2.8L" ${t.tank_size === '2.8L' ? 'selected' : ''}>2.8L</option>
                            <option value="3.5L" ${t.tank_size === '3.5L' || !t.tank_size ? 'selected' : ''}>3.5L</option>
                            <option value="6L" ${t.tank_size === '6L' || t.tank_size === '6.0L' ? 'selected' : ''}>6.0L</option>
                            <option value="8L" ${t.tank_size === '8L' || t.tank_size === '8.0L' ? 'selected' : ''}>8.0L</option>
                        </select>
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <label>Lineage / Facility Notes:</label>
                        <input type="text" id="editTankNotes" value="${t.notes || ''}">
                    </div>
                </div>
            `;
            document.getElementById('modalEditRow').style.display = 'flex';
        }

        function recalcEditTankTotal() {
            const f = Number(document.getElementById('editTankFemale').value) || 0;
            const m = Number(document.getElementById('editTankMale').value) || 0;
            document.getElementById('editTankTotal').value = f + m;
        }

        function openEditCrossModal(cuid) {
            const c = currentCrosses.find(x => x.cuid === cuid);
            if (!c) return;
            currentEditMode = 'cross';
            currentEditTargetId = cuid;
            clearValidationAlert();

            document.getElementById('editModalTitle').innerText = `✏️ Edit Cross Record ${cuid}`;
            document.getElementById('editModalSubtitle').innerText = `Modify parental cross pair (Dam x Sire) or linked nursery data with referential integrity checks.`;

            const formContent = document.getElementById('editFormContent');
            formContent.innerHTML = `
                <div class="form-grid">
                    <div class="form-group">
                        <label>Cross ID (Read-Only):</label>
                        <input type="text" id="editCrossId" value="${c.cuid}" readonly style="background: rgba(255,255,255,0.05);">
                    </div>
                    <div class="form-group">
                        <label>Mating Date:</label>
                        <input type="date" id="editCrossDate" value="${c.mating_date}" required>
                    </div>
                    <div class="form-group">
                        <label>Dam (♀ Female Tank ID):</label>
                        <input type="text" id="editCrossDam" value="${c.dam}" required placeholder="e.g. T0135">
                    </div>
                    <div class="form-group">
                        <label>Sire (♂ Male Tank ID):</label>
                        <input type="text" id="editCrossSire" value="${c.sire}" required placeholder="e.g. T0099">
                    </div>
                    <div class="form-group">
                        <label>Nursery Fish Count (Yield):</label>
                        <input type="number" id="editCrossNurseryCount" min="0" value="${c.nursery_count || 0}">
                    </div>
                    <div class="form-group">
                        <label>Graduation Date:</label>
                        <input type="date" id="editCrossGradDate" value="${c.nursery_grad_date || ''}">
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <label>Resulting Offspring Tank IDs (comma-separated):</label>
                        <input type="text" id="editCrossOffspring" value="${(c.offspring_tanks || []).join(', ')}" placeholder="e.g. T0165, T0166">
                    </div>
                </div>
            `;
            document.getElementById('modalEditRow').style.display = 'flex';
        }

        function openEditEventModal(eventIndex) {
            const ev = currentEvents[eventIndex];
            if (!ev) return;
            currentEditMode = 'event';
            currentEditTargetId = eventIndex;
            clearValidationAlert();

            document.getElementById('editModalTitle').innerText = `✏️ Edit Spawning Event (${ev.date} - ${ev.tank_id})`;
            document.getElementById('editModalSubtitle').innerText = `Update egg counts or 24hpf live embryo survival. Viability SR% will automatically re-calculate.`;

            const formContent = document.getElementById('editFormContent');
            formContent.innerHTML = `
                <div class="form-grid">
                    <div class="form-group">
                        <label>Spawning Date:</label>
                        <input type="date" id="editEventDate" value="${ev.date}" required>
                    </div>
                    <div class="form-group">
                        <label>Tank / Pair ID:</label>
                        <input type="text" id="editEventTank" value="${ev.tank_id}" required>
                    </div>
                    <div class="form-group">
                        <label>Line / Strain:</label>
                        <select id="editEventLine">
                            <option value="AB" ${ev.line === 'AB' ? 'selected' : ''}>AB</option>
                            <option value="Casper" ${ev.line === 'Casper' ? 'selected' : ''}>Casper</option>
                            <option value="Fli" ${ev.line === 'Fli' ? 'selected' : ''}>Fli</option>
                            <option value="Gata" ${ev.line === 'Gata' ? 'selected' : ''}>Gata</option>
                            <option value="DESMA" ${ev.line === 'DESMA' ? 'selected' : ''}>DESMA</option>
                            <option value="Other" ${ev.line === 'Other' ? 'selected' : ''}>Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Total Eggs Spawned (0hpf):</label>
                        <input type="number" id="editEventEggs" min="0" value="${ev.eggs_0h}" required>
                    </div>
                    <div class="form-group">
                        <label>Viable Live Embryos (24hpf):</label>
                        <input type="number" id="editEventLive" min="0" value="${ev.live_24h}" required>
                    </div>
                    <div class="form-group">
                        <label>Staff / Operator:</label>
                        <input type="text" id="editEventStaff" value="${ev.staff || ''}" placeholder="e.g. AA, MA">
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <label>Log Notes / Observations:</label>
                        <input type="text" id="editEventNotes" value="${ev.notes || ''}">
                    </div>
                </div>
            `;
            document.getElementById('modalEditRow').style.display = 'flex';
        }

        function submitRowEdit(e) {
            e.preventDefault();
            clearValidationAlert();

            if (currentEditMode === 'tank') {
                saveTankEdit();
            } else if (currentEditMode === 'cross') {
                saveCrossEdit();
            } else if (currentEditMode === 'event') {
                saveEventEdit();
            }
        }

        function saveTankEdit() {
            const tuid = currentEditTargetId;
            const t = currentTanks[tuid];
            if (!t) return;

            const newLine = document.getElementById('editTankLine').value;
            const newStatus = document.getElementById('editTankStatus').value;
            const newFemale = Number(document.getElementById('editTankFemale').value);
            const newMale = Number(document.getElementById('editTankMale').value);
            const newTotal = newFemale + newMale;
            const newDob = document.getElementById('editTankDob').value;
            const newSize = document.getElementById('editTankSize').value;
            const newNotes = document.getElementById('editTankNotes').value.trim();

            if (newFemale < 0 || newMale < 0) {
                showValidationAlert('Fish counts cannot be negative.');
                return;
            }

            if (newFemale === 0) {
                const asDam = currentCrosses.find(c => c.dam === tuid);
                if (asDam) {
                    showValidationAlert(`Biological Incompatibility: Tank <strong>${tuid}</strong> is recorded as the Dam (Female Parent) in Cross <strong>${asDam.cuid}</strong>. A tank with 0 females cannot produce eggs. Please update the cross record or retain female breeders.`);
                    return;
                }
            }

            if (newMale === 0) {
                const asSire = currentCrosses.find(c => c.sire === tuid);
                if (asSire) {
                    showValidationAlert(`Biological Incompatibility: Tank <strong>${tuid}</strong> is recorded as the Sire (Male Parent) in Cross <strong>${asSire.cuid}</strong>. A tank with 0 males cannot serve as Sire.`);
                    return;
                }
            }

            const sizeNum = parseFloat(newSize) || 3.5;
            const density = (newTotal / sizeNum).toFixed(1);
            if (density > 7.0 && newStatus === 'Active') {
                if (!confirm(`⚠️ Welfare Warning: Total ${newTotal} fish in a ${sizeNum}L tank results in a density of ${density} fish/L (exceeds the facility threshold of 5.0-7.0 fish/L).\n\nDo you want to proceed?`)) {
                    showValidationAlert(`Welfare threshold exceeded: Density of ${density} fish/L is above 7.0 fish/L maximum.`);
                    return;
                }
            }

            if (newDob && new Date(newDob) > new Date()) {
                showValidationAlert('Chronological Conflict: Date of Birth (DOB) cannot be set in the future.');
                return;
            }

            t.line = newLine;
            t.status = newStatus;
            t.female = newFemale;
            t.male = newMale;
            t.total = newTotal;
            t.dob = newDob;
            t.tank_size = newSize;
            t.notes = newNotes;

            if (newFemale > 0 && newMale === 0) t.sex_type = 'Female-Only';
            else if (newFemale === 0 && newMale > 0) t.sex_type = 'Male-Only';
            else if (newFemale > 0 && newMale > 0) t.sex_type = 'Mixed Colony';
            else t.sex_type = 'Unsexed / Juvenile';

            if (newDob) {
                const dobDt = new Date(newDob);
                const now = new Date();
                const diffDays = Math.max(0, Math.floor((now - dobDt) / (1000 * 3600 * 24)));
                t.age_days = diffDays;
                t.age_months = Number((diffDays / 30.4).toFixed(1));
                const turnDt = new Date(dobDt);
                turnDt.setDate(turnDt.getDate() + 540);
                t.turnover_date = turnDt.toISOString().substring(0, 10);
                t.turnover_date_resolved = t.turnover_date;
                const remDays = Math.floor((turnDt - now) / (1000 * 3600 * 24));
                t.days_remaining = remDays;
                if (remDays < 0) t.turnover_urgency = 'Turnover Overdue';
                else if (remDays <= 30) t.turnover_urgency = 'Due Soon (<=30d)';
                else if (remDays <= 90) t.turnover_urgency = 'Upcoming (31-90d)';
                else t.turnover_urgency = 'Future (>90d)';
            }

            persistEdits();

            renderInventory();
            renderScorecards();
            renderTurnoverTable();
            renderAuditTab();
            calculatePlanner();
            renderBenchmarks();
            populateFocalDropdown();

            closeEditModal();
            alert(`✅ Tank ${tuid} updated and synchronized across all modules!`);
        }

        function saveCrossEdit() {
            const cuid = currentEditTargetId;
            const c = currentCrosses.find(x => x.cuid === cuid);
            if (!c) return;

            const newDam = document.getElementById('editCrossDam').value.trim().toUpperCase();
            const newSire = document.getElementById('editCrossSire').value.trim().toUpperCase();
            const newDate = document.getElementById('editCrossDate').value;
            const newNurseryCount = Number(document.getElementById('editCrossNurseryCount').value) || 0;
            const newGradDate = document.getElementById('editCrossGradDate').value;
            const newOffspringStr = document.getElementById('editCrossOffspring').value;
            const newOffspring = newOffspringStr.split(',').map(s => s.trim().toUpperCase()).filter(s => s.length > 0);

            if (!currentTanks[newDam]) {
                showValidationAlert(`Integrity Conflict: Dam Tank <strong>${newDam}</strong> does not exist in the facility tank database.`);
                return;
            }
            if (!currentTanks[newSire]) {
                showValidationAlert(`Integrity Conflict: Sire Tank <strong>${newSire}</strong> does not exist in the facility tank database.`);
                return;
            }

            if (currentTanks[newDam].female === 0) {
                showValidationAlert(`Biological Conflict: Dam Tank <strong>${newDam}</strong> has 0 recorded females. A male-only tank cannot serve as the Dam.`);
                return;
            }
            if (currentTanks[newSire].male === 0) {
                showValidationAlert(`Biological Conflict: Sire Tank <strong>${newSire}</strong> has 0 recorded males. A female-only tank cannot serve as the Sire.`);
                return;
            }

            if (newDate && new Date(newDate) > new Date()) {
                showValidationAlert('Chronological Conflict: Cross mating date cannot be set in the future.');
                return;
            }

            c.dam = newDam;
            c.sire = newSire;
            c.mating_date = newDate;
            c.nursery_count = newNurseryCount;
            c.nursery_grad_date = newGradDate;
            c.offspring_tanks = newOffspring;
            c.line_pair = `${currentTanks[newDam].line} x ${currentTanks[newSire].line}`;

            persistEdits();

            renderCrossesRegistry();
            renderFocalPedigreeTree();
            renderCrosses();
            calculatePlanner();

            closeEditModal();
            alert(`✅ Cross ${cuid} updated and synced across pedigree and nursery registry!`);
        }

        function saveEventEdit() {
            const eventIndex = currentEditTargetId;
            const ev = currentEvents[eventIndex];
            if (!ev) return;

            const newDate = document.getElementById('editEventDate').value;
            const newTank = document.getElementById('editEventTank').value.trim().toUpperCase();
            const newLine = document.getElementById('editEventLine').value;
            const newEggs = Number(document.getElementById('editEventEggs').value) || 0;
            const newLive = Number(document.getElementById('editEventLive').value) || 0;
            const newStaff = document.getElementById('editEventStaff').value.trim();
            const newNotes = document.getElementById('editEventNotes').value.trim();

            if (newEggs < 0 || newLive < 0) {
                showValidationAlert('Egg and embryo counts cannot be negative.');
                return;
            }

            if (newLive > newEggs) {
                showValidationAlert(`Mathematical Impossibility: 24hpf Live Embryos (<strong>${newLive}</strong>) cannot exceed 0hpf Total Eggs Spawned (<strong>${newEggs}</strong>).`);
                return;
            }

            if (newDate && new Date(newDate) > new Date()) {
                showValidationAlert('Chronological Conflict: Spawning date cannot be set in the future.');
                return;
            }

            ev.date = newDate;
            ev.tank_id = newTank;
            ev.line = newLine;
            ev.eggs_0h = newEggs;
            ev.live_24h = newLive;
            ev.sr_24h = newEggs > 0 ? Number(((newLive / newEggs) * 100).toFixed(1)) : 0;
            ev.staff = newStaff;
            ev.notes = newNotes;

            persistEdits();

            renderRawEvents();
            renderBenchmarks();
            renderScorecards();
            renderTrends();
            calculatePlanner();

            closeEditModal();
            alert(`✅ Spawning record updated and re-computed across all performance charts!`);
        }

        function persistEdits() {
            try {
                localStorage.setItem('fishnet_persisted_tanks', JSON.stringify(currentTanks));
                localStorage.setItem('fishnet_persisted_crosses', JSON.stringify(currentCrosses));
                localStorage.setItem('fishnet_persisted_events', JSON.stringify(currentEvents));
            } catch(e) {
                console.warn('LocalStorage save error:', e);
            }
        }

        function loadPersistedEdits() {
            try {
                const savedTanks = localStorage.getItem('fishnet_persisted_tanks');
                if (savedTanks) currentTanks = JSON.parse(savedTanks);

                const savedCrosses = localStorage.getItem('fishnet_persisted_crosses');
                if (savedCrosses) currentCrosses = JSON.parse(savedCrosses);

                const savedEvents = localStorage.getItem('fishnet_persisted_events');
                if (savedEvents) currentEvents = JSON.parse(savedEvents);
            } catch(e) {
                console.warn('LocalStorage load error:', e);
            }
        }

        function closeModal(e) {
            if (!e || e.target.id === 'tankModal' || e.target.id === 'modalEditRow' || e.target.className === 'close-btn') {
                if (document.getElementById('tankModal')) document.getElementById('tankModal').style.display = 'none';
                if (document.getElementById('modalEditRow')) document.getElementById('modalEditRow').style.display = 'none';
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
            loadPersistedEdits();
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
