import json
from pathlib import Path

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import pandas as pd
import pytest
from PIL import Image

from src.f4_puntos_5_7 import (
    _es, analizar_asociacion, cargar_contrato, controles_tecnicos, figura_asociacion_votos,
    figura_umbral_votos, persistir, persistir_apoyo, preparar_evaluacion, verificar_contra_f3,
)

BASE = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def entradas():
    return cargar_contrato(BASE)


def test_catalogo_exacto(entradas):
    x_y, pares, estratos, excluidas = analizar_asociacion(
        pd.concat(entradas[:2], ignore_index=True),
    )
    assert x_y == ("vote_count", "popularity")
    assert len(pares) == 3 and excluidas == 0
    assert estratos["n"].tolist() == [17978, 10615, 7355, 8]
    assert estratos["rho"].tolist() == pytest.approx(
        [0.626438, 0.751378, 0.377962, 0.571429], abs=1e-6,
    )


def test_controles_y_fuga_de_ids(entradas):
    controles = controles_tecnicos(*entradas)
    assert controles["estado"].eq("OK").all()
    assert controles.groupby("escenario").size().to_dict() == {"normal": 7, "límite": 6, "excepción": 2}
    entrenamiento, prueba, *resto = entradas
    repetido = prueba.copy()
    repetido.loc[0, "movie_id"] = entrenamiento.loc[0, "movie_id"]
    alterado = controles_tecnicos(entrenamiento, repetido, *resto)
    assert alterado.loc[alterado["control"].str.startswith("movie_id"), "estado"].tolist() == ["FALLA"]


def test_constante_en_un_estrato():
    tabla = pd.DataFrame({
        "lang_clean": ["en", "en", "es", "es", None],
        "vote_count": [1, 1, 2, 3, 4],
        "vote_average": [5, 6, 4, 7, 5],
        "popularity": [8, 9, 10, 11, 12],
    })
    _, _, estratos, _ = analizar_asociacion(tabla)
    assert pd.isna(estratos.loc[estratos["grupo"].eq("Idioma inglés"), "rho"].iloc[0])


def test_exporta_imagenes_a_200_ppp_y_tabla_unica(tmp_path, entradas):
    figuras = {f"fig{i}": Figure() for i in range(1, 4)}
    for figura in figuras.values():
        # El CI no necesita una ventana ni una instalación de Tcl/Tk para guardar un PNG.
        FigureCanvasAgg(figura)
        figura.subplots().plot([1, 2], [2, 3])
    hallazgos = pd.DataFrame([
        {"figura": clave, "hallazgo": f"Prueba {clave}", "evidencia": "Dato sintético"} for clave in figuras
    ])
    controles = controles_tecnicos(*entradas)
    try:
        with pytest.raises(ValueError, match="exactamente un hallazgo"):
            persistir(tmp_path, figuras, hallazgos.iloc[:2], controles, entradas[3])
        assert not list(tmp_path.iterdir())
        rutas = persistir(tmp_path, figuras, hallazgos, controles, entradas[3])
        assert len(rutas) == 3
        for rel in rutas.values():
            with Image.open(tmp_path / rel) as imagen:
                assert imagen.format == "PNG"
                assert imagen.info["dpi"] == pytest.approx((200, 200), abs=0.02)
        pd.testing.assert_frame_equal(hallazgos, pd.read_csv(tmp_path / "docs/hallazgos_f4.csv"))
        meta = json.loads((tmp_path / "docs/metadatos_f4.json").read_text())
        assert meta["figuras"] == rutas and meta["controles_superados"] == len(controles)
    finally:
        for figura in figuras.values():
            figura.clear()


def test_cifras_con_formato_es_cl(entradas):
    assert _es(14382) == "14.382" and _es(0.6264, 3) == "0,626" and _es(-0.0231, 3) == "-0,023"
    detalles = controles_tecnicos(*entradas)["detalle"].astype(str)
    assert not detalles.str.contains(r"\.\d{4,}").any()
    assert detalles.str.contains("14.382 + 3.596", regex=False).any()


def test_apoyo_grafico_versionado_y_separado(tmp_path, entradas, monkeypatch):
    monkeypatch.setenv("MPLBACKEND", "Agg")
    from matplotlib import pyplot as plt
    plt.switch_backend("Agg")

    catalogo = pd.concat(entradas[:2], ignore_index=True)
    figura_asociacion, asociacion = figura_asociacion_votos(catalogo)
    figura_umbral, umbral = figura_umbral_votos(entradas[-1])
    try:
        assert {"0,751", "10.615", "0,378", "7.355"} <= set(
            asociacion["evidencia"].replace("ρ=", "").replace("(n=", "").replace(")", "")
            .replace(";", "").split()
        )
        assert "427,75" in umbral["evidencia"] and "4.495 de 17.978" in umbral["evidencia"]
        assert figura_asociacion.axes[0].get_xlim() == figura_asociacion.axes[1].get_xlim()
        assert figura_asociacion.axes[0].collections[0].norm is figura_asociacion.axes[1].collections[0].norm
        controles = controles_tecnicos(*entradas)
        registro = [(figura_asociacion, asociacion), (figura_umbral, umbral)]
        with pytest.raises(ValueError, match="controles"):
            persistir_apoyo(tmp_path, registro, controles.assign(estado="FALLA"))
        assert not list(tmp_path.iterdir())
        (tmp_path / "docs").mkdir()
        principal = tmp_path / "docs/hallazgos_f4.csv"
        principal.write_text("registro grupal")
        rutas = persistir_apoyo(tmp_path, registro, controles)
        for ruta in rutas[:-1]:
            with Image.open(tmp_path / ruta) as imagen:
                assert imagen.format == "PNG"
                assert imagen.info["dpi"] == pytest.approx((200, 200), abs=0.02)
        assert pd.read_csv(tmp_path / rutas[-1])["figura"].tolist() == [asociacion["figura"], umbral["figura"]]
        assert principal.read_text() == "registro grupal"
    finally:
        plt.close(figura_asociacion)
        plt.close(figura_umbral)


def test_capitulo_8_reproduce_la_evaluacion_de_f3():
    prep = preparar_evaluacion(BASE)
    assert prep["N_CATALOGO"] == 17978 and len(prep["CONSULTAS_TEST"]) == 3596 and prep["TOP_K"] == 10
    assert prep["P75"] == pytest.approx(427.75)
    assert set(prep["vis"].loc[prep["CONSULTAS_TEST"], "movie_id"]) == set(prep["test_f3"]["movie_id"])
    q = int(prep["CONSULTAS_TEST"][0])
    elegidas = prep["top_k_por_score"](prep["puntajes_consulta"](q), q)
    assert len(elegidas) == 10 and q not in elegidas
    verificacion = verificar_contra_f3(prep, BASE)
    assert len(verificacion) == 6 and verificacion["coincide"].all()
