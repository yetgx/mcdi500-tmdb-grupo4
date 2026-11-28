"""Transformadores: la clase base y sus clases hijas.

Módulo del proyecto MCDI500 - Grupo 4, adaptado del proyecto modelo de la Semana 2.
Lo usa el cuaderno F3/F3_NucleoAlgoritmico_TMDB.ipynb.

Los pasos propios de TMDB (DuracionPorGenero, CerosComoAusentes, ConstructorSopa,
CalidadPonderada, LogNaturalPlus1 y EscaladorMinMax con destino) reproducen la
Fase 2 llamando a las funciones de src/preparacion.py en lugar de copiarlas;
parten de la propuesta de Daniela Baeza (PR #43).
"""

import numpy as np

from .preparacion import (
    calculate_weighted_rating,
    ceros_a_nan,
    clean_genres,
    clean_text_feature,
    construir_sopa,
    genero_principal,
    imputar_metadatos,
)


class Transformador:
    """Clase base: lo que todos los pasos del pipeline comparten.

    Esta clase NO se usa directamente. Su trabajo es definir el contrato:
    qué métodos tendrá todo paso del pipeline y cómo se controla su estado.
    Las clases hijas solo completan lo que cambia de un paso a otro.
    """

    def __init__(self, columna):
        # Atributo público: cualquiera puede leerlo y cambiarlo
        self.columna = columna

        # Atributos con guion bajo: por convención, INTERNOS.
        # Python no lo impide, pero el guion bajo le dice a quien lee el código
        # que no debe tocarlos desde fuera de la clase.
        self._parametros = {}       # lo que el paso aprende del conjunto
        self._ajustado = False      # controla que no se transforme antes de ajustar

    # @property convierte un método en algo que se lee como atributo:
    # se escribe paso.nombre y no paso.nombre(). Y como no hay setter,
    # el valor NO se puede asignar desde fuera. Eso es encapsulamiento.
    @property
    def nombre(self):
        # type(self).__name__ devuelve el nombre de la clase REAL del objeto,
        # así que una CalidadPonderada se identifica como tal y no como Transformador
        return f"{type(self).__name__}({self.columna})"

    @property
    def parametros(self):
        # dict(...) crea una COPIA. Si devolviéramos self._parametros
        # directamente, quien lo recibe podría modificar el estado interno
        # del objeto sin que la clase se entere. A esto se le llama
        # copia defensiva.
        return dict(self._parametros)

    @property
    def _columnas_entrada(self):
        """Columnas que el paso necesita. Las hijas que leen varias la amplían."""
        return (self.columna,)

    def _validar_entrada(self, df):
        faltantes = [c for c in self._columnas_entrada if c not in df.columns]
        if faltantes:
            raise KeyError(f"{self.nombre}: faltan columnas de entrada {faltantes}.")

    def ajustar(self, df):
        """Aprende los parámetros del conjunto que recibe."""
        # 1) Validar la entrada ANTES de trabajar: si algo falta, se avisa
        #    acá y no veinte líneas más abajo con un error incomprensible
        self._validar_entrada(df)

        # 2) Delegar el cálculo a la clase hija. La base no sabe QUÉ se aprende;
        #    solo sabe CUÁNDO hay que aprenderlo.
        self._parametros = self.aprender(df)

        # 3) Registrar que ya se ajustó, para poder controlarlo después
        self._ajustado = True

        # 4) Devolver self permite encadenar: paso.ajustar(df).transformar(df)
        return self

    def transformar(self, df):
        """Aplica la transformación usando lo aprendido en ajustar()."""
        # Esta guarda es el corazón del encapsulamiento: impide un uso
        # incorrecto que de otro modo pasaría inadvertido
        if not self._ajustado:
            raise RuntimeError(f"{self.nombre}: hay que ajustar antes de transformar.")
        # Prueba puede traer un esquema distinto del de entrenamiento
        self._validar_entrada(df)

        # df.copy() evita modificar el DataFrame que nos pasaron. Sin esto,
        # el objeto original del usuario cambiaría sin que él lo pidiera.
        return self.aplicar(df.copy())

    def ajustar_transformar(self, df):
        """Atajo para el caso habitual: aprender y aplicar sobre el mismo conjunto."""
        return self.ajustar(df).transformar(df)

    # ---- Métodos que cada clase hija DEBE implementar -------------------
    # Se definen acá lanzando NotImplementedError para dejar el contrato
    # explícito: si una hija olvida implementarlos, el error lo dice claro.

    def aprender(self, df):
        """Calcula y devuelve los parámetros. Lo implementa cada clase hija."""
        raise NotImplementedError("Cada clase hija debe implementar aprender().")

    def aplicar(self, df):
        """Aplica la transformación. Lo implementa cada clase hija."""
        raise NotImplementedError("Cada clase hija debe implementar aplicar().")


class LogNaturalPlus1(Transformador):
    """Aplica log1p a una columna sesgada a la derecha (p. ej. popularity).

    No aprende nada del conjunto, pero conserva el contrato ajustar/transformar
    para encajar en el Pipeline sin tratamientos especiales. Con `destino`
    escribe en otra columna y conserva la original.
    """

    def __init__(self, columna, destino=None):
        super().__init__(columna)
        self._destino = destino or columna

    def aprender(self, df):
        return {"minimo": float(df[self.columna].min()), "destino": self._destino}

    def aplicar(self, df):
        if (df[self.columna] < 0).any():
            raise ValueError(f"{self.nombre}: log1p no admite valores negativos.")
        df[self._destino] = np.log1p(df[self.columna])
        return df


class EscaladorMinMax(Transformador):
    """Lleva la columna al rango [0, 1] con el mínimo y el máximo del ajuste.

    En prueba se aplican el mínimo y el rango de entrenamiento, así que un valor
    nuevo puede quedar fuera de [0, 1]: no se recorta, para no ocultarlo.
    """

    def __init__(self, columna, destino=None):
        super().__init__(columna)
        self._destino = destino or columna

    def aprender(self, df):
        minimo, maximo = float(df[self.columna].min()), float(df[self.columna].max())
        return {"minimo": minimo, "rango": (maximo - minimo) or 1.0, "destino": self._destino}

    def aplicar(self, df):
        df[self._destino] = (df[self.columna] - self._parametros["minimo"]) / self._parametros["rango"]
        return df


class ConstructorSopa(Transformador):
    """Construye la 'sopa de metadatos' del recomendador con las reglas de la Fase 2.

    Imputa los nulos ('Unknown' en géneros e idioma, vacío en productoras),
    limpia cada columna con clean_genres y clean_text_feature y las une con
    construir_sopa. Deja también genres_clean, companies_clean y lang_clean,
    que forman parte del conjunto exportado por F2.
    """

    def __init__(self, columna="metadata_soup", genero="genres",
                 productoras="production_companies", idioma="original_language",
                 max_productoras=3):
        super().__init__(columna)
        self._origen = {"genero": genero, "productoras": productoras, "idioma": idioma}
        self._max_productoras = max_productoras

    @property
    def _columnas_entrada(self):
        # La columna destino todavía no existe: se validan las de origen
        return tuple(self._origen.values())

    def aprender(self, df):
        return {"origen": dict(self._origen), "max_productoras": self._max_productoras}

    def aplicar(self, df):
        nombres_f2 = ["genres", "production_companies", "original_language"]
        metadatos = imputar_metadatos(df[list(self._origen.values())].set_axis(nombres_f2, axis="columns"))
        df["genres_clean"] = metadatos["genres"].map(clean_genres)
        df["companies_clean"] = metadatos["production_companies"].map(
            lambda texto: clean_text_feature(texto, self._max_productoras))
        df["lang_clean"] = metadatos["original_language"].str.lower()
        df[self.columna] = construir_sopa(df["genres_clean"], df["companies_clean"], df["lang_clean"])
        return df


class CerosComoAusentes(Transformador):
    """Interpreta el cero como dato no informado (budget, revenue): NaN sin imputar."""

    def __init__(self, columna, destino):
        super().__init__(columna)
        self._destino = destino

    def aprender(self, df):
        return {"ceros_en_ajuste": int((df[self.columna] == 0).sum()), "destino": self._destino}

    def aplicar(self, df):
        df[self._destino] = ceros_a_nan(df[self.columna])
        return df


class CalidadPonderada(Transformador):
    """Weighted Rating: aprende C (nota media) y m (percentil de votos) en el ajuste."""

    def __init__(self, columna="vote_average", votos="vote_count", destino="weighted_rating",
                 percentil=0.75):
        super().__init__(columna)
        self._votos = votos
        self._destino = destino
        self._percentil = percentil

    @property
    def _columnas_entrada(self):
        return (self.columna, self._votos)

    def aprender(self, df):
        c = float(df[self.columna].mean())
        m = float(df[self._votos].quantile(self._percentil))
        if not np.isfinite(c) or not np.isfinite(m) or m <= 0:
            raise ValueError(f"{self.nombre}: se requiere C finito y un percentil de votos positivo.")
        return {"C": c, "m": m, "percentil": self._percentil}

    def aplicar(self, df):
        df[self._destino] = calculate_weighted_rating(
            df[self._votos], df[self.columna], self._parametros["m"], self._parametros["C"])
        return df


class DuracionPorGenero(Transformador):
    """Imputa las duraciones en cero con la mediana de su género principal.

    Las medianas se aprenden en el ajuste; un género que no estaba en
    entrenamiento cae a la mediana global.
    """

    def __init__(self, columna="runtime", genero="genres", destino="runtime_clean"):
        super().__init__(columna)
        self._genero = genero
        self._destino = destino

    @property
    def _columnas_entrada(self):
        return (self.columna, self._genero)

    def aprender(self, df):
        positivos = ceros_a_nan(df[self.columna])
        if positivos.isna().all():
            raise ValueError(f"{self.nombre}: se requiere al menos una duración positiva.")
        grupos = genero_principal(df[self._genero])
        return {"medianas": positivos.groupby(grupos).median().dropna().to_dict(),
                "global": float(positivos.median())}

    def aplicar(self, df):
        medianas = genero_principal(df[self._genero]).map(self._parametros["medianas"])
        df[self._destino] = ceros_a_nan(df[self.columna]).fillna(medianas).fillna(self._parametros["global"])
        return df
