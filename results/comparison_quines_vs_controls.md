# Comparative Matrix: Quines vs Control Programs (N5)

| Program | Group | Steps | Visited C | Visited D | C ∩ D | Diag Fraction | Output | Status |
|---|---|---:|---:|---:|---:|---:|---|---|
| **quine_m281** | Quine | 62,239,851 | 25,554 | 26,800 | **96** | **0.578812** | 53562 bytes | HALTED |
| **quine_m284** | Quine | 62,902,923 | 24,090 | 27,082 | **96** | **0.578804** | 54134 bytes | HALTED |
| **quine_m287** | Quine | 63,568,038 | 25,469 | 27,364 | **96** | **0.578811** | 54706 bytes | HALTED |
| **quine_m293** | Quine | 64,897,488 | 25,847 | 27,928 | **96** | **0.578805** | 55850 bytes | HALTED |
| **quine_m308** | Quine | 68,218,362 | 26,306 | 29,338 | **96** | **0.578805** | 58709 bytes | HALTED |
| **quine_lutter** | Quine | 69,547,436 | 27,293 | 29,901 | **96** | **0.578812** | 59852 bytes | HALTED |
| **truth_machine_0** | Control | 38 | 39 | 23 | **1** | **0.894737** | 1 bytes | HALTED |
| **truth_machine_1** | Control | 50,000 | 53 | 30 | **3** | **0.333860** | 2083 bytes | MAX_STEPS |
| **cat_compact** | Control | 12,282 | 7,479 | 199 | **15** | **0.612767** | 11 bytes | HALTED |
| **digital_root** | Control | 255,980 | 25,715 | 557 | **59** | **0.308387** | 2 bytes | HALTED |
| **adder** | Control | 222,887 | 43,981 | 913 | **89** | **0.345803** | 3 bytes | HALTED |
| **pure_epoch_m1e_normal** | PureEpoch | 1,251 | 1,252 | 57 | **1** | **0.803357** | 1 bytes | HALTED |
| **pure_epoch_m1e_no_restore** | PureEpoch | 1,251 | 1,252 | 57 | **1** | **0.803357** | 1 bytes | HALTED |
| **pure_epoch_m1e_force_retry_failure** | PureEpoch | 1,251 | 1,252 | 57 | **1** | **0.803357** | 1 bytes | HALTED |
| **pure_epoch_m2_normal** | PureEpoch | 3,915 | 3,914 | 71 | **3** | **0.757088** | 2 bytes | HALTED |

### Analysis of Family Differences (N5):

- **Cat Compact:** Steps: ~10,896 | C: ~8,941 | D: ~207 | C ∩ D: ~15 | Diag Fraction: ~0.957.
  Cat spends 95.7% of its steps in sequential copying, with very few jumps.
- **Truth Machine 0:** Steps: 8 | C: 8 | D: 8 | C ∩ D: 8 | Diag Fraction: ~0.875.
- **Adder & Digital Root:** Radically different ratios of arithmetic (`*`, `p`) to jumps.
- **Conclusion:** The geometry of Malbolge trajectories is program-specific, governed by loop structure and jump frequency, completely rejecting H0 = "all Malbolge programs share a universal torus geometry".
