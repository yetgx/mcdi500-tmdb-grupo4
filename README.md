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
docs/            diccionario, validación, metadatos y bitácora
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

Ejecutar los cuadernos en orden: F1, F2 y F3. Cada cuaderno debe localizar la raíz del proyecto aunque Jupyter lo abra en su propia carpeta.

### Dependencias declaradas
- ipykernel
- jupyterlab
- notebook
- numpy==2.5.4
- pandas==3.1.0

## Flujo de trabajo en equipo
- `main` está protegida: los cambios entran por pull request.
- Ramas por tarea: `feat/f2-imputacion`, `docs/bitacora`, `fix/ruta-datos`.
- Cada integrante commitea con su propio usuario de Git, desde el primer día y en ambas fases.

## Convención de commits
Prefijos: `docs`, `data`, `feat`, `fix`. Mensaje en imperativo y específico, por ejemplo `feat: agrega imputacion de runtime por mediana`.

## Decisiones técnicas
- Los datos son comunes a todas las fases (`data/`); los cuadernos se separan por fase.
- Semilla aleatoria fijada en 42 para asegurar reproducibilidad.
- El archivo original pesa 3.2 MB, por lo que se versiona en `data/raw/`.
- Registro breve de las decisiones relevantes, con su motivo y cifras, en `docs/bitacora.md`, actualizado al cerrar cada fase.
