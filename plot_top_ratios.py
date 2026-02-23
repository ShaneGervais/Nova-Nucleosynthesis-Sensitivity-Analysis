import matplotlib.pyplot as plt
from abundance_io import *
import argparse
import numpy as np

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="e.g. runs/baseline")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--min-init", type=float, default=1e-10, 
                    help="Ignore isotopes with tiny initial X")
    ap.add_argument("--logtol", type=float, default=0.1, 
                    help="Ignore istopes with |log10(Xf/Xi)| < logtol")
    args = ap.parse_args()

    # reading abundances into df
    df_i = read_initial_abundances()
    df_f, run_dir = read_final_abundances(args.run)
    df = df_i.merge(df_f, on="isotope", how="outer", suffixes=("_i", "_f"))
    if df.empty:
        raise RuntimeError(
            "No isotopes left after removing unchanged ones "
            f"(logtol={args.logtol})"
        )

    #print(df)
    df["X_i"] = df["X_i"].fillna(0.0)
    df["X_f"] = df["X_f"].fillna(0.0)
    #df = df[df["X_i"] > args.min_init]
    #print(df)
    # take the ratio then sort_values
    
    # classifying changes from nova
    created = df[(df["X_i"] == 0) & (df["X_f"] > 0)].copy()
    destroyed = df[(df["X_i"] > 0) & (df["X_f"] == 0)].copy()

    # computing ratio while ignore ratios being 0 or inf (using min_init)
    ratio_df = df[(df["X_i"] > args.min_init) & df["X_f"] > args.min_init].copy()
    ratio_df["ratio"] = ratio_df["X_f"] / ratio_df["X_i"]
    ratio_df["log_ratio"] = np.log10(ratio_df["ratio"])
    
    # ignore unchanged isotopes only
    ratio_df = ratio_df[np.abs(ratio_df["log_ratio"]) > args.logtol].head(args.top)

    # gathering isotopes that were enhanced and depleted during nova (these are used in the ratio plot
    #not the ones created or destroyed i.e. no X_i or X_f)
    enhanced = ratio_df[ratio_df["ratio"] > 1].copy()
    depleted = ratio_df[ratio_df["ratio"] < 1].copy()

    # rank by magnitude of change and keep the top based on --top argument
    ratio_df = ratio_df.reindex(
        ratio_df["log_ratio"].abs().sort_values(ascending=False).index
    ).head(args.top)

    # ---------------------------------------------------------------------
    # PRINTING SUMMMARIES
    # contains isotopes created, destroyed (completely), enhanced and depleted during synthesis
    # ---------------------------------------------------------------------
    if not created.empty:
        print("\n=== Newly synthesized isotopes (Xi = 0) ===")
        for _, r in created.sort_values("X_f", ascending=False).iterrows():
            print(f"{r['isotope']:>6s} X_f = {r['X_f']:.3e}")

    if not destroyed.empty:
        print("\n=== Completely destroyed isotopes (Xf = 0) ===")
        for _, r in destroyed.sort_values("X_i", ascending=False).iterrows():
            print(f"{r['isotope']:>6s}")

    print("\n=== Enhanced isotopes ===")
    for _, r in enhanced.iterrows():
        print(f"{r['isotope']:>6s} x{r['ratio']:.2e}")

    print("\n=== Depleted isotopes ===")
    for _, r in depleted.iterrows():
        print(f"{r['isotope']:>6s} x{r['ratio']:.2e} ")

    # ---------------------------------------------------------------------
    # PLOTTING
    # ---------------------------------------------------------------------
    
    # create output directory for plots or basically add the plot to the created folder
    outdir = run_dir / "plots"
    outdir.mkdir(exist_ok=True)

    #ratio_df = ratio_df["log_ratio"] > args.top

    # plotting
    plt.figure()
    plt.barh(ratio_df["isotope"], ratio_df["log_ratio"])
    plt.axvline(0.0, color='k', linestyle="--")
    plt.xlabel(r"$\log_{10}(X_f / X_i)$")
    #plt.xscale("log")
    plt.title(f"Top {args.top} abundance changes during nova \n({run_dir.name})")
    plt.grid(True, which="both", ls=":")
    plt.tight_layout()

    outfile = outdir / f"top{args.top}_synthesis_ratios.png"
    plt.savefig(outfile, dpi=200)
    plt.show()

    print(f"[OK] Saved {outfile}")
    

if __name__ == "__main__":
    main()
