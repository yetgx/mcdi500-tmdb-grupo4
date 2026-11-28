"""Pruebas de src/transformadores.py y src/pipeline.py: los pasos que reproducen la Fase 2.

Ejecutar desde la raíz del repositorio:  python -m pytest
"""

import numpy as np
import pandas as pd
import pytest

from src.pipeline import Pipeline
from src.transformadores import (
    CalidadPonderada,
    CerosComoAusentes,
    ConstructorSopa,
    DuracionPorGenero,
    EscaladorMinMax,
    LogNaturalPlus1,
)


@pytest.fixture
def peliculas():
    return pd.DataFrame({
        "genres": ["Drama|Thriller", "Comedy", None, "Drama"],
        "production_companies": ["Warner Bros. Pictures|A24", None, "Lionsgate", "Pixar|Disney|Fox|Sony"],
        "original_language": ["en", "fr", None, "EN"],
        "runtime": [120.0, 0.0, 95.0, 0.0],
        "budget": [0.0, 1e6, 0.0, 5e5],
        "vote_average": [7.0, 6.0, 5.0, 8.0],
        "vote_count": [100, 10, 1000, 50],
        "popularity": [1.0, 0.0, 20.0, 3.0],
    })


def test_sopa_aplica_las_reglas_de_f2(peliculas):
    salida = ConstructorSopa().ajustar_transformar(peliculas)
    assert salida["metadata_soup"].tolist() == [
        "drama thriller warnerbrospictures a24 en",   # sin puntuación ni espacios en la productora
        "comedy fr",                                   # sin productoras: no aparece 'unknown'
        "unknown lionsgate unknown",                   # géneros e idioma nulos -> 'unknown'
        "drama pixar disney fox en",                   # solo 3 productoras; idioma en minúsculas
    ]
    assert {"genres_clean", "companies_clean", "lang_clean"} <= set(salida.columns)


def test_sopa_valida_columnas_de_origen(peliculas):
    with pytest.raises(KeyError, match="genres"):
        ConstructorSopa().ajustar(peliculas.drop(columns=["genres"]))


def test_transformar_valida_el_esquema_de_prueba(peliculas):
    paso = ConstructorSopa().ajustar(peliculas)
    with pytest.raises(KeyError, match="original_language"):
        paso.transformar(peliculas.drop(columns=["original_language"]))


def test_duracion_por_genero_aprende_solo_en_ajuste(peliculas):
    paso = DuracionPorGenero().ajustar(peliculas)
    assert paso.parametros["medianas"] == {"Drama": 120.0, "Unknown": 95.0}
    salida = paso.transformar(peliculas)
    # Comedy no tiene duraciones positivas: cae a la mediana global (107,5)
    assert salida["runtime_clean"].tolist() == [120.0, 107.5, 95.0, 120.0]
    assert salida["runtime"].tolist() == peliculas["runtime"].tolist()   # conserva el original


def test_duracion_sin_positivos_falla():
    with pytest.raises(ValueError, match="duración positiva"):
        DuracionPorGenero().ajustar(pd.DataFrame({"runtime": [0.0, 0.0], "genres": ["Drama", "Comedy"]}))


def test_ceros_como_ausentes(peliculas):
    salida = CerosComoAusentes("budget", "budget_clean").ajustar_transformar(peliculas)
    assert salida["budget_clean"].isna().tolist() == [True, False, True, False]


def test_calidad_ponderada_aprende_c_y_m(peliculas):
    paso = CalidadPonderada().ajustar(peliculas)
    assert paso.parametros["C"] == pytest.approx(6.5)
    assert paso.parametros["m"] == pytest.approx(peliculas["vote_count"].quantile(0.75))
    wr = paso.transformar(peliculas)["weighted_rating"]
    assert wr.between(5.0, 8.0).all()   # el WR queda entre la nota propia y la media global


def test_calidad_ponderada_sin_votos_falla():
    with pytest.raises(ValueError, match="percentil"):
        CalidadPonderada().ajustar(pd.DataFrame({"vote_average": [5.0], "vote_count": [0]}))


def test_destino_conserva_la_columna_original(peliculas):
    salida = LogNaturalPlus1("popularity", "popularity_log").ajustar_transformar(peliculas)
    assert salida["popularity"].tolist() == peliculas["popularity"].tolist()
    np.testing.assert_allclose(salida["popularity_log"], np.log1p(peliculas["popularity"]))


def test_minmax_usa_parametros_de_entrenamiento():
    entrenamiento = pd.DataFrame({"x": [0.0, 10.0]})
    paso = EscaladorMinMax("x", "x_norm").ajustar(entrenamiento)
    prueba = paso.transformar(pd.DataFrame({"x": [5.0, 20.0]}))
    assert prueba["x_norm"].tolist() == [0.5, 2.0]   # fuera de [0, 1]: no se recorta


def test_pipeline_completo_no_modifica_la_entrada(peliculas):
    original = peliculas.copy()
    pipe = Pipeline([DuracionPorGenero(), ConstructorSopa(), CalidadPonderada(),
                     LogNaturalPlus1("popularity", "popularity_log"),
                     EscaladorMinMax("weighted_rating", "score_quality_norm"),
                     EscaladorMinMax("popularity_log", "score_popularity_norm")])
    salida = pipe.ajustar(peliculas).transformar(peliculas)
    pd.testing.assert_frame_equal(peliculas, original)
    assert salida["score_quality_norm"].between(0, 1).all()
    assert salida["score_popularity_norm"].between(0, 1).all()


def test_pipeline_exige_ajuste_y_transformadores():
    with pytest.raises(RuntimeError):
        Pipeline([ConstructorSopa()]).transformar(pd.DataFrame())
    with pytest.raises(TypeError):
        Pipeline().agregar("no soy un transformador")
