"""Algoritmos recursivos y sus equivalentes iterativos.

Módulo del proyecto MCDI500 - Grupo 4. Lo usa el cuaderno F3/F3_NucleoAlgoritmico_TMDB.ipynb.

Dos problemas del proyecto, cada uno resuelto de forma recursiva y de forma
iterativa, con el mismo resultado:

- aplanar los metadatos anidados de una película (géneros, productoras e
  idioma) en una lista de tokens. Parte de la propuesta de Juan Pablo
  González (PR #41) y de Elías Manríquez (PR #44);
- elegir las k películas de mayor puntaje entre todo el catálogo, que es el
  último paso de cada recomendación.
"""

import heapq

import numpy as np

PROFUNDIDAD_MAXIMA = 50


# ---- Aplanar metadatos anidados ----------------------------------------------

def aplanar_recursivo(datos, profundidad=0, max_profundidad=PROFUNDIDAD_MAXIMA):
    """Devuelve los textos no vacíos de una estructura de listas o tuplas anidadas.

    Caso base: un texto (se devuelve en una lista) o None (lista vacía).
    Caso recursivo: una lista, cuyo resultado es la concatenación de aplanar
    cada elemento. Conserva el orden de izquierda a derecha.
    """
    if profundidad > max_profundidad:
        raise RecursionError(f"aplanar_recursivo: la estructura supera {max_profundidad} niveles.")
    if datos is None:
        return []
    if isinstance(datos, str):
        return [datos] if datos.strip() else []
    if not isinstance(datos, (list, tuple)):
        raise TypeError(f"aplanar_recursivo: tipo no soportado {type(datos).__name__}.")
    resultado = []
    for elemento in datos:
        resultado.extend(aplanar_recursivo(elemento, profundidad + 1, max_profundidad))
    return resultado


def aplanar_iterativo(datos):
    """Mismo resultado que aplanar_recursivo con una pila explícita y sin límite de profundidad."""
    pila, resultado = [datos], []
    while pila:
        actual = pila.pop()
        if actual is None:
            continue
        if isinstance(actual, str):
            if actual.strip():
                resultado.append(actual)
        elif isinstance(actual, (list, tuple)):
            pila.extend(reversed(actual))   # al revés, para sacar primero el de la izquierda
        else:
            raise TypeError(f"aplanar_iterativo: tipo no soportado {type(actual).__name__}.")
    return resultado


def profundidad(datos):
    """Niveles de anidación de la estructura (un texto o None tiene profundidad 0), recursivo."""
    if not isinstance(datos, (list, tuple)):
        return 0
    return 1 + max((profundidad(e) for e in datos), default=0)


# ---- Las k películas de mayor puntaje --------------------------------------------
# Las cuatro versiones devuelven los mismos índices en el mismo orden: puntaje de
# mayor a menor y, ante un empate, el índice menor primero. Sin esa regla de
# desempate dos versiones correctas podrían devolver películas distintas.

def _validar_top_k(puntajes, k):
    puntajes = np.asarray(puntajes, dtype=float)
    if puntajes.ndim != 1:
        raise ValueError("top_k: los puntajes deben ser un vector.")
    if not isinstance(k, (int, np.integer)) or k < 1:
        raise ValueError(f"top_k: k debe ser un entero positivo y se recibió {k!r}.")
    if np.isnan(puntajes).any():
        raise ValueError("top_k: los puntajes no admiten NaN.")
    return puntajes, min(int(k), len(puntajes))


def _ordenar(puntajes, indices):
    # lexsort ordena por la última clave primero: -puntaje y luego el índice
    indices = np.asarray(indices, dtype=np.int64)
    return indices[np.lexsort((indices, -puntajes[indices]))]


def top_k_ordenando(puntajes, k):
    """Ordena el catálogo completo y toma los k primeros: O(N log N)."""
    puntajes, k = _validar_top_k(puntajes, k)
    return _ordenar(puntajes, np.arange(len(puntajes)))[:k]


def top_k_recursivo(puntajes, k, hoja=64):
    """Divide y vencerás: el top k de cada mitad y luego el top k de la unión.

    T(N) = 2·T(N/2) + O(k log k): con k fijo crece en forma lineal con N y la
    profundidad de la recursión es log2(N / hoja), unas 9 llamadas anidadas
    para el catálogo completo.
    """
    puntajes, k = _validar_top_k(puntajes, k)

    def resolver(inicio, fin):
        if fin - inicio <= hoja:                          # caso base: se ordena el tramo
            return _ordenar(puntajes, np.arange(inicio, fin))[:k]
        medio = (inicio + fin) // 2
        candidatos = np.concatenate((resolver(inicio, medio), resolver(medio, fin)))
        return _ordenar(puntajes, candidatos)[:k]

    return resolver(0, len(puntajes))


def top_k_monticulo(puntajes, k):
    """Recorrido iterativo con un montículo de tamaño k: O(N log k) y memoria O(k)."""
    puntajes, k = _validar_top_k(puntajes, k)
    # heapq.nlargest con la clave (puntaje, -índice) aplica el mismo desempate
    mejores = heapq.nlargest(k, range(len(puntajes)), key=lambda i: (puntajes[i], -i))
    return np.asarray(mejores, dtype=np.int64)


def top_k_vectorizado(puntajes, k):
    """np.argpartition separa los k mayores en O(N) y solo esos se ordenan."""
    puntajes, k = _validar_top_k(puntajes, k)
    if k == len(puntajes):
        return top_k_ordenando(puntajes, k)
    umbral = puntajes[np.argpartition(-puntajes, k - 1)[k - 1]]   # k-ésimo puntaje más alto
    seguros = np.flatnonzero(puntajes > umbral)
    empatados = np.flatnonzero(puntajes == umbral)[: k - len(seguros)]   # los de menor índice
    return _ordenar(puntajes, np.concatenate((seguros, empatados)))
