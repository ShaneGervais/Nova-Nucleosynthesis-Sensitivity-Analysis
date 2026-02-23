import argparse
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
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
        reactions[rxn] = flux

    return reactions

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--reaction", required=True)
    args = ap.parse_args()

    run_path = Path(args.run)

    flux_files = sorted(run_path.glob("flux_*.DAT"))

    times = []
    fluxes = []

    for f in flux_files:
        idx = int(re.search(r"flux_(\d+).DAT", f.name).group(1))
        reactions = parse_flux_file(f)

        flux = reactions.get(args.reaction, 0.0)

        times.append(idx)
        fluxes.append(abs(flux))

    times = np.array(times)
    fluxes = np.array(fluxes)

    plt.figure()
    plt.plot(times, np.log10(np.maximum(fluxes, 1e-30)))
    plt.xlabel("Flux file index")
    plt.ylabel("log10 |flux|")
    plt.title(f"Time evolution of flux\n{args.reaction}")
    plt.grid(True, ls=":")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
