"""Cargue de un vehículo del banco de alimentos: mochila 0/1 por PD.

Responsable: Mateo Orozco Oquendo.

La tabla ``mejor[i][c]`` guarda el máximo valor nutricional que se puede
cargar usando solo los primeros ``i`` lotes con una capacidad de ``c`` kg.
"""

Lote = tuple[int, int, int]  # (peso_kg, valor_nutricional, dias_para_vencer)


def construir_tabla(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[list[list[int]], int]:
    """Llena la tabla de la mochila 0/1 de abajo hacia arriba.

    Recurrencia, para i = 1..n y c = 0..W:
        mejor[0][c] = 0
        mejor[i][c] = mejor[i-1][c]                          si peso_i > c
        mejor[i][c] = max(mejor[i-1][c],
                          mejor[i-1][c - peso_i] + valor_i)  si peso_i <= c

    Args:
        lotes: lotes candidatos de la ruta; no se fraccionan.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.

    Returns:
        La tabla de (n + 1) x (W + 1) celdas y el número de celdas calculadas
        (operación elemental que se cuenta en la medición).
    """
    n = len(lotes)
    mejor = [[0] * (capacidad_kg + 1) for _ in range(n + 1)]
    celdas = 0
    for i in range(1, n + 1):
        peso, valor, _ = lotes[i - 1]
        fila_anterior = mejor[i - 1]
        fila = mejor[i]
        for c in range(capacidad_kg + 1):
            sin_lote = fila_anterior[c]
            if peso <= c:
                con_lote = fila_anterior[c - peso] + valor
                fila[c] = con_lote if con_lote > sin_lote else sin_lote
            else:
                fila[c] = sin_lote
            celdas += 1
    return mejor, celdas


def reconstruir_lotes(
    mejor: list[list[int]], lotes: list[Lote], capacidad_kg: int
) -> list[int]:
    """Recorre la tabla desde la última fila para saber qué lotes subieron.

    Si ``mejor[i][c]`` difiere de ``mejor[i-1][c]``, el lote ``i`` subió al
    vehículo y se descuenta su peso de la capacidad restante.

    Args:
        mejor: tabla llena por ``construir_tabla``.
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.

    Returns:
        Los índices (base 0) de los lotes cargados, en orden creciente.
    """
    elegidos: list[int] = []
    c = capacidad_kg
    for i in range(len(lotes), 0, -1):
        if mejor[i][c] != mejor[i - 1][c]:
            elegidos.append(i - 1)
            c -= lotes[i - 1][0]
    elegidos.reverse()
    return elegidos


def cargar_vehiculo_con_conteo(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int], int]:
    """Resuelve la mochila 0/1 y devuelve también las celdas calculadas.

    Args:
        lotes: lotes candidatos de la ruta; no se fraccionan.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.

    Returns:
        El valor nutricional máximo, los índices de los lotes cargados y el
        número de celdas de la tabla que se calcularon.
    """
    if capacidad_kg < 0:
        raise ValueError("La capacidad del vehículo no puede ser negativa.")
    mejor, celdas = construir_tabla(lotes, capacidad_kg)
    elegidos = reconstruir_lotes(mejor, lotes, capacidad_kg)
    return mejor[len(lotes)][capacidad_kg], elegidos, celdas


def cargar_vehiculo(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int]]:
    """Elige los lotes de mayor valor nutricional que caben en el vehículo.

    Args:
        lotes: lotes candidatos de la ruta; no se fraccionan.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.

    Returns:
        El valor nutricional máximo y los índices de los lotes cargados.
    """
    valor, elegidos, _ = cargar_vehiculo_con_conteo(lotes, capacidad_kg)
    return valor, elegidos
