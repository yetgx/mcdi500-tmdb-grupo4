"""Pruebas de src/recursividad.py: versiones recursivas e iterativas equivalentes.

Ejecutar desde la raíz del repositorio:  python -m pytest
"""

import numpy as np
import pytest

from src.recursividad import (
    aplanar_iterativo,
    aplanar_recursivo,
    profundidad,
    top_k_monticulo,
    top_k_ordenando,
    top_k_recursivo,
    top_k_vectorizado,
)

VERSIONES_TOP_K = [top_k_ordenando, top_k_recursivo, top_k_monticulo, top_k_vectorizado]


def test_aplanar_conserva_orden_y_omite_vacios():
    pelicula = [["Drama", "Thriller"], ["Warner Bros.", None, ""], "en"]
    esperado = ["Drama", "Thriller", "Warner Bros.", "en"]
    assert aplanar_recursivo(pelicula) == esperado
    assert aplanar_iterativo(pelicula) == esperado


@pytest.mark.parametrize("datos", [[], None, "", [[[]]], ("a", ("b", ["c"]))])
def test_aplanar_casos_limite_equivalentes(datos):
    assert aplanar_recursivo(datos) == aplanar_iterativo(datos)


def test_aplanar_tipo_no_soportado():
    for funcion in (aplanar_recursivo, aplanar_iterativo):
        with pytest.raises(TypeError):
            funcion(["Drama", 3])


def test_aplanar_recursivo_limita_profundidad_e_iterativo_no():
    anidada = "Drama"
    for _ in range(60):
        anidada = [anidada]
    assert profundidad(anidada) == 60
    with pytest.raises(RecursionError):
        aplanar_recursivo(anidada)
    assert aplanar_iterativo(anidada) == ["Drama"]


@pytest.mark.parametrize("k", [1, 10, 100])
def test_top_k_versiones_equivalentes(k):
    puntajes = np.random.default_rng(42).random(5_000)
    esperado = np.argsort(-puntajes, kind="stable")[:k]
    for funcion in VERSIONES_TOP_K:
        np.testing.assert_array_equal(funcion(puntajes, k), esperado)


def test_top_k_desempata_por_indice_menor():
    puntajes = np.array([0.5, 0.9, 0.9, 0.1, 0.9, 0.5])
    for funcion in VERSIONES_TOP_K:
        np.testing.assert_array_equal(funcion(puntajes, 3), [1, 2, 4])
        np.testing.assert_array_equal(funcion(puntajes, 4), [1, 2, 4, 0])


def test_top_k_con_infinito_negativo_y_k_mayor_que_n():
    puntajes = np.array([0.2, -np.inf, 0.7])
    for funcion in VERSIONES_TOP_K:
        np.testing.assert_array_equal(funcion(puntajes, 10), [2, 0, 1])


@pytest.mark.parametrize("k", [0, -1, 2.5])
def test_top_k_k_invalido(k):
    for funcion in VERSIONES_TOP_K:
        with pytest.raises(ValueError):
            funcion(np.array([1.0, 2.0]), k)


def test_top_k_rechaza_nan():
    for funcion in VERSIONES_TOP_K:
        with pytest.raises(ValueError, match="NaN"):
            funcion(np.array([1.0, np.nan]), 1)
