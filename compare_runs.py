import argparse
import matplotlib.pyplot as plt
import numpy as np
from abundance_io import read_final_abundances

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runA", required=True, help="Reference run (e.g. runs/baseline)")
    ap.add_argument("--runB", required=True, help="Comparison run (e.g. runs/test)")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--logtol", type=float, default=0.1,
                    help="Ignore changes with |log10(Xf_B/Xf_A)| < logtol")
    args = ap.parse_args()

    # read final abundances of both runs
    df_A, runA_dir = read_final_abundances(args.runA)
    df_B, runB_dir = read_final_abundances(args.runB)

    df_A = df_A.rename(columns={"X": "X_A"})
    df_B = df_B.rename(columns={"X": "X_B"})
    
    #print(df_A)

    # merge
    df = df_A.merge(df_B, on="isotope", how="outer")
    df["X_A"] = df["X_A"].fillna(0.0)
    df["X_B"] = df["X_B"].fillna(0.0)

    #print(df)

    # classify changes
    created_B = df[(df["X_A"] == 0) & (df["X_B"] > 0)].copy()
    destroyed_B = df[(df["X_A"] > 0) & (df["X_B"] == 0)].copy()
    both = df[(df["X_A"] > 0) & (df["X_B"] > 0)].copy()

    #print(created_B)
    print(both)
    # ratio analysis
    both["ratio_BA"] = both["X_B"] / both["X_A"]
    both["log_ratio"] = np.log10(both["ratio_BA"])
    print(both["ratio_BA"])
    print(both["log_ratio"])
    both = both[np.abs(both["log_ratio"]) > args.logtol]

    if both.empty:
        print("\n------------------------------------------------------")
        print(f"No significant change with a tolerance of {args.logtol}")
        return 0

    #both["log_ratio"] = both["log_ratio"].fillna(0.0)
    #both["log_ratio"] = both["log_ratio"].replace([-np.inf, np.inf], 1000)

    print(both["ratio_BA"])
    print(both["log_ratio"])

    # rank
    both = both.reindex(
        both["log_ratio"].abs().sort_values(ascending=False).index
    ).head(args.top)

    enhanced = both[both["log_ratio"] > 0]
    depleted = both[both["log_ratio"] < 0]

    # -------------------------------------------------
    # PRINT SUMMARY
    # -------------------------------------------------

    print(f"\n=== Comparison: {runB_dir.name} relative to {runA_dir.name} ===")
    print("\n--- Created only in run B ---")
    for _, r in created_B.sort_values("X_B", ascending=False).iterrows():
        print(f"{r['isotope']:>6s} X_f(B) = {r['X_B']:.3e}")

    print("\n--- Destroyed only in run B ---")
    for _, r in destroyed_B.sort_values("X_A", ascending=False).iterrows():
        print(f"{r['isotope']:>6s}")

    print("\n--- Enhanced in run B ---")
    for _, r in enhanced.iterrows():
        print(f"{r['isotope']:>6s} x{r['ratio_BA']:.2e}")

    print("\n--- Depleted in run B ---")
    for _, r in depleted.iterrows():
        print(f"{r['isotope']:>6s} /{1/r['ratio_BA']:.2e}")

    # -------------------------------------------------
    # PLOT
    # -------------------------------------------------

    outdir = runB_dir / "plots"
    outdir.mkdir(exist_ok=True)

    plt.figure()
    plt.barh(both["isotope"], both["log_ratio"])
    plt.axvline(0.0, color='k', linestyle="--")
    
    xmin = min(both["log_ratio"].min(), -0.05)
    xmax = max(both["log_ratio"].max(), 0.05)
    plt.xlim(xmin, xmax)
    plt.xlabel(r"$\log_{10}(X_f^{(B)} / X_f^{(A)})$")
    plt.title(
        f"Final abundance changes\n"
        f"{runB_dir.name} vs {runA_dir.name}"
    )
    plt.grid(True, axis="x", ls=":")
    plt.tight_layout()

    outfile = outdir / f"compare_{runB_dir.name}_vs_{runA_dir.name}.png"
    plt.savefig(outfile, dpi=200)
    plt.show()

    print(f"\n[OK] Saved {outfile}\n")

if __name__ == "__main__":
    main()
