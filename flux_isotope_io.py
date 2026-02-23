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

def parse_flux_file(path: Path, min_flux=1e-30) -> pd.DataFrame:
    data = np.loadtxt(path)
    rows = []
    for row in data:
        # columns: idx, Z1,A1,Z3,A3,Z5,A5,Z7,A7, flux, energy, timescale
        Z1, A1, Z3, A3, Z5, A5, Z7, A7 = map(int, row[1:9])
        flux = float(row[9])

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
            "reactants": reactants,
            "products": products,
            "reactants_str": " + ".join(reactants),
            "products_str": " + ".join(products),
        })
    return pd.DataFrame(rows)

def pretty_print(df: pd.DataFrame, title: str, top: int):
    if df.empty:
        print(f"\n{title}\n  (none above threshold)\n")
        return
    df = df.sort_values("abs_flux", ascending=False).head(top)
    print(f"\n{title}\n")
    print(df[["log10_abs_flux", "flux", "reaction"]].to_string(index=False))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="path to flux_XXXXX.DAT")
    ap.add_argument("--iso", required=True, help="e.g. O-15, F-19")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--min-flux", type=float, default=1e-30)
    ap.add_argument("--csvdir", default=None, help="optional directory to write CSV tables")
    args = ap.parse_args()

    path = Path(args.file)
    df = parse_flux_file(path, min_flux=args.min_flux)

    if df.empty:
        print("No reactions passed the flux threshold.")
        return

    iso = args.iso

    producers = df[df["products"].apply(lambda lst: iso in lst)].copy()
    destroyers = df[df["reactants"].apply(lambda lst: iso in lst)].copy()

    # Separate by sign can be useful, but keep simple for now:
    # flux sign conventions can be subtle depending on implementation.
    pretty_print(producers, f"=== Top producers of {iso} (appears in products) ===", args.top)
    pretty_print(destroyers, f"=== Top destroyers of {iso} (appears in reactants) ===", args.top)

    if args.csvdir:
        outdir = Path(args.csvdir)
        outdir.mkdir(parents=True, exist_ok=True)

        prod_csv = outdir / f"{iso}_producers_{path.name}.csv"
        dest_csv = outdir / f"{iso}_destroyers_{path.name}.csv"

        producers.sort_values("abs_flux", ascending=False).to_csv(prod_csv, index=False)
        destroyers.sort_values("abs_flux", ascending=False).to_csv(dest_csv, index=False)

        print(f"\n[OK] Wrote {prod_csv}")
        print(f"[OK] Wrote {dest_csv}")

if __name__ == "__main__":
    main()
