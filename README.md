## Nova Nucleosynthesis Sensitivity Analysis
# NuGrid PPN Post-Processing Framework

## 1. Physics Overview
# 1.1 Classical Novae

A classical nova is a thermonuclear explosion occurring on the surface of a white dwarf in a close binary system.

Binary System Components

White Dwarf (WD):

Composed of either:

CO (carbon–oxygen)

ONe (oxygen–neon–magnesium)

Supported by electron degeneracy pressure

Has:

Degenerate core

Thin hydrogen-rich accreted envelope

Electron degeneracy implies:

𝑃
≈
𝑃
(
𝜌
)
P≈P(ρ)

and is largely independent of temperature.

This allows:

Temperature to increase without pressure regulation.

Companion Star

Usually:

Main sequence

Hydrogen-rich

Mass transfer occurs via:

Roche lobe overflow

Accretion disk formation

Deposition of material onto WD surface

1.2 Thermonuclear Runaway (TNR)

As hydrogen accumulates:

Compression increases temperature.

CNO burning begins.

Reaction rates increase rapidly:

⟨
𝜎
𝑣
⟩
∝
exp
⁡
(
−
𝑇
−
1
/
3
)
⟨σv⟩∝exp(−T
−1/3
)

Energy generation accelerates.

Degeneracy prevents expansion.

Thermal runaway occurs.

Peak temperatures:

𝑇
peak
∼
0.1
−
0.4
 GK
T
peak
	​

∼0.1−0.4 GK

Dominant burning regimes:

Hot CNO cycle

Leakage into NeNa and MgAl cycles

In hotter cases: flow toward Si–S–Ar region

2. NuGrid PPN Framework

NuGrid PPN is a post-processing nuclear reaction network.

It solves:

𝑑
𝑌
𝑖
𝑑
𝑡
=
∑
𝑗
𝑁
𝑖
𝑗
𝐹
𝑗
dt
dY
i
	​

	​

=
j
∑
	​

N
ij
	​

F
j
	​


where:

𝑌
𝑖
=
𝑋
𝑖
/
𝐴
𝑖
Y
i
	​

=X
i
	​

/A
i
	​

 (abundance per baryon)

𝑁
𝑖
𝑗
N
ij
	​

 = stoichiometric matrix

𝐹
𝑗
F
j
	​

 = reaction flux

For a two-body reaction:

𝐹
𝑗
=
𝜌
𝑁
𝐴
⟨
𝜎
𝑣
⟩
𝑌
𝑎
𝑌
𝑏
F
j
	​

=ρN
A
	​

⟨σv⟩Y
a
	​

Y
b
	​


PPN:

Uses prescribed temperature-density trajectory 
𝑇
(
𝑡
)
,
𝜌
(
𝑡
)
T(t),ρ(t)

Evolves isotope abundances

Does NOT solve hydrodynamics

It is strictly nuclear post-processing.

3. Project Structure
ppn_nova/
│
├── initial_abundance.dat
├── trajectory.input
├── ppn.exe
├── runs/
│   ├── baseline/
│   ├── reaction_fact_X/
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
4. Tools Directory
extract_final_iso.f90

Extracts final abundance summary from PPN output into:

final_abundances.csv
batch_iso.f90

Extracts isotope time evolution data across time snapshots.

new_run.sh

Automates:

Reaction rate multiplication

Directory creation

Execution of PPN

Organizing output

These tools are required before running analysis scripts.

5. Analysis Scripts Overview
5.1 plot_initial_abundances.py
Input

initial_abundance.dat

Output

Log-scale horizontal abundance plot

Purpose

Visualizes initial fuel composition:

𝑋
𝑖
initial
X
i
initial
	​


Physically shows:

WD mixing signature

Initial CNO catalyst abundance

Metallic content

5.2 plot_final.py
Input

runs/<run_name>/final_abundances.csv

Output

Final abundance plot

Purpose

Displays:

𝑋
𝑖
final
X
i
final
	​


Represents nucleosynthesis result after TNR.

Shows:

Synthesized isotopes

Destroyed isotopes

Heavy-element production

5.3 plot_ratio.py
Input

Initial abundances

Final abundances

Output

Ratio plot:

𝑋
𝑓
𝑋
𝑖
X
i
	​

X
f
	​

	​

Purpose

Removes initial composition bias.

Identifies:

Synthesized isotopes 
𝑋
𝑓
/
𝑋
𝑖
>
1
X
f
	​

/X
i
	​

>1

Destroyed isotopes 
𝑋
𝑓
/
𝑋
𝑖
<
1
X
f
	​

/X
i
	​

<1

5.4 plot_top_ratios.py
Input

Run directory

Top N value

Output

Top isotopes ranked by:

∣
log
⁡
10
(
𝑋
𝑓
𝑋
𝑖
)
∣
	​

log
10
	​

(
X
i
	​

X
f
	​

	​

)
	​

Purpose

Identifies isotopes most sensitive to nuclear processing.

Useful for:

Observational diagnostics

Targeted sensitivity studies

5.5 compare_runs_isotope.py
Input

Isotope name

Multiple runs

Output

Abundance vs rate factor curve

Physics

Plots:

𝑋
𝑖
(
𝑓
)
X
i
	​

(f)

where 
𝑓
f is rate multiplication factor.

Slope gives:

𝛼
=
𝑑
log
⁡
𝑋
𝑖
𝑑
log
⁡
𝑟
α=
dlogr
dlogX
i
	​

	​


Sensitivity coefficient.

5.6 compare_A_less_than_40.py
Input

Multiple runs

Isotopes with 
𝐴
<
40
A<40

Output

Multi-isotope normalized comparison

Purpose

Shows collective response of light nuclei.

Distinguishes:

CO vs ONe nova signatures

Global structural shifts

5.7 plot_flux_snapshot.py
Input

flux_XXXX.DAT

Output

Dominant reaction fluxes at given timestep

Physics

Flux:

𝐹
𝑗
=
𝜌
𝑁
𝐴
⟨
𝜎
𝑣
⟩
𝑌
𝑎
𝑌
𝑏
F
j
	​

=ρN
A
	​

⟨σv⟩Y
a
	​

Y
b
	​


Represents instantaneous reaction flow.

Identifies:

Burning regime

Dominant reaction channels

Active nuclear pathways

5.8 integrate_flux_over_run.py
Input

All flux files in run

Output

Ranked reactions by:

∫
𝐹
𝑗
𝑑
𝑡
∫F
j
	​

dt
Purpose

Measures total material processed through each reaction.

Identifies:

Structurally important reactions

Dominant nucleosynthesis pathways

5.9 flux_isotope_io.py

Utility for:

Parsing flux files

Mapping reactions

Aggregating flows by isotope

Foundation for:

Reaction importance ranking

Integrated flow comparison

6. Sensitivity Study Workflow

Identify dominant reactions via integrated flux.

Multiply rate by factors:

0.01, 0.1, 2, 10, 100

Run PPN.

Compare abundances to baseline.

Extract sensitivity slopes.

Construct uncertainty tables.

Inspired by:

Iliadis et al.

Longland Monte Carlo rate analysis

7. Future Extensions

Monte Carlo rate sampling

Lognormal uncertainty propagation

Error band visualization

Reaction family grouping

Network flow visualization

8. Core Mathematical Summary

Network equation:

𝑑
𝑌
𝑖
𝑑
𝑡
=
∑
𝑗
𝑁
𝑖
𝑗
𝐹
𝑗
dt
dY
i
	​

	​

=
j
∑
	​

N
ij
	​

F
j
	​


Flux term:

𝐹
𝑗
=
𝜌
𝑁
𝐴
⟨
𝜎
𝑣
⟩
𝑌
𝑎
𝑌
𝑏
F
j
	​

=ρN
A
	​

⟨σv⟩Y
a
	​

Y
b
	​


Rate coefficient:

𝑁
𝐴
⟨
𝜎
𝑣
⟩
=
exp
⁡
(
𝑎
0
+
𝑎
1
𝑇
−
1
+
𝑎
2
𝑇
−
1
/
3
+
…
 
)
N
A
	​

⟨σv⟩=exp(a
0
	​

+a
1
	​

T
−1
+a
2
	​

T
−1/3
+…)

Sensitivity slope:

𝛼
=
𝑑
log
⁡
𝑋
𝑑
log
⁡
𝑟
α=
dlogr
dlogX
	​

9. Scientific Goal

This framework enables:

Reproduction of classical nova sensitivity studies

Extension using modern reaction rates

Statistical uncertainty quantification

Direct comparison to observational nova abundances

Foundation for PhD-level publication work
