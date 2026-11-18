"""Medición de tiempo y memoria de una función.

Módulo del proyecto MCDI500 - Grupo 4, adaptado del proyecto modelo de la Semana 2.
Lo usa el cuaderno F3/F3_NucleoAlgoritmico_TMDB.ipynb.
"""

import time
import timeit
import tracemalloc

import pandas as pd


def medir(funcion, *args, **kwargs):
    """Ejecuta la función y devuelve resultado, segundos y memoria pico en MB.

    *args recoge los argumentos posicionales en una tupla y **kwargs los
    argumentos con nombre en un diccionario. El asterisco es lo que hace el
    trabajo; los nombres args y kwargs son solo convención.
    """
    tracemalloc.start()
    try:
        inicio = time.perf_counter()
        resultado = funcion(*args, **kwargs)
        transcurrido = time.perf_counter() - inicio
        _, pico = tracemalloc.get_traced_memory()
    finally:
        # Si la función falla, el rastreo no debe quedar activo: inflaría la siguiente medición
        tracemalloc.stop()
    return resultado, transcurrido, pico / 1024 / 1024


def tiempo_minimo(funcion, *args, repeticiones=7, **kwargs):
    """Devuelve el resultado de la función y su menor tiempo en segundos entre varias ejecuciones.

    Sigue el protocolo de la guía de la Sumativa 2: timeit.repeat con
    number=1 y se conserva el mínimo, que es la ejecución con menos
    interferencia de otros procesos (el resto solo suma ruido, no información).
    """
    if repeticiones < 1:
        raise ValueError("tiempo_minimo: repeticiones debe ser al menos 1.")
    resultado = funcion(*args, **kwargs)
    tiempos = timeit.repeat(lambda: funcion(*args, **kwargs), number=1, repeat=repeticiones)
    return resultado, min(tiempos)


def comparar_versiones(versiones, entrada, iguales, repeticiones=7):
    """Mide tiempo (mínimo de varias ejecuciones) y memoria pico de varias versiones de un mismo algoritmo.

    versiones: diccionario nombre -> función de un argumento. Antes de medir se
    exige, con la función iguales(a, b), que todas den el mismo resultado que la
    primera: comparar algoritmos que responden distinto no tiene sentido.
    """
    if not versiones:
        raise ValueError("comparar_versiones: se necesita al menos una versión.")
    filas, referencia = [], None
    for nombre, funcion in versiones.items():
        resultado, segundos = tiempo_minimo(funcion, entrada, repeticiones=repeticiones)
        if referencia is None:
            referencia = resultado
        elif not iguales(referencia, resultado):
            raise AssertionError(f"comparar_versiones: '{nombre}' no da el mismo resultado que la primera versión.")
        _, _, memoria = medir(funcion, entrada)   # aparte: tracemalloc ralentiza
        filas.append({"versión": nombre, "tiempo_s": segundos, "memoria_pico_MB": memoria})
    return pd.DataFrame(filas)


def escalabilidad(versiones, tamaños, generar_entrada, iguales, repeticiones=7):
    """comparar_versiones para entradas de tamaño creciente, en formato largo (una fila por tamaño y versión)."""
    tablas = [comparar_versiones(versiones, generar_entrada(n), iguales, repeticiones).assign(n=n)
              for n in tamaños]
    return pd.concat(tablas, ignore_index=True)[["n", "versión", "tiempo_s", "memoria_pico_MB"]]
