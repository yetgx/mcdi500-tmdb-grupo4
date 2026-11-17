# Fase 3 – Estructura compatible con el repositorio original

Este paquete contiene rutas relativas a la raíz de `mcdi500-tmdb-grupo4`:

- `F3/F3_NucleoAlgoritmico_TMDB_Mejorado.ipynb`: notebook principal
- `F3/results/`: resultados ilustrativos guardados de la ejecución de verificación; al ejecutar se pueden regenerar
- `src/`: módulos compartidos del proyecto (versiones mejoradas)
- `tests/test_f3.py`: pruebas nuevas

**Antes de integrar:** crea una rama Git, registra el estado local y respalda cualquier archivo preexistente de `src/`. El ZIP contiene archivos con nombres iguales a módulos actuales: revisar diferencias antes de sobrescribir. No modifica `F1/`, `F2/`, `F4/`, `data/`, `docs/`, `.github/`, el README principal, ni `requirements.txt`.

**Datos requeridos en el repositorio existente:** `data/raw/movies_raw.csv` y `data/processed/movies_procesado.csv`.

En VS Code abre el notebook desde `F3/` con el kernel de tu entorno local. El notebook busca automáticamente la raíz que contiene `src/pipeline.py` y `data/raw/movies_raw.csv`.

Para Colab, descomprime esta estructura en `/content/`, añade los archivos CSV en las rutas anteriores o clona el repositorio completo, y ejecuta el notebook desde su primera celda.

Pruebas: desde la raíz, ejecuta `python -m pytest tests/test_f3.py -q`.
