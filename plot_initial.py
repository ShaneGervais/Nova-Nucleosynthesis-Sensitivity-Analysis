import argparse
#from pathlib import Path
import matplotlib.pyplot as plt
from abundance_io import read_initial_abundances, normalize_run_path

def main():
    ap = argparse.ArgumentParser()
    
    # Used to use an argument to set where the initial_abundance is
    # its assuming you're runnning from root and the file is found there (for initial only)!
    #ap.add_argument("--file", default="../initial_abundance.dat")
    ap.add_argument("--run", required=True, help="runs/baseline")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--threshold", type=float, default=0.0)
    args = ap.parse_args()

    # may need to pass args.file if you eventually have a diff file path for initial X
    df = read_initial_abundances()

    if args.threshold > 0:
        df = df[df["X"] > args.threshold]

    top = df.head(args.top)

    run_dir = normalize_run_path(args.run)
    outdir = run_dir / "plots"
    outdir.mkdir(exist_ok=True)

    plt.figure()
    plt.xscale("log")
    plt.barh(top["isotope"], top["X"])
    plt.xlabel("Mass fraction")
    plt.title(f"Initial abundance (top {args.top})")
    plt.tight_layout()

    outfile = outdir / f"initial_abundances_top{args.top}.png"
    plt.savefig(outfile, dpi=200)
    plt.show()

if __name__ == "__main__":
    main()
