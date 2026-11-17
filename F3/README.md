# Fase 3

Núcleo algorítmico, eficiencia y programación orientada a objetos. Guía del docente: `docs/evaluaciones/guia_sumativa2_fase3.md`.

- `F3_NucleoAlgoritmico_TMDB.ipynb` (ejecutado completo, celdas 1–19):
  1. Carga con verificación de esquema.
  2. Pipeline de clases (`Transformador` y 8 hijas; patrones *Template Method* y *Strategy*) y equivalencia exacta con F2 con `ejecutar(df)`.
  3. Partición entrenamiento/prueba sin fuga de datos.
  4. Validación: caso normal, casos límite y excepciones.
  5. Recomendador híbrido: elección de pesos con la regla «maximizar el peor criterio» y evaluación en prueba frente a la línea base de F1.
  6. Recursividad frente a iteración (aplanar metadatos; top k con cuatro algoritmos equivalentes).
  7. Eficiencia: mínimo de 7 ejecuciones con `timeit` y memoria con `tracemalloc`, con tamaños crecientes.
  8. Guardado y relectura de resultados.
- El cuaderno solo importa de `src/`: `pipeline` (`ejecutar`, `pipeline_tmdb`), `transformadores`, `preparacion`, `recomendador`, `recursividad`, `medicion` y `carga`. Pruebas en `tests/` (`python -m pytest`).
- Salidas en `data/processed/`: `entrenamiento_f3.csv` y `prueba_f3.csv` (mismas columnas que F2) y `parametros_f3.json` (semilla, parámetros aprendidos y pesos del recomendador). En `F3/results/`: `evaluacion_recomendador.csv`, `rejilla_pesos.csv`, `mediciones.csv` y `entorno_mediciones.txt`.
- Decisiones de diseño con sus cifras: `docs/bitacora.md`, sección Fase 3.
