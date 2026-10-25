# INFORME CIENTÍFICO FINAL: EXPERIMENTO DE GEOMETRÍA TOROIDAL EN MALBOLGE CLASSIC
## BolgeForge × FLOW — Falsificación, Evidencia y Veredicto

**Fecha:** 2026-10-25  
**Proyecto:** ISyCo — Malbolge Trace Geometry  
**Autores / Agentes:** Antigravity (Researcher + Implementer)  
**Estado Final del Experimento:** `EXPERIMENT_EXECUTED`  
**Rama Git:** `experiment/malbolge-flow-torus`  
**Directorio de Resultados:** `/home/danny/Development/ISyCo-worktrees/malbolge-flow-torus/experiments/MALBOLGE_FLOW_TORUS_V0/results`  

---

## 1. Procedencia de Repositorios, Commits y Artefactos

Todos los experimentos fueron ejecutados directamente sobre el árbol de trabajo local en la rama experimental aislada `experiment/malbolge-flow-torus`:

- **BolgeForge:** `/home/danny/Development/ISyCo Git/BolgeForge` (HEAD `e4de81b`)
- **FLOW:** `/home/danny/Development/ISyCo Git/FLOW` (HEAD `1304592`)
- **FlowGen:** `/home/danny/Development/ISyCo Git/FlowGen` (HEAD `afcad9c`)
- **Autobolge:** `/home/danny/Development/ISyCo Git/Autobolge` (HEAD `dcfcd6f`)
- **PureEpoch:** `/home/danny/Development/ISyCo Git/PureEpoch-2026-10-25` (HEAD `20478f8`)
- **ISyCo (Worktree):** `/home/danny/Development/ISyCo-worktrees/malbolge-flow-torus` (Commit base `efc519f8`)

Ningún código original de los repositorios fue sobrescrito. Los artefactos históricos y las evidencias previas permanecen intactos.

---

## 2. Programas Ejecutados y Verificación de Oráculos (Gate G0 & Gate G1)

Se ejecutaron **15 configuraciones de programas** bajo la semántica estricta de Ben Olmstead implementada en C (`trace_extractor` compilado con `gcc -O3` con SHA-256 de flujo de eventos y de salida):

### Grupo A — Quines Certificadas (Reproducción 100% Bit a Bit)
| Programa | Bytes Fuente | SHA-256 Fuente | Pasos | Salida Obtenida | Reproducción Exacta |
|---|---:|---|---:|---:|:---:|
| `candidate_m281_53562b.mal` | 53,562 | `96b670b825372a0f41fa3b574d47457f92654b76411e5d5be4c438003087610e` | 62,239,851 | 53,562 B | **PASS (Byte-Exact)** |
| `candidate_m284_54134b.mal` | 54,134 | `1808fd4d862a274abc6b9f7b8965d1eee65fc11aa2424c23a8077040876b483c` | 62,902,924 | 54,134 B | **PASS (Byte-Exact)** |
| `candidate_m287_54706b.mal` | 54,706 | `3da997b9e559230d43acf828188269d441afc03d773e71a83f49ae7e9d663efb` | 63,565,997 | 54,706 B | **PASS (Byte-Exact)** |
| `candidate_m293_55850b.mal` | 55,850 | `1719515d85fa2d5dfc0c36cdcc935eefd363fca0a435b2588ef36a1509b1b2ea` | 64,892,143 | 55,850 B | **PASS (Byte-Exact)** |
| `candidate_m308_58709b.mal` | 58,709 | `67628cf1cd8befe907c39aac6476d31927499f0421013c34195891f2ec4ca071` | 68,207,508 | 58,709 B | **PASS (Byte-Exact)** |
| `quine_lutter.malbolge` | 59,852 | `dca8476f8b70c8462c32f661f63c5f8b1ad6c33946b3c7a9a35186c824117d98` | 69,547,437 | 59,852 B | **PASS (Byte-Exact)** |

### Grupo B — Programas de Control
- `truth_machine_classic_90b.mal` con stdin `'0'`: 8 pasos, salida `'0'`, HALT limpio.
- `truth_machine_classic_90b.mal` con stdin `'1'`: 50,000 pasos (presupuesto), flujo continuo de `'1'`, MAX_STEPS.
- `cat_compact.mal` con stdin `'FLOW_TORUS
'`: 10,896 pasos, salida `'FLOW_TORUS
'`, HALT limpio.
- `digital_root_compressed.mal` con stdin `'12345
'`: 18,241 pasos, salida `'6
'`, HALT limpio.
- `adder_compressed.mal` con stdin `'12 34
'`: 24,198 pasos, salida `'46
'`, HALT limpio.

### Grupo C — PureEpoch
- `m1e_normal.mal` con stdin ``: 1,438 pasos, salida `'V'`, HALT limpio.
- `m1e_no_restore.mal` con stdin ``: 1,438 pasos, salida `'V'`, HALT limpio.
- `m1e_force_retry_failure.mal` con stdin ``: 1,438 pasos, salida `'V'`, HALT limpio.
- `m2_normal.mal` con stdin ``: 2,876 pasos, salida `'VV'`, HALT limpio.

---

## 3. Matriz Numérica Comparativa de las Seis Quines

| Métrica | m281 | m284 | m287 | m293 | m308 | Lutter |
|---|---:|---:|---:|---:|---:|---:|
| **Pasos Totales** | 62,239,851 | 62,902,924 | 63,565,997 | 64,892,143 | 68,207,508 | 69,547,437 |
| **Celdas C (Fetch)** | 25,554 | 24,090 | 25,188 | 25,584 | 26,762 | 27,293 |
| **Celdas D (Datos)** | 26,800 | 27,082 | 27,364 | 27,928 | 29,338 | 29,901 |
| **C ∩ D (Intersección)** | **96** | **96** | **96** | **96** | **96** | **96** |
| **C ∪ D (Unión)** | 52,258 | 51,076 | 52,456 | 53,416 | 55,004 | 57,098 |
| **Memoria No Visitada** | 6,791 | 7,973 | 6,593 | 5,633 | 4,045 | 1,951 |
| **Pasos Diagonales** | 36,025,153 | 36,408,493 | 36,791,835 | 37,558,517 | 39,475,223 | 40,254,921 |
| **Fracción Diagonal Medida** | **0.57881168** | **0.57880447** | **0.57879743** | **0.57878342** | **0.57875249** | **0.57881244** |
| **Fracción Teórica `(steps-1-bi-bj)/steps`** | **0.57881167** | **0.57880448** | **0.57879743** | **0.57878342** | **0.57875249** | **0.57881244** |
| **Bifurcaciones `i` (Saltos)** | 21,389,393 | 21,617,925 | 21,846,457 | 22,303,521 | 23,446,181 | 23,901,063 |
| **Bifurcaciones `j` (Mov D)** | 4,825,305 | 4,876,504 | 4,927,703 | 5,030,101 | 5,286,096 | 5,391,451 |
| **Segmentos Diagonales** | 26,214,699 | 26,494,430 | 26,774,161 | 27,333,623 | 28,732,278 | 29,292,515 |
| **Longitud Máx Segmento** | 23 | 24 | 24 | 22 | 23 | 22 |
| **Pares (c,d) Únicos** | 132,515 | 132,179 | 134,882 | 139,120 | 144,302 | 146,662 |
| **Revisitas de Pares (c,d)** | 62,107,337 | 62,770,745 | 63,431,115 | 64,753,023 | 68,063,206 | 69,400,775 |
| **Colisiones Simultáneas c==d** | 1 | 1 | 1 | 1 | 1 | 1 |
| **Período Cíclico Mínimo C** | 59,049 | 59,049 | 59,049 | 59,049 | 59,049 | 59,049 |

---

## 4. Falsación y Demostración de las Preguntas Clave

### A. La Coincidencia de 96 Direcciones en C ∩ D
**¿Es 96 una constante universal de las quines o de la geometría de Malbolge?**  
**VEREDICTO: `DESTROYED` (como propiedad universal); `DEMONSTRATED` (como herencia constructiva).**  
- `BolgeForge/synthesize.py` deriva las 5 quines m281..m308 reubicando la quine histórica de Lutter mediante `Delta = 94 * (314 - m)`.
- El conjunto de 96 direcciones de C ∩ D se descompone exactamente en:
  - **49 direcciones fijas:** `{0, 99, 117..161, 59047, 59048}`.
  - **47 direcciones móviles:** que se trasladan exactamente en `Delta` entre m281, m284 y Lutter.
- La coincidencia de 96 no es un atractor toroidal ni un principio físico: es la huella digital del código fuente de Lou Scheffer / Ben Olmstead / Malcolm Kesson / Anthony de Lutter reproducida por el sintetizador.

### B. La Fracción Diagonal ~0.578812
**¿Indica una órbita toroidal o una simetría continua en el espacio (c,d)?**  
**VEREDICTO: `DESTROYED` (como evidencia de toro no trivial); `DEMONSTRATED` (como identidad algebraica de instrucciones).**  
- En Malbolge Classic:
  `c_(t+1) = (c_t + 1) mod 59049` (salvo que la instrucción sea `i`, jump)
  `d_(t+1) = (d_t + 1) mod 59049` (salvo que la instrucción sea `j`, mov d)
- Por tanto, para cualquier instrucción ordinaria (`*`, `p`, `<`, `/`, `o`):
  `c_(t+1) - d_(t+1) = (c_t + 1) - (d_t + 1) = c_t - d_t mod 59049`.
  El vector de avance en el plano `(c, d)` es `(1, 1)`, una recta puramente diagonal de pendiente 45°.
- En el bucle de Lutter, exactamente:
  `Breaks_i = 21,389,393`
  `Breaks_j = 4,825,305`
  `Pasos no-jump = Pasos - 1 - Breaks_i - Breaks_j = 36,025,153`
  `36,025,153 / 62,239,851 = 0.578811684495`
- La fracción diagonal es la **proporción de instrucciones que no son saltos** en el generador de la quine. No tiene relación con una geometría toroidal intrínseca.

### C. Par proyectado (c,d) vs Ciclo de Estado Completo (H1 vs H5)
- Los pares `(c, d)` se revisitan más de 62 millones de veces en m281.
- **Sin embargo, el control negativo N7 demuestra categóricamente:**
  - Cuando el par `(c, d)` se repite, la memoria ha sido automodificada por `*`, `p` y cifrada por `xlat2`.
  - El acumulador `a` y los contenidos de las celdas difieren radicalmente.
  - **No existe ningún ciclo de estado físico completo en la VM.**
  - `H5 (Topología Toroidal de Estado Completo): DESTROYED`.
  - `H1 (Recurrencia de Punteros Proyectados): DEMONSTRATED`.

---

## 5. Resultados de los Controles Negativos Obligatorios (N1–N7)

| Control | Nombre | Resultado | Conclusión Científica |
|---|---|:---:|---|
| **N1** | Renderer Circular | **DEMONSTRATED** | El perfil `orbit` de FLOW dibuja círculos concéntricos y organiza entidades en anillos incluso sobre un paseo aleatorio sin periodicidad. Las figuras circulares de `orbit` son un artefacto de presentación visual del renderer. |
| **N2** | Cambio de Dimensiones | **DEMONSTRATED** | Al proyectar la memoria en cuadrículas W = 47, 94, 188 y 376, los bloques visuales cambian drásticamente de aspecto. La periodicidad aparente en W=94 se debe al ciclo de 94 caracteres del loader/cifrador, no a una topología toroidal 2D. |
| **N3** | Permutación Temporal | **DEMONSTRATED** | Al permutar temporalmente los eventos manteniendo el histograma espacial, la fracción diagonal consecutiva colapsa a casi 0. Esto demuestra que la fracción diagonal es una propiedad dinámica del orden de ejecución, no un artefacto de densidad estática. |
| **N4** | Secuencia Sintética | **DEMONSTRATED** | Al alimentar una órbita modular sintética con período P=729, el algoritmo detecta con 100% de exactitud P=729 sin inventar propiedades adicionales. |
| **N5** | Comparación de Familias | **DEMONSTRATED** | Quines vs Cat vs Truth Machine vs Adder presentan perfiles totalmente divergentes. Cat tiene fracción diagonal de 0.957 (copia lineal) y solo 15 intersecciones C∩D. No existe una geometría universal compartida. |
| **N6** | Mutación y Divergencia | **DEMONSTRATED** | Al mutar un solo byte en un programa loader-valid, el extractor localiza con exactitud quirúrgica el paso exacto donde la traza diverge del original. |
| **N7** | Falsa Vuelta | **DEMONSTRATED** | Regresar a una dirección `c` o par `(c, d)` NO restaura el estado completo de la máquina `(a, c, d, memoria)`. Se rechaza cualquier afirmación de ciclo completo. |

---

## 6. Veredicto Final sobre las Hipótesis

- **H0 (Hipótesis Nula):** `DEMONSTRATED`.  
  Las apariencias circulares y toroidales proceden de la aritmética modular `mod 59049`, el renderer `orbit`, la herencia del código de Lutter y la periodicidad del cifrador ASCII de 94 elementos.
- **H1 (Ciclos de punteros proyectados):** `DEMONSTRATED`.  
  Existen recurrencias de coordenadas en `(Z/59049Z)^2`.
- **H2 (Regularidades espaciales invariantes):** `DESTROYED / BOUNDED`.  
  Las formas geométricas cambian al variar el ancho W de proyección.
- **H3 (Relación con automodificación):** `DEMONSTRATED`.  
  Las celdas de memoria mutan durante la ejecución y son posteriormente ejecutadas como código transformado.
- **H4 (Especificidad de las quines):** `DEMONSTRATED`.  
  La familia de Lutter posee la huella C∩D=96 y DiagFrac~0.5788, ausente en Cat, Adder y Truth Machine.
- **H5 (Topología toroidal no trivial del estado):** `DESTROYED`.  
  No hay una variedad toroidal física ni un ciclo de estado completo. La trayectoria es un espagueti determinista automodificable en un espacio discreto con avance modular.

---

## 7. Catálogo de Artefactos Producidos

Todos los artefactos requeridos han sido generados y se encuentran en sus rutas canónicas:

- **Panel Comparativo de las 6 Quines:**
  `results/comparison_quines.png`
- **Animación de Divergencia (m281 vs m284):**
  `results/divergence_animation_m281_vs_m284.gif`
- **Matrices Comparativas:**
  `results/comparison_quines.md`
  `results/comparison_quines_vs_controls.md`
- **Controles Negativos (N1–N7):**
  `results/negative_controls/n1_orbit_artificial_circle.gif`
  `results/negative_controls/n2_block_w*.png`
  `results/negative_controls/negative_controls_summary.json`
- **Por cada uno de los 15 programas investigados (`results/<program_id>/`):**
  - `provenance.json`
  - `oracle_verdict.json`
  - `trace_index.json`
  - `geometry_metrics.json`
  - `linear_memory.csv`
  - `trace_sample.json`
  - `stdout.bin`
  - `linear_memory.png`
  - `block_94.png`, `block_188.png`, `block_376.png`
  - `modular_circular.png`
  - `cd_trajectory.png`
  - `mutation_heatmap.png`
  - `flow_debug.gif`, `flow_trails.gif`, `flow_heatmap.gif`, `flow_orbit.gif`, `flow_cinematic.gif`
  - `interpretation.md`
