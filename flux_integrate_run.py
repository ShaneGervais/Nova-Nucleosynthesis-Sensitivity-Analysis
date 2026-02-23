import argparse
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict

elements = {
    1:"H", 2:"He", 3:"Li", 4:"Be", 5:"B", 6:"C",
    7:"N", 8:"O", 9:"F", 10:"Ne", 11:"Na", 12:"Mg",
    13:"Al", 14:"Si", 15:"P", 16:"S", 17:"Cl", 18:"Ar",
    19:"K", 20:"Ca"
}

def ZA_to_label(Z, A):
    if Z == 0:
        return None
    return f"{elements.get(Z, f'Z{Z}')}-{A}"

def parse_flux_file(path):
    data = np.loadtxt(path)
    reactions = {}

    for row in data:
        Z1,A1,Z3,A3,Z5,A5,Z7,A7 = map(int, row[1:9])
        flux = float(row[9])

        reactants = [ZA_to_label(Z1,A1), ZA_to_label(Z3,A3)]
        products  = [ZA_to_label(Z5,A5), ZA_to_label(Z7,A7)]

        reactants = [x for x in reactants if x]
        products  = [x for x in products if x]

        rxn = " + ".join(reactants) + " -> " + " + ".join(products)
        reactions[rxn] = abs(flux)

    return reactions

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--csv", default=None)
    ap.add_argument("--plot", action="store_true")
    args = ap.parse_args()

    run_path = Path(args.run)
    flux_files = sorted(run_path.glob("flux_*.DAT"))

    if not flux_files:
        raise RuntimeError("No flux_*.DAT files found.")

    integrated_flux = defaultdict(float)

    for f in flux_files:
        reactions = parse_flux_file(f)

        for rxn, flux in reactions.items():
            integrated_flux[rxn] += flux

    df = pd.DataFrame({
        "reaction": list(integrated_flux.keys()),
        "integrated_flux": list(integrated_flux.values())
    })

    df["log10_integrated_flux"] = np.log10(
        np.maximum(df["integrated_flux"], 1e-300)
    )

    df = df.sort_values("integrated_flux", ascending=False)

    print(f"\n=== Top {args.top} reactions by integrated flow ===\n")
    print(df.head(args.top)[
        ["log10_integrated_flux", "reaction"]
    ].to_string(index=False))

    if args.csv:
        df.to_csv(args.csv, index=False)
        print(f"\n[OK] Wrote {args.csv}")

    if args.plot:
        top_df = df.head(args.top)

        plt.figure(figsize=(8,6))
        plt.barh(
            top_df["reaction"][::-1],
            top_df["log10_integrated_flux"][::-1]
        )
        plt.xlabel("log10 Integrated |Flux|")
        plt.title(f"Integrated reaction flow\n{run_path.name}")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()
