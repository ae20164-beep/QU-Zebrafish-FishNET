import shutil
import os
import json

print("Preparing clean Vercel & GitHub deployment package...")

# 1. Copy the dashboards to standard web routes
shutil.copyfile('FishNET_Interactive_Dashboard.html', 'colony.html')
shutil.copyfile('FishNET_Interactive_Dashboard_With_Breeding.html', 'breeding.html')

# 2. Create the Master Unified Web Portal (index.html)
master_portal_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FishNET Zebrafish Colony & Breeding Intelligence Portal | Qatar University</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #0b1120;
            --bg-nav: #0f172a;
            --border-color: #1e293b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-teal: #0d9488;
            --accent-blue: #0284c7;
            --accent-indigo: #6366f1;
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
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* Top Unified Navigation Bar */
        header {
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-color);
            padding: 10px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 100;
            flex-shrink: 0;
        }

        .brand-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-logo {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #0d9488, #0284c7);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3);
        }

        .brand-text h1 {
            font-size: 15px;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .brand-badge {
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 9999px;
            background: rgba(13, 148, 136, 0.2);
            color: #2dd4bf;
            border: 1px solid rgba(13, 148, 136, 0.4);
            text-transform: uppercase;
        }

        .brand-text p {
            font-size: 11px;
            color: var(--text-secondary);
        }

        /* Nav Tab Switcher */
        .portal-nav {
            display: flex;
            align-items: center;
            gap: 6px;
            background: #090e17;
            padding: 4px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }

        .nav-link-btn {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 7px 16px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
        }

        .nav-link-btn:hover {
            color: #ffffff;
            background: rgba(255, 255, 255, 0.05);
        }

        .nav-link-btn.active {
            background: #0d9488;
            color: #ffffff;
            box-shadow: 0 2px 8px rgba(13, 148, 136, 0.4);
        }

        /* Right Quick Actions */
        .header-actions {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .action-btn {
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .action-btn:hover {
            background: #334155;
            color: #ffffff;
            border-color: #475569;
        }

        /* Full Height Responsive Frame */
        .portal-frame-container {
            flex: 1;
            width: 100%;
            height: calc(100vh - 61px);
            position: relative;
            background: #0b1120;
        }

        iframe {
            width: 100%;
            height: 100%;
            border: none;
            display: block;
        }

        @media (max-width: 860px) {
            header {
                flex-direction: column;
                gap: 8px;
                padding: 10px;
            }
            .brand-text p {
                display: none;
            }
        }
    </style>
</head>
<body>

    <!-- Unified Master Header -->
    <header>
        <div class="brand-section">
            <div class="brand-logo">🐟</div>
            <div class="brand-text">
                <h1>
                    FishNET Intelligence Portal
                    <span class="brand-badge">QU Biology Lab</span>
                </h1>
                <p>Zebrafish Colony Architecture, 4-Mode Pedigrees & Reproductive Intelligence</p>
            </div>
        </div>

        <!-- Master Navigation Switcher -->
        <nav class="portal-nav">
            <button onclick="switchPortalView('colony')" id="btn-view-colony" class="nav-link-btn active">
                <span>🌳 Colony & Pedigree Explorer</span>
            </button>
            <button onclick="switchPortalView('breeding')" id="btn-view-breeding" class="nav-link-btn">
                <span>🧬 Breeding & Mating Intelligence</span>
            </button>
        </nav>

        <!-- Lab Actions -->
        <div class="header-actions">
            <a href="FishNET_Colony_Analytics_Report.xlsx" download class="action-btn" title="Download Master Excel Report">
                <span>📊 Master Excel</span>
            </a>
            <button onclick="openExternalCurrentView()" class="action-btn" title="Open Fullscreen in New Tab">
                <span>↗️ Fullscreen</span>
            </button>
        </div>
    </header>

    <!-- Main Content Frame -->
    <div class="portal-frame-container">
        <iframe id="portalFrame" src="colony.html" title="FishNET Active Dashboard"></iframe>
    </div>

    <script>
        let currentView = 'colony';

        function switchPortalView(view) {
            currentView = view;
            const frame = document.getElementById('portalFrame');
            const btnColony = document.getElementById('btn-view-colony');
            const btnBreeding = document.getElementById('btn-view-breeding');

            if (view === 'colony') {
                frame.src = 'colony.html';
                btnColony.classList.add('active');
                btnBreeding.classList.remove('active');
            } else {
                frame.src = 'breeding.html';
                btnBreeding.classList.add('active');
                btnColony.classList.remove('active');
            }
        }

        function openExternalCurrentView() {
            const targetUrl = currentView === 'colony' ? 'colony.html' : 'breeding.html';
            window.open(targetUrl, '_blank');
        }
    </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(master_portal_html)

# 3. Create vercel.json
vercel_config = {
    "version": 2,
    "cleanUrls": True,
    "trailingSlash": False,
    "headers": [
        {
            "source": "/(.*)",
            "headers": [
                { "key": "X-Content-Type-Options", "value": "nosniff" },
                { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
                { "key": "X-XSS-Protection", "value": "1; mode=block" }
            ]
        }
    ]
}

with open('vercel.json', 'w', encoding='utf-8') as f:
    json.dump(vercel_config, f, indent=2)

# 4. Create .gitignore
gitignore_content = """# Temporary & Build artifacts
*.pyc
__pycache__/
temp_*
*.tmp
.DS_Store
"""

with open('.gitignore', 'w', encoding='utf-8') as f:
    f.write(gitignore_content)

# 5. Create README.md
readme_content = """# 🐟 FishNET Zebrafish Colony & Breeding Intelligence Portal
**Qatar University — Department of Biological & Environmental Sciences**

An integrated, interactive web intelligence portal and pedigree management platform for the Zebrafish (*Danio rerio*) research colony (2024–2026).

---

## 🚀 Live Access & Deployment
This web portal is deployed and accessible on **Vercel** and **GitHub Pages**:
* **Unified Master Portal:** `index.html`
* **Colony & 4-Mode Pedigree Explorer:** `colony.html`
* **Breeding Intelligence & Mating Planner:** `breeding.html`
* **Master Colony Analytics Workbook:** `FishNET_Colony_Analytics_Report.xlsx`

---

## 🌟 Key Features

### 1. 🌳 Colony Architecture & 4-Mode Pedigree Explorer (`colony.html`)
* **180 Confirmed Tanks** (112 Active / 68 Euthanized) classified across the 4 primary lines (**AB**, **Casper**, **Fli**, **Gata**).
* **4-Mode Interactive Pedigree Explorer:**
  1. **🎯 3-Gen Family Tree:** 5-column card flow (Grandparents $\\to$ Parents $\\to$ 🎯 Focus Tank $\\to$ Offspring $\\to$ Grandchildren) with dynamic breadcrumb trails and printable pedigree certificates.
  2. **🌿 Line-by-Line Flowcharts:** Clean top-down generation tiers (F0 $\\to$ F1 $\\to$ F2 $\\to$ F3+).
  3. **📑 Collapsible Lineage Tree Table:** Hierarchical table with live search and CSV export.
  4. **🕸️ Global Network Map:** 2D interactive vis.js physics network.
* **Turnover & Aging Schedule:** Automated countdown tracking tanks approaching the 540-day (18-month) senescence threshold.
* **Density & Animal Welfare Monitoring:** Real-time fish/Liter stocking compliance audits.
* **In-Browser File Uploader:** Instant analysis of updated `.xlsx`, `.tab`, `.tsv`, or `.csv` files.

---

### 2. 🧬 Reproductive Intelligence & Mating Planner (`breeding.html`)
* **2,233 Spawning Events (2024–2026)** with longitudinal fecundity analysis.
* **4-Line Reproductive Benchmarks:** Egg counts, 0hpf fertilization rates, and 24hpf viability metrics.
* **Cross-Pairing Synergies:** Canonical Dam (♀) $\\times$ Sire (♂) cross matrices.
* **🎯 Intelligent Mating Planner:**
  * **Pair-Wise Strategy:** Recommends verified pure single-pair combinations (e.g. `T0095(♀) x T0093(♂)` with 84.0% 24h SR).
  * **In-Tank Spawning Strategy:** Identifies active communal colony tanks, calculating required setups and husbandry rest intervals ($\\ge 14$ days).

---

## 📦 Local Usage
To run locally on any computer or lab intranet:
```bash
python -m http.server 8080
```
Open `http://localhost:8080` in your web browser.
"""

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("Created index.html, colony.html, breeding.html, vercel.json, .gitignore, and README.md successfully!")
