import csv
import json
import math
import numpy as np
from datetime import datetime

# Load breeding events from breeding_dashboard_data.json
with open('breeding_dashboard_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

events = data.get('events', [])

clean_events = []
monthly_stats = {m: {'events': 0, 'total_eggs': 0, 'live_24h': 0, 'sr_list': [], 'eggs_list': []} for m in range(1, 13)}

# Doha monthly climate approximations (Mean Temp in Celsius, Humidity %)
doha_climate = {
    1: {'temp': 17.5, 'humidity': 71},
    2: {'temp': 18.5, 'humidity': 70},
    3: {'temp': 22.1, 'humidity': 63},
    4: {'temp': 26.8, 'humidity': 55},
    5: {'temp': 32.5, 'humidity': 44},
    6: {'temp': 35.1, 'humidity': 41},
    7: {'temp': 36.6, 'humidity': 49},
    8: {'temp': 36.2, 'humidity': 58},
    9: {'temp': 33.6, 'humidity': 62},
    10: {'temp': 29.6, 'humidity': 63},
    11: {'temp': 24.4, 'humidity': 68},
    12: {'temp': 19.5, 'humidity': 74}
}

for ev in events:
    d_str = ev.get('date', '')
    eggs = ev.get('eggs_0h', 0)
    sr_24h = ev.get('sr_24h', 0)
    live_24h = ev.get('live_24h', 0)
    line = ev.get('line', '')
    
    dt = None
    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']:
        try:
            dt = datetime.strptime(d_str, fmt)
            break
        except Exception:
            pass
            
    if dt is not None:
        m = dt.month
        monthly_stats[m]['events'] += 1
        monthly_stats[m]['total_eggs'] += eggs
        monthly_stats[m]['live_24h'] += live_24h
        monthly_stats[m]['sr_list'].append(sr_24h)
        monthly_stats[m]['eggs_list'].append(eggs)
        
        # Season definition for Qatar:
        # Winter: Dec, Jan, Feb
        # Spring: Mar, Apr, May
        # Summer: Jun, Jul, Aug
        # Autumn: Sep, Oct, Nov
        season = 'Winter' if m in [12, 1, 2] else ('Spring' if m in [3, 4, 5] else ('Summer' if m in [6, 7, 8] else 'Autumn'))
        
        clean_events.append({
            'date': dt,
            'year': dt.year,
            'month': m,
            'season': season,
            'eggs_0h': eggs,
            'sr_24h': sr_24h,
            'live_24h': live_24h,
            'line': line,
            'doha_temp': doha_climate[m]['temp'],
            'doha_humidity': doha_climate[m]['humidity']
        })

print(f"Dataset: {len(clean_events)} valid dated breeding events analyzed (2024-2026).")

# 1. Monthly Summary Table
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
print("\n=== 1. MONTH-BY-MONTH CLIMATE & EMBRYO BENCHMARKS ===")
print(f"{'Month':<6} | {'Events':<7} | {'Total Eggs':<10} | {'Mean Clutch':<12} | {'Mean 24h SR%':<12} | {'Outdoor Temp':<13} | {'Outdoor RH%'}")
print("-" * 85)

for m in range(1, 13):
    st = monthly_stats[m]
    cnt = st['events']
    if cnt > 0:
        avg_clutch = np.mean(st['eggs_list']) if st['eggs_list'] else 0
        avg_sr = np.mean(st['sr_list']) if st['sr_list'] else 0
        print(f"{month_names[m-1]:<6} | {cnt:<7} | {st['total_eggs']:<10} | {avg_clutch:<12.1f} | {avg_sr:<11.1f}% | {doha_climate[m]['temp']:<5.1f} deg C    | {doha_climate[m]['humidity']}%")

# 2. Seasonal Aggregates
seasons = ['Winter', 'Spring', 'Summer', 'Autumn']
season_data = {s: {'events': 0, 'eggs': [], 'sr': []} for s in seasons}

for ev in clean_events:
    s = ev['season']
    season_data[s]['events'] += 1
    season_data[s]['eggs'].append(ev['eggs_0h'])
    season_data[s]['sr'].append(ev['sr_24h'])

print("\n=== 2. SEASONAL AGGREGATES (QATAR CLIMATIC CYCLES) ===")
print(f"{'Season':<8} | {'Spawns':<7} | {'Mean Clutch Size':<17} | {'Mean 24h SR%':<14} | {'Survival StdDev'}")
print("-" * 75)
for s in seasons:
    sd = season_data[s]
    mean_clutch = np.mean(sd['eggs'])
    mean_sr = np.mean(sd['sr'])
    std_sr = np.std(sd['sr'])
    print(f"{s:<8} | {sd['events']:<7} | {mean_clutch:<17.1f} | {mean_sr:<13.1f}% | {std_sr:.1f}%")

# 3. Harmonic Regression Analysis (Fourier 1-Harmonic Model)
t = np.array([ev['month'] for ev in clean_events])
y_sr = np.array([ev['sr_24h'] for ev in clean_events])
y_eggs = np.array([ev['eggs_0h'] for ev in clean_events])
temp_arr = np.array([ev['doha_temp'] for ev in clean_events])
hum_arr = np.array([ev['doha_humidity'] for ev in clean_events])

sin_t = np.sin(2 * np.pi * t / 12)
cos_t = np.cos(2 * np.pi * t / 12)
X_harm = np.column_stack([np.ones_like(t), sin_t, cos_t])

# OLS for SR
beta_sr, _, _, _ = np.linalg.lstsq(X_harm, y_sr, rcond=None)
amplitude_sr = math.sqrt(beta_sr[1]**2 + beta_sr[2]**2)
# Peak month of harmonic curve: tan(omega * t_peak) = beta_1 / beta_2
phase_rad = math.atan2(beta_sr[1], beta_sr[2])
peak_month = (phase_rad * 12 / (2 * np.pi)) % 12
if peak_month <= 0: peak_month += 12
trough_month = (peak_month + 6) % 12
if trough_month <= 0: trough_month += 12

# ANOVA / F-test for Harmonic Seasonality
n = len(y_sr)
k = 2 # 2 harmonic predictors
ss_tot = np.sum((y_sr - np.mean(y_sr))**2)
ss_res = np.sum((y_sr - X_harm @ beta_sr)**2)
ss_reg = ss_tot - ss_res
f_stat = (ss_reg / k) / (ss_res / (n - k - 1))
r2 = ss_reg / ss_tot

# Correlations
r_sr_temp = np.corrcoef(temp_arr, y_sr)[0, 1]
r_sr_hum = np.corrcoef(hum_arr, y_sr)[0, 1]
r_clutch_temp = np.corrcoef(temp_arr, y_eggs)[0, 1]

print("\n=== 3. STATISTICAL HARMONIC & CLIMATE CORRELATION FINDINGS ===")
print(f"Overall Facility Mean 24h Survival: {beta_sr[0]:.2f}%")
print(f"Harmonic Model: SR%(m) = {beta_sr[0]:.2f} + ({beta_sr[1]:.2f} * sin(2pi*m/12)) + ({beta_sr[2]:.2f} * cos(2pi*m/12))")
print(f"Seasonal Amplitude: +/- {amplitude_sr:.2f}% (Peak-to-Trough Delta: {2*amplitude_sr:.2f}%)")
print(f"Calculated Peak Month: Month {peak_month:.1f} (~{month_names[int(peak_month)-1]} / {month_names[int(peak_month)%12]})")
print(f"Calculated Trough Month: Month {trough_month:.1f} (~{month_names[int(trough_month)-1]} / {month_names[int(trough_month)%12]})")
print(f"ANOVA F-Statistic for Seasonality: F = {f_stat:.3f} (n = {n})")
print(f"Correlation with Outdoor Temperature: r = {r_sr_temp:+.4f}")
print(f"Correlation with Outdoor Relative Humidity: r = {r_sr_hum:+.4f}")
print(f"Correlation with Clutch Size: r = {r_clutch_temp:+.4f}")
