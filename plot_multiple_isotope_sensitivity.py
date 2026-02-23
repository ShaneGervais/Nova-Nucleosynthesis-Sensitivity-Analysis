
import argparse
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def extract_factor(run_name):
    match = re.search(r"fact_([0-9eE\.\-]+)", run_name)
    if match:
        return float(match.group(1))
    return None

def get_final_abundances(run_dir):
    csv = run_dir / "final_abundances.csv"
    if not csv.exists():
        return None
    return pd.read_csv(csv)

def get_A_from_isotope(isotope):
    # assumes format like F-19
    return int(isotope.split("-")[1])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", required=True,
                    help="e.g. 15O_ag")
    ap.add_argument("--baseline", default="runs/baseline")
    ap.add_argument("--runs-dir", default="runs")
    ap.add_argument("--Amax", type=int, default=40)
    args = ap.parse_args()

    runs_path = Path(args.runs_dir)
    baseline_dir = Path(args.baseline)

    # ----------------------------
    # Load baseline abundances
    # ----------------------------
    df_base = get_final_abundances(baseline_dir)
    if df_base is None:
        raise RuntimeError("Baseline final_abundances.csv not found")

    # keep only A < Amax
    df_base["A"] = df_base["isotope"].apply(get_A_from_isotope)
    df_base = df_base[df_base["A"] < args.Amax]

    base_dict = dict(zip(df_base["isotope"], df_base["X"]))

    # ----------------------------
    # Loop over runs
    # ----------------------------
    results = {}

    for run in runs_path.iterdir():
        if not run.is_dir():
            continue
        if args.pattern not in run.name:
            continue

        factor = extract_factor(run.name)
        if factor is None:
            continue

        df = get_final_abundances(run)
        if df is None:
            continue

        df["A"] = df["isotope"].apply(get_A_from_isotope)
        df = df[df["A"] < args.Amax]

        run_dict = dict(zip(df["isotope"], df["X"]))

        for iso in base_dict:
            if iso not in run_dict:
                continue

            if iso not in results:
                results[iso] = {"factor": [], "ratio": []}

            ratio = run_dict[iso] / base_dict[iso]
            results[iso]["factor"].append(factor)
            results[iso]["ratio"].append(ratio)

    # ----------------------------
    # Plot
    # ----------------------------
    plt.figure(figsize=(8,6))

    for iso, data in results.items():
        factors = np.array(data["factor"])
        ratios = np.array(data["ratio"])

        idx = np.argsort(factors)
        factors = factors[idx]
        ratios = ratios[idx]

        plt.plot(factors, ratios, marker="o", label=iso)

    plt.xscale("log")
    plt.yscale("log")
    plt.axhline(1.0, linestyle="--", color="k")

    plt.xlabel("Rate multiplier")
    plt.ylabel("X(run) / X(baseline)")
    plt.title(f"Sensitivity (A < {args.Amax}) to {args.pattern}")
    plt.grid(True, which="both", ls=":")
    plt.tight_layout()

    plt.legend(fontsize=8, ncol=2)
    plt.show()

if __name__ == "__main__":
    main()
