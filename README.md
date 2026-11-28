# MCDI 2026 · Grupo 4

[![Reproducibilidad MCDI500](https://github.com/yetgx/mcdi-2026-grupo4/actions/workflows/reproducibilidad.yml/badge.svg)](https://github.com/yetgx/mcdi-2026-grupo4/actions/workflows/reproducibilidad.yml)

Repositorio del Grupo 4 del Magíster en Ciencia de Datos e Inteligencia Artificial (UNAB). Una carpeta por módulo; cada una es autocontenida (código, datos, informes, pruebas y entorno propios).

| Módulo | Curso | Carpeta | Estado |
| --- | --- | --- | --- |
| MCDI500 | Programación para la Ciencia de Datos | [`mcdi500/`](mcdi500/) | Cerrado: recomendador de películas TMDB 2010–2025 (F1–F4) |
| MCDI501 | Estadística Computacional para la Toma de Decisiones | [`mcdi501/`](mcdi501/) | En curso: F1, S1, F2, S2 y S3 |

## Integrantes
- Yestxander Rada (@yetgx)
- Daniela Baeza (@Daninela)
- Elías Manríquez (@EliasManriquez)
- Juan Pablo González (@jp-IArtificial)

## Cómo trabajar
- Cada módulo tiene su propio `requirements.txt` y versión de Python (MCDI500 fija 3.13.0 en `mcdi500/.python-version`). Crear el entorno **dentro** de la carpeta del módulo que se va a usar.
- Ramas y PR como siempre (plantilla en `.github/`; `CODEOWNERS` pide revisión a los demás integrantes). Los commits y PR se prefijan con `docs`, `data`, `feat`, `fix` o `chore`; indicar el módulo en el título (p. ej. `[mcdi501] S1: ...`).
- La verificación automática de cada módulo corre solo si el PR toca su carpeta (`.github/workflows/`).
- Módulo nuevo: carpeta `mcdiNNN/` en la raíz con su README, entorno y pruebas, y una fila en la tabla de arriba.
