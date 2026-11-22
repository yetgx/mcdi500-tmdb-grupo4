"""Fase 4 TMDB: asociación, controles y persistencia. No modifica F1–F3."""
from __future__ import annotations

import json
import re
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

ENTRADAS = {
    "entrenamiento": "data/processed/entrenamiento_f3.csv",
    "prueba": "data/processed/prueba_f3.csv",
    "diccionario": "data/processed/movies_procesado_diccionario.csv",
    "parametros": "data/processed/parametros_f3.json",
    "original": "data/raw/movies_raw.csv",
}
COLUMNAS = ("vote_average", "vote_count", "popularity")
NULOS_INTENCIONALES = {"budget": "budget_clean", "revenue": "revenue_clean"}


def _es(valor, decimales=0):
    """Formato es-CL: punto para miles, coma para decimales."""
    return f"{valor:,.{decimales}f}".translate({44: ".", 46: ","})


def cargar_contrato(raiz):
    rutas = {nombre: Path(raiz) / rel for nombre, rel in ENTRADAS.items()}
    for nombre, ruta in rutas.items():
        if not ruta.is_file():
            fase = {"original": "restaurar data/raw/", "diccionario": "ejecutar F2"}.get(nombre, "ejecutar F3")
            raise FileNotFoundError(f"Falta {ENTRADAS[nombre]}; {fase}.")
    with rutas["parametros"].open(encoding="utf-8") as archivo:
        parametros = json.load(archivo)
    return (
        pd.read_csv(rutas["entrenamiento"]),
        pd.read_csv(rutas["prueba"]),
        pd.read_csv(rutas["diccionario"]),
        parametros,
        pd.read_csv(rutas["original"], usecols=[
            "movie_id", "original_language", "budget", "revenue", *COLUMNAS
        ]),
    )


def _rho(x, y):
    # Spearman equivale a Pearson de rangos medios; sin rango, no está definido.
    if len(x) < 2 or x.nunique() < 2 or y.nunique() < 2:
        return float("nan")
    return float(x.rank(method="average").corr(y.rank(method="average")))


def analizar_asociacion(catalogo):
    """Selecciona el |rho| mayor entre las tres columnas originales; no incluye derivados."""
    convenidas = list(COLUMNAS)
    datos = catalogo.loc[:, convenidas + ["lang_clean"]].copy().dropna(subset=convenidas)
    if len(datos) < 2:
        raise ValueError("Se necesitan al menos dos películas válidas para medir asociación.")
    pares = pd.DataFrame([
        {"x": x, "y": y, "n": len(datos), "rho": _rho(datos[x], datos[y])}
        for x, y in combinations(convenidas, 2)
    ])
    candidatos = pares.dropna(subset=["rho"]).assign(fuerza=lambda d: d["rho"].abs())
    if candidatos.empty:
        raise ValueError("No se puede calcular Spearman con columnas constantes.")
    x, y = candidatos.sort_values("fuerza", ascending=False, kind="stable").iloc[0][["x", "y"]]
    idioma = datos["lang_clean"].astype("string").str.strip().str.lower()
    conocidos = idioma.notna() & ~idioma.isin(["", "unknown", "und", "xx"])
    grupos = [
        ("Catálogo completo", datos),
        ("Idioma inglés", datos.loc[conocidos & idioma.eq("en").fillna(False)]),
        ("Otros idiomas conocidos", datos.loc[conocidos & idioma.ne("en").fillna(False)]),
        ("Idioma no informado", datos.loc[~conocidos]),
    ]
    estratos = pd.DataFrame([
        {"grupo": grupo, "n": len(tabla), "rho": _rho(tabla[x], tabla[y])}
        for grupo, tabla in grupos
    ])
    return (x, y), pares, estratos, len(catalogo) - len(datos)


def controles_tecnicos(entrenamiento, prueba, diccionario, parametros, original):
    controles = []
    def registrar(escenario, control, pasa, detalle=""):
        controles.append({
            "escenario": escenario, "control": control,
            "estado": "OK" if pasa else "FALLA", "detalle": detalle,
        })

    def excepcion(control, tipo, funcion):
        try:
            funcion()
        except tipo:
            registrar("excepción", control, True, tipo.__name__)
        else:
            registrar("excepción", control, False, "No lanzó la excepción esperada")

    columnas = diccionario["columna"].tolist()
    combinado = pd.concat([entrenamiento, prueba], ignore_index=True)
    ids = combinado["movie_id"]
    id_ok = all(t["movie_id"].notna().all() and t["movie_id"].is_unique for t in (combinado, original))
    registrar("normal", "Columnas y orden según el diccionario", list(entrenamiento) == list(prueba) == columnas,
              f"{_es(len(columnas))} columnas")
    registrar("normal", "Particiones versionadas: 14.382 + 3.596", (len(entrenamiento), len(prueba)) == (14382, 3596),
              f"{_es(len(entrenamiento))} + {_es(len(prueba))}")
    registrar("normal", "movie_id no nulo, único, sin cruces y mismo conjunto que el original",
              id_ok and len(combinado) == len(original) and set(ids) == set(original["movie_id"]),
              f"{_es(len(combinado))} ids")
    valido = id_ok and len(combinado) == len(original) and set(ids) == set(original["movie_id"])
    fuente = original.set_index("movie_id").reindex(ids) if valido else None
    for nombre in COLUMNAS:
        igual = valido and np.allclose(combinado[nombre], fuente[nombre], rtol=0, atol=0, equal_nan=True)
        registrar("normal", f"{nombre} coincide con el original por movie_id", igual)
    for origen, destino in NULOS_INTENCIONALES.items():
        mascara_cero_nulo = (fuente[origen].eq(0) | fuente[origen].isna()).to_numpy() if valido else None
        es_nulo = combinado[destino].isna().to_numpy()
        igual = valido and np.array_equal(mascara_cero_nulo, es_nulo) and np.allclose(
            combinado[destino].to_numpy()[~es_nulo], fuente[origen].to_numpy()[~es_nulo],
            rtol=0, atol=0,
        )
        registrar("límite", f"{destino}: ceros/nulos conservados como ausentes; montos restantes intactos",
                  igual, f"{_es(es_nulo.sum())} valores ausentes")
    calidad = parametros["pasos"]["CalidadPonderada(vote_average)"]
    c, m = float(calidad["C"]), float(calidad["m"])
    votos = combinado["vote_count"].to_numpy()
    promedio = combinado["vote_average"].to_numpy()
    esperado = (votos * promedio + m * c) / (votos + m)
    registrar("normal", "Weighted Rating coincide con la fórmula y los parámetros F3",
              m > 0 and np.allclose(combinado["weighted_rating"], esperado, rtol=1e-12, atol=1e-12),
              f"C={_es(c, 4)}; m={_es(m)}")
    minimo = votos.min()
    banda_minima = votos == minimo
    desvio_original = np.abs(promedio[banda_minima] - c)
    desvio_ponderado = np.abs(combinado["weighted_rating"].to_numpy()[banda_minima] - c)
    registrar("límite", "Con el mínimo de votos observado, Weighted Rating no se aleja de C",
              bool(np.all(desvio_ponderado <= desvio_original + 1e-12)),
              f"{_es(banda_minima.sum())} películas con {_es(minimo)} voto(s)")
    escalas = {
        "weighted_rating": combinado["weighted_rating"].to_numpy(),
        "popularity_log": np.log1p(combinado["popularity"].to_numpy()),
    }
    for nombre, values in escalas.items():
        escala = parametros["pasos"][f"EscaladorMinMax({nombre})"]
        minimo, rango = float(escala["minimo"]), float(escala["rango"])
        destino = escala["destino"]
        esperado = (values - minimo) / rango
        obtenido = combinado[destino].to_numpy()
        de_prueba = obtenido[len(entrenamiento):]
        fuera = ((de_prueba < 0) | (de_prueba > 1)).sum()
        registrar("límite", f"{destino}: MinMax de entrenamiento sin recorte en prueba",
                  rango > 0 and np.allclose(obtenido, esperado, rtol=1e-12, atol=1e-12)
                  and np.all((obtenido[:len(entrenamiento)] >= -1e-12)
                             & (obtenido[:len(entrenamiento)] <= 1 + 1e-12)),
                  f"prueba [{_es(de_prueba.min(), 9)}; {_es(de_prueba.max(), 9)}]; {_es(fuera)} fuera de [0; 1]")
    registrar("límite", "Estrato sin variación: rho no se declara como 0",
              bool(np.isnan(_rho(pd.Series([1, 1]), pd.Series([1, 2])))))
    excepcion("Falta un artefacto", FileNotFoundError, _cargar_en_carpeta_temporal_vacia)
    excepcion("Asociación con una fila", ValueError, lambda: analizar_asociacion(combinado.iloc[:1]))
    return pd.DataFrame(controles)


def _cargar_en_carpeta_temporal_vacia():
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as carpeta:
        cargar_contrato(carpeta)


def persistir(raiz, figuras, hallazgos, controles, parametros):
    """figuras: id -> Figure; hallazgos: DataFrame con figura/hallazgo/evidencia."""
    if controles.empty or not controles["estado"].eq("OK").all():
        raise ValueError("Hay controles técnicos sin superar; no se publicarán artefactos.")
    if len(figuras) < 3:
        raise ValueError("Faltan las tres figuras principales de la entrega.")
    if any(not re.fullmatch(r"[a-z0-9][a-z0-9_]*", id_) for id_ in figuras):
        raise ValueError("Los identificadores de figuras deben ser alfanuméricos, con guiones bajos.")
    requeridas = ["figura", "hallazgo", "evidencia"]
    exportar = hallazgos.loc[:, requeridas].copy()
    completo = exportar.notna().to_numpy().all() and all(
        exportar[c].map(lambda x: isinstance(x, str) and bool(x.strip())).all() for c in requeridas
    )
    if not completo or not exportar["figura"].is_unique or set(exportar["figura"]) != set(figuras):
        raise ValueError("Cada figura requiere exactamente un hallazgo y su evidencia, sin filas vacías.")
    raiz = Path(raiz)
    dir_figuras = raiz / "F4/figuras"
    docs = raiz / "docs"
    dir_figuras.mkdir(parents=True, exist_ok=True)
    docs.mkdir(parents=True, exist_ok=True)
    rutas = {}
    for id_, figura in figuras.items():
        ruta = dir_figuras / f"{id_}.png"
        figura.savefig(ruta, dpi=200, bbox_inches="tight")
        rutas[id_] = ruta.relative_to(raiz).as_posix()
    exportar.to_csv(docs / "hallazgos_f4.csv", index=False)
    controles.to_csv(docs / "controles_f4.csv", index=False)
    metadata = {"fase": "F4", "semilla_f3": parametros["semilla"],
                "entradas_contrato": list(ENTRADAS.values()), "figuras": rutas,
                "controles_superados": len(controles)}
    (docs / "metadatos_f4.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    return rutas
