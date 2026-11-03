import json
import numpy as np
from datetime import datetime
from collections import defaultdict

tanks_dob = {}
with open('FishNet Exported Data/tanks.tab', 'r', encoding='utf-8-sig', errors='replace') as f:
    f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 6:
            tuid = parts[0].strip()
            dob_str = parts[5].strip()
            for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%b-%y', '%m/%d/%y']:
                try:
                    tanks_dob[tuid] = datetime.strptime(dob_str, fmt)
                    break
                except: pass

with open('breeding_dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

events = d.get('events', [])
parsed = []
for ev in events:
    d_str = ev.get('date', '')
    dt = None
    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']:
        try:
            dt = datetime.strptime(d_str, fmt)
            break
        except Exception: pass
    if not dt: continue
    parsed.append((dt, ev.get('tank_id', ''), ev))

parsed.sort(key=lambda x: x[0])

tank_prev = {}
clean_dataset = []

for dt, tid, ev in parsed:
    m = dt.month
    s = 'Winter' if m in [12, 1, 2] else ('Spring' if m in [3, 4, 5] else ('Summer' if m in [6, 7, 8] else 'Autumn'))
    l = ev.get('line', 'Other')
    sr = ev.get('sr_24h', 0.0)
    eggs = ev.get('eggs_0h', 0)
    
    # Rest interval
    interval = None
    if tid and tid in tank_prev:
        delta = (dt - tank_prev[tid]).days
        if 0 < delta <= 120:
            interval = delta
    if tid:
        tank_prev[tid] = dt
        
    # Age
    age_m = None
    if tid in tanks_dob:
        age = (dt - tanks_dob[tid]).days / 30.4375
        if 2 <= age <= 36:
            age_m = age
            
    if age_m is not None and interval is not None and l in ['AB', 'Casper', 'Fli', 'Gata']:
        clean_dataset.append({
            'sr_24h': sr,
            'eggs': eggs,
            'age_m': age_m,
            'interval': interval,
            'line': l,
            'season': s,
            'tank_id': tid
        })

print(f'Events with full covariates (Age + Interval + Line + Season): N = {len(clean_dataset)}')

# Design matrix for OLS:
# Baseline: Line = AB, Season = Winter
y = np.array([row['sr_24h'] for row in clean_dataset])
X_cols = ['Intercept', 'Age_Months', 'Interval_Days', 'Line_Casper', 'Line_Fli', 'Line_Gata', 'Season_Spring', 'Season_Summer', 'Season_Autumn']
X = []
for r in clean_dataset:
    row_x = [
        1.0,
        r['age_m'],
        r['interval'],
        1.0 if r['line'] == 'Casper' else 0.0,
        1.0 if r['line'] == 'Fli' else 0.0,
        1.0 if r['line'] == 'Gata' else 0.0,
        1.0 if r['season'] == 'Spring' else 0.0,
        1.0 if r['season'] == 'Summer' else 0.0,
        1.0 if r['season'] == 'Autumn' else 0.0
    ]
    X.append(row_x)

X = np.array(X)
beta, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
n = len(y)
p = X.shape[1]
df_resid = n - p
sigma2 = np.sum((y - X @ beta)**2) / df_resid
cov_beta = sigma2 * np.linalg.inv(X.T @ X)
se_beta = np.sqrt(np.diag(cov_beta))
t_stats = beta / se_beta

# 2-tailed p-values approximation from t-stat (for large df normal approx)
import math
p_vals = [2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))) for t in t_stats]

print('\n=== MULTIVARIABLE REGRESSION (MUTUALLY CONTROLLING FOR CONFOUNDERS) ===')
print(f'Dependent Variable: 24h Survival Rate (%), N = {n}, Residual SE = {np.sqrt(sigma2):.2f}%')
print(f'{"Predictor":<18} | {"Coef":<10} | {"Std.Err":<9} | {"t-stat":<9} | {"p-value":<10} | {"Significance"}')
print('-'*75)
for i, name in enumerate(X_cols):
    sig = '***' if p_vals[i] < 0.001 else ('**' if p_vals[i] < 0.01 else ('*' if p_vals[i] < 0.05 else 'ns'))
    print(f'{name:<18} | {beta[i]:<+10.3f} | {se_beta[i]:<9.3f} | {t_stats[i]:<+9.3f} | {p_vals[i]:<10.4e} | {sig}')
