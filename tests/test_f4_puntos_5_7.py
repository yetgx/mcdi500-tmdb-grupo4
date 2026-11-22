import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest
from PIL import Image

from src.f4_puntos_5_7 import analizar_asociacion, cargar_contrato, controles_tecnicos, persistir

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
    figuras = {f"fig{i}": plt.subplots()[0] for i in range(1, 4)}
    for figura in figuras.values():
        figura.axes[0].plot([1, 2], [2, 3])
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
            plt.close(figura)
