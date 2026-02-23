import argparse
import re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def agej_from_iso_file(path: Path) -> float:
    pat = re.compile(r"\bagej\b\s*([0-9.+-Ee]+)")
    with path.open("r") as f:
        for _ in range(120):
            line = f.readline()
            if not line:
                break
            m = pat.search(line)
            if m:
                return float(m.group(1))
    return float("nan")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="Run folder, e.g. runs/baseline")
    ap.add_argument("--iso", required=True, help="Isotope label like H-2, HE-4, N-14, PROT-1")
    ap.add_argument("--logy", action="store_true", help="Log scale y-axis")
    args = ap.parse_args()

    run = Path(args.run)
    summary = run / "summary.csv"
    if not summary.exists():
        raise FileNotFoundError(f"Missing {summary}. Run tools/batch_iso first.")

    abund_df = pd.read_csv(summary)
    sub = abund_df[abund_df["isotope"] == args.iso].copy()
    if sub.empty:
        ex = ", ".join(abund_df["isotope"].unique()[:25])
        raise ValueError(f"Isotope {args.iso} not found. Examples: {ex}")

    # Build a map: iso_massfXXXXX.DAT -> time (agej)
    time_map = {}
    for p in sorted(run.glob("iso_massf*.DAT")):
        time_map[p.name] = agej_from_iso_file(p)

    sub["time"] = sub["file"].map(time_map)
    sub = sub.dropna(subset=["time"]).sort_values("time")

    outdir = run / "plots"
    outdir.mkdir(exist_ok=True)

    plt.figure()
    plt.plot(sub["time"], sub["X"])
    if args.logy:
        plt.yscale("log")
    plt.xlabel("Time - agej (s)")
    plt.ylabel(f"Mass fraction X({args.iso})")
    plt.title(f"Time evolution of {args.iso} - {run.name}")
    plt.tight_layout()
    plt.savefig(outdir / f"{args.iso}_time_evolution.png", dpi=200)
    plt.show()

if __name__ == "__main__":
    main()

