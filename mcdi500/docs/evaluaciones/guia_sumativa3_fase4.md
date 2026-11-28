# Guía de la Sumativa 3 (Fase 4) · Grupo 4

Referencia de trabajo para el recomendador TMDB. Resume los requisitos del curso y los conecta con los archivos del proyecto. No sustituye la guía ni la plantilla institucional.

## Material del docente

- [Guía de desarrollo de la Sumativa 3 (Word)](https://github.com/magistercienciadatos/Material_Didactico_Semana_3/blob/main/3_Guias_de_Apoyo/Guia_apoyo_Sumativa3_Fase4.docx): entregables, 26 criterios (150 puntos), estructura del informe y revisión final.
- [Cuaderno guía](https://github.com/magistercienciadatos/Material_Didactico_Semana_3/blob/main/3_Guias_de_Apoyo/f4_s03_guia_visualizacion.ipynb) y [Fase 4 del proyecto modelo](https://github.com/magistercienciadatos/Material_Didactico_Semana_3/blob/main/proyecto-grupoX-mcdi500/F4/S3_F4_Visualizacion_Comunicacion.ipynb): estructura y ejemplo práctico. El caso del profesor es de ACV; su variable objetivo, escalamiento y reglas de faltantes no se trasladan a TMDB.
- [Apunte de Fase 4](https://github.com/magistercienciadatos/Material_Didactico_Semana_3/blob/main/3_Guias_de_Apoyo/MCDI500_Apunte_Fase4.pdf): material complementario disponible en la maleta de la Semana 3.
- [Anuncio del docente en Canvas](https://canvas.unab.cl/courses/243133/announcements/1939593): extensión al miércoles 25 de noviembre de 2026 a las 23:59 y recordatorio de reproducibilidad. Consultar Canvas para la entrega.

## Qué exige la entrega

| Producto | Requisito del curso | Qué comprobar en el proyecto |
| --- | --- | --- |
| Informe | PDF de hasta 10 páginas en plantilla institucional; conservar la numeración de sus apartados. Incluir tres visualizaciones analíticas e interpretar cada una. | La introducción conecta las cuatro fases; alcance, restricciones y supuestos se distinguen. Los resultados, discusión y conclusiones coinciden con F4. Incluir al menos cinco fuentes APA 7 citadas: dos del curso, dos técnicas oficiales y una académica complementaria. |
| Notebooks | F1 a F4 ejecutables de principio a fin; dejar el cuaderno final ejecutado y guardado con sus salidas. | Desde un clon limpio, usar Python 3.13.0 y las dependencias del repo. Ejecutar F1 → F2 → F3 → F4, reiniciando el kernel y ejecutando todas las celdas. F4 consume las salidas de F3, sin volver a limpiar ni ajustar el modelo. |
| GitHub | Carpetas F1–F4, README técnico, historial de aportes individuales y trazabilidad de mejoras. | Revisar la retroalimentación anterior; registrar observación, cambio y enlace al commit en el changelog. La bitácora documenta las decisiones. Verificar que la rama principal contiene la versión de entrega; cada integrante deja sus propios commits de F4. |
| Video | 5–8 minutos en Canvas Studio, con apoyo visual y participación de todo el equipo. | Presentar problema, método, resultados y límites. Usar las mismas figuras y cifras que en el informe y el notebook. |

Cada figura principal debe respaldar un objetivo e incluir un título que cuente el hallazgo, ejes y unidades claros, leyenda cuando corresponda, fuente e interpretación. La guía formal pide **tres** figuras; las adicionales pueden quedar como evidencia complementaria. La autoevaluación y coevaluación se tramitan por separado en Canvas.

## Cómo aplicarlo al recomendador TMDB

| Objetivo de F1 | Evidencia disponible | Figura sugerida (no es un requisito adicional) |
| --- | --- | --- |
| 1. Caracterizar el catálogo | [Cuaderno de F1](../../F1/F1_Definicion.ipynb) y [particiones de F3](../../data/processed/) | Estrenos por año, indicando cobertura del extracto. Complementaria. |
| 2. Preparar las entradas | [Diccionario de columnas](../../data/processed/movies_procesado_diccionario.csv) y particiones de F3 | Proporción de faltantes de presupuesto y recaudación, con denominador explícito. Complementaria. |
| 3. Ponderar la calidad | `vote_average`, `vote_count` y `weighted_rating` en los artefactos de F3 | Comparar nota original y ponderada por tramos de votos. Mostrar el tamaño de cada tramo y aclarar la escala. Principal: contexto. |
| 4. Implementar y medir | [Mediciones de F3](../../F3/results/mediciones.csv), experimento `top_k` | Comparar tiempo y memoria de las alternativas a medida que crece el catálogo. Principal: contraste técnico. |
| 5. Evaluar recomendaciones | [Evaluación de F3](../../F3/results/evaluacion_recomendador.csv) | Comparar línea base aleatoria, similitud e híbrido en género, idioma y respaldo de votos. Principal: resultado. |

El CSV de evaluación muestra que el híbrido aumenta el respaldo de votos frente a solo similitud (15,6 % → 80,0 %), pero reduce la coherencia de idioma (95,3 % → 81,4 %). Presentar ambos resultados juntos, sin convertir métricas indirectas en una afirmación de satisfacción de usuarios. El corte de evaluación es **428 votos**; no confundirlo con el parámetro de **421** del cálculo de `Weighted Rating`.

## Verificación antes del cierre

- [ ] Leer `entrenamiento_f3.csv`, `prueba_f3.csv`, `movies_procesado_diccionario.csv` y `parametros_f3.json` desde `data/processed/`. Si falta un archivo, indicar qué fase ejecutar en lugar de generar un sustituto.
- [ ] Comprobar esquema y `movie_id` no nulo, único y sin cruces entre las dos particiones. Para el conjunto versionado: 14.382 filas en entrenamiento y 3.596 en prueba.
- [ ] Conservar los nulos intencionales de `budget_clean` y `revenue_clean`. Para las figuras, utilizar columnas interpretables que F3 conserva, como `weighted_rating` o `popularity`. Si se usa una inversa, aplicar el contrato real de `parametros_f3.json`, no el del modelo de ACV. Contrastar columnas sin modificación con la fuente, emparejando las películas por `movie_id`.
- [ ] Usar una tabla de hallazgos como fuente de cifras para figuras, informe y video. El proyecto modelo usa `docs/hallazgos_f4.csv`, `docs/metadatos_f4.json` y `F4/figuras/`; es una convención sugerida. Verificar que estén las tres figuras principales y sus hallazgos, no solo que existan los archivos.
- [ ] Ejecutar F4 explícitamente al final. [El flujo actual de GitHub Actions](../../.github/workflows/reproducibilidad.yml) comprueba F1–F3; un resultado verde todavía no demuestra que F4 corra.
