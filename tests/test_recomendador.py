"""Pruebas de src/recomendador.py.

Ejecutar desde la raíz del repositorio:  python -m pytest
"""

import numpy as np
import pandas as pd
import pytest

from src.recomendador import RecomendadorHibrido, evaluar_recomendaciones, similitud_coseno_bucle


@pytest.fixture
def catalogo():
    return pd.DataFrame({
        "movie_id": [1, 2, 3, 4, 5],
        "title": ["A", "B", "C", "D", "E"],
        "metadata_soup": ["drama thriller en", "drama thriller en", "comedy fr",
                          "drama fr", "horror ko"],
        "score_quality_norm": [0.5, 0.1, 0.9, 0.4, 1.0],
        "score_popularity_norm": [0.2, 0.3, 0.1, 0.0, 1.0],
    })


def test_solo_similitud_recomienda_la_mas_parecida(catalogo):
    r = RecomendadorHibrido(1.0, 0.0, 0.0, n=2).ajustar(catalogo)
    tabla = r.recomendar(1)
    assert tabla["movie_id"].tolist() == [2, 4]   # misma sopa, luego comparte 'drama'
    assert tabla["similitud"].iloc[0] == pytest.approx(1.0)
    assert 1 not in tabla["movie_id"].tolist()    # no se recomienda a sí misma


def test_puntaje_es_la_combinacion_lineal(catalogo):
    r = RecomendadorHibrido(0.5, 0.3, 0.2, n=4).ajustar(catalogo)
    tabla = r.recomendar(1)
    esperado = 0.5 * tabla["similitud"] + 0.3 * tabla["calidad"] + 0.2 * tabla["popularidad"]
    np.testing.assert_allclose(tabla["puntaje"], esperado)
    assert tabla["puntaje"].is_monotonic_decreasing


def test_coseno_vectorizado_igual_al_bucle(catalogo):
    r = RecomendadorHibrido().ajustar(catalogo)
    analizador = r.vectorizador.build_analyzer()
    for i, sopa in enumerate(catalogo["metadata_soup"]):
        bucle = similitud_coseno_bucle(sopa, catalogo["metadata_soup"], analizador)
        np.testing.assert_allclose(r.similitudes([i])[0], bucle)


def test_vocabulario_de_entrenamiento_ignora_tokens_nuevos(catalogo):
    base = RecomendadorHibrido().ajustar(catalogo.iloc[:3])
    r = RecomendadorHibrido().ajustar(catalogo, vectorizador=base.vectorizador)
    assert r.matriz.shape == (5, len(base.vectorizador.vocabulary_))
    assert r.matriz[4].nnz == 0   # 'horror ko' no estaba en entrenamiento: vector nulo, coseno 0
    analizador = base.vectorizador.build_analyzer()
    bucle = similitud_coseno_bucle("drama horror", catalogo["metadata_soup"], analizador,
                                   base.vectorizador.vocabulary_)
    np.testing.assert_allclose(bucle, (base.vectorizador.transform(["drama horror"]) @ r.matriz.T).toarray()[0])


def test_catalogo_con_n_o_menos_peliculas(catalogo):
    # con 5 películas no hay 5 distintas de la consultada, ni 10: antes devolvía la propia película o fallaba al asignar
    for n in (5, 10):
        with pytest.raises(ValueError, match="más de n"):
            RecomendadorHibrido(n=n).ajustar(catalogo).recomendar(1)
    tabla = RecomendadorHibrido(n=4).ajustar(catalogo).recomendar(1)
    assert sorted(tabla["movie_id"]) == [2, 3, 4, 5]   # con n = 4 sí: las otras cuatro


@pytest.mark.parametrize("pesos", [(0.5, 0.5, 0.5), (1.2, -0.2, 0.0)])
def test_pesos_invalidos(pesos):
    with pytest.raises(ValueError, match="pesos"):
        RecomendadorHibrido(*pesos)


def test_errores_de_uso(catalogo):
    with pytest.raises(RuntimeError):
        RecomendadorHibrido().recomendar(1)
    with pytest.raises(KeyError, match="metadata_soup"):
        RecomendadorHibrido().ajustar(catalogo.drop(columns=["metadata_soup"]))
    with pytest.raises(ValueError, match="único"):
        RecomendadorHibrido().ajustar(pd.concat([catalogo, catalogo.iloc[:1]]))
    with pytest.raises(KeyError, match="999"):
        RecomendadorHibrido().ajustar(catalogo).recomendar(999)


def test_evaluar_recomendaciones():
    generos = [{"Drama"}, {"Drama", "Crime"}, {"Comedy"}]
    idiomas = ["en", "en", "fr"]
    votos = [10, 500, 1000]
    resultado = evaluar_recomendaciones([0, 2], np.array([[1, 2], [0, 1]]), generos, idiomas, votos, 428)
    assert resultado.tolist() == pytest.approx([0.25, 0.25, 0.75])

