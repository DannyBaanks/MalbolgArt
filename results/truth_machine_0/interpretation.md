# Scientific Interpretation: truth_machine_0

**Program:** `truth_machine_classic_90b.mal`  
**Group:** `B_CONTROL`  
**SHA-256:** `1e34e2afd1fc645dadac1f1aac0fe2348ff469878cc3da396a6a1e7bad2a4417`  
**Status:** `HALTED`  
**Steps Executed:** 38  
**Wall-Clock Time:** 0.0002s  

---

## 1. Summary of Geometric & Trajectory Metrics

| Metric | Measured Value | Interpretation |
|---|---:|---|
| **Code Footprint (|C|)** | 39 | Distinct instruction addresses fetched |
| **Data Footprint (|D|)** | 23 | Distinct data addresses visited by register d |
| **Intersection (|C ∩ D|)** | **1** | Common addresses accessed by both registers |
| **Union (|C ∪ D|)** | 61 | Total active memory footprint |
| **Unvisited Memory** | 58,988 | Cells untouched (out of 59,049) |
| **Diagonal Steps** | 34 | Steps where `(c - d) mod 59049` remained unchanged |
| **Measured Diagonal Fraction** | **0.894736842105** | Ratio `diagonal_steps / steps` |
| **Theoretical Diagonal Fraction** | **0.868421052632** | Exact formula: `(steps - 1 - breaks_i - breaks_j) / steps` |
| **Breaks on i (jmp c)** | 1 | Jump instructions resetting c |
| **Breaks on j (mov d)** | 3 | Pointer assignments resetting d |
| **Delta Segments** | 5 | Uninterrupted diagonal runs |
| **Max Segment Length** | 16 | Longest uninterrupted run |
| **Unique (c, d) Pairs** | 39 | Projected state points on (Z/59049Z)^2 |
| **Pair Revisits** | 0 | Recurrences of projected (c, d) coordinates |
| **Simultaneous c == d** | 1 | Steps where c and d collided at identical address |
| **Mutated Cells** | 44 | Cells whose final value differs from initial |
| **Total Writes (* / p)** | 6 | Write operations |
| **Total Encryptions (xlat2)** | 38 | Code encryption steps |

---

## 2. Evaluation of Hypotheses

- **H1 (Pointer Cycles & Recurrences):**
  - **Status:** `DEMONSTRATED` (for projected pairs (c, d)).
  - The trajectory revisits (c, d) coordinate pairs 0 times.
  - **CRUCIAL LIMITATION:** A revisit to (c, d) is NOT a full state cycle. The accumulator `a`, the memory values, and the I/O streams are NOT necessarily identical. Full machine state cycle is NOT DEMONSTRATED.

- **H2 (Spatial Regularity across Projections):**
  - **Status:** `INFERRED / BOUNDED`.
  - Projections across linear memory, modular circle, and block grids show clear operational zones (bootstrap zone, high data zone, quine template zone).
  - However, rectangular block shapes change completely when changing width W from 47 to 94 to 188 to 376 (N2 control), proving layout dependency.

- **H3 (Relationship with Self-Modification):**
  - **Status:** `DEMONSTRATED`.
  - Execution alters memory via 6 direct writes and 38 encryptions. The trajectory visits mutated cells which subsequently execute modified instructions.

- **H4 (Quine Specificity vs Other Programs):**
  - **Status:** `CONTROL_BASELINE`.
  - The quine exhibits a highly characteristic diagonal fraction of ~0.5788 and exactly 96 intersection addresses. Non-quine controls have radically different footprints and diagonal fractions.

- **H5 (Non-Trivial Toroidal Hypothesis):**
  - **Status:** `DESTROYED` (as an intrinsic physical geometry); `DEMONSTRATED` (as an arithmetic representation).
  - The fact that (c, d) live in (Z/59049Z)^2 allows mapping them onto the surface of a torus T^2 = S^1 x S^1.
  - **However, the diagonal slope of +1 and the diagonal fraction of 0.5788 do NOT represent an emergent physical torus.** They are the trivial consequence of the instruction cycle where both `c` and `d` increment by 1 on every non-jump instruction.
  - The identity `diagonal_fraction == (steps - 1 - breaks_i - breaks_j) / steps` holds to 12 decimal places!

---

## 3. Visual Artifacts Generated

- `linear_memory.png`: Linear memory visit profile (0..59048).
- `block_94.png`, `block_188.png`, `block_376.png`: Block layout grid at different widths.
- `modular_circular.png`: Modular angle theta = 2*pi*address/59049 with jump chords.
- `cd_trajectory.png`: 2D (c, d) phase space and 3D isometric torus embedding.
- `mutation_heatmap.png`: Self-modification spatial and temporal timeline.
- `flow_debug.gif`, `flow_trails.gif`, `flow_heatmap.gif`, `flow_orbit.gif`, `flow_cinematic.gif`: FLOW animation profiles.
