"""Pipeline: encadena transformadores y los ejecuta en orden.

Módulo del proyecto MCDI500 - Grupo 4, adaptado del proyecto modelo de la Semana 2.
Lo usa el cuaderno F3/F3_NucleoAlgoritmico_TMDB.ipynb.
"""

import pandas as pd

from .transformadores import Transformador


class Pipeline:
    """Encadena transformadores y los ejecuta en orden."""

    def __init__(self, pasos=None):
        self._pasos = list(pasos) if pasos else []
        self._ajustado = False

    def agregar(self, transformador):
        if not isinstance(transformador, Transformador):
            raise TypeError(
                f"Se esperaba un Transformador y se recibió {type(transformador).__name__}."
            )
        self._pasos.append(transformador)
        return self

    def ajustar(self, df):
        """Aprende los parámetros de cada paso SOLO con estos datos."""
        intermedio = df.copy()
        for paso in self._pasos:
            intermedio = paso.ajustar_transformar(intermedio)
        self._ajustado = True
        return self

    def transformar(self, df):
        if not self._ajustado:
            raise RuntimeError("Pipeline: hay que ajustar antes de transformar.")
        resultado = df.copy()
        for paso in self._pasos:
            resultado = paso.transformar(resultado)
        return resultado

    def pasos_ejecutados(self):
        """Devuelve los pasos, para poder registrar sus parámetros aprendidos."""
        return tuple(self._pasos)

    def resumen(self):
        return pd.DataFrame([
            {"orden": i, "paso": p.nombre, "clase": type(p).__name__}
            for i, p in enumerate(self._pasos, start=1)
        ])

    def __len__(self):
        return len(self._pasos)

    def __repr__(self):
        estado = "ajustado" if self._ajustado else "sin ajustar"
        return f"Pipeline({len(self._pasos)} pasos, {estado})"
