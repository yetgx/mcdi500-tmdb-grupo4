"""Pruebas de src/preparacion.py: caso normal, casos límite y errores explícitos.

Ejecutar desde la raíz del repositorio:  python -m pytest
"""

import numpy as np
import pandas as pd
import pytest

from src.preparacion import (
    calcular_indicadores,
    calculate_weighted_rating,
    ceros_a_nan,
    clean_genres,
    clean_text_feature,
    comparar_imputaciones,
    construir_sopa,
    contar_atipicos_iqr,
    contar_duplicados,
    diccionario_procesado,
    genero_principal,
    imputar_mediana_por_grupo,
    imputar_metadatos,
)


# ---- Limpieza textual --------------------------------------------------------

def test_clean_genres_normal_y_limite():
    assert clean_genres("Drama") == "drama"
    assert clean_genres("Drama|Sci-Fi") == "drama sci-fi"
    assert clean_genres("") == ""


@pytest.mark.parametrize("valor", [float("nan"), None, 3])
def test_clean_genres_rechaza_no_texto_con_valueerror(valor):
    with pytest.raises(ValueError, match="se esperaba texto"):
        clean_genres(valor)


def test_clean_text_feature():
    assert clean_text_feature("") == ""
    assert clean_text_feature("Warner Bros.|Legendary Pictures") == "warnerbros legendarypictures"
    assert len(clean_text_feature("A|B|C|D|E").split()) == 3
    assert clean_text_feature("A|B|C", max_productoras=1) == "a"


def test_clean_text_feature_errores():
    with pytest.raises(ValueError, match="se esperaba texto"):
        clean_text_feature(np.nan)
    with pytest.raises(ValueError, match="max_productoras"):
        clean_text_feature("A", max_productoras=0)


def test_imputar_metadatos_no_modifica_el_original():
    df = pd.DataFrame({"genres": [None, "Drama"], "production_companies": [None, "A"],
                       "original_language": [None, "en"]})
    salida = imputar_metadatos(df)
    assert salida["genres"].tolist() == ["Unknown", "Drama"]
    assert salida["production_companies"].tolist() == ["", "A"]
    assert salida["original_language"].tolist() == ["Unknown", "en"]
    assert df["genres"].isna().sum() == 1


def test_imputar_metadatos_exige_columnas():
    with pytest.raises(ValueError, match="faltan las columnas"):
        imputar_metadatos(pd.DataFrame({"genres": ["Drama"]}))


def test_construir_sopa_sin_espacios_repetidos():
    sopa = construir_sopa(pd.Series(["drama", "unknown"]), pd.Series(["", "a b"]), pd.Series(["en", "fr"]))
    assert sopa.tolist() == ["drama en", "unknown a b fr"]


def test_construir_sopa_rechaza_nulos():
    with pytest.raises(ValueError, match="tiene nulos"):
        construir_sopa(pd.Series(["drama"]), pd.Series([None]), pd.Series(["en"]))


# ---- Diagnóstico y ceros -------------------------------------------------------

def test_contar_duplicados():
    df = pd.DataFrame({"movie_id": [1, 2, 2], "title": ["A", "A", "A"],
                       "release_date": ["2010-01-01", "2011-01-01", "2011-01-01"]})
    r = contar_duplicados(df)
    assert r["movie_id repetido"] == 1
    assert r["filas completas repetidas"] == 1
    assert r["títulos repetidos (películas distintas)"] == 2
    with pytest.raises(ValueError):
        contar_duplicados(df.drop(columns=["title"]))


def test_contar_atipicos_iqr():
    assert contar_atipicos_iqr(pd.Series([1, 2, 3, 4, 100])) == 1
    assert contar_atipicos_iqr(pd.Series([5, 5, 5])) == 0           # IQR = 0, sin atípicos
    with pytest.raises(ValueError, match="no es numérica"):
        contar_atipicos_iqr(pd.Series(["a", "b"]))
    with pytest.raises(ValueError, match="pd.Series"):
        contar_atipicos_iqr([1, 2, 3])


def test_imputar_mediana_por_grupo_y_ceros():
    serie = pd.Series([0, 100, 120, 0, 80], name="runtime")
    grupos = genero_principal(pd.Series(["Drama|X", "Drama", "Drama", "Horror", "Comedy"]))
    resultado = imputar_mediana_por_grupo(serie, grupos)
    assert resultado.tolist() == [110.0, 100.0, 120.0, 100.0, 80.0]   # Horror sin dato: mediana global
    assert ceros_a_nan(pd.Series([0, 5])).isna().tolist() == [True, False]


def test_imputar_mediana_por_grupo_errores():
    with pytest.raises(ValueError, match="largos distintos"):
        imputar_mediana_por_grupo(pd.Series([1, 2]), pd.Series(["a"]))
    with pytest.raises(ValueError, match="no tiene valores positivos"):
        imputar_mediana_por_grupo(pd.Series([0, 0], name="budget"), pd.Series(["a", "b"]))


def test_comparar_imputaciones_eliminar_conserva_la_desviacion():
    serie = pd.Series([0, 10, 20, 30, 0])
    tabla = comparar_imputaciones(serie, pd.Series(["a", "a", "b", "b", "b"]))
    assert tabla.loc["Eliminar filas", "n"] == 3
    assert tabla.loc["Eliminar filas", "Δ desv_est %"] == 0
    assert (tabla["Δ desv_est %"] <= 0).all()       # imputar un valor central nunca agrega variabilidad


# ---- Weighted Rating ---------------------------------------------------------------

def test_weighted_rating_queda_entre_la_nota_y_la_media():
    v, R = pd.Series([0, 50, 5000]), pd.Series([9.0, 4.0, 7.0])
    wr = calculate_weighted_rating(v, R, m=428, C=6.3)
    assert wr.iloc[0] == pytest.approx(6.3)          # sin votos: solo la media global
    assert 4.0 <= wr.iloc[1] <= 6.3
    assert 6.3 <= wr.iloc[2] <= 7.0


@pytest.mark.parametrize("m", [0, -5, float("nan")])
def test_weighted_rating_rechaza_m_no_positivo(m):
    with pytest.raises(ValueError, match="m debe ser"):
        calculate_weighted_rating(pd.Series([10]), pd.Series([7.0]), m=m, C=6.3)


def test_weighted_rating_rechaza_votos_negativos_y_c_invalido():
    with pytest.raises(ValueError, match="negativos"):
        calculate_weighted_rating(pd.Series([-1]), pd.Series([7.0]), m=10, C=6.3)
    with pytest.raises(ValueError, match="C debe ser"):
        calculate_weighted_rating(pd.Series([1]), pd.Series([7.0]), m=10, C=float("inf"))


def test_calcular_indicadores():
    s = pd.Series([1.0, 2.0, 3.0])
    r = calcular_indicadores(s, s)
    assert r["Diferencia media absoluta (MAE)"] == 0
    assert r["Correlación con vote_average"] == pytest.approx(1.0)
    with pytest.raises(ValueError, match="largos distintos"):
        calcular_indicadores(s, s.iloc[:2])


def test_diccionario_declara_columnas_que_no_usa_el_recomendador():
    d = diccionario_procesado()
    assert d["columna"].is_unique and len(d) == 16
    no_usadas = set(d.loc[d["uso"].str.startswith("no la usa"), "columna"])
    assert no_usadas == {"runtime_clean", "budget_clean", "revenue_clean"}
