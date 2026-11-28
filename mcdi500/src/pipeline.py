"""Pipeline: encadena transformadores y los ejecuta en orden.

Módulo del proyecto MCDI500 - Grupo 4, adaptado del proyecto modelo de la Semana 2.
Lo usa el cuaderno F3/F3_NucleoAlgoritmico_TMDB.ipynb.
"""

import pandas as pd

from .preparacion import diccionario_procesado
from .transformadores import (CalidadPonderada, CerosComoAusentes, ConstructorSopa, DuracionPorGenero,
                              EscaladorMinMax, LogNaturalPlus1, Transformador)


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


# ---- Pipeline del proyecto TMDB ----------------------------------------------------

def pipeline_tmdb():
    """Los 8 pasos de la Fase 2, en orden, como transformadores sin ajustar."""
    return Pipeline([
        DuracionPorGenero(),                                       # runtime_clean
        CerosComoAusentes("budget", "budget_clean"),
        CerosComoAusentes("revenue", "revenue_clean"),
        ConstructorSopa(),                                         # genres/companies/lang_clean y metadata_soup
        CalidadPonderada(),                                        # weighted_rating (aprende C y m)
        LogNaturalPlus1("popularity", "popularity_log"),
        EscaladorMinMax("weighted_rating", "score_quality_norm"),
        EscaladorMinMax("popularity_log", "score_popularity_norm"),
    ])


def ejecutar(datos, ajustar_con=None):
    """Prepara el conjunto con una sola llamada y devuelve las columnas de F2, en su orden.

    Los parámetros se aprenden con `ajustar_con` (por defecto, los mismos
    datos, como hizo F2 sobre el catálogo completo) y se aplican a `datos`.
    """
    columnas = diccionario_procesado()["columna"].tolist()
    pipe = pipeline_tmdb().ajustar(datos if ajustar_con is None else ajustar_con)
    return pipe.transformar(datos)[columnas].reset_index(drop=True)
