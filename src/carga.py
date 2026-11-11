"""Carga y verificación del conjunto de datos.

Módulo del proyecto MCDI500 - Grupo 4, adaptado del proyecto modelo de la Semana 2.
Lo usa el cuaderno F3/F3_NucleoAlgoritmico_TMDB.ipynb.
"""

import os

import pandas as pd


def leer_archivo(ruta):
    """Lee el archivo según su extensión y devuelve un DataFrame."""
    extension = os.path.splitext(ruta)[1].lower()

    if extension in (".csv", ".txt"):
        # sep=None con engine="python" infiere el separador: útil con datos
        # públicos chilenos, que suelen venir con punto y coma
        return pd.read_csv(ruta, sep=None, engine="python", encoding="utf-8")
    if extension in (".xlsx", ".xls"):
        return pd.read_excel(ruta)
    if extension == ".parquet":
        return pd.read_parquet(ruta)

    raise ValueError(
        f"Extensión no reconocida: '{extension}'. "
        "Se admiten .csv, .txt, .xlsx, .xls y .parquet."
    )


def verificar_esquema(df, columnas_esperadas):
    """Comprueba que estén todas las columnas declaradas en la configuración."""
    faltantes = [c for c in columnas_esperadas if c not in df.columns]
    if faltantes:
        raise KeyError(
            f"Faltan columnas declaradas en la configuración: {faltantes}\n"
            f"Columnas disponibles en el archivo: {list(df.columns)}"
        )
    sobrantes = [c for c in df.columns if c not in columnas_esperadas]
    return {"declaradas": len(columnas_esperadas),
            "en_archivo": df.shape[1],
            "no_declaradas": sobrantes}


def cargar(ruta, columnas_esperadas, columnas_numericas=()):
    """Carga el conjunto desde el archivo y verifica su esquema.

    A diferencia de la versión del cuaderno, no tiene datos de demostración:
    en el proyecto, si el archivo no está, el error debe detener la ejecución.
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    df = leer_archivo(ruta)
    # Las columnas numéricas se fuerzan a número: un texto suelto las
    # convertiría en columna de objetos sin ningún aviso
    for columna in columnas_numericas:
        if columna in df.columns:
            df[columna] = pd.to_numeric(df[columna], errors="coerce")
    verificar_esquema(df, columnas_esperadas)
    return df
