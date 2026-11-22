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


def _estratos_idioma(datos):
    idioma = datos["lang_clean"].astype("string").str.strip().str.lower()
    conocidos = idioma.notna() & ~idioma.isin(["", "unknown", "und", "xx"])
    return [
        ("Catálogo completo", datos),
        ("Idioma inglés", datos.loc[conocidos & idioma.eq("en").fillna(False)]),
        ("Otros idiomas conocidos", datos.loc[conocidos & idioma.ne("en").fillna(False)]),
        ("Idioma no informado", datos.loc[~conocidos]),
    ]


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
    grupos = _estratos_idioma(datos)
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


def figura_asociacion_votos(catalogo):
    """Gráfico complementario: densidad y Spearman sobre los mismos casos completos."""
    from matplotlib import pyplot as plt
    from matplotlib.colors import LogNorm

    datos = catalogo.loc[:, [*COLUMNAS, "lang_clean"]].dropna(subset=list(COLUMNAS))
    _, ingles, otros, sin_idioma = _estratos_idioma(datos)
    x, y = "vote_count", "popularity"
    valores = datos[[x, y]].to_numpy()
    if not (np.isfinite(valores).all() and (valores >= 0).all()):
        raise ValueError("Votos y popularidad deben ser finitos y no negativos para graficar log(1 + valor).")

    log_valores = np.log1p(valores)
    bajos = log_valores.min(axis=0)
    altos = log_valores.max(axis=0)
    margen = np.maximum((altos - bajos) * 0.02, 0.01)
    extension = (bajos[0] - margen[0], altos[0] + margen[0],
                 bajos[1] - margen[1], altos[1] + margen[1])
    figura, ejes = plt.subplots(1, 2, figsize=(9, 4.4), sharex=True, sharey=True, layout="constrained")
    mallas = []
    resumen = []
    for eje, (nombre, tabla) in zip(ejes, [ingles, otros]):
        rho = _rho(tabla[x], tabla[y])
        rho_txt = _es(rho, 3) if np.isfinite(rho) else "no definido"
        resumen.append(f"{nombre}: ρ={rho_txt} (n={_es(len(tabla))})")
        malla = eje.hexbin(np.log1p(tabla[x]), np.log1p(tabla[y]), extent=extension,
                         gridsize=32, mincnt=1, cmap="viridis")
        mallas.append(malla)
        eje.set_title(f"{nombre}\nρ de Spearman={rho_txt} · n={_es(len(tabla))}")
        eje.set_xlabel("log(1 + número de votos)")
        eje.set_xlim(extension[:2])
        eje.set_ylim(extension[2:])
    maximo = max((malla.get_array().max() for malla in mallas if malla.get_array().size), default=1)
    norma = LogNorm(vmin=1, vmax=max(2, maximo))
    for malla in mallas:
        malla.set_norm(norma)
    ejes[0].set_ylabel("log(1 + popularidad TMDB)")
    figura.colorbar(mallas[-1], ax=ejes, label="Películas por celda (escala log)")
    titulo = "La asociación entre votos y popularidad varía según el idioma"
    figura.suptitle(titulo, fontweight="bold")
    figura.supxlabel("Fuente: particiones versionadas de F3. Misma escala y recuento por celda en ambos grupos.",
                     fontsize=8)
    evidencia = "; ".join(resumen) + f"; idioma no informado fuera de la figura: {_es(len(sin_idioma[1]))}."
    return figura, {"figura": "p05_votos_popularidad", "hallazgo": titulo,
                    "evidencia": evidencia + " Asociación descriptiva, no causal."}


def figura_umbral_votos(original):
    """Diagnóstico complementario del corte de evaluación: P75 del catálogo original."""
    from matplotlib import pyplot as plt

    votos = original["vote_count"].dropna()
    valores = votos.to_numpy()
    if not len(votos) or not (np.isfinite(valores).all() and (valores >= 0).all()
                             and np.equal(valores, np.floor(valores)).all()):
        raise ValueError("Se necesitan recuentos de votos enteros, finitos y no negativos.")
    p75 = votos.quantile(0.75)
    corte = int(np.ceil(p75))
    cantidad = int(votos.ge(corte).sum())
    porcentaje = 100 * cantidad / len(votos)
    figura, eje = plt.subplots(figsize=(8, 4), layout="constrained")
    eje.hist(np.log1p(votos), bins=38, color="#437f90", edgecolor="white", linewidth=0.45)
    eje.axvline(np.log1p(p75), color="#9a391e", linestyle="--", linewidth=2,
                label=f"P75 = {_es(p75, 2)}; corte ≥ {_es(corte)} votos")
    eje.set(xlabel="log(1 + número de votos)", ylabel="Películas por intervalo (n)")
    eje.legend(frameon=False)
    titulo = "El corte de respaldo de votos deja fuera a la mayoría del catálogo"
    eje.set_title(titulo, fontweight="bold")
    figura.supxlabel(f"Fuente: data/raw/movies_raw.csv · {_es(len(votos))} películas con votos informados.",
                     fontsize=8)
    evidencia = (f"P75 del catálogo: {_es(p75, 2)} votos. {_es(cantidad)} de {_es(len(votos))} películas "
                 f"({_es(porcentaje, 1)} %) alcanzan al menos {_es(corte)} votos. "
                 "No es el parámetro m del Weighted Rating, estimado con entrenamiento.")
    return figura, {"figura": "p06_umbral_respaldo_votos", "hallazgo": titulo, "evidencia": evidencia}


def persistir_apoyo(raiz, figuras_con_hallazgos, controles):
    """Guarda solo los gráficos complementarios de este aporte; no toca la entrega final."""
    if controles.empty or not controles["estado"].eq("OK").all():
        raise ValueError("Hay controles técnicos sin superar; no se exportará el apoyo visual.")
    apoyo = list(figuras_con_hallazgos)
    tabla = pd.DataFrame(h for _, h in apoyo)
    esperadas = {"p05_votos_popularidad", "p06_umbral_respaldo_votos"}
    if len(tabla) != len(esperadas) or "figura" not in tabla or set(tabla["figura"]) != esperadas:
        raise ValueError("El apoyo visual necesita las dos figuras complementarias con sus hallazgos.")
    raiz = Path(raiz)
    carpeta = raiz / "F4/figuras/apoyo_puntos_5_7"
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = []
    for figura, hallazgo in apoyo:
        ruta = carpeta / f"{hallazgo['figura']}.png"
        figura.savefig(ruta, dpi=200)
        rutas.append(ruta.relative_to(raiz).as_posix())
    csv = carpeta / "hallazgos_apoyo.csv"
    tabla.to_csv(csv, index=False)
    return [*rutas, csv.relative_to(raiz).as_posix()]
