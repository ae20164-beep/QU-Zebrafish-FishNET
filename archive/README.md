# 🐟 FishNET Zebrafish Colony & Breeding Intelligence Portal
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
  1. **🎯 3-Gen Family Tree:** 5-column card flow (Grandparents $\to$ Parents $\to$ 🎯 Focus Tank $\to$ Offspring $\to$ Grandchildren) with dynamic breadcrumb trails and printable pedigree certificates.
  2. **🌿 Line-by-Line Flowcharts:** Clean top-down generation tiers (F0 $\to$ F1 $\to$ F2 $\to$ F3+).
  3. **📑 Collapsible Lineage Tree Table:** Hierarchical table with live search and CSV export.
  4. **🕸️ Global Network Map:** 2D interactive vis.js physics network.
* **Turnover & Aging Schedule:** Automated countdown tracking tanks approaching the 540-day (18-month) senescence threshold.
* **Density & Animal Welfare Monitoring:** Real-time fish/Liter stocking compliance audits.
* **In-Browser File Uploader:** Instant analysis of updated `.xlsx`, `.tab`, `.tsv`, or `.csv` files.

---

### 2. 🧬 Reproductive Intelligence & Mating Planner (`breeding.html`)
* **2,233 Spawning Events (2024–2026)** with longitudinal fecundity analysis.
* **4-Line Reproductive Benchmarks:** Egg counts, 0hpf fertilization rates, and 24hpf viability metrics.
* **Cross-Pairing Synergies:** Canonical Dam (♀) $\times$ Sire (♂) cross matrices.
* **🎯 Intelligent Mating Planner:**
  * **Pair-Wise Strategy:** Recommends verified pure single-pair combinations (e.g. `T0095(♀) x T0093(♂)` with 84.0% 24h SR).
  * **In-Tank Spawning Strategy:** Identifies active communal colony tanks, calculating required setups and husbandry rest intervals ($\ge 14$ days).

---

## 📦 Local Usage
To run locally on any computer or lab intranet:
```bash
python -m http.server 8080
```
Open `http://localhost:8080` in your web browser.
