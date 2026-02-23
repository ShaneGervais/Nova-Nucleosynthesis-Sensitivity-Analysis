
import os
import re
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ======================================
# CONFIG
# ======================================
RUNS_DIR = "runs"

if len(sys.argv) < 2:
    print("Usage: python analysis/plot_final_vs_factor.py F-19")
    sys.exit(1)

ISOTOPE = sys.argv[1]
PLOT_RATIO = True

# ======================================
# Extract factor
# ======================================
def extract_factor(folder_name):
    if folder_name == "baseline":
        return 1.0

    match = re.search(r'fact_([0-9eE\.\-]+)', folder_name)
    if match:
        return float(match.group(1))

    return None

# ======================================
# Scan runs
# ======================================
factors = []
abundances = []

for folder in os.listdir(RUNS_DIR):
    full_path = os.path.join(RUNS_DIR, folder)

    if not os.path.isdir(full_path):
        continue

    factor = extract_factor(folder)
    if factor is None:
        continue

    final_file = os.path.join(full_path, "final_abundances.csv")
    if not os.path.exists(final_file):
        continue

    df = pd.read_csv(final_file)

    isotope_column = df.columns[0]
    value_column = df.columns[1]

    row = df[df[isotope_column] == ISOTOPE]

    if row.empty:
        continue

    abundance = float(row.iloc[0][value_column])

    factors.append(factor)
    abundances.append(abundance)

# Convert to arrays
factors = np.array(factors)
abundances = np.array(abundances)

# Sort
order = np.argsort(factors)
factors = factors[order]
abundances = abundances[order]

# ======================================
# Compute ratio
# ======================================
if PLOT_RATIO:
    if 1.0 not in factors:
        raise RuntimeError("Baseline (factor=1) not found.")

    baseline_value = abundances[factors == 1.0][0]
    ratios = abundances / baseline_value
else:
    ratios = abundances

# ======================================
# Print Results
# ======================================
print("\nSensitivity Results for", ISOTOPE)
print("======================================")

for f, a, r in zip(factors, abundances, ratios):
    print(f"Factor = {f:>10g} | Final = {a:.6e} | Ratio = {r:.6e}")

# ======================================
# Save CSV summary
# ======================================
summary_df = pd.DataFrame({
    "Factor": factors,
    "Final_Abundance": abundances,
    "Ratio_to_Baseline": ratios
})

output_csv = f"analysis/{ISOTOPE}_sensitivity.csv"
summary_df.to_csv(output_csv, index=False)

print("\nSaved numerical results to:", output_csv)

# ======================================
# Save Plot
# ======================================
plt.figure(figsize=(8,6))
plt.plot(factors, ratios, marker='o')
plt.xscale('log')

plt.xlabel("Rate Multiplication Factor")
plt.ylabel(f"{ISOTOPE} Final / Baseline")
plt.title(f"Sensitivity Study for {ISOTOPE}")

plt.grid(True)
plt.tight_layout()

output_png = f"analysis/{ISOTOPE}_sensitivity.png"
plt.savefig(output_png, dpi=300)

print("Saved plot to:", output_png)
plt.show()
