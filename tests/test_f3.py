import pandas as pd
import pytest
from src.transformadores import ConstructorSopa, EscaladorMinMax
from src.pipeline import Pipeline
from src.recursividad import aplanar_recursivo, aplanar_iterativo
from src.medicion import AnalizadorRendimiento
from src.visualizacion import VisualizadorRendimiento

def test_recursividad_equivalencia():
    x=["drama",["comedia",["accion",None]],()]
    assert aplanar_recursivo(x)==aplanar_iterativo(x)==["drama","comedia","accion"]

def test_recursividad_excepciones():
    with pytest.raises(TypeError): aplanar_recursivo([3])
    with pytest.raises(ValueError): aplanar_recursivo([["a"]],max_profundidad=0)

def test_pipeline_estado():
    p=Pipeline([EscaladorMinMax("x")])
    with pytest.raises(RuntimeError): p.transformar(pd.DataFrame({"x":[1,2]}))
    p.ajustar(pd.DataFrame({"x":[1,2]}))
    assert p.transformar(pd.DataFrame({"x":[3]}))["x"].iloc[0] == 2

def test_pipeline_ajuste_transaccional():
    p=Pipeline([EscaladorMinMax("x"),EscaladorMinMax("no_existe")])
    with pytest.raises(KeyError): p.ajustar(pd.DataFrame({"x":[1,2]}))
    assert not p._ajustado
    assert not p.pasos_ejecutados()[0]._ajustado

def test_sopa_texto_invalido():
    df=pd.DataFrame({"genres":[3],"production_companies":["A"],"original_language":["es"]})
    with pytest.raises(TypeError): ConstructorSopa().ajustar_transformar(df)

def test_visualizador_grafico_aceleracion():
    resultados = pd.DataFrame({
        "n": [100, 100, 200, 200],
        "algoritmo": ["iterrows", "columnas", "iterrows", "columnas"],
        "segundos": [4.0, 2.0, 6.0, 3.0],
        "memoria_MB_trazada": [2.0, 1.0, 3.0, 1.5],
    })
    analizador = AnalizadorRendimiento(resultados)
    figura = VisualizadorRendimiento(analizador).grafico_aceleracion()
    assert list(figura.axes[0].lines[0].get_ydata()) == [2.0, 2.0]
