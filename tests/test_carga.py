"""Pruebas de src/carga.py.

Ejecutar desde la raíz del repositorio:  python -m pytest
"""

import pandas as pd
import pytest

from src.carga import cargar, leer_archivo, verificar_esquema

COLUMNAS = ["movie_id", "title", "vote_count"]


@pytest.fixture
def csv_coma(tmp_path):
    ruta = tmp_path / "peliculas.csv"
    pd.DataFrame({"movie_id": [1, 2, 3], "title": ["A", "B", "C"], "vote_count": ["10", "20", "x"]}).to_csv(ruta, index=False)
    return ruta


def test_cargar_fuerza_las_columnas_numericas(csv_coma):
    df = cargar(csv_coma, COLUMNAS, columnas_numericas=["vote_count"])
    assert df.shape == (3, 3)
    assert df["vote_count"].tolist()[:2] == [10, 20]
    assert pd.isna(df["vote_count"].iloc[2])   # un texto suelto se vuelve NaN y no deja una columna de objetos


def test_cargar_infiere_el_punto_y_coma(tmp_path):
    ruta = tmp_path / "punto_y_coma.csv"
    pd.DataFrame({"movie_id": [1, 2, 3], "title": ["A", "B", "C"], "vote_count": [10, 20, 30]}).to_csv(ruta, sep=";", index=False)
    df = cargar(ruta, COLUMNAS)
    assert list(df.columns) == COLUMNAS and len(df) == 3


def test_verificar_esquema_informa_las_columnas_no_declaradas():
    df = pd.DataFrame({"movie_id": [1], "title": ["A"], "vote_count": [1], "extra": [0]})
    assert verificar_esquema(df, COLUMNAS) == {"declaradas": 3, "en_archivo": 4, "no_declaradas": ["extra"]}


def test_archivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError, match="no_existe"):
        cargar(tmp_path / "no_existe.csv", COLUMNAS)


def test_columna_faltante_nombra_la_columna(csv_coma):
    with pytest.raises(KeyError, match="director"):
        cargar(csv_coma, [*COLUMNAS, "director"])


def test_extension_no_reconocida(tmp_path):
    ruta = tmp_path / "datos.json"
    ruta.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="Extensión no reconocida"):
        leer_archivo(ruta)
