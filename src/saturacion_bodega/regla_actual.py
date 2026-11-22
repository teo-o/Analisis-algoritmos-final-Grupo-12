"""Tramo de mayor crecimiento del inventario por fuerza bruta.

``tramo_cubico`` reproduce el programa actual del banco: evalúa todos los
tramos posibles y suma cada uno desde cero, Θ(n³). ``tramo_cuadratico`` es
la mejora inmediata: reutiliza la suma del tramo anterior, Θ(n²). Las dos
son exactas y sirven para verificar las estrategias rápidas.
"""

Tramo = tuple[int, int, int]  # (crecimiento_kg, hora_inicio, hora_fin)


def validar_serie(cambios: list[int]) -> None:
    """Rechaza una serie vacía: no existe ningún tramo que reportar.

    Args:
        cambios: cambio neto del inventario por hora, en kilogramos.

    Raises:
        ValueError: si la serie no tiene ninguna hora.
    """
    if not cambios:
        raise ValueError("La serie de cambios por hora está vacía.")


def tramo_cubico_con_conteo(cambios: list[int]) -> tuple[Tramo, int]:
    """Evalúa todos los tramos y suma cada uno desde cero.

    Args:
        cambios: cambio neto del inventario por hora, en kilogramos.

    Returns:
        El tramo (crecimiento, inicio, fin) de mayor crecimiento y el número
        de sumas realizadas.
    """
    validar_serie(cambios)
    n = len(cambios)
    mejor: Tramo = (cambios[0], 0, 0)
    sumas = 0
    for inicio in range(n):
        for fin in range(inicio, n):
            total = 0
            for hora in range(inicio, fin + 1):
                total += cambios[hora]
                sumas += 1
            if total > mejor[0]:
                mejor = (total, inicio, fin)
    return mejor, sumas


def tramo_cubico(cambios: list[int]) -> Tramo:
    """Reproduce el programa actual: todos los tramos, Θ(n³).

    Args:
        cambios: cambio neto del inventario por hora, en kilogramos.

    Returns:
        El crecimiento máximo y las horas de inicio y fin del tramo.
    """
    return tramo_cubico_con_conteo(cambios)[0]


def tramo_cuadratico_con_conteo(cambios: list[int]) -> tuple[Tramo, int]:
    """Evalúa todos los tramos reutilizando la suma del tramo anterior.

    Para cada hora de inicio, el tramo que termina en ``fin`` es el que
    terminaba en ``fin - 1`` más ``cambios[fin]``.

    Args:
        cambios: cambio neto del inventario por hora, en kilogramos.

    Returns:
        El tramo (crecimiento, inicio, fin) de mayor crecimiento y el número
        de sumas realizadas.
    """
    validar_serie(cambios)
    n = len(cambios)
    mejor: Tramo = (cambios[0], 0, 0)
    sumas = 0
    for inicio in range(n):
        total = 0
        for fin in range(inicio, n):
            total += cambios[fin]
            sumas += 1
            if total > mejor[0]:
                mejor = (total, inicio, fin)
    return mejor, sumas


def tramo_cuadratico(cambios: list[int]) -> Tramo:
    """Fuerza bruta mejorada: todos los tramos en Θ(n²).

    Args:
        cambios: cambio neto del inventario por hora, en kilogramos.

    Returns:
        El crecimiento máximo y las horas de inicio y fin del tramo.
    """
    return tramo_cuadratico_con_conteo(cambios)[0]