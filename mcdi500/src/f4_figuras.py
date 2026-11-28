"""Fase 4 TMDB: las tres figuras principales de la entrega, con su hallazgo y evidencia.

Cada función devuelve (figura, hallazgo) y el hallazgo tiene las columnas que exige
persistir() en src/f4_puntos_5_7.py: figura, hallazgo y evidencia. Las cifras salen
de los artefactos de F3; ninguna se escribe a mano. No modifica F1-F3.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import numpy as np
import pandas as pd

from .f4_puntos_5_7 import _es

TRAMOS_VOTOS = (0, 100, 200, 428, 1000, 5000, np.inf)
ETIQUETAS_TRAMOS = ("50–99", "100–199", "200–427", "428–999", "1.000–4.999", "≥ 5.000")
ORDEN_TOP_K = ("ordenar todo (estructurado)", "divide y vencerás (recursivo)",
               "montículo (iterativo)", "argpartition (vectorizado)")
COLORES_TOP_K = dict(zip(ORDEN_TOP_K, ("#738DA3", "#D98C3F", "#4E8C71", "#A93238")))
COLORES_EVALUACION = {"Línea base aleatoria (F1)": "#8BA3B3", "Solo similitud": "#D98C3F",
                      "Híbrido (pesos elegidos)": "#A93238"}
TAMANO = (12, 6.75)   # 16:9: sirve para el informe y para el video


def cargar_resultados_f3(raiz):
    """Mediciones y evaluación de F3; si falta un archivo, indica qué fase ejecutar."""
    raiz = Path(raiz)
    rutas = {"mediciones": raiz / "F3/results/mediciones.csv",
             "evaluacion": raiz / "F3/results/evaluacion_recomendador.csv"}
    for ruta in rutas.values():
        if not ruta.is_file():
            raise FileNotFoundError(f"Falta {ruta.relative_to(raiz).as_posix()}; ejecutar F3.")
    return pd.read_csv(rutas["mediciones"]), pd.read_csv(rutas["evaluacion"], index_col=0)


def _fuente(figura, texto):
    """Nota al pie en varias líneas, para que no se corte en el borde de la figura."""
    figura.supxlabel(textwrap.fill(texto, 150), fontsize=8)


def _exigir(tabla, columnas, nombre):
    faltan = [c for c in columnas if c not in tabla.columns]
    if faltan:
        raise ValueError(f"{nombre} no tiene las columnas {faltan}.")


def figura_nota_ponderada(catalogo, parametros):
    """Figura 1: dispersión de la nota original y de la ponderada según los votos de la película."""
    from matplotlib import pyplot as plt

    _exigir(catalogo, ["vote_average", "vote_count", "weighted_rating"], "El catálogo")
    calidad = parametros["pasos"]["CalidadPonderada(vote_average)"]
    c, m = float(calidad["C"]), float(calidad["m"])
    datos = catalogo.loc[:, ["vote_average", "vote_count", "weighted_rating"]].dropna()
    if datos["vote_count"].lt(0).any() or datos.empty:
        raise ValueError("Se necesitan votos no negativos y al menos una película.")
    tramo = pd.cut(datos["vote_count"], list(TRAMOS_VOTOS), right=False, labels=list(ETIQUETAS_TRAMOS))
    resumen = datos.groupby(tramo, observed=False).agg(
        n=("vote_count", "size"), original=("vote_average", "std"), ponderada=("weighted_rating", "std"))
    if resumen["n"].eq(0).any():
        raise ValueError("Hay tramos de votos sin películas; revisar los cortes.")

    figura, eje = plt.subplots(figsize=TAMANO, layout="constrained")
    x = np.arange(len(resumen))
    ancho = 0.38
    barras = [eje.bar(x - ancho / 2, resumen["original"], ancho, color="#8BA3B3", label="Nota original (vote_average)"),
              eje.bar(x + ancho / 2, resumen["ponderada"], ancho, color="#A93238", label=f"Nota ponderada (m = {_es(m)})")]
    for grupo in barras:
        eje.bar_label(grupo, labels=[_es(v, 2) for v in grupo.datavalues], padding=3, fontsize=10)
    eje.set_xticks(x, [f"{t}\nn = {_es(n)}" for t, n in zip(resumen.index, resumen["n"])])
    eje.set(xlabel="Votos de la película (n = películas del tramo)", ylabel="Desviación estándar de la nota (puntos de 0 a 10)",
            ylim=(0, resumen[["original", "ponderada"]].to_numpy().max() * 1.18))
    eje.grid(axis="y", alpha=0.2)
    eje.spines[["top", "right"]].set_visible(False)
    eje.legend(frameon=False, loc="upper right")
    titulo = "La nota ponderada acerca a la media las películas con pocos votos"
    figura.suptitle(titulo, fontweight="bold", fontsize=15)
    _fuente(figura, f"Fuente: particiones de F3 ({_es(len(datos))} películas). Ponderada = (v·R + m·C) / (v + m), con C = {_es(c, 3)} "
                    "y m = 421 estimados en entrenamiento. El corte de 428 votos de la evaluación es otro parámetro.")
    primero, ultimo = resumen.iloc[0], resumen.iloc[-1]
    evidencia = (f"Con menos de 100 votos ({_es(primero['n'])} películas), la desviación estándar baja de {_es(primero['original'], 3)} "
                 f"a {_es(primero['ponderada'], 3)}; con 5.000 votos o más ({_es(ultimo['n'])} películas), de {_es(ultimo['original'], 3)} "
                 f"a {_es(ultimo['ponderada'], 3)}. Con más votos, la nota propia pesa más.")
    return figura, {"figura": "f1_nota_ponderada_por_votos", "hallazgo": titulo, "evidencia": evidencia}


def figura_tiempo_memoria(mediciones):
    """Figura 2: tiempo y memoria pico de las cuatro formas de elegir el top 10, en los mismos tamaños."""
    from matplotlib import pyplot as plt

    _exigir(mediciones, ["versión", "tiempo_s", "memoria_pico_MB", "experimento", "n"], "mediciones.csv")
    top_k = mediciones[mediciones["experimento"].eq("top_k")]
    tiempo = top_k.pivot(index="n", columns="versión", values="tiempo_s").sort_index()
    memoria = top_k.pivot(index="n", columns="versión", values="memoria_pico_MB").sort_index()
    if set(tiempo.columns) != set(ORDEN_TOP_K) or tiempo.isna().any().any() or memoria.isna().any().any():
        raise ValueError("El experimento top_k debe tener las cuatro alternativas en todos los tamaños.")

    figura, ejes = plt.subplots(1, 2, figsize=TAMANO, layout="constrained", sharex=True)
    for version in ORDEN_TOP_K:
        ejes[0].plot(tiempo.index, tiempo[version] * 1000, marker="o", lw=2, color=COLORES_TOP_K[version], label=version)
        ejes[1].plot(memoria.index, memoria[version], marker="s", lw=2, color=COLORES_TOP_K[version])
    ejes[0].set(title="Tiempo (escala logarítmica)", ylabel="Milisegundos", yscale="log")
    ejes[1].set(title="Memoria pico rastreada", ylabel="MiB")
    for eje in ejes:
        eje.set_xlabel("Películas procesadas (n)")
        eje.grid(axis="y", alpha=0.2)
        eje.spines[["top", "right"]].set_visible(False)
    ejes[0].legend(frameon=False, loc="upper left", fontsize=10)
    titulo = "Para elegir el top 10, argpartition es la más rápida y el montículo usa menos memoria"
    figura.suptitle(titulo, fontweight="bold", fontsize=15)
    _fuente(figura, "Fuente: F3/results/mediciones.csv, experimento top_k (mínimo de repeticiones; "
                    "los tiempos dependen del equipo y no miden el recomendador completo).")
    n = tiempo.index.max()
    rapida, lenta = tiempo.loc[n].idxmin(), "ordenar todo (estructurado)"
    liviana, pesada = memoria.loc[n].idxmin(), memoria.loc[n].idxmax()
    evidencia = (f"Con {_es(n)} películas, {rapida} tardó {_es(tiempo.loc[n, rapida] * 1000, 2)} ms y {lenta} {_es(tiempo.loc[n, lenta] * 1000, 2)} ms. "
                 f"El menor pico de memoria fue de {liviana} ({_es(memoria.loc[n, liviana], 3)} MiB) y el mayor de {pesada} "
                 f"({_es(memoria.loc[n, pesada], 3)} MiB). Ganar en una métrica no implica ganar en la otra.")
    return figura, {"figura": "f2_tiempo_memoria_top_k", "hallazgo": titulo, "evidencia": evidencia}


def figura_evaluacion(evaluacion):
    """Figura 3: línea base de F1, solo similitud e híbrido en los tres criterios de F1."""
    from matplotlib import pyplot as plt

    columnas = list(COLORES_EVALUACION)
    _exigir(evaluacion, columnas, "evaluacion_recomendador.csv")
    if len(evaluacion) != 3:
        raise ValueError("Se esperaban los tres criterios de F1.")
    valores = evaluacion[columnas] * 100
    criterios = [i.replace(">=", "≥") for i in valores.index]

    figura, eje = plt.subplots(figsize=TAMANO, layout="constrained")
    x = np.arange(len(valores))
    ancho = 0.26
    for k, columna in enumerate(columnas):
        grupo = eje.bar(x + (k - 1) * ancho, valores[columna], ancho, color=COLORES_EVALUACION[columna], label=columna)
        eje.bar_label(grupo, labels=[f"{_es(v, 1)} %" for v in grupo.datavalues], padding=3, fontsize=10)
    eje.set_xticks(x, criterios)
    eje.set(ylabel="% de recomendaciones que cumplen el criterio", ylim=(0, 112))
    eje.grid(axis="y", alpha=0.2)
    eje.spines[["top", "right"]].set_visible(False)
    eje.legend(frameon=False, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 1.0))
    titulo = "El híbrido supera al azar en los tres criterios y gana respaldo de votos a costa de coincidencia de idioma"
    figura.suptitle(titulo, fontweight="bold", fontsize=14)
    _fuente(figura, "Fuente: F3/results/evaluacion_recomendador.csv (3.596 consultas de prueba). La línea aleatoria viene de F1 y no está "
                    "emparejada con esas consultas. El corte de 428 votos no es el parámetro m = 421 de la nota ponderada.")
    h, s, a = (valores.loc[:, c] for c in ("Híbrido (pesos elegidos)", "Solo similitud", "Línea base aleatoria (F1)"))
    voto, idioma = valores.index[2], valores.index[1]
    evidencia = (f"Híbrido frente a azar: género {_es(h.iloc[0], 1)} % frente a {_es(a.iloc[0], 1)} %, idioma {_es(h.iloc[1], 1)} % frente a "
                 f"{_es(a.iloc[1], 1)} %, votos {_es(h.iloc[2], 1)} % frente a {_es(a.iloc[2], 1)} %. Frente a solo similitud, el respaldo de votos sube de "
                 f"{_es(s[voto], 1)} % a {_es(h[voto], 1)} % y la coincidencia de idioma baja de {_es(s[idioma], 1)} % a {_es(h[idioma], 1)} %. "
                 "Métricas indirectas: no miden satisfacción de usuarios.")
    return figura, {"figura": "f3_evaluacion_azar_similitud_hibrido", "hallazgo": titulo, "evidencia": evidencia}
