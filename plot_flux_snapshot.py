import re
import matplotlib.pyplot as plt
import numpy as np
import argparse
from pathlib import Path

elements = {
    1:"H", 2:"He", 3:"Li", 4:"Be", 5:"B", 6:"C",
    7:"N", 8:"O", 9:"F", 10:"Ne", 11:"Na", 12:"Mg"
}

def ZA_to_label(Z, A):
    if Z == 0:
        return ""
    return f"{elements.get(Z, 'Z'+str(Z))}-{A}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()

    data = np.loadtxt(args.file)

    reactions = []
    fluxes = []

    for row in data:
        Z1, A1, Z3, A3, Z5, A5, Z7, A7 = map(int, row[1:9])
        flux = row[9]

        if abs(flux) < 1e-30:
            continue

        reactants = []
        products = []

        if Z1 > 0: reactants.append(ZA_to_label(Z1,A1))
        if Z3 > 0: reactants.append(ZA_to_label(Z3,A3)) 
        if Z5 > 0: products.append(ZA_to_label(Z5,A5))
        if Z7 > 0: products.append(ZA_to_label(Z7,A7))

        reaction_str = " , ".join(reactants) + "->" + " , ".join(products)
        reactions.append(reaction_str)
        fluxes.append(abs(flux))

    reactions = np.array(reactions)
    fluxes = np.array(fluxes)

    idx = np.argsort(fluxes)[::-1][:args.top]

    reactions = reactions[idx]
    fluxes = fluxes[idx]

    plt.figure()
    plt.plot(reactions, np.log10(fluxes))
    plt.xlabel("log10 |dY/dt|")
    plt.title("Dominant Reaction Fluxes at time stamp")
    #plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
