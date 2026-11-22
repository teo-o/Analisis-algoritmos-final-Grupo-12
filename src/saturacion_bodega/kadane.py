
Tramo = tuple[int, int, int]  # (crecimiento_kg, hora_inicio, hora_fin)


def tramo_kadane_con_conteo(cambios: list[int]) -> tuple[Tramo, int]:
    """Recorre la serie una vez y devuelve también las horas revisadas.

    Recurrencia:
        mejor_aqui(0) = cambios[0]
        mejor_aqui(j) = max(cambios[j], mejor_aqui(j - 1) + cambios[j])
        respuesta     = max sobre j de mejor_aqui(j)

    Args:
        cambios: cambio neto del inventario por hora, en kilogramos.

    Returns:
        El tramo (crecimiento, inicio, fin) de mayor crecimiento y el número
        de horas revisadas.

    Raises:
        ValueError: si la serie está vacía.
    """
    if not cambios:
        raise ValueError("La serie de cambios por hora está vacía.")
    mejor_aqui = cambios[0]
    inicio_aqui = 0
    mejor: Tramo = (cambios[0], 0, 0)
    for hora in range(1, len(cambios)):
        if mejor_aqui < 0:
            mejor_aqui, inicio_aqui = cambios[hora], hora
        else:
            mejor_aqui += cambios[hora]
        if mejor_aqui > mejor[0]:
            mejor = (mejor_aqui, inicio_aqui, hora)
    return mejor, len(cambios)


def tramo_kadane(cambios: list[int]) -> Tramo:
    """Encuentra el tramo de horas consecutivas de mayor crecimiento.

    Args:
        cambios: cambio neto del inventario por hora, en kilogramos.

    Returns:
        El crecimiento máximo y las horas de inicio y fin del tramo.
    """
    return tramo_kadane_con_conteo(cambios)[0]