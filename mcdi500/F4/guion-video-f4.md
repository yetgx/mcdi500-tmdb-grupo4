# Guion del video · Fase 4 · Grupo 4

Recomendador de películas TMDB · MCDI500 · Sumativa 3. Cuatro partes, una por integrante.

**Duración objetivo: 7:15** (límite del curso: 8:00). Con el ritmo de lectura de cada voz, el total estimado es **7:02** (6:32 si se lee más rápido, 7:38 si se lee más lento), incluyendo unos 20 s de portada, transiciones y cierre en pantalla.

Este guion reemplaza al del PR #68 (`guion-fase-4-tmdb.docx`), que es anterior a los capítulos 8 a 14 del cuaderno. Usa las tres figuras principales ya integradas en `F4/figuras/` y las cifras de `docs/`.

## Cómo se usa

- Cada integrante lee **solo su parte**. Lo que está entre corchetes o en «PANTALLA» no se lee.
- Las pausas marcadas van **dentro** del bloque, para que el público alcance a leer el gráfico.
- Ritmo de referencia: 2,3 palabras por segundo (unas 138 por minuto). Ensayen con cronómetro y avisen si su parte se pasa más de 10 segundos.
- Formato del video: fondo animado a pantalla completa, con una miniatura de cámara de quien habla y su nombre y rol al comenzar su parte.
- Cada uno graba **audio y cámara** de su parte por separado, con el mismo micrófono si es posible. La imagen de fondo se genera después, a partir del audio real.

## Resumen

| Parte | Quién | Tema | Tiempo | Palabras | Figura |
| --- | --- | --- | --- | --- | --- |
| 1 | Yestxander Rada | Problema y datos | 0:00–1:40 | 212 | — |
| 2 | Daniela Baeza | Preparación y calidad | 1:40–3:25 | 203 | Figura 1 |
| 3 | Elías Manríquez | Algoritmo y eficiencia | 3:25–5:10 | 191 | Figura 2 |
| 4 | Juan Pablo González | Resultados, límites y cierre | 5:10–7:15 | 262 | Figura 3 |
| | | **Total** | **0:00–7:15** | **868** | |

## Parte 1 · Yestxander Rada — Problema y datos

**Tiempo:** 0:00–1:40 · **Palabras:** 212 · **Lectura estimada:** 1:36

**PANTALLA**

- 0:00–0:05 · Portada con los cuatro nombres. Luego, nombre y rol de quien habla en la miniatura de cámara.
- Catálogo TMDB → película de entrada → diez recomendaciones (diagrama animado).
- Al final: las tres medidas de F1 con la línea base aleatoria en cifras grandes (41,8 % · 36,6 % · 25,0 %).

**TEXTO**

> Cuando buscamos una película parecida a otra, una buena nota no basta: puede ser de otro género, estar en otro idioma o tener apenas unos pocos votos. Nuestro proyecto parte de una pregunta: si damos una película como entrada, ¿podemos recomendar diez que sean coherentes con ella y que, además, tengan suficiente respaldo de votos?

> En este video recorremos las cuatro fases del proyecto: definimos el problema, preparamos los datos, construimos el algoritmo y evaluamos el resultado, siempre con las mismas tres medidas.

> Para probarlo usamos un extracto de The Movie Database con 17.978 películas estrenadas entre 2010 y 2025. De cada una tomamos el género, las productoras y el idioma original para describir su contenido, y la nota promedio y el número de votos para juzgar qué tan confiable es esa nota. No usamos historiales de usuarios: la lista depende solo de la película de entrada.

> Desde la Fase 1 definimos tres medidas: que la recomendación comparta género, que coincida en idioma y que tenga al menos 428 votos, el percentil 75 del catálogo.

> *[PAUSA 4 s · mostrar las tres cifras de la línea base]*

> Un recomendador que elige al azar cumple esas medidas el 41,8, el 36,6 y el 25 por ciento de las veces. Ese es el piso que tenemos que superar. Daniela les muestra ahora cómo preparamos los datos.

## Parte 2 · Daniela Baeza — Preparación y calidad

**Tiempo:** 1:40–3:25 · **Palabras:** 203 · **Lectura estimada:** 1:34

**PANTALLA**

- Flujo F2 → F3: limpieza → sopa de metadatos (géneros, hasta tres productoras, idioma) → bolsa de palabras → vector.
- Partición: 14.382 películas de entrenamiento y 3.596 de prueba, semilla 42.
- FIGURA 1 · f1_nota_ponderada_por_votos.png completa; luego resaltar el tramo 50–99 votos y el tramo ≥ 5.000.

**TEXTO**

> En la preparación separamos lo que describe el catálogo de lo que realmente necesita el recomendador. Por ejemplo, un presupuesto o una recaudación reportados como cero no significan que la película no costó nada: los conservamos como faltantes y no los usamos en el ranking.

> Para representar el contenido armamos una sopa de metadatos con los géneros, hasta tres productoras y el idioma original. Esa sopa se transforma en una bolsa de palabras: cada película queda como un vector que se puede comparar con los demás. En la Fase 3 organizamos todo en un pipeline de clases y separamos 14.382 películas para entrenar y 3.596 para probar, con semilla 42.

> *[PAUSA 6 s · figura 1; señalar las barras de 50–99 votos]*

> Este gráfico muestra por qué ponderamos la nota. Con menos de 100 votos, que son 6.243 películas, la dispersión de la nota original es de 0,94 puntos; con la nota ponderada baja a 0,13. En cambio, con 5.000 votos o más casi no cambia: 0,65 contra 0,63. La ponderación usa un promedio general de 6,33 y 421 votos de referencia: con pocos votos manda el promedio general; con muchos, manda la nota propia de la película. Esa señal de calidad no reemplaza a la similitud: se combina con ella. Elías les cuenta cómo.

## Parte 3 · Elías Manríquez — Algoritmo y eficiencia

**Tiempo:** 3:25–5:10 · **Palabras:** 191 · **Lectura estimada:** 1:30

**PANTALLA**

- Fórmula: puntaje = 0,50 · similitud + 0,50 · calidad + 0,00 · popularidad.
- FIGURA 2 · f2_tiempo_memoria_top_k.png; resaltar el último tamaño (17.978) en ambos paneles.

**TEXTO**

> El recomendador mide qué tan parecidas son dos películas con la similitud del coseno entre sus vectores, y la combina con la nota ponderada que explicó Daniela. Probamos 36 combinaciones de pesos con 2.000 consultas de entrenamiento y elegimos la que maximizaba el más débil de los tres criterios: la mitad del peso para la similitud, la otra mitad para la calidad y cero para la popularidad. Con ella, el criterio más débil, la coincidencia de idioma, llegó a 81,3 por ciento. Esa elección no se reajustó con la prueba.

> También comparamos cuatro formas de obtener las diez mejores recomendaciones. Lo ideal es separarlas sin ordenar todo el catálogo, y eso hace argpartition.

> *[PAUSA 7 s · figura 2; señalar el último tamaño en ambos paneles]*

> El gráfico separa el tiempo de la memoria, porque ganar en una no significa ganar en la otra. Con 17.978 películas, la selección vectorizada con argpartition tardó 0,10 milisegundos y ordenar todo tardó 1,35. En memoria, el montículo usó 0,017 megabytes y ordenar todo, 0,49. Son medidas del paso que elige el top diez, en nuestro computador; no son el tiempo del recomendador completo. Ahora Juan Pablo vuelve a la pregunta inicial: ¿qué tan buenas fueron las recomendaciones?

## Parte 4 · Juan Pablo González — Resultados, límites y cierre

**Tiempo:** 5:10–7:15 · **Palabras:** 262 · **Lectura estimada:** 2:01

**PANTALLA**

- FIGURA 3 · f3_evaluacion_azar_similitud_hibrido.png completa; resaltar primero género, luego idioma y al final votos.
- Texto en pantalla (5 s): «Misma comparación sobre las 3.596 consultas de prueba · IC 95 % por bootstrap».
- Dos cifras grandes: inglés 98,9 % vs otros idiomas 56,5 % (coincidencia de idioma); híbrido 21 % del catálogo, 16,5 % en diez títulos.
- Captura lista (no correr código): Parasite → solo similitud: Sunny; híbrido: The Handmaiden.
- Cierre: las tres conclusiones en una línea cada una + «Gracias».

**TEXTO**

> Comparamos tres alternativas con las tres medidas de la Fase 1: el azar, solo similitud y el híbrido. En género, el híbrido llega al 99,0 por ciento frente al 41,8 del azar; con solo similitud ya teníamos 99,6, así que prácticamente lo conserva. En idioma, el híbrido logra 81,4 frente al 36,6 del azar, pero queda bajo el 95,3 de solo similitud.

> *[PAUSA 8 s · figura 3; señalar el grupo de respaldo de votos]*

> La ganancia grande está en el respaldo de votos: con solo similitud, el 15,6 por ciento de las recomendaciones alcanzaba los 428 votos; con el híbrido, el 80. Tras la retroalimentación de la Fase 3, repetimos la comparación con las 3.596 consultas de prueba y un bootstrap por consulta: la ventaja sobre el azar es positiva en los tres criterios y ningún intervalo incluye el cero.

> Pero el híbrido tiene costos. Con consultas en inglés, el 98,9 por ciento de las recomendaciones coincide en idioma; en los demás idiomas, solo el 56,5. Y en las consultas de prueba recomienda apenas el 21 por ciento del catálogo: diez películas reúnen el 16,5 por ciento de todas sus apariciones.

> Un caso: para Parasite, el primer resultado pasó de Sunny a The Handmaiden. Eso muestra que cambia el orden, no que una persona lo prefiera. Nuestras medidas son indirectas: para medir satisfacción haría falta una prueba con usuarios. Si el idioma fuera un requisito estricto, el siguiente paso sería probar un filtro explícito y volver a medir. En síntesis, el híbrido supera al azar en los tres criterios y gana respaldo de votos a cambio de coincidencia de idioma y de diversidad. Gracias.

## Cifras del guion y su fuente

Todo número que se dice sale de un archivo del repositorio. Si una cifra cambia, se corrige aquí y en el informe.

| Se dice | Valor exacto | Fuente |
| --- | --- | --- |
| 17.978 películas, 2010–2025 | 17.978 | `data/raw/movies_raw.csv`; F4, capítulo 2 |
| 14.382 de entrenamiento y 3.596 de prueba, semilla 42 | 14.382 + 3.596; 42 | `data/processed/parametros_f3.json` |
| Azar de F1: 41,8 · 36,6 · 25 | 41,8 % · 36,6 % · 25,0 % | `F3/results/evaluacion_recomendador.csv` (columna de línea base); F1, sección 3 |
| 428 votos, percentil 75 | P75 = 427,75 | `F4/figuras/apoyo_puntos_5_7/hallazgos_apoyo.csv` |
| Menos de 100 votos: 6.243 películas, 0,94 → 0,13 | 6.243; 0,941 → 0,134 | `docs/hallazgos_f4.csv` (figura 1) |
| 5.000 votos o más: 0,65 → 0,63 | 576 películas; 0,651 → 0,626 | `docs/hallazgos_f4.csv` (figura 1) |
| Promedio general 6,33 y 421 votos de referencia | C = 6,327; m = 421 | `data/processed/parametros_f3.json` |
| 36 combinaciones, 2.000 consultas de entrenamiento | 36; 2.000 | `F3/results/rejilla_pesos.csv`; `parametros_f3.json` (regla de elección) |
| Pesos 0,50 / 0,50 / 0 y criterio más débil 81,3 % | peor criterio 81,26 % (idioma) | `F3/results/rejilla_pesos.csv`; `docs/cifras_f4.csv` |
| argpartition 0,10 ms; ordenar todo 1,35 ms | 0,097 ms; 1,35 ms (n = 17.978) | `docs/hallazgos_f4.csv` (figura 2); `F3/results/mediciones.csv` |
| Memoria: montículo 0,017; ordenar todo 0,49 | 0,017 y 0,488 MiB | `docs/hallazgos_f4.csv` (figura 2). Se dice «megabytes» por simplicidad; la unidad medida es MiB. |
| Género 99,0 vs 41,8; similitud 99,6 | 99,0 · 41,8 · 99,6 % | `docs/hallazgos_f4.csv` (figura 3) |
| Idioma 81,4 vs 36,6; similitud 95,3 | 81,4 · 36,6 · 95,3 % | `docs/hallazgos_f4.csv` (figura 3) |
| Votos: 15,6 → 80 | 15,6 % → 80,0 % | `docs/hallazgos_f4.csv` (figura 3) |
| Ningún intervalo incluye el cero | diferencias +56,34 · +44,68 · +55,04 pp; IC 95 % todos positivos | `docs/cifras_f4.csv`; F4, capítulo 8 |
| Inglés 98,9 vs otros idiomas 56,5 | 98,85 % (2.109 consultas) · 56,53 % (1.487) | `docs/cifras_f4.csv`; F4, capítulo 9 |
| 21 % del catálogo; diez películas reúnen 16,5 % | 20,99 % · 16,52 % | `docs/cifras_f4.csv`; F4, capítulo 10 |
| Parasite: Sunny → The Handmaiden | primer resultado de cada método | F4, capítulo 11 (salida del caso) |

## Lo que no se debe afirmar

- Que el híbrido «gusta más» o mejora la satisfacción: las tres medidas (género, idioma, votos) son indirectas.
- Que los tiempos valen para cualquier computador o para el recomendador completo: son del paso que elige el top 10.
- Que el azar de F1 y las 3.596 consultas son el mismo experimento: la línea de F1 no está emparejada con esas consultas (el capítulo 8 repite el azar sobre ellas y da 42,6 · 36,7 · 25,0 %, casi igual).
- Que 428 y 421 son lo mismo: 428 es el corte de evaluación; 421 es el parámetro de la nota ponderada.

## Antes de grabar

- [ ] Confirmar que las tres figuras y las cifras del video son las mismas del informe y del cuaderno (`F4/figuras/`, `docs/hallazgos_f4.csv`).
- [ ] Revisar la retroalimentación del docente en Canvas y, si corresponde, decir en el video qué cambió (observación → cambio).
- [ ] Cada integrante ensaya su parte con cronómetro, con la figura a la vista.
- [ ] Verificar la duración final en Canvas Studio: entre 5:00 y 8:00.
