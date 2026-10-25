# Comparative Matrix: The Six Malbolge Classic Quines

| Program | Steps | Visited C | Visited D | C ∩ D | C ∪ D | Unvisited | Diag Fraction | Theoretical Diag | Breaks i | Breaks j | Max Seg | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **quine_m281** | 62,239,851 | 25,554 | 26,800 | **96** | 52,258 | 6,791 | **0.578812** | 0.578812 | 21,389,393 | 4,825,305 | 23 | DEMONSTRATED (Structural Heritage from Lutter) |
| **quine_m284** | 62,902,923 | 24,090 | 27,082 | **96** | 51,076 | 7,973 | **0.578804** | 0.578804 | 21,617,925 | 4,876,504 | 23 | DEMONSTRATED (Structural Heritage from Lutter) |
| **quine_m287** | 63,568,038 | 25,469 | 27,364 | **96** | 52,737 | 6,312 | **0.578811** | 0.578811 | 21,846,027 | 4,928,156 | 23 | DEMONSTRATED (Structural Heritage from Lutter) |
| **quine_m293** | 64,897,488 | 25,847 | 27,928 | **96** | 53,679 | 5,370 | **0.578805** | 0.578805 | 22,303,091 | 5,031,424 | 23 | DEMONSTRATED (Structural Heritage from Lutter) |
| **quine_m308** | 68,218,362 | 26,306 | 29,338 | **96** | 55,548 | 3,501 | **0.578805** | 0.578805 | 23,444,531 | 5,288,715 | 23 | DEMONSTRATED (Structural Heritage from Lutter) |
| **quine_lutter** | 69,547,436 | 27,293 | 29,901 | **96** | 57,098 | 1,951 | **0.578812** | 0.578812 | 23,901,063 | 5,391,451 | 21 | DEMONSTRATED (Structural Heritage from Lutter) |

### Key Discoveries & Falsifications:

1. **Exact 96 C ∩ D Intersection:**
   - In all six quines (m281, m284, m287, m293, m308, and Lutter), `|C ∩ D| == 96`.
   - **Why?** Because all `candidate_m*` variants are synthesized directly in `BolgeForge/synthesize.py` by relocating Lutter's quine loop by `Delta = 94 * (314 - m)`.
   - The 96 shared addresses consist of 49 fixed addresses `{0, 99, 117..161, 59047, 59048}` and 47 addresses translated by the exact relocation delta!
   - **Verdict:** This is `INFERRED: STRUCTURAL HERITAGE`, NOT a universal constant of computation.

2. **The 0.578812 Diagonal Fraction:**
   - In all six quines, the diagonal fraction is ~0.578812.
   - The theoretical formula `(steps - 1 - breaks_i - breaks_j) / steps` matches the measured value to **12 decimal places**.
   - In Malbolge Classic, whenever an opcode is not `i` (jump) and not `j` (mov d), both `c` and `d` increment by 1:
     `(c_{t+1} - d_{t+1}) mod 59049 == (c_t - d_t) mod 59049`.
   - In Lutter's quine loop, the non-jump instruction frequency happens to be ~57.88%.
   - **Verdict:** `DESTROYED` as proof of an emergent torus. It is purely the instruction dispatch frequency of non-jump opcodes.
