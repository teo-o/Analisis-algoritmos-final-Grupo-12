"""Tramo de mayor crecimiento del inventario por dividir y vencer.

Responsable: Mateo Orozco Oquendo.

El tramo óptimo está completo en la mitad izquierda, completo en la mitad
derecha, o cruza el punto medio. Las dos primeras opciones se resuelven
recursivamente; la tercera se calcula en tiempo lineal. Costo Θ(n log n).
"""

Tramo = tuple[int, int, int]  # (crecimiento_kg, hora_inicio, hora_fin)


def tramo_cruzado(
    cambios: list[int], bajo: int, medio: int, alto: int
) -> tuple[Tramo, int]:
    """Calcula el mejor tramo que contiene las horas ``medio`` y ``medio+1``.

    Crece desde el medio hacia la izquierda y hacia la derecha guardando la
    mejor suma de cada lado; el tramo cruzado es la unión de los dos.

    Args:
        cambios: cambio neto del inventario por hora, en kilogramos.
        bajo: primera hora del subarreglo.
        medio: última hora de la mitad izquierda.
        alto: última hora del subarreglo.

    Returns:
        El tramo (crecimiento, inicio, fin) que cruza el medio y el número de
        horas sumadas.
    """
    mejor_izq = cambios[medio]
    inicio = medio
    total = 0
    for hora in range(medio, bajo - 1, -1):
        total += cambios[hora]
        if total > mejor_izq:
            mejor_izq, inicio = total, hora
    mejor_der = cambios[medio + 1]
    fin = medio + 1
    total = 0
    for hora in range(medio + 1, alto + 1):
        total += cambios[hora]
        if total > mejor_der:
            mejor_der, fin = total, hora
    return (mejor_izq + mejor_der, inicio, fin), alto - bajo + 1


def tramo_recursivo(
    cambios: list[int], bajo: int, alto: int
) -> tuple[Tramo, int]:
    """Resuelve el subarreglo ``cambios[bajo..alto]`` recursivamente.

    Args:
        cambios: cambio neto del inventario por hora, en kilogramos.
        bajo: primera hora del subarreglo.
        alto: última hora del subarreglo.

    Returns:
        El mejor tramo del subarreglo y el número de horas sumadas.
    """
    if bajo == alto:
        return (cambios[bajo], bajo, bajo), 1
    medio = (bajo + alto) // 2
    izquierdo, ops_izq = tramo_recursivo(cambios, bajo, medio)
    derecho, ops_der = tramo_recursivo(cambios, medio + 1, alto)
    cruzado, ops_cruz = tramo_cruzado(cambios, bajo, medio, alto)
    mejor = max(izquierdo, derecho, cruzado, key=lambda tramo: tramo[0])
    return mejor, ops_izq + ops_der + ops_cruz


def tramo_dyv_con_conteo(cambios: list[int]) -> tuple[Tramo, int]:
    """Aplica dividir y vencer y devuelve también las horas sumadas.

    Args:
        cambios: cambio neto del inventario por hora, en kilogramos.

    Returns:
        El tramo (crecimiento, inicio, fin) de mayor crecimiento y el número
        de horas sumadas.

    Raises:
        ValueError: si la serie está vacía.
    """
    if not cambios:
        raise ValueError("La serie de cambios por hora está vacía.")
    return tramo_recursivo(cambios, 0, len(cambios) - 1)


def tramo_dyv(cambios: list[int]) -> Tramo:
    """Encuentra el tramo de horas consecutivas de mayor crecimiento.

    Args:
        cambios: cambio neto del inventario por hora, en kilogramos.

    Returns:
        El crecimiento máximo y las horas de inicio y fin del tramo.
    """
    return tramo_dyv_con_conteo(cambios)[0]
