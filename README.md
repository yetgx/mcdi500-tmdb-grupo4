# Películas TMDB 2010–2025 — Grupo 4

Proyecto de MCDI500 (Programación para la Ciencia de Datos, Magíster en Ciencia de Datos e Inteligencia Artificial, UNAB). Trabaja con un extracto de The Movie Database (TMDB) con estrenos entre 2010 y 2025: presupuesto, recaudación, duración, géneros, productoras, países, idiomas, valoración y popularidad. La definición del problema y los objetivos se completan en la Fase 1 (`F1/`).

## Integrantes
- Yestxander Rada (@yetgx)
- Daniela Baeza (@Daninela)
- Elías Manríquez (@EliasManriquez)
- Juan Pablo González (@jp-IArtificial) 

## Datos
- Fuente: TMDB Raw Movie Dataset (2010–2025), Evan Christiawan (Binus University), Zenodo.
- Enlace: https://zenodo.org/records/21920642 (DOI 10.5281/zenodo.21920642)
- Licencia: CC BY 4.0. Recolectado con fines educativos y no comerciales; no afiliado oficialmente a TMDB.
- Estructura: 17978 filas (una película por fila) × 16 columnas.
- Ubicación: `data/raw/movies_raw.csv` (original, no se modifica).
- SHA-256: `129fbd840dd13857f72ff4673da23820ac73ea548236b1f47baa621438cd0a5c`
- Validación de requisitos del curso: `docs/validacion_dataset.md`.

## Estructura del repositorio
```
data/raw/        datos originales, sin modificar
data/processed/  datos tras limpieza y transformación (F2)
docs/            validación del dataset, informe, bitácora, guías y práctica del curso
src/             módulos reutilizables: carga, transformadores, pipeline y medición
F1/ F2/ F3/ F4/  cuadernos e informes de cada fase
validar_dataset.py  validador de dataset del curso
```

## Requisitos y ejecución
Python 3.12 o superior

    python -m venv .venv
    source .venv/Scripts/activate    # Windows, Git Bash
    # .venv\Scripts\Activate.ps1     # Windows, PowerShell
    # source .venv/bin/activate      # macOS y Linux
    python -m pip install -r requirements.txt

Si el equipo tiene la variable de entorno `PYTHONPATH` definida, vaciarla antes de instalar: contamina las librerías del `.venv`.

Ejecutar los cuadernos en orden, F1, F2 y F3, desde `jupyter lab` con el kernel del `.venv` y con *Restart Kernel and Run All Cells*. Las rutas son relativas a la raíz del repositorio y la semilla aleatoria es 42. Cada cuaderno localiza la raíz del proyecto aunque Jupyter lo abra en su propia carpeta.

| Cuaderno | Qué hace | Entrada | Salida |
|---|---|---|---|
| `F1/F1_Definicion.ipynb` | Definición del problema, entorno y reconocimiento inicial del dataset (no modifica datos) | `data/raw/movies_raw.csv` | Tablas y gráficos exploratorios |
| `F2/Fase2-Preparacion-Recomendador.ipynb` | Diagnóstico, limpieza, sopa de metadatos, vectorización y escalado | `data/raw/movies_raw.csv` | Conjunto preparado para F3 |
| `F3/F3_NucleoAlgoritmico_TMDB.ipynb` | Núcleo algorítmico: clases del pipeline (`src/`), eficiencia y mediciones de tiempo y memoria | `data/raw/movies_raw.csv` | Resultados del pipeline modular y mediciones |

### Dependencias principales
Todas las versiones están fijadas en `requirements.txt` (generado con `pip freeze`, codificación UTF-8):

| Librería | Versión |
|---|---|
| numpy | 2.5.4 |
| pandas | 3.1.1 |
| scikit-learn | 1.9.1 |
| matplotlib | 3.11.2 |
| seaborn | 0.13.2 |
| jupyterlab | 4.6.5 |
| notebook | 7.6.4 |
| ipykernel | 7.4.0 |

### Regenerar `data/processed/`
Al ejecutar `F2/Fase2-Preparacion-Recomendador.ipynb` completo (Pasos 7 y 8) se escriben `data/processed/movies_procesado.csv` (17.978 filas, una película por fila) y `data/processed/movies_bow_matrix.npz` (matriz dispersa del *Bag of Words*, mismo orden de filas). El Paso 7 valida el conjunto con `assert` antes de exportarlo y el Paso 8 verifica la relectura. `data/raw/` nunca se modifica.

## Flujo de trabajo en equipo
- `main` está protegida: los cambios entran por pull request.
- Ramas por tarea: `feat/f2-imputacion`, `docs/bitacora`, `fix/ruta-datos`.
- Cada integrante commitea con su propio usuario de Git, desde el primer día y en ambas fases.

## Convención de commits
Prefijos: `docs`, `data`, `feat`, `fix`, `chore`. Mensaje en imperativo y específico, por ejemplo `feat: agrega imputacion de runtime por mediana`.

## Decisiones técnicas
- Los datos son comunes a todas las fases (`data/`); los cuadernos se separan por fase.
- Semilla aleatoria fijada en 42 para asegurar reproducibilidad.
- El archivo original pesa 3.2 MB, por lo que se versiona en `data/raw/`.
- Registro breve de las decisiones relevantes, con su motivo y cifras, en `docs/bitacora.md`, actualizado al cerrar cada fase.

## Autoría
Cada integrante tiene más de una identidad de Git en el historial (cambios de nombre de usuario o de equipo). El archivo `.mailmap` las unifica: `git shortlog -sne` muestra una sola línea por persona.
