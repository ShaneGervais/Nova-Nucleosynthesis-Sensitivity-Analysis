
import argparse
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def extract_factor(run_name):
    m = re.search(r"fact_([0-9eE\.\-]+)", run_name)
    return float(m.group(1)) if m else None

def get_final_abundances(run_dir: Path):
    csv = run_dir / "final_abundances.csv"
    if not csv.exists():
        return None
    return pd.read_csv(csv)

def get_A(isotope: str) -> int:
    return int(isotope.split("-")[1])

def safe_log10(x):
    # avoid log10(0)
    return np.log10(np.maximum(x, 1e-300))

def fit_slope(logr, logy):
    # linear fit: logy = a*logr + b
    if len(logr) < 2:
        return np.nan
    a, b = np.polyfit(logr, logy, 1)
    return a

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", required=True, help="e.g. 15O_ag")
    ap.add_argument("--baseline", default="runs/baseline")
    ap.add_argument("--runs-dir", default="runs")
    ap.add_argument("--Amax", type=int, default=40)

    ap.add_argument("--topN", type=int, default=12,
                    help="Plot only the top-N most sensitive isotopes")
    ap.add_argument("--minS", type=float, default=0.0,
                    help="Minimum sensitivity S=max|log10(X/Xb)| to include")

    ap.add_argument("--minXb", type=float, default=1e-30,
                    help="Ignore isotopes with tiny baseline abundance")

    args = ap.parse_args()

    runs_path = Path(args.runs_dir)
    baseline_dir = Path(args.baseline)

    # ----------------------------
    # Baseline
    # ----------------------------
    df_base = get_final_abundances(baseline_dir)
    if df_base is None:
        raise RuntimeError(f"Baseline final_abundances.csv not found in {baseline_dir}")

    df_base["A"] = df_base["isotope"].apply(get_A)
    df_base = df_base[df_base["A"] < args.Amax]

    base = dict(zip(df_base["isotope"], df_base["X"]))

    # ----------------------------
    # Collect run curves
    # results[iso] = list of (factor, ratio)
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

        df["A"] = df["isotope"].apply(get_A)
        df = df[df["A"] < args.Amax]
        runX = dict(zip(df["isotope"], df["X"]))

        for iso, Xb in base.items():
            if Xb <= args.minXb:
                continue
            if iso not in runX:
                continue

            ratio = runX[iso] / Xb

            results.setdefault(iso, []).append((factor, ratio))

    if not results:
        raise RuntimeError("No matching runs or no data collected.")

    # ----------------------------
    # Compute sensitivity metrics
    # ----------------------------
    rows = []
    for iso, pts in results.items():
        pts = sorted(pts, key=lambda t: t[0])
        f = np.array([p[0] for p in pts])
        r = np.array([p[1] for p in pts])

        logr = safe_log10(f)
        logy = safe_log10(r)

        S = np.max(np.abs(logy))               # max|log10 ratio|
        alpha = fit_slope(logr, logy)          # dlogX/dlogr

        rows.append((iso, get_A(iso), S, alpha, f, r))

    # rank by sensitivity S
    rows.sort(key=lambda t: t[2], reverse=True)

    # apply minS, then topN
    rows = [t for t in rows if t[2] >= args.minS]
    rows_plot = rows[:args.topN]

    # ----------------------------
    # Print ranked table
    # ----------------------------
    print(f"\n=== Sensitivity ranking for pattern '{args.pattern}' (A < {args.Amax}) ===")
    print(" iso     A     S=max|log10(X/Xb)|     alpha=dlog10(X/Xb)/dlog10(r)")
    print("---------------------------------------------------------------")
    for iso, A, S, alpha, *_ in rows[:max(args.topN, 20)]:
        print(f"{iso:>6s}  {A:>2d}        {S:8.3f}                    {alpha:8.3f}")

    # ----------------------------
    # Plot only the top sensitive isotopes
    # ----------------------------
    plt.figure(figsize=(8,6))

    for iso, A, S, alpha, f, r in rows_plot:
        idx = np.argsort(f)
        f = f[idx]
        r = r[idx]
        plt.plot(f, r, marker="o", label=f"{iso} (S={S:.2f}, α={alpha:.2f})")

    plt.xscale("log")
    plt.yscale("log")
    plt.axhline(1.0, linestyle="--", color="k")
    plt.xlabel("Rate multiplier")
    plt.ylabel("X(run) / X(baseline)")
    plt.title(f"Top {len(rows_plot)} sensitive isotopes (A < {args.Amax})\npattern: {args.pattern}")
    plt.grid(True, which="both", ls=":")
    plt.tight_layout()
    plt.legend(fontsize=8, ncol=2)
    plt.show()


    # ----------------------------
    # Derivative (sensitivity slope) plot
    # ----------------------------
    plt.figure(figsize=(7,6))

    iso_labels = []
    alpha_vals = []

    for iso, A, S, alpha, f, r in rows_plot:
        if not np.isnan(alpha):
            iso_labels.append(iso)
            alpha_vals.append(alpha)

    alpha_vals = np.array(alpha_vals)

    # sort by magnitude of alpha
    idx = np.argsort(np.abs(alpha_vals))[::-1]
    iso_labels = np.array(iso_labels)[idx]
    alpha_vals = alpha_vals[idx]

    plt.barh(iso_labels, alpha_vals)
    plt.axvline(0.0, linestyle="--")

    plt.xlabel(r"$\alpha = d\log_{10}(X/X_b) / d\log_{10}(r)$")
    plt.title(
        f"Sensitivity slopes (A < {args.Amax})\n"
        f"pattern: {args.pattern}"
    )
    plt.grid(True, axis="x", ls=":")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
