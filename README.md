# Películas TMDB 2010–2025 — Grupo 4

[![Reproducibilidad](https://github.com/yetgx/mcdi500-tmdb-grupo4/actions/workflows/reproducibilidad.yml/badge.svg)](https://github.com/yetgx/mcdi500-tmdb-grupo4/actions/workflows/reproducibilidad.yml)

Proyecto de MCDI500 (Programación para la Ciencia de Datos, Magíster en Ciencia de Datos e Inteligencia Artificial, UNAB). Trabaja con un extracto de The Movie Database (TMDB) con estrenos entre 2010 y 2025: presupuesto, recaudación, duración, géneros, productoras, países, idiomas, valoración y popularidad. El proyecto construye un recomendador híbrido de películas: similitud de contenido (géneros, productoras e idioma) ponderada por calidad (*Weighted Rating*) y popularidad.

**Pregunta:** ¿en qué medida ese recomendador entrega, para una película dada, recomendaciones coherentes con ella en género e idioma y respaldadas por un volumen suficiente de votos? Se evalúa con tres proporciones sobre las 10 recomendaciones de cada película (comparte género, mismo idioma, votos ≥ percentil 75) frente a una línea base al azar: 41,8 %, 36,6 % y 25,0 % (`F1/F1_Definicion.ipynb`, sección 3).

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
data/processed/  datos tras limpieza y transformación (F2) y su diccionario
docs/            validación del dataset, informe, mapa, bitácora y guía de subida
docs/evaluaciones/  rúbricas y retroalimentación recibidas, para preparar las próximas entregas
src/             módulos reutilizables: preparación (F2), carga, transformadores, pipeline y medición
tests/           pruebas unitarias de src/ (pytest)
F1/ F2/ F3/ F4/  cuadernos e informes de cada fase
.github/workflows/  verificación en Ubuntu, macOS y Windows en cada PR
validar_dataset.py  validador de dataset del curso
```

## Requisitos y ejecución
Python 3.12 (fijado en `.python-version`; los cuadernos se ejecutan con 3.12). Si tu `.venv` se creó con otra versión, bórralo y créalo de nuevo.

    python3.12 -m venv .venv         # Windows: py -3.12 -m venv .venv
    source .venv/Scripts/activate    # Windows, Git Bash
    # .venv\Scripts\Activate.ps1     # Windows, PowerShell
    # source .venv/bin/activate      # macOS y Linux
    python -m pip install -r requirements.txt
    python -m pytest                 # pruebas de src/

Si el equipo tiene la variable de entorno `PYTHONPATH` definida, vaciarla antes de instalar: contamina las librerías del `.venv`.

Ejecutar los cuadernos en orden, F1, F2 y F3, desde `jupyter lab` con el kernel del `.venv` y con *Restart Kernel and Run All Cells*. Las rutas son relativas a la raíz del repositorio y la semilla aleatoria es 42. Cada cuaderno localiza la raíz del proyecto aunque Jupyter lo abra en su propia carpeta.

| Cuaderno | Qué hace | Entrada | Salida |
|---|---|---|---|
| `F1/F1_Definicion.ipynb` | Definición del problema y del criterio de evaluación, entorno, reconocimiento inicial del dataset, línea base y vínculo con el mapa (no modifica datos) | `data/raw/movies_raw.csv` | Tablas y gráficos exploratorios |
| `F2/Fase2-Preparacion-Recomendador.ipynb` | Diagnóstico, limpieza, sopa de metadatos, vectorización y escalado, con las funciones de `src/preparacion.py` | `data/raw/movies_raw.csv` | Conjunto preparado para F3 |
| `F3/F3_NucleoAlgoritmico_TMDB.ipynb` | Núcleo algorítmico: clases del pipeline (`src/`), eficiencia y mediciones de tiempo y memoria | `data/raw/movies_raw.csv` | Resultados del pipeline modular y mediciones |

### Dependencias
`requirements.txt` contiene solo las dependencias directas, con versión exacta y sin paquetes propios de un sistema operativo; pip resuelve el resto. El flujo de GitHub Actions comprueba en cada PR que se instala y que los cuadernos corren en Ubuntu, macOS y Windows.

| Librería | Versión |
|---|---|
| numpy | 2.5.4 |
| pandas | 3.1.1 |
| scikit-learn | 1.9.1 |
| matplotlib | 3.11.2 |
| scipy | 1.18.1 |
| seaborn | 0.13.2 |
| jupyterlab | 4.6.5 |
| ipykernel | 7.4.0 |
| nbconvert | 7.17.2 |
| pytest | 9.2.0 |

### Regenerar `data/processed/`
Al ejecutar `F2/Fase2-Preparacion-Recomendador.ipynb` completo (Pasos 7 y 8) se escriben `data/processed/movies_procesado.csv` (17.978 filas, una película por fila), `data/processed/movies_procesado_diccionario.csv` (uso de cada columna; `runtime_clean`, `budget_clean` y `revenue_clean` no las usa el recomendador) y `data/processed/movies_bow_matrix.npz` (matriz dispersa del *Bag of Words*, mismo orden de filas). El Paso 7 valida el conjunto con `assert` antes de exportarlo y el Paso 8 verifica la relectura. `data/raw/` nunca se modifica.

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
