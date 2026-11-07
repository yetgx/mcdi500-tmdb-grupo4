# Informe Sumativa 1 — Fases 1 y 2

**Título:** Análisis exploratorio de las tendencias cinematográficas mundiales (2010–2025)
**Asignatura:** MCDI500 · Programación para la Ciencia de Datos — Magíster en Ciencia de Datos e Inteligencia Artificial, UNAB
**Profesor:** Omar Salinas Silva
**Fecha de entrega:** domingo 8 de noviembre de 2026
**Grupo 4:** Daniela Baeza Rocha · Juan González Elgueta · Elías Manríquez Armijo · Yestxander Rada Gutierrez
**Repositorio:** https://github.com/yetgx/mcdi500-tmdb-grupo4

> Nota: la guía oficial de la Sumativa 1 no está en el repositorio. Esta plantilla sigue la estructura de `F1/movies.ipynb` y los 5 indicadores del cuaderno práctico. Ajustar secciones y extensión al enunciado de Canvas.

---

## Resumen ejecutivo
<!-- 150–200 palabras: problema, datos, método, 2–3 hallazgos con cifra, conclusión. Escribir al final. -->

## 1. Introducción y contexto
<!-- Industria del cine 2010–2025: streaming, pandemia, cambios en consumo. Por qué importa. -->

## 2. Problema y objetivos
**Pregunta central:** <!-- ej. ¿Qué factores (presupuesto, género, país, idioma, año) se asocian a mayor recaudación y valoración? -->

**Objetivo general:** Desarrollar un análisis exploratorio de 17 978 películas de TMDB estrenadas entre 2010 y 2025.

**Objetivos específicos:**
1. <!-- caracterizar la estructura y calidad de los datos -->
2. <!-- describir la evolución anual de estrenos, popularidad y valoración -->
3. <!-- explorar la relación presupuesto–recaudación -->
4. <!-- identificar países, idiomas y géneros predominantes -->

## 3. Datos
| Atributo | Detalle |
|---|---|
| Fuente | TMDB Raw Movie Dataset (2010–2025), Evan Christiawan, Zenodo — DOI 10.5281/zenodo.21920642 |
| Licencia | CC BY 4.0 (uso educativo, no comercial) |
| Tamaño | 17 978 filas × 16 columnas · 3,2 MB |
| SHA-256 | `129fbd840dd13857f72ff4673da23820ac73ea548236b1f47baa621438cd0a5c` |
| Validación | `docs/validacion_dataset.md` — cumple los 11 requisitos del curso |

### 3.1 Diccionario de variables
| Variable | Tipo | Rol | Nulos % | Descripción |
|---|---|---|---|---|
| movie_id | int64 | identificador | 0 | ID TMDB |
| title | str | identificador | 0 | Título |
| release_date | str → datetime | fecha | 0 | Fecha de estreno |
| status | str | nominal | 0 | Constante («Released») |
| budget | int64 | continua | 0 | Presupuesto (USD) |
| revenue | int64 | continua | 0 | Recaudación (USD) |
| runtime | int64 | discreta | 0 | Duración (min) |
| genres | str | alta cardinalidad | 0,06 | Géneros separados por `\|` |
| production_companies | str | alta cardinalidad | 2,75 | Productoras separadas por `\|` |
| production_countries | str | alta cardinalidad | 0,98 | Países separados por `\|` |
| spoken_languages | str | alta cardinalidad | 0,51 | Idiomas hablados |
| original_language | str | alta cardinalidad | 0 | Idioma original (80 valores) |
| vote_average | float64 | continua | 0 | Valoración media |
| vote_count | int64 | continua | 0 | N.º de votos (mín. 50) |
| popularity | float64 | continua | 0 | Índice de popularidad TMDB |
| adult | bool | nominal | 0 | Constante (`False`) |

### 3.2 Calidad de los datos (hallazgos a documentar)
- `status` y `adult` son constantes: sin poder informativo.
- `budget` y `revenue`: mediana = 0, es decir, el cero codifica «dato no informado», no un valor real. <!-- cuantificar % de ceros -->
- `runtime` con mínimo 0 y máximo 585: revisar valores atípicos.
- Nulos solo en columnas multivalor (`genres`, `production_*`, `spoken_languages`), máx. 2,75 %.
- Títulos repetidos (17 322 únicos de 17 978): confirmar que no son duplicados de `movie_id`.
- Columnas multivalor separadas por `|`: requieren expansión (`explode`) para contar.

## 4. Metodología
- Entorno: Python 3.12+, pandas 3.1.0, numpy 2.5.4, semilla 42, dependencias en `requirements.txt`.
- Flujo: `F1/` (definición y exploración) → `F2/` (limpieza y transformación) → `data/processed/`.
- Control de versiones: `main` protegida, ramas por tarea, PR con revisión (`CODEOWNERS`), commits con prefijos `docs/data/feat/fix`.
- Decisiones registradas con motivo y cifra en `docs/bitacora.md`.

## 5. Análisis exploratorio
Para cada figura: título, ejes con unidades, interpretación de 2–4 líneas con cifra.

### 5.1 Estrenos por año
<!-- figura + interpretación (¿caída 2020–2021 por pandemia?) -->

### 5.2 Popularidad promedio por año
<!-- figura + interpretación -->

### 5.3 Presupuesto vs. recaudación
<!-- excluir ceros; escala log; correlación -->

### 5.4 Países productores
<!-- top N tras explode de production_countries -->

### 5.5 <!-- géneros / idiomas / valoración -->

## 6. Preprocesamiento (Fase 2)
| Problema | Tratamiento | Alternativa descartada | Motivo (cifra) |
|---|---|---|---|
| Ceros en budget/revenue | <!-- NaN / excluir en análisis --> | <!-- imputar mediana --> | <!-- % de ceros --> |
| Nulos multivalor | <!-- categoría «Desconocido» --> | | |
| Columnas constantes | <!-- eliminar --> | | |
| Fechas | `to_datetime`, derivar `release_year` | | |

## 7. Resultados y discusión
<!-- Responder la pregunta central. 3–5 hallazgos con cifra. Contrastar con el contexto de la sección 1. -->

## 8. Limitaciones
- Presupuesto y recaudación ausentes en gran parte de los registros.
- Sesgo de TMDB hacia producciones occidentales y con más votos (mín. 50 votos).
- Análisis descriptivo: asociación, no causalidad.
- Moneda nominal, sin ajuste por inflación.

## 9. Conclusiones y trabajo futuro
<!-- 1 párrafo + 3 líneas de próximos pasos (Fases 3 y 4). -->

## 10. Contribución del equipo
| Integrante | Usuario GitHub | Aporte | Commits / PR |
|---|---|---|---|
| Daniela Baeza Rocha | @Daninela | | |
| Juan González Elgueta | @jp-IArtificial | | |
| Elías Manríquez Armijo | @EliasManriquez | | |
| Yestxander Rada Gutierrez | @yetgx | | |

## Referencias (APA)
- Christiawan, E. (2026). *TMDB Raw Movie Dataset (2010–2025)* [Conjunto de datos]. Zenodo. https://doi.org/10.5281/zenodo.21920642
- The Movie Database (TMDB). (s. f.). https://www.themoviedb.org/
- <!-- pandas, matplotlib, seaborn, material del curso -->

## Anexos
- A. Informe de validación del dataset (`docs/validacion_dataset.md`).
- B. Mapa conceptual Formativa 1 (`F1/Formativa/Final/mcdi500_s1_grupo4.pdf`).
- C. Bitácora de decisiones (`docs/bitacora.md`).
