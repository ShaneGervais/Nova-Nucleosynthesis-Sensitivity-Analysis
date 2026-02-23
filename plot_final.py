import argparse
#from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from abundance_io import read_final_abundances

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="Run folder, e.g. runs/baseline")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()

    #run = Path(args.run)
    #df = pd.read_csv(run / "final_abundances.csv").sort_values("X", ascending=False)
    df, run_dir = read_final_abundances(args.run)
    top = df.head(args.top)

    outdir = run_dir / "plots"
    outdir.mkdir(exist_ok=True)

    plt.figure()
    plt.barh(top["isotope"], top["X"])
    plt.xlabel("Mass Fraction")
    plt.title(f"Final abundances (top {args.top}) - {run_dir.name}")
    plt.tight_layout()
    plt.savefig(outdir / f"final_top{args.top}.png", dpi=200)
    outfile = outdir / f"final_abundances_top{args.top}.png"
    plt.savefig(outfile, dpi=200)
    plt.show()

    print(f"[OK] Saved {outfile}")

if __name__ == "__main__":
    main()
