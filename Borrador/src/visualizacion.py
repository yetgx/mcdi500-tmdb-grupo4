
import matplotlib.pyplot as plt
import pandas as pd


class VisualizadorRendimiento:
    """
    Genera gráficos de rendimiento a partir
    de un objeto AnalizadorRendimiento.

    No ejecuta benchmarks ni modifica las mediciones.
    """

    def __init__(self, analizador):
        from .medicion import AnalizadorRendimiento

        if not isinstance(analizador, AnalizadorRendimiento):
            raise TypeError(
                "Se requiere un objeto AnalizadorRendimiento."
            )

        self._analizador = analizador

    def _graficar(self, variable, titulo, eje_y):
        """Método interno compartido por ambas visualizaciones."""

        datos = self._analizador.resultados

        fig, ax = plt.subplots(figsize=(9, 5))

        for algoritmo, grupo in datos.groupby("algoritmo"):
            grupo = grupo.sort_values("n")

            ax.plot(
                grupo["n"],
                grupo[variable],
                marker="o",
                linewidth=2,
                label=algoritmo
            )

        ax.set_title(titulo)
        ax.set_xlabel("Cantidad de películas procesadas (N)")
        ax.set_ylabel(eje_y)

        ax.grid(True, alpha=0.3)
        ax.legend(title="Implementación")

        fig.tight_layout()

        return fig

    def grafico_tiempo(self):
        """Visualiza la evolución temporal del benchmark."""

        return self._graficar(
            variable="segundos",
            titulo="Comparación de tiempo de ejecución",
            eje_y="Tiempo de ejecución (segundos)"
        )

    def grafico_memoria(self):
        """Visualiza la memoria pico rastreada."""

        return self._graficar(
            variable="memoria_MB_trazada",
            titulo="Comparación de memoria pico rastreada",
            eje_y="Memoria pico rastreada (MiB)"
        )

    def grafico_aceleracion(self):
        """Visualiza la aceleración de la implementación por columnas."""
        aceleracion = self._analizador.calcular_aceleracion()
        fig, ax = plt.subplots(figsize=(9, 5))

        ax.plot(
            aceleracion.index,
            aceleracion.values,
            marker="o",
            linewidth=2
        )
        ax.axhline(1, color="gray", linestyle="--", linewidth=1)
        ax.set_title("Factor de aceleración de operaciones por columnas")
        ax.set_xlabel("Cantidad de películas procesadas (N)")
        ax.set_ylabel("Aceleración (x)")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

        return fig
