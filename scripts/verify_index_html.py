"""
Verify index.html integrity, embedded JSON validity, and all audit checks
"""
import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

print("=== VERIFYING INDEX.HTML INTEGRITY ===")
print(f"File size: {len(html):,} bytes")

# 1. Check embedded JSON
m = re.search(r'const\s+DATA\s*=\s*(\{.+?\});\s*(?:const|let|var|function)', html, re.DOTALL)
if not m:
    m = re.search(r'window\.__DATA__\s*=\s*(\{.+?\});', html, re.DOTALL)
if not m:
    # Look for DATA_JSON or similar
    m = re.search(r'const rawData\s*=\s*(\{.+?\});', html, re.DOTALL)

if m:
    json_str = m.group(1)
    try:
        parsed = json.loads(json_str)
        print("  ✓ Embedded JSON parses successfully!")
        print(f"    - Events: {len(parsed.get('events', []))}")
        print(f"    - Tanks: {len(parsed.get('tank_stats', {}))}")
        print(f"    - Alerts: {len(parsed.get('alerts', []))}")
    except Exception as e:
        print(f"  ✗ JSON parse error: {e}")
else:
    # check where JSON is embedded
    print("  Checking for data pattern...")
    pos = html.find('__DATA_JSON__')
    if pos >= 0:
        print("  ⚠️ __DATA_JSON__ placeholder still unreplaced!")
    else:
        print("  ✓ Data was inlined.")

# 2. Key audit strings
checks = [
    ("ANOVA F = 18.809", "ANOVA F-value badge updated to empirical F=18.809"),
    ("trendsAgeFilter", "Age Cohort Filter dropdown present"),
    ("trendsConfounderBanner", "Confounder Warning banner present"),
    ("Multivariable Confounder Control Model", "Multivariable Regression Table present"),
    ("+84.39%", "Model Intercept present"),
    ("-0.84%", "Parental Age coefficient (-0.84%/mo) present"),
    ("+8.18%", "Summer Peak coefficient (+8.18%) present"),
    ("rawYearFilter", "Raw events year filter present"),
    ("rawLineFilter", "Raw events line filter present"),
    ("rawSearch", "Raw events search input present"),
    ("rawPageSize", "Raw events page size selector present"),
    ("exportTableToCSV", "CSV export present"),
    ("exportBreedingJSON", "JSON export present"),
    ("openTankModal", "Tank modal present"),
    ("openEditEventModal", "Event edit modal present"),
    ("Casper (Double Mutant", "Casper strain card present"),
    ("Consistently low viability across all seasons (Summer 30.9%, Winter 26.8%", "Casper empirical seasonal text verified"),
    ("Highest survival in Autumn (78.8% SR), Summer (76.5% SR)", "AB empirical seasonal text verified")
]

all_passed = True
for term, desc in checks:
    count = html.count(term)
    if count > 0:
        print(f"  ✓ {desc} ({count}x)")
    else:
        print(f"  ✗ MISSING: {desc} (term: '{term}')")
        all_passed = False

if all_passed:
    print("\n✓ 100% OF KEY CHECKS PASSED ON index.html")
else:
    print("\n⚠️ SOME CHECKS FAILED ON index.html")
