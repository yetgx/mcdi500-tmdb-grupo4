"""Transformadores: la clase base y sus clases hijas.

Módulo del proyecto MCDI500 - Grupo 4, adaptado del proyecto modelo de la Semana 2.
Lo usa el cuaderno F3/F3_NucleoAlgoritmico_TMDB.ipynb.
"""

import numpy as np


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
        # así que un ImputadorMediana se identifica como tal y no como Transformador
        return f"{type(self).__name__}({self.columna})"

    @property
    def parametros(self):
        # dict(...) crea una COPIA. Si devolviéramos self._parametros
        # directamente, quien lo recibe podría modificar el estado interno
        # del objeto sin que la clase se entere. A esto se le llama
        # copia defensiva.
        return dict(self._parametros)

    def ajustar(self, df):
        """Aprende los parámetros del conjunto que recibe."""
        # 1) Validar la entrada ANTES de trabajar: si algo falta, se avisa
        #    acá y no veinte líneas más abajo con un error incomprensible
        if self.columna not in df.columns:
            raise KeyError(f"{self.nombre}: la columna no existe en el conjunto.")

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


class ImputadorMediana(Transformador):
    """Rellena los nulos con la mediana aprendida.

    El paréntesis (Transformador) es la HERENCIA: esta clase recibe todo lo
    que tiene Transformador sin volver a escribirlo. Solo implementa los dos
    métodos que le faltaban.
    """

    def aprender(self, df):
        return {"mediana": float(df[self.columna].median()),
                "nulos_en_ajuste": int(df[self.columna].isna().sum())}

    def aplicar(self, df):
        df[self.columna] = df[self.columna].fillna(self._parametros["mediana"])
        return df


class CodificadorNominal(Transformador):
    """Convierte una columna de categorías en columnas 0/1.

    El vocabulario se aprende en el ajuste: una categoría que solo aparece en
    prueba no genera columna nueva, porque el modelo no pudo aprender de ella.
    """

    def aprender(self, df):
        # Se guarda la lista de categorías ORDENADA, para que el resultado sea
        # el mismo en cada ejecución. Sin sorted(), el orden podría variar.
        return {"categorias": sorted(df[self.columna].dropna().unique())}

    def aplicar(self, df):
        # Se recorre el vocabulario aprendido, NO las categorías de este df.
        # Por eso una categoría nueva en prueba no genera columna: el modelo
        # nunca la vio y no podría haber aprendido nada de ella.
        for categoria in self._parametros["categorias"]:
            # Los nombres de columna no deben llevar espacios ni guiones
            etiqueta = str(categoria).strip().replace(" ", "_").replace("-", "_")
            # La comparación devuelve True/False; astype(int) lo pasa a 1/0
            df[f"{self.columna}_{etiqueta}"] = (df[self.columna] == categoria).astype(int)

        # La columna original ya no aporta: su información quedó en las nuevas
        return df.drop(columns=[self.columna])


class EscaladorEstandar(Transformador):
    """Centra en cero y escala a desviación uno."""

    def aprender(self, df):
        desviacion = float(df[self.columna].std())
        return {"media": float(df[self.columna].mean()),
                "desviacion": desviacion if desviacion != 0 else 1.0}

    def aplicar(self, df):
        df[self.columna] = ((df[self.columna] - self._parametros["media"])
                            / self._parametros["desviacion"])
        return df


class EliminadorColumnas(Transformador):
    """Quita columnas que no aportan al análisis, como el identificador."""

    def aprender(self, df):
        return {"existe": self.columna in df.columns}

    def aplicar(self, df):
        return df.drop(columns=[self.columna]) if self.columna in df.columns else df


class LogNaturalPlus1(Transformador):
    """Aplica log1p a una columna sesgada a la derecha (p. ej. popularity).

    No aprende nada del conjunto, pero conserva el contrato ajustar/transformar
    para encajar en el Pipeline sin tratamientos especiales.
    """

    def aprender(self, df):
        return {"minimo": float(df[self.columna].min())}

    def aplicar(self, df):
        if (df[self.columna] < 0).any():
            raise ValueError(f"{self.nombre}: log1p no admite valores negativos.")
        df[self.columna] = np.log1p(df[self.columna])
        return df


class EscaladorMinMax(Transformador):
    """Lleva la columna al rango [0, 1] con el mínimo y el máximo del ajuste."""

    def aprender(self, df):
        minimo, maximo = float(df[self.columna].min()), float(df[self.columna].max())
        return {"minimo": minimo, "rango": (maximo - minimo) or 1.0}

    def aplicar(self, df):
        df[self.columna] = (df[self.columna] - self._parametros["minimo"]) / self._parametros["rango"]
        return df


class ConstructorSopa(Transformador):
    """Construye la 'sopa de metadatos' del recomendador a partir de varias columnas.

    Cada columna aporta tokens en minúsculas; las productoras se compactan
    (sin espacios) para tratarlas como entidades únicas y se limitan a las
    primeras `max_productoras`. Los nulos quedan como cadena vacía.
    """

    def __init__(self, columna="metadata_soup", genero="genres",
                 productoras="production_companies", idioma="original_language",
                 max_productoras=3):
        super().__init__(columna)
        self._origen = {"genero": genero, "productoras": productoras, "idioma": idioma}
        self._max_productoras = max_productoras

    def ajustar(self, df):
        # La columna destino todavía no existe: se validan las de origen
        faltantes = [c for c in self._origen.values() if c not in df.columns]
        if faltantes:
            raise KeyError(f"{self.nombre}: faltan columnas de origen {faltantes}.")
        self._parametros = self.aprender(df)
        self._ajustado = True
        return self

    def aprender(self, df):
        return {"origen": dict(self._origen), "max_productoras": self._max_productoras}

    def aplicar(self, df):
        genero = df[self._origen["genero"]].fillna("").str.replace("|", " ", regex=False).str.lower()
        productoras = df[self._origen["productoras"]].fillna("").map(
            lambda t: " ".join(p.replace(" ", "").lower()
                               for p in t.split("|")[: self._max_productoras] if p)
        )
        idioma = df[self._origen["idioma"]].fillna("").str.lower()
        df[self.columna] = (genero + " " + productoras + " " + idioma).str.split().str.join(" ")
        return df
