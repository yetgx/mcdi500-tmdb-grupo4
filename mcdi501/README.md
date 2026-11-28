# MCDI501 · Proyecto del grupo (dentro del repo `mcdi-2026-grupo4`)

Estadística Computacional para la Toma de Decisiones (UNAB, 2026-83).

> Completar: integrantes, dataset elegido, variable objetivo y enlace al repositorio de GitHub.

| Carpeta | Evaluación | Entregables (nombres que esperan las pruebas) |
| --- | --- | --- |
| `F1/` | Formativa 1 — EDA e inferencia | `formativa1.ipynb`, `informe-formativa1.pdf` (o `.tex`/`.docx` mientras se escribe) |
| `S1/` | Sumativa 1 — Análisis exploratorio e inferencial (20 %) | `sumativa1.ipynb`, `informe-sumativa1.pdf` (máx. 8 págs.) |
| `F2/` | Formativa 2 — Modelamiento predictivo | `formativa2.ipynb` (síntesis final en Markdown) |
| `S2/` | Sumativa 2 — Validación, simulación y remuestreo (20 %) | `sumativa2.ipynb`, `informe-sumativa2.pdf` (máx. 7 págs.), `resultados_validados.{md,csv,json}` |
| `S3/` | Sumativa 3 — Modelamiento predictivo integrado (60 %) | `notebook_maestro.ipynb`, `informe-sumativa3.pdf` (máx. 10 págs.), `presentacion.{md,pdf,pptx}` |

## Entorno

Usa el entorno del repo (`requirements.txt` de la raíz, Python 3.13.0): agregar ahí `scipy`, `statsmodels`, `imbalanced-learn`, `seaborn`, `joblib` al comenzar MCDI501. Los datos van en `mcdi501/data/raw/` y no se versionan. El docente versiona los notebooks sin salidas (`nbstripout`); la copia para Canvas va ejecutada.

## Verificar contra la rúbrica

Desde la raíz del repo personal `Magister CDIA` (no de este repo):

```bash
python -m evaluador cursos/mcdi501-estadistica-computacional/evaluaciones/formativa-1-eda-inferencia --guardar
```

Escribe `revision.md` en la carpeta de la evaluación con lo que cumple, lo que falta y lo que hay que revisar a mano.
