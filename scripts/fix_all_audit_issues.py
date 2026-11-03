"""
FishNET Dashboard - Comprehensive Audit Fix Script
Fixes ALL issues found during the full audit run on 2026-11-04.

ISSUES FIXED:
1. ANOVA F-value: hardcoded 21.601 → actual 18.809
2. AB insight block: stale seasonal SR % (78.6-83.8%) → actual (69.2-78.8%)
3. Casper insight block: stale (71.4% summer, 49-59% winter/spring) → actual (30.9% summer, 26.8% winter, 23.8% spring)
4. Fli insight block: partially wrong SR claims → actual values
5. Gata insight block: wrong winter/autumn SR → actual
6. All-lines summary box: wrong per-line SR claims → actual
7. ANOVA badge in Tab 7 header: F = 21.601 → 18.809
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

GENERATOR = 'scripts/generate_integrated_dashboard.py'

with open(GENERATOR, 'r', encoding='utf-8') as f:
    gen = f.read()

original = gen
fixes_applied = 0

def fix(gen, old, new, label):
    global fixes_applied
    if old in gen:
        gen = gen.replace(old, new)
        fixes_applied += 1
        print(f'  [FIX {fixes_applied}] {label}')
    else:
        print(f'  [SKIP] Not found: {label}')
    return gen

print('=== APPLYING AUDIT FIXES ===')
print()

# ------------------------------------------------------------------
# FIX 1: ANOVA F-value hardcoded in Tab 7 header badge
# ------------------------------------------------------------------
gen = fix(gen,
    'ANOVA F = 21.601 (p &lt; 0.0001)',
    'ANOVA F = 18.809 (p &lt; 0.0001)',
    'ANOVA F-value badge: 21.601 → 18.809'
)

# ------------------------------------------------------------------
# FIX 2: AB Line specific insight block (Autumn 83.8%, Summer 82.9%, Winter 80.5%, Spring 78.6%)
# Actual: Winter 69.2%, Spring 74.1%, Summer 76.5%, Autumn 78.8%
# ------------------------------------------------------------------
gen = fix(gen,
    '<li><strong>Thermal Resilience:</strong> Remarkable survival rate stability across seasons (Autumn 83.8%, Summer 82.9%, Winter 80.5%, Spring 78.6%).</li>',
    '<li><strong>Thermal Resilience:</strong> Highest survival in Autumn (78.8% SR), Summer (76.5% SR), Spring (74.1% SR) and Winter (69.2% SR) — a stable but seasonally progressive gradient consistent with thermal influence on embryo viability.</li>',
    'AB line insight: stale SR percentages → actual values'
)

# ------------------------------------------------------------------
# FIX 3: Casper line-specific insight block
# Stale: peaks in summer (71.4% SR), dips winter/spring (49–59% SR)
# Actual: Winter 26.8%, Spring 23.8%, Summer 30.9%, Autumn 21.1%
# ------------------------------------------------------------------
gen = fix(gen,
    '<li><strong>Climate Seasonality:</strong> Highest survival in Summer (71.4% SR), but experiences substantial mortality during cooler months (Winter 59.0%, Spring 51.1%).</li>',
    '<li><strong>Climate Seasonality:</strong> Consistently low viability across all seasons (Summer 30.9%, Winter 26.8%, Spring 23.8%, Autumn 21.1%), reflecting the inherent double-mutant physiological burden rather than a thermal effect. No season rescues Casper to AB-level performance.</li>',
    'Casper line insight: stale SR → actual (30.9%/26.8%/23.8%/21.1%)'
)

# Fix also the clutch range for Casper in line insight
gen = fix(gen,
    '<li><strong>Clutch Output:</strong> Lower fecundity (avg 130–260 eggs/spawn) due to physiological burdens of the double pigment mutation.</li>',
    '<li><strong>Clutch Output:</strong> Lower fecundity (avg 127–260 eggs/spawn) due to physiological burdens of the double pigment mutation; summer clutches are smaller (127 eggs), autumn largest (260 eggs).</li>',
    'Casper clutch range: refined to actual'
)

# ------------------------------------------------------------------
# FIX 4: Fli line-specific insight block
# Stale: "Summer viability peaks at 72.4% SR; maintains ~66% SR across Winter, Spring, and Autumn."
# Actual: Winter 63.1%, Spring 50.6%, Summer 66.8%, Autumn 62.3%
# Note: "72.4%" is close to but not matching actual 66.8% — also Spring is notably low at 50.6%
# ------------------------------------------------------------------
gen = fix(gen,
    '<li><strong>Survival Stability:</strong> Summer viability peaks at 72.4% SR; maintains ~66% SR across Winter, Spring, and Autumn.</li>',
    '<li><strong>Survival Stability:</strong> Peaks in Summer (66.8% SR) and Winter (63.1% SR); notably lower in Spring (50.6% SR) and Autumn (62.3% SR). Spring represents a vulnerability window for transgenic embryo supply.</li>',
    'Fli line insight: stale SR → actual (66.8% summer, 63.1% winter, 50.6% spring, 62.3% autumn)'
)

# ------------------------------------------------------------------
# FIX 5: Gata line-specific insight block
# Stale: "Excellent performance in Autumn (73.5% SR) and Winter (71.1% SR), with a temporary dip in Spring (56.8% SR)."
# Actual: Winter 27.9%, Spring 37.9%, Summer 55.6%, Autumn 31.8%
# These are MASSIVELY wrong - Gata is a low-SR line like Casper
# ------------------------------------------------------------------
gen = fix(gen,
    '<li><strong>Seasonal Variance:</strong> Excellent performance in Autumn (73.5% SR) and Winter (71.1% SR), with a temporary dip in Spring (56.8% SR).</li>',
    '<li><strong>Seasonal Variance:</strong> Peaks in Summer (55.6% SR), with moderate but consistent performance in Spring (37.9% SR), Autumn (31.8% SR) and Winter (27.9% SR). Summer is the optimal collection window for Gata transgenic embryos.</li>',
    'Gata line insight: stale SR (73.5%/71.1%) → actual (55.6% summer, 37.9% spring, 31.8% autumn, 27.9% winter)'
)

# ------------------------------------------------------------------
# FIX 6: All-lines summary box (COMPARE / ALL view)
# Stale: "AB (Wild-Type Baseline): ... Highly stable viability (78.6% – 83.8%)"
# Actual: 69.2% – 78.8%
# ------------------------------------------------------------------
gen = fix(gen,
    'Highly stable viability (78.6% – 83.8%) and large clutches (avg 640 eggs) across all 4 seasons.',
    'Progressive seasonal gradient (Winter 69.2% → Autumn 78.8% SR) with large clutches (avg 643 eggs). Most stable line; thermal influence is real but mild.',
    'AB summary box: stale 78.6-83.8% → actual 69.2-78.8%'
)

# Fix Casper summary in all-lines box
gen = fix(gen,
    'Marked seasonal thermal sensitivity; peaks in summer (71.4% SR), but dips severely in winter/spring (49–59% SR) with smaller clutches (130–260 eggs).',
    'Consistently low viability across all seasons (Summer 30.9%, Winter 26.8%, Spring 23.8%, Autumn 21.1%). Smaller clutches (127–260 eggs). Double-mutant burden is the dominant driver — thermal influence is secondary.',
    'Casper summary box: stale 71.4%/49-59% → actual 30.9%/26.8%/23.8%/21.1%'
)

# Fix Fli summary in all-lines box
gen = fix(gen,
    'Steady clutch size (avg 420–550 eggs) with robust summer survival (72.4% SR) and consistent autumn viability (67.4% SR).',
    'Moderate clutch sizes (avg 387–547 eggs). Peaks in Summer (66.8% SR) and Winter (63.1% SR); Spring is the low-performance season (50.6% SR). Plan additional setups in spring for Fli-dependent assays.',
    'Fli summary box: stale 72.4%/67.4% → actual 66.8% summer, 50.6% spring'
)

# Fix Gata summary in all-lines box
gen = fix(gen,
    'Modest clutch sizes (160–310 eggs), peaking in autumn (73.5% SR) and sensitive to spring temperature changes (56.8% SR).',
    'Modest clutch sizes (162–307 eggs). Peaks in Summer (55.6% SR); consistently lower in other seasons (Autumn 31.8%, Spring 37.9%, Winter 27.9%). Schedule intensive Gata collections in summer.',
    'Gata summary box: stale 73.5% autumn / 56.8% spring → actual summer 55.6% peak'
)

# ------------------------------------------------------------------
# FIX 7: metadata year counts in generator variables (if any hardcoded)
# The year counts are dynamically pulled from JSON so this is OK.
# But check if generator hardcodes events_2024 = 460 etc.
# ------------------------------------------------------------------
# Check if already correct in output (they are dynamic from JSON metadata)
print()
print(f'Total fixes applied: {fixes_applied}')

if gen != original:
    with open(GENERATOR, 'w', encoding='utf-8') as f:
        f.write(gen)
    print(f'Generator saved: {GENERATOR}')
else:
    print('No changes made (all targets may have been already fixed)')
