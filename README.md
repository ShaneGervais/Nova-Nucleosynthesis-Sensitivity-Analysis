# Nova Nucleosynthesis Sensitivity Analysis
## NuGrid PPN Post-Processing Framework

# 1. Physics Overview
## 1.1 Classical Novae

A classical nova is a thermonuclear explosion occurring on the surface of a white dwarf in a close binary system.

### Binary System Components

**White Dwarf (WD):**

Composed of either:

- CO (carbon–oxygen)

- ONe (oxygen–neon–magnesium)

Has:

- Degenerate core

- Thin hydrogen-rich accreted envelope

The electron degenerate nature of the WD implies that $P\\approxP(\rho)$ and is largely independent of temperature; allowing temperature to increase without pressure regulation.

**Companion Star**

Usually: a main sequence and hydrogen-rich star

Mass transfer occurs via *Roche lobe overflow* forming an accretion disk and depositing stellar material onto the WD surface.

## 1.2 Thermonuclear Runaway (TNR)

As hydrogen accumulates:

- Compression increases temperature.

- CNO burning begins (as a catalyst).

- Reaction rates increase rapidly

$$<\sigma v> \\prop exp(-T^{-1/3})$$

- Energy generation accelerates.

- Degeneracy prevents expansion.

-> Thermal runaway occurs.

Peak temperatures are around $T~0.1-0.4$ $GK$

**Dominant burning regimes:**

- Hot CNO cycle

- Leakage into NeNa and MgAl cycles

- In hotter cases: flow toward Si–S–Ar region

# 2. NuGrid PPN Framework

NuGrid PPN is a post-processing nuclear reaction network.

It solves:

$$\dot{Y_i} = \sum_j N_{ij}F_j
	​


where:

- $Y_i=X_i/A_i$ (abundance = mass_fraction/mass_number per baryon $i$)
- $N_{ij}$ stoichiometric matrix for baryon $i$ and reaction $j$
- $F_j$ reaction flux

e.g. For a two-body reaction (a+b):

$$F_j = \rho N_A <\sigma v>Y_a Y_b$$

with the rate coefficient usually in the form of:

$$N_A <\sigma v> = exp(a_0 + a_1 T^{-1} + a_2 T^{-1/3} + \dots)$$

depending on experimentally found values for each coefficient $a_k$

**PPN:**

- Uses prescribed temperature-density trajectory $T(t)$, $\rho(t)$

- Evolves isotope abundances

- Does NOT solve hydrodynamics

It is strictly nuclear post-processing.

# 3. Personal working structure
```
{
	ppn_nova/
	│
	├── initial_abundance.dat
	├── trajectory.input
	├── ppn.exe
	├── runs/
	│	├── baseline/
	│	├── reaction_fact_X/
	│
	├── tools/
	│   ├── extract_final_iso.f90
	│   ├── batch_iso.f90
	│   ├── new_run.sh
	│
	└── analysis/
    	├── abundance_io.py
    	├── flux_isotope_io.py
    	├── plot_initial_abundances.py
    	├── plot_final.py
    	├── plot_ratio.py
    	├── plot_top_ratios.py
    	├── compare_runs_isotope.py
    	├── compare_A_less_than_40.py
    	├── plot_flux_snapshot.py
    	├── integrate_flux_over_run.py
}
```
# 4. Tools Directory

`extract_final_iso.f90`

Extracts final abundance summary from PPN output into:

`final_abundances.csv`
`batch_iso.f90`

Extracts isotope time evolution data across time snapshots.

`new_run.sh`

Automates:

- Reaction rate multiplication

- Directory creation

- Execution of PPN

- Organizing output

These tools are required before running analysis scripts.

# 5. Analysis Scripts Overview

## 5.1 `plot_initial_abundances.py`

Input

`initial_abundance.dat`

Output

Log-scale horizontal abundance plot

Visualizes initial fuel composition:

$$X_{i}^{initial}$$

Physically shows:

- WD mixing signature

- Initial CNO catalyst abundance

- Metallic content

## 5.2 `plot_final.py`
Input

`runs/<run_name>/final_abundances.csv`

Output

Final abundance plot

Displays:

$$X_{i}^{final}$$
	​


Represents nucleosynthesis result after **TNR**.

Shows:

- Synthesized isotopes

- Destroyed isotopes

- Heavy-element production

## 5.3 `plot_ratio.py`
Input

Initial abundances

Final abundances

Output

Ratio plot:

$$\frac{X_f}{X_i}$$


Purpose: Removes initial composition bias.

Identifies:

- Synthesized isotopes $X_f/X_i > 1$
- Destroyed isotopes $X_f/X_i < 1$

## 5.4 `plot_top_ratios.py`
Input

- Run directory
- Top N value

Output

Top isotopes ranked by:

$$|log(\frac{X_f}{X_i})|$$
​

Purpose: Identifies isotopes most sensitive to nuclear processing.

Useful for:

- Observational diagnostics

- Targeted sensitivity studies

## 5.5 `compare_runs_isotope.py`
Input

- Isotope name

- Multiple runs

Output

Abundance vs rate factor curve

Slope gives sensitivity coefficient $\alpha$

## 5.6 `compare_A_less_than_40.py`
Input

- Multiple runs

- Isotopes with $A<40$ by default but can be changed

Output

Multi-isotope normalized comparison

Purpose: Shows collective response of light nuclei.

Distinguishes:

- CO vs ONe nova signatures

- Global structural shifts

## 5.7 `plot_flux_snapshot.py`
Input

`flux_XXXX.DAT`

Output

- Dominant reaction fluxes at given timestep

- Represents instantaneous reaction flow.

Identifies:

- Burning regime

- Dominant reaction channels

- Active nuclear pathways

in current snapshot

## 5.8 `integrate_flux_over_run.py`
Input

All flux files in run

Output

Ranked reactions by:

$$\phi = \int F_j dt$$

Purpose: Measures total material processed through each reaction.

Identifies:

- Structurally important reactions

- Dominant nucleosynthesis pathways

## 5.9 `flux_isotope_io.py`

Utility for:

- Parsing flux files

- Mapping reactions

- Aggregating flows by isotope

Foundation for:

- Reaction importance ranking

- Integrated flow comparison

# 6. Sensitivity Study Workflow

1. Identify dominant reactions via integrated flux.

2. Multiply rate by factors: $0.01$, $0.1$, $2$, $10$, $100$

3. Run PPN.

4. Compare abundances to baseline.

5. Extract sensitivity slopes.

6. Construct uncertainty tables.

Inspired by: Iliadis et al. (2002) & Longland Monte Carlo rate analysis (2010)

# 7. Future Extensions

- Monte Carlo rate sampling

- Lognormal uncertainty propagation

- Error band visualization

- Reaction family grouping

- Network flow visualization


# 8. Scientific Goal

This framework enables:

- Reproduction of classical nova sensitivity studies

- Extension using modern reaction rates

- Statistical uncertainty quantification

- Direct comparison to observational nova abundances

- Foundation for PhD-level publication work
