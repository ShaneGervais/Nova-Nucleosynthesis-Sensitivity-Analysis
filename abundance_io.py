from pathlib import Path
import pandas as pd
import re

ROOT = Path(__file__).resolve().parents[1] #ppn_nova/

def normalize_run_path(run_arg):
    run_path = Path(run_arg)

    if not run_path.is_absolute():
        run_path = ROOT / run_path
    if not run_path.exists():
        raise FileNotFoundError(run_path)

    return run_path

def read_initial_abundances(fname=None):
    
    # ASSUMING: you're runnning from root! SO the default is that the file is there
    # if not might need to change the code directly

    if fname is None:
        fname = ROOT / "initial_abundance.dat"
    else:
        fname = Path(fname)


    isotopes, X = [], []

    with open(fname, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            xi = float(parts[-1])

            if len(parts) >= 4 and parts[1].isalpha() and parts[2].isdigit():
                el, A = parts[1], parts[2]
            else:
                m = re.match(r"([a-zA-Z]+)(\d+)", parts[1])
                if not m:
                    continue
                el, A = m.groups()

            isotopes.append(f"{el.capitalize()}-{A}")
            X.append(xi)

    df = pd.DataFrame({"isotope": isotopes, "X": X})
    return df.sort_values("X", ascending=False)

def read_final_abundances(run_arg):
    run_dir = normalize_run_path(run_arg)
    csv = run_dir / "final_abundances.csv"

    if not csv.exists():
        raise FileNotFoundError(csv)

    df = pd.read_csv(csv)
    return df.sort_values("X", ascending=False), run_dir
