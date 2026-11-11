# Bitácora de decisiones técnicas

Registro de las decisiones del proyecto con su motivo y sus cifras, tomado de la sección «Por qué» de cada pull request integrado a `main`. Se actualiza al cerrar cada fase. El número entre paréntesis es el PR donde se tomó la decisión; el detalle completo y la discusión están en GitHub.

## Fase 1 — Entorno, repositorio y exploración (4 a 9 de noviembre de 2026)

- **Flujo de trabajo único: rama propia + PR revisado** (#1). Para que todos los integrantes suban cambios de la misma forma sin depender de saber Git; la guía queda en `docs/GUIA_SUBIR_CAMBIOS.md`.
- **Verificación del entorno antes de analizar** (#5). Se comprueba que las herramientas se ejecutan y que la configuración sirve para el proyecto antes de empezar con los datos.
- **Dependencias fijadas en `requirements.txt`** (#9). Todos instalan las mismas versiones que se usaron en el desarrollo.
- **Plantilla común del informe** (#10). Base compartida para redactar la Sumativa 1: diccionario de variables, hallazgos de calidad (ceros en `budget` y `revenue`, `status` y `adult` constantes) y campos por completar.
- **Mapa conceptual y gráficos nuevos en F1** (#11, #23). Se usan para reflexionar sobre la problemática con la combinación de variables disponible y dejar trazabilidad de por qué se eligió, y de los desafíos que se abordarán en el preprocesamiento.

## Fase 2 — Preparación de datos (8 a 11 de noviembre de 2026)

- **`requirements.txt` en UTF-8** (#21). Venía de `pip freeze` redirigido desde PowerShell (UTF-16): GitHub lo mostraba como binario y los cambios no se podían revisar línea por línea; además rompía `pip install -r` en otros equipos.
- **Productoras sin `unknown` y sin puntuación en la sopa de metadatos** (#19). Las 494 películas sin productora compartían el token `unknown` y el recomendador las veía como parecidas sin razón temática; ahora quedan vacías. 1.309 productoras tienen puntuación (`Warner Bros.`) y el tokenizador las partía; ahora `Warner Bros. Pictures` → `warnerbrospictures`.
- **`CountVectorizer` con vocabulario completo** (#22). `stop_words='english'` borraba los códigos de idioma `it`, `de`, `no`, `he`, `is`, `am` (1.253 películas perdían su idioma) y `max_features=5000` dejaba al 50,6 % de las películas sin al menos un token. Memoria real medida: 1,27 MB en formato disperso frente a 1,91 GB denso.
- **Weighted Rating con umbral mínimo de votos justificado visualmente** (#27). Se explica qué logra la función y se muestra con un diagrama de dispersión y un KDE por qué se fija ese umbral.
- **`log1p` antes de `MinMaxScaler` en `popularity`** (#18). Con el escalado directo el 93,4 % de las películas queda bajo 0,05 (asimetría 9,16); con `log1p` baja a 1,3 % y la media pasa de 0,02 a 0,20. La transformación es monótona y no cambia el orden. `weighted_rating` es casi simétrica y se escala directo.
- **Celda de verificación del entorno en F1 y F2** (#29). Compara cada librería con `requirements.txt` (marca `DIFIERE` sin detener la ejecución) y registra la rama y el commit para vincular cada resultado con una versión del repositorio.
- **Comparar alternativas antes de imputar** (#29). Toda imputación central reduce la variabilidad: en `budget` la media o la mediana bajan la desviación estándar un 44,6 % / 42,0 %, en `revenue` un 38,4 % / 36,4 %, en `runtime` solo un 0,13 % / 0,06 %.
  - `runtime` (46 ceros, 0,26 %) → mediana por género principal, la que más conserva la variabilidad. Descartado: eliminar filas.
  - `budget` (69,3 % de ceros) y `revenue` (62,1 %) → `NaN` sin imputar; un valor central inventaría el dato de más de 11.000 películas. El recomendador no usa estas columnas.
- **Los atípicos no se eliminan** (#29). `vote_count` (asimetría 7,0) y `popularity` (9,16) son películas realmente muy votadas; se controlan con el Weighted Rating y con `log1p`.
- **Validación con `assert` en lugar de revisión visual** (#29). 25 comprobaciones que detienen el notebook donde nace el problema, con casos límite y la excepción esperada de `clean_genres(NaN)`, que justifica imputar antes de limpiar.
- **Exportar CSV + `.npz`** (#29). F3 lee el resultado sin repetir el pipeline; la matriz se guarda dispersa (CSR, 0,16 MB) y la relectura se verifica con `assert`.
- **F1 no transforma el conjunto** (#28). Las interpretaciones y la conclusión se reescribieron; las conversiones de fecha y los filtros de F1 se hacen sobre copias (`popularidad_años`, `df_runtime`) y la limpieza queda en F2.

## Fase 3 — Núcleo algorítmico (iniciada)

- **Código en módulos (`src/`) y no en celdas sueltas** (#24). El cuaderno comprueba con `assert_frame_equal` que el pipeline con clases reproduce la Fase 2, valida caso normal, límite y excepciones, y mide tiempo y memoria por separado porque `tracemalloc` ralentiza el tiempo. La sopa por columnas es ~8× más rápida que `iterrows`, pero usa más memoria pico (12,6 MB frente a 4,8 MB).

## Repositorio y reproducibilidad

- **`.mailmap` en lugar de reescribir el historial** (#30). El historial mostraba 8 identidades para 4 personas; `.mailmap` las agrupa y `git shortlog -sne` da una línea por integrante. Descartado: `git filter-repo`, que cambiaría todos los hashes y rompería los PR abiertos.
- **Práctica del curso fuera de `F1/`** (#30). Es el cuaderno de ejercicios de la asignatura, no un entregable; se movió a `docs/practica/` con `git mv` para conservar su historial.
- **Informe regenerado desde un script, no reescrito** (#31). Se cambian solo los bloques desactualizados y las cifras salen de los notebooks ejecutados y del repositorio, no de memoria.
- **Cuaderno de F1 renombrado a `F1_Definicion.ipynb`** (#32). Sigue el patrón de nombre que pide la guía y el de F2 y F3; se hizo después de integrar #28 para no crear un conflicto en el notebook de Juan Pablo.
- **Kernel genérico `python3` en los notebooks** (#33). El kernel `mcdi500-tmdb-grupo4` solo existía en un equipo y `nbconvert --execute` fallaba con `NoSuchKernel` en cualquier otro. Descartado: pedir a cada integrante que registre un kernel con ese nombre.
- **Las ramas se borran al integrar el PR** (configuración del repositorio, 11 de noviembre). Evita acumular ramas ya mergeadas.
