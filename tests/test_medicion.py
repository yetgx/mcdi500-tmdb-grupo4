"""Pruebas de src/medicion.py.

Ejecutar desde la raíz del repositorio:  python -m pytest
"""

import pytest

from src.medicion import comparar_versiones, escalabilidad, tiempo_minimo


def test_comparar_versiones_exige_mismo_resultado():
    versiones = {"suma": sum, "python": lambda xs: sum(x for x in xs)}
    tabla = comparar_versiones(versiones, list(range(100)), iguales=lambda a, b: a == b, repeticiones=2)
    assert tabla["versión"].tolist() == ["suma", "python"]
    with pytest.raises(AssertionError, match="mismo resultado"):
        comparar_versiones({"suma": sum, "max": max}, [1, 2, 3], iguales=lambda a, b: a == b)


def test_comparar_versiones_sin_versiones():
    with pytest.raises(ValueError):
        comparar_versiones({}, [1], iguales=lambda a, b: a == b)


def test_escalabilidad_y_tiempo_minimo():
    tabla = escalabilidad({"suma": sum}, [10, 100], lambda n: list(range(n)), lambda a, b: a == b, 2)
    assert tabla["n"].tolist() == [10, 100]
    resultado, segundos = tiempo_minimo(sum, [1, 2, 3], repeticiones=3)
    assert resultado == 6 and segundos >= 0
    with pytest.raises(ValueError):
        tiempo_minimo(sum, [1], repeticiones=0)
