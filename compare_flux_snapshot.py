import argparse
import numpy as np
import pandas as pd
from pathlib import Path

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

def parse_flux(path):
    data = np.loadtxt(path)
    rows = []

    for row in data:
        Z1,A1,Z3,A3,Z5,A5,Z7,A7 = map(int, row[1:9])
        flux = float(row[9])

        reactants = [ZA_to_label(Z1,A1), ZA_to_label(Z3,A3)]
        products  = [ZA_to_label(Z5,A5), ZA_to_label(Z7,A7)]

        reactants = [x for x in reactants if x]
        products  = [x for x in products if x]

        rxn = " + ".join(reactants) + " -> " + " + ".join(products)

        rows.append({
            "reaction": rxn,
            "flux": flux,
            "abs_flux": abs(flux),
            "reactants": reactants,
            "products": products
        })

    return pd.DataFrame(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fileA", required=True)
    ap.add_argument("--fileB", required=True)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--iso", default=None,
                    help="Optional isotope to focus on (e.g. O-15)")
    args = ap.parse_args()

    dfA = parse_flux(Path(args.fileA))
    dfB = parse_flux(Path(args.fileB))

    # merge on reaction string
    df = dfA.merge(dfB, on="reaction", suffixes=("_A", "_B"))

    # avoid zero division
    df = df[(df["abs_flux_A"] > 0) & (df["abs_flux_B"] > 0)]

    df["delta_log10"] = np.log10(df["abs_flux_B"]) - np.log10(df["abs_flux_A"])

    # sort by largest absolute change
    df = df.reindex(df["delta_log10"].abs().sort_values(ascending=False).index)

    print("\n=== Reactions with largest flux change ===\n")
    print(df[["delta_log10", "reaction"]].head(args.top).to_string(index=False))

    # Optional isotope-specific view
    if args.iso:
        iso = args.iso

        prod = df[df["products_A"].apply(lambda lst: iso in lst)]
        dest = df[df["reactants_A"].apply(lambda lst: iso in lst)]

        print(f"\n=== Flux change affecting production of {iso} ===\n")
        print(prod[["delta_log10", "reaction"]]
              .head(args.top).to_string(index=False))

        print(f"\n=== Flux change affecting destruction of {iso} ===\n")
        print(dest[["delta_log10", "reaction"]]
              .head(args.top).to_string(index=False))

if __name__ == "__main__":
    main()
