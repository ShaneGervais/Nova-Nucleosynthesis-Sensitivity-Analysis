
import argparse
import numpy as np
import pandas as pd

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

def parse_flux_file(path, flux_col=9, min_flux=1e-30):
    data = np.loadtxt(path)
    rows = []

    for row in data:
        # columns: idx, Z1,A1,Z3,A3,Z5,A5,Z7,A7, flux, energy, timescale
        Z1, A1, Z3, A3, Z5, A5, Z7, A7 = map(int, row[1:9])
        flux = float(row[flux_col])
        if abs(flux) < min_flux:
            continue

        reactants = [ZA_to_label(Z1, A1), ZA_to_label(Z3, A3)]
        products  = [ZA_to_label(Z5, A5), ZA_to_label(Z7, A7)]

        reactants = [x for x in reactants if x]
        products  = [x for x in products if x]

        rxn = " + ".join(reactants) + " -> " + " + ".join(products)

        rows.append({
            "reaction": rxn,
            "flux": flux,
            "abs_flux": abs(flux),
            "log10_abs_flux": np.log10(abs(flux)),
            "reactants": " + ".join(reactants),
            "products": " + ".join(products),
        })

    return pd.DataFrame(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="path to flux_XXXXX.DAT")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--min-flux", type=float, default=1e-30)
    ap.add_argument("--csv", default=None, help="optional output CSV path")
    args = ap.parse_args()

    df = parse_flux_file(args.file, min_flux=args.min_flux)
    if df.empty:
        print("No reactions passed the flux threshold.")
        return

    df = df.sort_values("abs_flux", ascending=False).head(args.top)

    # pretty print (fixed-width)
    print(f"\nTop {args.top} reactions by |flux| from {args.file}\n")
    print(df[["log10_abs_flux", "flux", "reaction"]].to_string(index=False))

    if args.csv:
        df.to_csv(args.csv, index=False)
        print(f"\n[OK] Wrote {args.csv}")

if __name__ == "__main__":
    main()
