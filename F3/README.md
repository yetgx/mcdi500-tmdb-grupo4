# Fase 3

Núcleo algorítmico, eficiencia y programación orientada a objetos.

- `F3_NucleoAlgoritmico_TMDB.ipynb`: carga con verificación de esquema, pipeline de clases (sopa de metadatos, `log1p` y MinMax), equivalencia con la Fase 2, validación en tres escenarios, medición de tiempo y memoria, y guardado del resultado.
- Los módulos viven en `src/` (`carga`, `transformadores`, `pipeline`, `medicion`) y el cuaderno los importa. Parten del proyecto modelo de la Semana 2 (`Material_Didactico_Semana2`) y se extendieron con los pasos propios de TMDB.
- Salidas en `data/processed/`: `entrenamiento_f3.csv`, `prueba_f3.csv` y `parametros_f3.json` (semilla y parámetros aprendidos de cada paso).
