"""Pruebas de src/pipeline.py: el pipeline del proyecto en una sola llamada.

Ejecutar desde la raíz del repositorio:  python -m pytest
"""

import pandas as pd
import pytest

from src.pipeline import ejecutar, pipeline_tmdb
from src.preparacion import construir_sopa_por_fila, diccionario_procesado
from src.transformadores import ConstructorSopa, Transformador


@pytest.fixture
def peliculas():
    return pd.DataFrame({
        "movie_id": [1, 2, 3, 4],
        "title": ["A", "B", "C", "D"],
        "release_date": ["2010-01-01"] * 4,
        "genres": ["Drama|Thriller", "Comedy", None, "Drama"],
        "production_companies": ["Warner Bros. Pictures|A24", None, "Lionsgate", "Pixar|Disney|Fox|Sony"],
        "original_language": ["en", "fr", None, "EN"],
        "runtime": [120.0, 0.0, 95.0, 0.0],
        "budget": [0.0, 1e6, 0.0, 5e5],
        "revenue": [0.0, 2e6, 0.0, 0.0],
        "vote_average": [7.0, 6.0, 5.0, 8.0],
        "vote_count": [100, 10, 1000, 50],
        "popularity": [1.0, 0.0, 20.0, 3.0],
    })


def test_pipeline_tmdb_tiene_los_ocho_pasos_sin_ajustar():
    pipe = pipeline_tmdb()
    assert len(pipe) == 8
    assert all(isinstance(p, Transformador) for p in pipe.pasos_ejecutados())
    with pytest.raises(RuntimeError):
        pipe.transformar(pd.DataFrame())


def test_ejecutar_devuelve_las_columnas_de_f2_en_orden(peliculas):
    salida = ejecutar(peliculas)
    assert list(salida.columns) == diccionario_procesado()["columna"].tolist()
    assert salida["movie_id"].tolist() == [1, 2, 3, 4]
    assert salida["score_quality_norm"].min() == 0 and salida["score_quality_norm"].max() == 1


def test_ejecutar_aprende_con_ajustar_con(peliculas):
    entrenamiento, prueba = peliculas.iloc[:2], peliculas.iloc[2:]
    salida = ejecutar(prueba, ajustar_con=entrenamiento)
    # runtime 0 de la película D (Drama) toma la mediana de Drama aprendida en entrenamiento (120)
    assert salida["runtime_clean"].tolist() == [95.0, 120.0]


def test_ejecutar_falla_si_falta_una_columna(peliculas):
    with pytest.raises(KeyError, match="genres"):
        ejecutar(peliculas.drop(columns=["genres"]))


def test_sopa_por_fila_igual_a_la_de_columnas(peliculas):
    por_fila = construir_sopa_por_fila(peliculas)
    por_columnas = ConstructorSopa().ajustar_transformar(peliculas)["metadata_soup"]
    pd.testing.assert_series_equal(por_fila, por_columnas)
