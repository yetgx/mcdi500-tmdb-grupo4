from pathlib import Path

import pandas as pd
import pytest

from src.f4_figuras import (
    cargar_resultados_f3, figura_evaluacion, figura_nota_ponderada, figura_tiempo_memoria,
)
from src.f4_puntos_5_7 import cargar_contrato

BASE = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def datos():
    entrenamiento, prueba, _, parametros, _ = cargar_contrato(BASE)
    mediciones, evaluacion = cargar_resultados_f3(BASE)
    return pd.concat([entrenamiento, prueba], ignore_index=True), parametros, mediciones, evaluacion


@pytest.fixture(autouse=True)
def cerrar_figuras():
    from matplotlib import pyplot as plt
    plt.switch_backend("Agg")   # el CI no tiene Tcl/Tk
    yield
    plt.close("all")


def test_nota_ponderada_por_tramos(datos):
    catalogo, parametros, *_ = datos
    figura, hallazgo = figura_nota_ponderada(catalogo, parametros)
    assert hallazgo["figura"] == "f1_nota_ponderada_por_votos"
    # tramos con n = 6.243, 4.196, 3.044, 2.000, 1.919 y 576 suman el catálogo completo
    assert "6.243 películas" in hallazgo["evidencia"] and "576 películas" in hallazgo["evidencia"]
    assert "0,941" in hallazgo["evidencia"] and "0,134" in hallazgo["evidencia"]
    assert len(figura.axes[0].patches) == 12


def test_tiempo_y_memoria_con_los_mismos_tamanos(datos):
    _, _, mediciones, _ = datos
    figura, hallazgo = figura_tiempo_memoria(mediciones)
    tiempo, memoria = figura.axes[:2]
    assert [l.get_xdata().tolist() for l in tiempo.lines] == [l.get_xdata().tolist() for l in memoria.lines]
    assert "argpartition (vectorizado) tardó 0,10 ms" in hallazgo["evidencia"]
    assert "17.978" in hallazgo["evidencia"]


def test_evaluacion_cifras_de_f3(datos):
    *_, evaluacion = datos
    figura, hallazgo = figura_evaluacion(evaluacion)
    texto = hallazgo["evidencia"]
    assert "99,0 % frente a 41,8 %" in texto and "81,4 % frente a 36,6 %" in texto and "80,0 % frente a 25,0 %" in texto
    assert "de 15,6 % a 80,0 %" in texto and "de 95,3 % a 81,4 %" in texto
    assert "no miden satisfacción" in texto


def test_hallazgos_compatibles_con_persistir(datos):
    from src.f4_puntos_5_7 import controles_tecnicos, persistir
    catalogo, parametros, mediciones, evaluacion = datos
    pares = [figura_nota_ponderada(catalogo, parametros), figura_tiempo_memoria(mediciones), figura_evaluacion(evaluacion)]
    ids = [h["figura"] for _, h in pares]
    assert len(set(ids)) == 3 and all(h["evidencia"].strip() and h["hallazgo"].strip() for _, h in pares)
    entradas = cargar_contrato(BASE)
    import tempfile
    with tempfile.TemporaryDirectory() as carpeta:
        rutas = persistir(carpeta, {h["figura"]: f for f, h in pares}, pd.DataFrame([h for _, h in pares]),
                          controles_tecnicos(*entradas), parametros)
        assert sorted(rutas) == sorted(ids)


def test_errores_claros(datos, tmp_path):
    catalogo, parametros, mediciones, evaluacion = datos
    with pytest.raises(FileNotFoundError, match="ejecutar F3"):
        cargar_resultados_f3(tmp_path)
    with pytest.raises(ValueError, match="columnas"):
        figura_nota_ponderada(catalogo.drop(columns="weighted_rating"), parametros)
    with pytest.raises(ValueError, match="cuatro alternativas"):
        figura_tiempo_memoria(mediciones[~mediciones["versión"].eq("montículo (iterativo)")])
    with pytest.raises(ValueError, match="tres criterios"):
        figura_evaluacion(evaluacion.iloc[:2])
