import argparse
import matplotlib.pyplot as plt
from abundance_io import read_final_abundances, read_initial_abundances

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="runs/baseline")
    # assuming initial_abundance is in root (see abundance_io)
    #ap.add_argument("--init", default="../initial_abundance.dat")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()

    df_i = read_initial_abundances()
    df_f, run_dir = read_final_abundances(args.run)

    # merge and sort_values
    df = df_i.merge(df_f, on="isotope", suffixes=("_i", "_f"))
    df["ratio"] = df["X_f"]/df["X_i"]
    df = df.sort_values("X_f", ascending=False).head(args.top)

    outdir = run_dir / "plots"
    outdir.mkdir(exist_ok=True)

    # plotting
    fig, axs = plt.subplots(1, 3, sharey=True)
    
    # initial
    axs[0].barh(df["isotope"], df["X_i"])
    axs[0].set_xscale("log")
    axs[0].set_title("Initial")

    # final
    axs[1].barh(df["isotope"], df["X_f"])
    axs[1].set_xscale("log")
    axs[1].set_title("Final")

    # ratios
    axs[2].barh(df["isotope"], df["ratio"])
    axs[2].set_xscale("log")
    axs[2].set_title("Ratios (Final/Initial)")

    for ax in axs:
        ax.grid(True, which="both", ls=":")

    fig.suptitle(f"Abandance comparison - {args.run}")
    plt.tight_layout()
    
    outfile = outdir / f"abundance_ratios_top{args.top}.png"
    plt.savefig(outfile, dpi=200)
    plt.show()

    print(f"[OK] Saved {outfile}")

if __name__ == "__main__":
    main()
