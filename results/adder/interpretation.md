# Scientific Interpretation: adder

**Program:** `adder_compressed.mal`  
**Group:** `B_CONTROL`  
**SHA-256:** `5177cb74d0bfcdc1120f13f56bfaa08ac6f062123c3e3b1317523f492946c64b`  
**Status:** `HALTED`  
**Steps Executed:** 222,887  
**Wall-Clock Time:** 0.1155s  

---

## 1. Summary of Geometric & Trajectory Metrics

| Metric | Measured Value | Interpretation |
|---|---:|---|
| **Code Footprint (|C|)** | 43,981 | Distinct instruction addresses fetched |
| **Data Footprint (|D|)** | 913 | Distinct data addresses visited by register d |
| **Intersection (|C ∩ D|)** | **89** | Common addresses accessed by both registers |
| **Union (|C ∪ D|)** | 44,805 | Total active memory footprint |
| **Unvisited Memory** | 14,244 | Cells untouched (out of 59,049) |
| **Diagonal Steps** | 77,075 | Steps where `(c - d) mod 59049` remained unchanged |
| **Measured Diagonal Fraction** | **0.345803030235** | Ratio `diagonal_steps / steps` |
| **Theoretical Diagonal Fraction** | **0.345798543657** | Exact formula: `(steps - 1 - breaks_i - breaks_j) / steps` |
| **Breaks on i (jmp c)** | 112,410 | Jump instructions resetting c |
| **Breaks on j (mov d)** | 33,402 | Pointer assignments resetting d |
| **Delta Segments** | 145,813 | Uninterrupted diagonal runs |
| **Max Segment Length** | 47 | Longest uninterrupted run |
| **Unique (c, d) Pairs** | 44,548 | Projected state points on (Z/59049Z)^2 |
| **Pair Revisits** | 178,340 | Recurrences of projected (c, d) coordinates |
| **Simultaneous c == d** | 1 | Steps where c and d collided at identical address |
| **Mutated Cells** | 44,730 | Cells whose final value differs from initial |
| **Total Writes (* / p)** | 19,768 | Write operations |
| **Total Encryptions (xlat2)** | 222,887 | Code encryption steps |

---

## 2. Evaluation of Hypotheses

- **H1 (Pointer Cycles & Recurrences):**
  - **Status:** `DEMONSTRATED` (for projected pairs (c, d)).
  - The trajectory revisits (c, d) coordinate pairs 178,340 times.
  - **CRUCIAL LIMITATION:** A revisit to (c, d) is NOT a full state cycle. The accumulator `a`, the memory values, and the I/O streams are NOT necessarily identical. Full machine state cycle is NOT DEMONSTRATED.

- **H2 (Spatial Regularity across Projections):**
  - **Status:** `INFERRED / BOUNDED`.
  - Projections across linear memory, modular circle, and block grids show clear operational zones (bootstrap zone, high data zone, quine template zone).
  - However, rectangular block shapes change completely when changing width W from 47 to 94 to 188 to 376 (N2 control), proving layout dependency.

- **H3 (Relationship with Self-Modification):**
  - **Status:** `DEMONSTRATED`.
  - Execution alters memory via 19,768 direct writes and 222,887 encryptions. The trajectory visits mutated cells which subsequently execute modified instructions.

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
