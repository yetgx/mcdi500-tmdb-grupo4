"""Algoritmos explícitos para demostrar división recursiva sobre etiquetas anidadas."""

def aplanar_recursivo(datos, max_profundidad=30):
    """Obtiene tokens de str, list o tuple anidados; sin tratar str como iterable."""
    if max_profundidad < 0:
        raise ValueError("Profundidad máxima excedida")
    if datos is None:
        return []
    if isinstance(datos, str):
        return [datos] if datos.strip() else []
    if not isinstance(datos, (list, tuple)):
        raise TypeError(f"Tipo no soportado: {type(datos).__name__}")
    resultado=[]
    for item in datos:
        resultado.extend(aplanar_recursivo(item,max_profundidad-1))
    return resultado

def aplanar_iterativo(datos):
    """Implementación funcional equivalente usando pila explícita."""
    pila=[datos]; salida=[]
    while pila:
        actual=pila.pop()
        if actual is None: continue
        if isinstance(actual,str):
            if actual.strip():salida.append(actual)
        elif isinstance(actual,(list,tuple)):
            pila.extend(reversed(actual))
        else:raise TypeError(f"Tipo no soportado: {type(actual).__name__}")
    return salida
