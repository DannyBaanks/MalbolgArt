# 🌌 MalbolgArt
### Toroidal Execution Geometry & Visual Art of Malbolge Classic (BolgeForge × FLOW)

[![Malbolge Classic](https://img.shields.io/badge/Malbolge-Classic%203%5E10%20(59%2C049%20cells)-purple.svg)](#)
[![FLOW Engine](https://img.shields.io/badge/FLOW-Render%20Profiles%20v0.1.0-blue.svg)](#)
[![Quines Verified](https://img.shields.io/badge/Quines%20Bit--Exact-6%2F6%20PASS-green.svg)](#)
[![Hypothesis H5](https://img.shields.io/badge/Toroidal%20Hypothesis-DESTROYED%20(Algebraic%20Proof)-red.svg)](#)

> **"FLOW hace visible la evidencia; no la fabrica."**  
> Estudio experimental, visual y matemático riguroso sobre las trayectorias de ejecución, periodicidad, automodificación y supuesta estructura toroidal de programas Malbolge Classic.

---

## 🖼️ Galería Principal

### El Espacio de Fases de las Seis Quines
Comparación simultánea del plano proyectado $(c, d) \in (\mathbb{Z}/59,049\mathbb{Z})^2$ entre **m281, m284, m287, m293, m308** y la referencia de **Lutter**:

![Comparativa de las 6 Quines](assets/comparison_quines.png)

---

## ⚡ Animaciones Generadas con FLOW

| FLOW Cinematic (m281) | FLOW Orbit (m281) |
|:---:|:---:|
| ![FLOW Cinematic](assets/m281_flow_cinematic.gif) | ![FLOW Orbit](assets/m281_flow_orbit.gif) |
| **Trayectoria Dinámica Suavizada** | **Mapeo Angular Circular** |

| FLOW Trails (m281) | Divergencia Cinematográfica (m281 vs m284) |
|:---:|:---:|
| ![FLOW Trails](assets/m281_flow_trails.gif) | ![Divergence](assets/divergence_animation_m281_vs_m284.gif) |
| **Estelas de Desplazamiento y Saltos** | **Separación Temporal de Punteros C** |

---

## 🔬 Veredicto Científico sobre las Hipótesis

¿Las trayectorias de ejecución de programas Malbolge Classic presentan estructuras recurrentes compatibles con una topología toroidal no trivial?

### **VEREDICTO: `DESTROYED` (como geometría física); `DEMONSTRATED` (como identidad modular)**

| Hipótesis | Declaración | Veredicto | Hallazgo Clave |
|---|---|:---:|---|
| **H0** | La figura toroidal/circular proviene del renderer y la aritmética modular | **`DEMONSTRATED`** | Confirmado por el control N1: `orbit` genera anillos y círculos incluso sobre paseos aleatorios sin periodicidad. |
| **H1** | Existen ciclos en las trayectorias proyectadas de punteros | **`DEMONSTRATED`** | Los pares proyectados $(c, d)$ se revisitan >62 millones de veces durante la ejecución. |
| **H2** | Las regularidades espaciales sobreviven a distintas proyecciones | **`BOUNDED`** | Los bloques visuales cambian por completo al variar el ancho $W \in \{47, 94, 188, 376\}$ (control N2). |
| **H3** | Los patrones de ejecución se relacionan con fases de automodificación | **`DEMONSTRATED`** | Se correlacionaron 1.46M escrituras directas (`*`, `p`) y 62.2M cifrados (`xlat2`), observando las celdas mutadas antes y después. |
| **H4** | Las quines presentan regularidades distintas de otros programas | **`DEMONSTRATED`** | Las quines comparten $C \cap D = 96$ y fracción diagonal $\approx 0.5788$. Cat (0.6128, inter=15), Adder (0.3458, inter=89) y Truth Machine son radicalmente distintos. |
| **H5** | Estructura toroidal no trivial del estado completo | **`DESTROYED`** | La fracción diagonal deriva mecánicamente del despacho de opcodes. El control N7 prueba que reingresar a $c$ o $(c,d)$ **NO** restaura la memoria ni el acumulador $a$. **No existe ciclo toroidal de estado completo.** |

---

## 📐 Las Dos Grandes Falsaciones Matemáticas

### 1. El Misterio de la Fracción Diagonal ~0.578812
En análisis previos se reportó una `diagonal_fraction` cercana a $0.5788$, sospechada como evidencia de una órbita toroidal continua.

**Demostración:**  
En Malbolge Classic:
- Si la instrucción no es `i` (jump): $c_{t+1} = (c_t + 1) \pmod{59049}$.
- Si la instrucción no es `j` (mov d): $d_{t+1} = (d_t + 1) \pmod{59049}$.
- Para toda instrucción ordinaria (`*`, `p`, `<`, `/`, `o`):
  $$(c_{t+1} - d_{t+1}) \equiv (c_t - d_t) \pmod{59049}$$
  El vector en el plano $(c, d)$ es $(1, 1)$, una recta diagonal a 45°.

Por tanto, la fracción diagonal es exactamente:
$$\text{diagonal\_fraction} = \frac{\text{Pasos} - 1 - \text{Breaks}_i - \text{Breaks}_j}{\text{Pasos}}$$

En `candidate_m281_53562b.mal`:
$$\frac{62,239,851 - 1 - 21,389,393 - 4,825,305}{62,239,851} = \frac{36,025,152}{62,239,851} = 0.578811668428$$
**Coincide con la fracción medida experimentalmente hasta 12 decimales.**  
La fracción diagonal no describe un toro: es la proporción de opcodes que no son saltos en el bucle generador de Lutter.

---

### 2. El Misterio de las 96 Direcciones en $C \cap D$
Las 6 quines comparten exactamente 96 direcciones en su intersección $C \cap D$.

**Demostración:**  
Al auditar `BolgeForge/synthesize.py`, se descubre que las variantes `m281` a `m308` se generan trasladando el código de Lutter por:
$$\Delta = 94 \cdot (314 - m)$$
El conjunto de 96 direcciones se descompone exactamente en:
- **49 direcciones fijas:** $\{0, 99, 117..161, 59047, 59048\}$.
- **47 direcciones móviles:** que se trasladan exactamente en $\Delta$.

**Veredicto:** Es **herencia estructural** de la construcción de Anthony de Lutter reproducida por el sintetizador, no una constante universal de la computación.

---

## 📊 Matriz Numérica de las Seis Quines

Todas las quines alcanzaron el HALT legítimo reproduciendo su fuente **bit a bit idéntico** (0 bytes diff):

| Programa | Pasos | Celdas C | Celdas D | C ∩ D | C ∪ D | Frac. Diagonal | Saltos `i` | Movs `j` | Pares (c,d) | Quine PASS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| **m281** | 62,239,851 | 25,554 | 26,800 | **96** | 52,258 | **0.578812** | 21,389,393 | 4,825,305 | 132,515 | **PASS** |
| **m284** | 62,902,923 | 24,090 | 27,082 | **96** | 51,076 | **0.578804** | 21,617,925 | 4,876,504 | 132,179 | **PASS** |
| **m287** | 63,568,038 | 25,188 | 27,364 | **96** | 52,737 | **0.578811** | 21,847,150 | 4,927,867 | 134,882 | **PASS** |
| **m293** | 64,897,488 | 25,584 | 27,928 | **96** | 53,679 | **0.578805** | 22,305,373 | 5,030,500 | 139,120 | **PASS** |
| **m308** | 68,218,362 | 26,762 | 29,338 | **96** | 55,548 | **0.578752** | 23,449,907 | 5,286,947 | 144,302 | **PASS** |
| **Lutter** | 69,547,436 | 27,293 | 29,901 | **96** | 57,098 | **0.578812** | 23,901,063 | 5,391,451 | 146,662 | **PASS** |

---

## 🛡️ Controles Negativos (Falsificación Metodológica)

| Control | Nombre | Hallazgo | Veredicto |
|:---:|---|---|:---:|
| **N1** | Renderer Circular | `orbit` genera círculos artificiales sobre paseos aleatorios independientes. | **DEMONSTRATED** |
| **N2** | Variación de Dimensión | Las figuras rectangulares dependen del ancho $W \in \{47, 94, 188, 376\}$. | **DEMONSTRATED** |
| **N3** | Permutación Temporal | Barajar el orden temporal destruye la continuidad diagonal y la trayectoria. | **DEMONSTRATED** |
| **N4** | Secuencia Sintética | Se recuperó con exactitud matemática el período conocido $P=729$. | **DEMONSTRATED** |
| **N5** | Comparación de Familias | Cat ($D=0.6128$), Adder ($D=0.3458$) y Truth Machine poseen geometrías ajenas a las quines. | **DEMONSTRATED** |
| **N6** | Detección de Divergencia | Localizó el paso exacto 16 donde un mutante de un solo byte se separa del original. | **DEMONSTRATED** |
| **N7** | Falsa Vuelta (False Loop) | Retornar a la misma celda $c$ **NO** recupera la memoria ni el estado completo. | **DEMONSTRATED** |

---

## 🚀 Reproducción Rápida

Requisitos: Linux (Ubuntu 24.04 o similar), GCC 11+, Python 3.10+ con `Pillow` y `numpy`.

```bash
# 1. Clonar el repositorio
git clone https://github.com/DannyBaanks/MalbolgArt.git
cd MalbolgArt

# 2. Compilar el extractor Classic optimizado
gcc -O3 -Wall -Wextra src/trace_extractor.c -lcrypto -o src/trace_extractor

# 3. Ejecutar la suite completa (15 programas + controles + visualizaciones)
python3 run_experiment.py
```

---

## 📜 Licencia

MIT License — Copyright (c) 2026 Danny Baanks & ISyCo Research Team.
