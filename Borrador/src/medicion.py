"""Medición controlada de tiempo Python y pico de asignaciones rastreadas."""
import time
import tracemalloc
import statistics

def medir(funcion, *args, repeticiones=5, **kwargs):
    """Retorna resultado, mediana temporal, pico rastreado y tiempos individuales.

    La memoria de tracemalloc no equivale a RSS ni cubre necesariamente allocations C.
    """
    if repeticiones < 2:
        raise ValueError("Se requieren al menos dos repeticiones")
    tiempos=[]; picos=[]; resultado=None
    funcion(*args, **kwargs)  # calentamiento: no se mide
    for _ in range(repeticiones):
        tracemalloc.start()
        try:
            t0=time.perf_counter()
            resultado=funcion(*args, **kwargs)
            tiempos.append(time.perf_counter()-t0)
            picos.append(tracemalloc.get_traced_memory()[1]/(1024*1024))
        finally:
            tracemalloc.stop()
    return resultado, statistics.median(tiempos), max(picos), tiempos


import pandas as pd


class AnalizadorRendimiento:
    """
    Analiza resultados de rendimiento de distintas
    implementaciones sobre tamaños crecientes.

    Recibe el DataFrame generado por el benchmark.
    No modifica los datos originales.
    """

    COLUMNAS = (
        "n",
        "algoritmo",
        "segundos",
        "memoria_MB_trazada"
    )

    def __init__(self, resultados):
        self._validar(resultados)
        self._resultados = resultados.copy()

    @classmethod
    def _validar(cls, datos):
        """Verifica la estructura y coherencia del benchmark."""

        if not isinstance(datos, pd.DataFrame):
            raise TypeError("Se requiere un DataFrame de pandas.")

        faltantes = set(cls.COLUMNAS) - set(datos.columns)

        if faltantes:
            raise ValueError(
                f"Columnas faltantes: {sorted(faltantes)}"
            )

        if datos.empty:
            raise ValueError("El benchmark está vacío.")

        if datos.duplicated(["n", "algoritmo"]).any():
            raise ValueError(
                "Existen mediciones duplicadas para n y algoritmo."
            )

        if datos[list(("segundos", "memoria_MB_trazada"))].isna().any().any():
            raise ValueError("Hay mediciones ausentes.")

        if not (
            (datos["n"] > 0).all()
            and (datos["segundos"] > 0).all()
            and (datos["memoria_MB_trazada"] >= 0).all()
        ):
            raise ValueError("Se encontraron mediciones inválidas.")

    @property
    def resultados(self):
        """Devuelve una copia defensiva de las mediciones."""
        return self._resultados.copy()

    def tabla_comparativa(self):
        """Compara algoritmos en una fila por tamaño."""

        tabla = self._resultados.pivot(
            index="n",
            columns="algoritmo",
            values=["segundos", "memoria_MB_trazada"]
        )

        return tabla.sort_index()

    def calcular_aceleracion(
        self,
        referencia="iterrows",
        alternativa="columnas"
    ):
        """
        Calcula cuántas veces es más rápida
        la alternativa respecto de la referencia.
        """

        tabla = self.tabla_comparativa()["segundos"]

        if referencia not in tabla or alternativa not in tabla:
            raise ValueError("Algoritmos no encontrados.")

        if tabla[[referencia, alternativa]].isna().any().any():
            raise ValueError(
                "Faltan mediciones comparables para algunos tamaños."
            )

        return (
            tabla[referencia] / tabla[alternativa]
        ).rename("aceleracion_x")

    def relacion_memoria(
        self,
        referencia="iterrows",
        alternativa="columnas"
    ):
        """Calcula la razón de memoria entre implementaciones."""

        tabla = self.tabla_comparativa()["memoria_MB_trazada"]

        if referencia not in tabla or alternativa not in tabla:
            raise ValueError("Algoritmos no encontrados.")

        if tabla[[referencia, alternativa]].isna().any().any():
            raise ValueError("Faltan mediciones comparables.")

        if (tabla[referencia] <= 0).any():
            raise ValueError(
                "La memoria de referencia debe ser positiva."
            )

        return (
            tabla[alternativa] / tabla[referencia]
        ).rename("relacion_memoria_x")
