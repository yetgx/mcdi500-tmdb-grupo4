"""Funciones de preparación de datos de la Fase 2.

Módulo del proyecto MCDI500 - Grupo 4. Lo importa el cuaderno
F2/Fase2-Preparacion-Recomendador.ipynb y queda disponible para las fases
siguientes, que deben partir de estas funciones en lugar de copiarlas.

Cada función valida su entrada y falla con un ValueError explícito: un
AttributeError lanzado desde dentro de pandas o de str no es una validación,
es un defecto que obliga a recordar el orden correcto de las operaciones.
"""

import re

import numpy as np
import pandas as pd

MAX_PRODUCTORAS = 3

# Diccionario del conjunto exportado por F2 (data/processed/movies_procesado.csv).
# La columna "uso" declara qué consume el recomendador y qué se conserva solo
# como contexto, para que la Fase 3 no incorpore una columna sin decidirlo.
DICCIONARIO_PROCESADO = [
    ("movie_id", "Identificador TMDB", "identificación"),
    ("title", "Título de la película", "identificación"),
    ("release_date", "Fecha de estreno (texto ISO)", "identificación"),
    ("genres_clean", "Géneros en minúsculas separados por espacio", "similitud (vía metadata_soup)"),
    ("companies_clean", "Hasta 3 productoras sin espacios ni puntuación", "similitud (vía metadata_soup)"),
    ("lang_clean", "Idioma original en minúsculas", "similitud (vía metadata_soup)"),
    ("metadata_soup", "Texto que vectoriza CountVectorizer", "similitud"),
    ("vote_average", "Valoración promedio original (0-10)", "insumo de weighted_rating"),
    ("vote_count", "Cantidad de votos original", "insumo de weighted_rating"),
    ("popularity", "Popularidad original de TMDB", "insumo de score_popularity_norm"),
    ("weighted_rating", "Weighted Rating con m = percentil 75 de vote_count", "calidad"),
    ("score_quality_norm", "weighted_rating escalado a [0, 1]", "calidad (ponderación final)"),
    ("score_popularity_norm", "log1p(popularity) escalado a [0, 1]", "popularidad (ponderación final)"),
    ("runtime_clean", "Duración en minutos; ceros imputados por mediana del género principal", "no la usa el recomendador (contexto)"),
    ("budget_clean", "Presupuesto en USD; ceros convertidos a NaN, sin imputar", "no la usa el recomendador (69,3 % NaN)"),
    ("revenue_clean", "Recaudación en USD; ceros convertidos a NaN, sin imputar", "no la usa el recomendador (62,1 % NaN)"),
]


def _exigir_texto(nombre_funcion, valor):
    if not isinstance(valor, str):
        raise ValueError(
            f"{nombre_funcion}: se esperaba texto y se recibió {type(valor).__name__} ({valor!r}). "
            "Imputar los nulos antes de limpiar (ver imputar_metadatos)."
        )


def _exigir_serie(nombre_funcion, valor):
    if not isinstance(valor, pd.Series):
        raise ValueError(f"{nombre_funcion}: se esperaba una pd.Series y se recibió {type(valor).__name__}.")


# ---- Diagnóstico ------------------------------------------------------------

def contar_duplicados(df):
    """Duplicados por identificador, por fila completa y por título + fecha de estreno."""
    faltantes = [c for c in ("movie_id", "title", "release_date") if c not in df.columns]
    if faltantes:
        raise ValueError(f"contar_duplicados: faltan las columnas {faltantes}.")
    return pd.Series({
        "movie_id repetido": int(df["movie_id"].duplicated().sum()),
        "filas completas repetidas": int(df.duplicated().sum()),
        "título + fecha repetidos": int(df.duplicated(["title", "release_date"]).sum()),
        "títulos repetidos (películas distintas)": int(df["title"].duplicated().sum()),
    })


def contar_atipicos_iqr(serie):
    """Cantidad de valores fuera de [Q1 - 1,5·IQR, Q3 + 1,5·IQR]."""
    _exigir_serie("contar_atipicos_iqr", serie)
    if not pd.api.types.is_numeric_dtype(serie):
        raise ValueError(f"contar_atipicos_iqr: la serie '{serie.name}' no es numérica.")
    q1, q3 = serie.quantile([0.25, 0.75])
    iqr = q3 - q1
    return int(((serie < q1 - 1.5 * iqr) | (serie > q3 + 1.5 * iqr)).sum())


# ---- Tratamiento de ceros -----------------------------------------------------

def genero_principal(genres):
    """Primer género de cada película; 'Unknown' si no tiene."""
    _exigir_serie("genero_principal", genres)
    return genres.fillna("Unknown").astype(str).str.split("|").str[0]


def ceros_a_nan(serie):
    """Interpreta el cero como dato no informado: lo convierte en NaN sin imputar."""
    _exigir_serie("ceros_a_nan", serie)
    return serie.where(serie > 0)


def imputar_mediana_por_grupo(serie, grupos):
    """Trata los ceros como faltantes y los rellena con la mediana de su grupo.

    Si un grupo no tiene ningún valor positivo, cae a la mediana global.
    """
    _exigir_serie("imputar_mediana_por_grupo", serie)
    if len(grupos) != len(serie):
        raise ValueError("imputar_mediana_por_grupo: la serie y los grupos tienen largos distintos.")
    positivos = ceros_a_nan(serie)
    if positivos.isna().all():
        raise ValueError(f"imputar_mediana_por_grupo: '{serie.name}' no tiene valores positivos.")
    por_grupo = positivos.groupby(grupos).transform("median")
    return positivos.fillna(por_grupo).fillna(positivos.median())


def comparar_imputaciones(serie, grupos):
    """Compara eliminar, media, mediana y mediana por grupo sobre una serie con ceros como faltantes."""
    _exigir_serie("comparar_imputaciones", serie)
    s = ceros_a_nan(serie)
    base = s.dropna()
    if base.empty:
        raise ValueError(f"comparar_imputaciones: '{serie.name}' no tiene valores positivos.")
    alternativas = {
        "Eliminar filas": base,
        "Imputar media": s.fillna(base.mean()),
        "Imputar mediana": s.fillna(base.median()),
        "Mediana por género": imputar_mediana_por_grupo(serie, grupos),
    }
    filas = []
    for nombre, v in alternativas.items():
        filas.append({"alternativa": nombre, "n": len(v), "media": v.mean(), "mediana": v.median(),
                      "desv_est": v.std(), "Δ desv_est %": (v.std() / base.std() - 1) * 100})
    return pd.DataFrame(filas).set_index("alternativa").round(2)


# ---- Limpieza textual y sopa de metadatos ------------------------------------

def imputar_metadatos(df):
    """Devuelve una copia con los nulos de las columnas de contenido imputados.

    'Unknown' en géneros e idioma; cadena vacía en productoras, porque un valor
    común como 'Unknown' haría similares entre sí a las 494 películas sin dato.
    """
    faltantes = [c for c in ("genres", "production_companies", "original_language") if c not in df.columns]
    if faltantes:
        raise ValueError(f"imputar_metadatos: faltan las columnas {faltantes}.")
    salida = df.copy()
    salida["genres"] = salida["genres"].fillna("Unknown")
    salida["production_companies"] = salida["production_companies"].fillna("")
    salida["original_language"] = salida["original_language"].fillna("Unknown")
    return salida


def clean_genres(text):
    """'Drama|Sci-Fi' -> 'drama sci-fi'."""
    _exigir_texto("clean_genres", text)
    return text.replace("|", " ").lower()


def clean_text_feature(text, max_productoras=MAX_PRODUCTORAS):
    """Compacta cada productora en una entidad: 'Warner Bros.' -> 'warnerbros'.

    Conserva solo las primeras `max_productoras`.
    """
    _exigir_texto("clean_text_feature", text)
    if max_productoras < 1:
        raise ValueError("clean_text_feature: max_productoras debe ser al menos 1.")
    tokens = [re.sub(r"\W+", "", t.lower()) for t in text.split("|")[:max_productoras]]
    return " ".join(t for t in tokens if t)


def construir_sopa(genres_clean, companies_clean, lang_clean):
    """Une las tres columnas limpias en la 'sopa de metadatos', sin espacios repetidos."""
    for nombre, serie in (("genres_clean", genres_clean), ("companies_clean", companies_clean),
                          ("lang_clean", lang_clean)):
        _exigir_serie("construir_sopa", serie)
        if serie.isna().any():
            raise ValueError(f"construir_sopa: '{nombre}' tiene nulos; limpiar antes de unir.")
    return (genres_clean + " " + companies_clean + " " + lang_clean).str.replace(r"\s+", " ", regex=True).str.strip()


# ---- Calidad ponderada -------------------------------------------------------------

def calculate_weighted_rating(v, R, m, C):
    """Weighted Rating de IMDb: WR = v/(v+m)·R + m/(v+m)·C, vectorizado.

    v: cantidad de votos, R: nota promedio, m: votos mínimos de referencia,
    C: media global de las notas.
    """
    if not np.isfinite(m) or m <= 0:
        raise ValueError(f"calculate_weighted_rating: m debe ser un número positivo y se recibió {m!r}.")
    if not np.isfinite(C):
        raise ValueError(f"calculate_weighted_rating: C debe ser un número finito y se recibió {C!r}.")
    if np.any(np.asarray(v) < 0):
        raise ValueError("calculate_weighted_rating: v (cantidad de votos) no admite valores negativos.")
    return (v / (v + m)) * R + (m / (v + m)) * C


def calcular_indicadores(calificaciones, originales):
    """Indicadores de una calificación ponderada respecto de las originales."""
    _exigir_serie("calcular_indicadores", calificaciones)
    _exigir_serie("calcular_indicadores", originales)
    if len(calificaciones) != len(originales):
        raise ValueError("calcular_indicadores: las series tienen largos distintos.")
    return {
        "Media de calificaciones": calificaciones.mean(),
        "Desviación estándar": calificaciones.std(),
        "Diferencia media absoluta (MAE)": (calificaciones - originales).abs().mean(),
        "Correlación con vote_average": calificaciones.corr(originales),
    }


def diccionario_procesado():
    """DICCIONARIO_PROCESADO como DataFrame, en el orden de las columnas exportadas."""
    return pd.DataFrame(DICCIONARIO_PROCESADO, columns=["columna", "descripcion", "uso"])
