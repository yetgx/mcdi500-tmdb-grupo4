"""Núcleo del recomendador híbrido: similitud del coseno ponderada por calidad y popularidad.

Módulo del proyecto MCDI500 - Grupo 4. Lo usa el cuaderno F3/F3_NucleoAlgoritmico_TMDB.ipynb.

Para una película consultada i y cada película j del catálogo:

    puntaje(i, j) = w_s · coseno(i, j) + w_c · score_quality_norm(j) + w_p · score_popularity_norm(j)

con w_s + w_c + w_p = 1. El coseno compara las sopas de metadatos (géneros,
productoras e idioma) vectorizadas con CountVectorizer; la calidad es el
Weighted Rating escalado y la popularidad es log1p(popularity) escalada, ambas
de la Fase 2. Las tres van en [0, 1], así que los pesos se leen como la
importancia relativa de cada componente.
"""

from collections import Counter
import math

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize

from .recursividad import top_k_vectorizado

COLUMNAS_CATALOGO = ("movie_id", "title", "metadata_soup", "score_quality_norm", "score_popularity_norm")


class RecomendadorHibrido:
    """Recomienda las n películas de mayor puntaje híbrido, excluida la consultada.

    Sigue el mismo contrato que los transformadores: ajustar() aprende el
    vocabulario y la matriz del catálogo; recomendar() exige haber ajustado.
    Los pesos por defecto son los que elige el cuaderno F3 (sección 5): los
    que maximizan el peor de los tres criterios de evaluación en entrenamiento.
    """

    def __init__(self, peso_similitud=0.5, peso_calidad=0.5, peso_popularidad=0.0, n=10):
        pesos = (peso_similitud, peso_calidad, peso_popularidad)
        if any(p < 0 for p in pesos) or not math.isclose(sum(pesos), 1.0):
            raise ValueError(f"RecomendadorHibrido: los pesos deben ser no negativos y sumar 1; se recibió {pesos}.")
        if not isinstance(n, int) or n < 1:
            raise ValueError(f"RecomendadorHibrido: n debe ser un entero positivo y se recibió {n!r}.")
        self._pesos = {"similitud": peso_similitud, "calidad": peso_calidad, "popularidad": peso_popularidad}
        self._n = n
        self._ajustado = False

    @property
    def pesos(self):
        return dict(self._pesos)

    @property
    def n(self):
        return self._n

    @property
    def vectorizador(self):
        self._exigir_ajuste()
        return self._vectorizador

    @property
    def matriz(self):
        """Matriz dispersa del catálogo con filas de norma 1 (CSR)."""
        self._exigir_ajuste()
        return self._matriz

    def ajustar(self, catalogo, vectorizador=None):
        """Vectoriza el catálogo. Con un vectorizador ya ajustado (p. ej. en entrenamiento) solo lo aplica."""
        faltantes = [c for c in COLUMNAS_CATALOGO if c not in catalogo.columns]
        if faltantes:
            raise KeyError(f"RecomendadorHibrido: faltan columnas en el catálogo {faltantes}.")
        if len(catalogo) < 2:
            raise ValueError("RecomendadorHibrido: el catálogo necesita al menos dos películas.")
        if catalogo["movie_id"].duplicated().any():
            raise ValueError("RecomendadorHibrido: movie_id debe ser único en el catálogo.")
        puntuaciones = catalogo[["score_quality_norm", "score_popularity_norm"]]
        if puntuaciones.isna().any().any():
            raise ValueError("RecomendadorHibrido: las puntuaciones de calidad y popularidad no admiten nulos.")

        self._catalogo = catalogo[list(COLUMNAS_CATALOGO)].reset_index(drop=True)
        if vectorizador is None:
            vectorizador = CountVectorizer().fit(self._catalogo["metadata_soup"])
        self._vectorizador = vectorizador
        # Con filas de norma 1, el producto punto entre dos filas ES el coseno
        self._matriz = normalize(vectorizador.transform(self._catalogo["metadata_soup"]), norm="l2").tocsr()
        self._calidad = self._catalogo["score_quality_norm"].to_numpy(dtype=float)
        self._popularidad = self._catalogo["score_popularity_norm"].to_numpy(dtype=float)
        self._posicion = pd.Series(self._catalogo.index, index=self._catalogo["movie_id"])
        self._ajustado = True
        return self

    def _exigir_ajuste(self):
        if not self._ajustado:
            raise RuntimeError("RecomendadorHibrido: hay que ajustar antes de recomendar.")

    def posicion(self, movie_id):
        """Fila del catálogo que corresponde a un movie_id."""
        self._exigir_ajuste()
        if movie_id not in self._posicion.index:
            raise KeyError(f"RecomendadorHibrido: movie_id {movie_id!r} no está en el catálogo.")
        return int(self._posicion[movie_id])

    def similitudes(self, posiciones):
        """Coseno de cada consulta contra todo el catálogo: matriz densa (consultas × catálogo)."""
        self._exigir_ajuste()
        return (self._matriz[np.atleast_1d(posiciones)] @ self._matriz.T).toarray()

    def puntajes(self, posiciones):
        """Puntaje híbrido de cada consulta contra todo el catálogo."""
        p = self._pesos
        return (p["similitud"] * self.similitudes(posiciones)
                + p["calidad"] * self._calidad + p["popularidad"] * self._popularidad)

    def recomendar_posiciones(self, posiciones, seleccionar=top_k_vectorizado, bloque=500):
        """Las n mejores posiciones para cada consulta (una fila por consulta).

        Procesa por bloques para no materializar la matriz completa de
        similitudes: 500 consultas × 17.978 películas son ~72 MB en float64.
        """
        posiciones = np.atleast_1d(np.asarray(posiciones, dtype=np.int64))
        resultado = np.empty((len(posiciones), self._n), dtype=np.int64)
        for inicio in range(0, len(posiciones), bloque):
            lote = posiciones[inicio:inicio + bloque]
            puntajes = self.puntajes(lote)
            puntajes[np.arange(len(lote)), lote] = -np.inf   # una película no se recomienda a sí misma
            for fila, vector in enumerate(puntajes):
                resultado[inicio + fila] = seleccionar(vector, self._n)
        return resultado

    def recomendar(self, movie_id):
        """Tabla con las n recomendaciones de una película y cada componente de su puntaje."""
        i = self.posicion(movie_id)
        elegidas = self.recomendar_posiciones([i])[0]
        similitud = self.similitudes([i])[0, elegidas]
        tabla = self._catalogo.loc[elegidas, ["movie_id", "title", "metadata_soup"]].copy()
        tabla["similitud"] = similitud
        tabla["calidad"] = self._calidad[elegidas]
        tabla["popularidad"] = self._popularidad[elegidas]
        tabla["puntaje"] = self.puntajes([i])[0, elegidas]
        return tabla.reset_index(drop=True)

    def __repr__(self):
        estado = "ajustado" if self._ajustado else "sin ajustar"
        pesos = ", ".join(f"{k}={v:g}" for k, v in self._pesos.items())
        return f"RecomendadorHibrido({pesos}, n={self._n}, {estado})"


# ---- Versión con bucles, para validar y comparar la vectorizada ------------------

def similitud_coseno_bucle(consulta, catalogo, analizador, vocabulario=None):
    """Coseno de una sopa contra cada sopa del catálogo, con contadores de tokens y bucles de Python.

    Usa el mismo analizador que CountVectorizer, para que los tokens coincidan,
    y con `vocabulario` descarta los tokens que el vectorizador no aprendió.
    """
    def contar(texto):
        tokens = analizador(texto)
        return Counter(t for t in tokens if vocabulario is None or t in vocabulario)

    a = contar(consulta)
    norma_a = math.sqrt(sum(v * v for v in a.values()))
    resultado = []
    for texto in catalogo:
        b = contar(texto)
        norma_b = math.sqrt(sum(v * v for v in b.values()))
        producto = sum(conteo * b[token] for token, conteo in a.items())
        resultado.append(producto / (norma_a * norma_b) if norma_a and norma_b else 0.0)
    return np.asarray(resultado)


# ---- Criterio de evaluación de la Fase 1 ----------------------------------------------

def evaluar_recomendaciones(consultas, recomendadas, generos, idiomas, votos, umbral_votos):
    """Proporción de recomendaciones que comparten género, que tienen el mismo idioma y con votos ≥ umbral.

    consultas: posiciones consultadas (m,); recomendadas: posiciones recomendadas (m, n).
    generos: un conjunto de géneros por película; idiomas y votos, un valor por película.
    Es el criterio de F1 (sección 3), que se compara con la línea base aleatoria.
    """
    consultas = np.asarray(consultas)
    recomendadas = np.asarray(recomendadas)
    if recomendadas.ndim != 2 or len(recomendadas) != len(consultas):
        raise ValueError("evaluar_recomendaciones: se espera una fila de recomendaciones por consulta.")
    generos, idiomas, votos = np.asarray(generos, dtype=object), np.asarray(idiomas), np.asarray(votos)
    comparte = [[bool(generos[c] & generos[r]) for r in fila] for c, fila in zip(consultas, recomendadas)]
    return pd.Series({
        "Coherencia de género": float(np.mean(comparte)),
        "Coherencia de idioma": float(np.mean(idiomas[recomendadas] == idiomas[consultas][:, None])),
        f"Respaldo de votos (>= {umbral_votos:.0f})": float(np.mean(votos[recomendadas] >= umbral_votos)),
    })
