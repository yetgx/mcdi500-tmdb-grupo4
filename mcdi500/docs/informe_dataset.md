# Validación del dataset — MCDI500

**Archivo:** `movies_raw.csv` · 17978 filas × 16 columnas

## Perfil de variables

| variable | dtype | rol | unicos | pct_nulos |
| --- | --- | --- | --- | --- |
| movie_id | int64 | identificador | 17978 | 0.0 |
| title | str | identificador | 17322 | 0.0 |
| release_date | str | fecha | 4582 | 0.0 |
| status | str | nominal | 1 | 0.0 |
| budget | int64 | continua | 1091 | 0.0 |
| revenue | int64 | continua | 6443 | 0.0 |
| runtime | int64 | discreta | 217 | 0.0 |
| genres | str | alta cardinalidad | 2857 | 0.1 |
| production_companies | str | alta cardinalidad | 15387 | 2.7 |
| production_countries | str | alta cardinalidad | 1808 | 1.0 |
| spoken_languages | str | alta cardinalidad | 1505 | 0.5 |
| original_language | str | alta cardinalidad | 80 | 0.0 |
| vote_average | float64 | continua | 3652 | 0.0 |
| vote_count | int64 | continua | 2815 | 0.0 |
| popularity | float64 | continua | 13679 | 0.0 |
| adult | bool | nominal | 1 | 0.0 |

## Requisitos del curso

| estado | requisito | detalle |
| --- | --- | --- |
| OK | Al menos 2000 filas | 17978 filas |
| OK | Al menos 12 columnas | 16 columnas |
| OK | Combina al menos 3 roles analíticos | continua, alta cardinalidad, nominal, fecha, discreta |
| OK | Al menos una variable numérica | 6 numéricas (continuas o discretas) |
| OK | Al menos una variable categórica | 2 categóricas (nominales, binarias u ordinales) |
| OK | Presencia de valores faltantes | máximo 2.7% en una variable |
| OK | Ninguna variable sobre 60% de faltantes | máximo 2.7% |
| OK | Incluye alguna variable de fecha | 1 detectadas |
| OK | Incluye texto o categórica de alta cardinalidad | 5 detectadas |
| OK | Archivo bajo 100 MB | 3.2 MB |
| OK | Sin filas duplicadas exactas | ninguna |

## Resultado

El conjunto **cumple** los requisitos mínimos.