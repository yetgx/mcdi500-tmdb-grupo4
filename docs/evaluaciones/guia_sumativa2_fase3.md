# Guía de la Sumativa 2 (Fase 3)

**Fuente:** anuncio de Canvas del docente Omar Salinas Silva, 13 de noviembre de 2026, «Balance de la Sumativa 1 y guía paso a paso para la Fase 3». Las figuras citadas (1 a 6) están en el adjunto de Canvas `MCDI500_Seccion1_Retroalimentacion_S1_y_Guia_Sumativa2.pdf`.
**Entrega:** miércoles 18 de noviembre de 2026, hasta las 23:59.

Se copia aquí para que todo el grupo trabaje con el mismo texto. La columna «En el proyecto» indica dónde se cumple cada punto.

## I. Retroalimentación general de la Sumativa 1 (todo el curso)

1. La Fase 3 no es «análisis»: es el núcleo algorítmico (diseño modular, orientación a objetos y medición de eficiencia).
2. El objetivo general debe responder la pregunta del proyecto; la limpieza es metodología, no objetivo.
3. Las dependencias declaran solo lo que el código importa, con versión fija.
4. El historial no debe concentrarse en el cierre: aportes de todos, una identidad por integrante.
5. Notebooks ejecutados completos y en orden, sin editar después de la última ejecución.
6. El informe debe coincidir con el repositorio (procedimientos, cifras y archivos).
7. Sin datos personales en el repositorio, ni siquiera en el historial.
8. Al menos cinco referencias APA 7 citadas en el texto del informe.

## II. Guía paso a paso

| Paso | Qué pide | Evidencia esperada | En el proyecto |
|---|---|---|---|
| 1. Ordenar el código en una sola versión | Trasladar las funciones de F2 a módulos en `src/` e importarlas desde los notebooks; eliminar la lógica duplicada | Un notebook F3 que importa el código en lugar de copiarlo | `src/preparacion.py`, `src/transformadores.py`, `src/pipeline.py` (#45, #48) |
| 2. Diseñar las clases donde corresponde | Clases solo para componentes que aprenden de los datos; lo demás, funciones. Mostrar encapsulamiento, herencia y polimorfismo con fragmentos de código | Clases justificadas y tabla de principios en el informe | `Transformador` y sus hijas, `RecomendadorHibrido` (#45, #49); F3 sección 2 |
| 3. Construir el pipeline y justificar los patrones | Un componente que recibe la lista de pasos y los aplica; explicar qué problema resuelve cada patrón usado | Pipeline ejecutable con una sola llamada y justificación de cada patrón | `ejecutar(datos)` (#48); *Strategy* (F3 sección 2) |
| 4. Verificar que el resultado no cambia | Comparar el resultado de F3 con el conjunto procesado de F2 con `assert` | Celda de comparación ejecutada sin errores | F3 sección 2.1 (#45, #50) |
| 5. Medir la eficiencia con rigor | Dos versiones de una operación real con el mismo resultado; tamaño real; mínimo de 7 repeticiones con `timeit`; memoria con `tracemalloc`; interpretar | Tabla de tiempo y memoria, comprobación de igualdad e interpretación | `src/medicion.py` (#47); F3 sección 7 (#50) |
| 6. Probar y validar | Caso normal, caso límite y excepción por componente, con tablas pequeñas; recursividad solo si hay un caso natural, o justificar el enfoque iterativo | Pruebas ejecutadas, idealmente en `tests/` con un solo comando | `tests/` (`python -m pytest`); F3 secciones 4 y 6 (#46) |
| 7. Documentar, revisar y entregar | Ramas y PR revisados por otro integrante; bitácora con motivo, alternativa descartada y efecto; informe; revisión desde un clon limpio; coherencia de cifras | Historial con aportes de todos y un informe que coincide con el repositorio | `docs/bitacora.md`; CI en Ubuntu, macOS y Windows; informe de la Sumativa 2 |

## III. Lista de verificación antes de entregar

1. El código vive en `src` y los notebooks lo importan, sin duplicarlo.
2. Las clases se justifican porque aprenden algo de los datos.
3. Los principios de orientación a objetos y los patrones están explicados con fragmentos del código.
4. El pipeline de la Fase 3 produce exactamente el mismo resultado que la Fase 2.
5. La medición de eficiencia compara dos versiones con resultados iguales, con tiempo, memoria e interpretación.
6. Hay pruebas de casos normales, límite y excepción.
7. El notebook F3 está ejecutado de principio a fin, con numeración continua.
8. El archivo de dependencias contiene solo librerías del proyecto, con versión fija.
9. Todos los integrantes tienen commits propios, integrados mediante pull request.
10. El repositorio no contiene datos personales, ni siquiera en el historial.
11. El informe tiene al menos cinco referencias APA 7 citadas en el texto.

## IV. Calendario propuesto por el docente

| Días | Trabajo |
|---|---|
| Jueves 12 y viernes 13 | Ordenar el código en `src` y repartir tareas (pasos 1 y 2) |
| Sábado 14 y domingo 15 | Clases, pipeline y equivalencia con la Fase 2 (pasos 3 y 4) |
| Lunes 16 | Medición de eficiencia y pruebas (pasos 5 y 6) |
| Martes 17 | Informe, bitácora y revisión cruzada (paso 7) |
| Miércoles 18 | Revisión desde un clon limpio y entrega |
