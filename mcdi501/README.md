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

MCDI501 tiene su propio entorno, separado del de MCDI500 (otras librerías). Desde `mcdi501/`:

    py -3.13 -m venv .venv            # macOS/Linux: python3.13 -m venv .venv
    .venv\Scriptsctivate           # macOS/Linux: source .venv/bin/activate
    python -m pip install -r requirements.txt
    nbstripout --install              # el docente versiona los notebooks sin salidas

`requirements.txt` lista las librerías del curso sin fijar versión; al empezar la Formativa 1, fijarlas con `pip freeze` para que el entorno sea reproducible. Los datos van en `data/raw/` y no se versionan. La copia de cada notebook que se sube a Canvas va ejecutada.
