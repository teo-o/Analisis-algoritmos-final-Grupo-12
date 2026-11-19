"""Reglas voraces de cargue: la que usa hoy el banco y la de densidad.

Responsable: Cristian Jose Mendez.

Ninguna de las dos garantiza el valor nutricional máximo; sirven como línea
base del proceso actual y como contraste de la programación dinámica.
"""

Lote = tuple[int, int, int]  # (peso_kg, valor_nutricional, dias_para_vencer)


def cargar_por_vencimiento_con_conteo(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int], int]:
    """Carga por vencimiento y se detiene en el primer lote que no cabe.

    A igual número de días para vencer se respeta el orden de la lista
    (el ordenamiento de Python es estable).

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.

    Returns:
        El valor cargado, los índices de los lotes cargados y el número de
        lotes revisados.
    """
    orden = sorted(range(len(lotes)), key=lambda i: lotes[i][2])
    libre = capacidad_kg
    valor = 0
    elegidos: list[int] = []
    revisados = 0
    for i in orden:
        revisados += 1
        peso, valor_lote, _ = lotes[i]
        if peso > libre:
            break
        libre -= peso
        valor += valor_lote
        elegidos.append(i)
    return valor, sorted(elegidos), revisados


def cargar_por_vencimiento(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int]]:
    """Reproduce el procedimiento actual: carga por vencimiento.

    Se detiene en el primer lote que ya no cabe.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.

    Returns:
        El valor nutricional cargado y los índices de los lotes cargados.
    """
    valor, elegidos, _ = cargar_por_vencimiento_con_conteo(lotes, capacidad_kg)
    return valor, elegidos


def densidad(lote: Lote) -> float:
    """Calcula el valor nutricional por kilogramo de un lote.

    Args:
        lote: lote candidato (peso_kg, valor_nutricional, dias_para_vencer).

    Returns:
        El valor por kilogramo; infinito si el lote no pesa nada.
    """
    peso, valor, _ = lote
    return valor / peso if peso > 0 else float("inf")


def cargar_por_densidad_con_conteo(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int], int]:
    """Carga por mayor valor por kilogramo, saltando los lotes que no caben.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.

    Returns:
        El valor cargado, los índices de los lotes cargados y el número de
        lotes revisados.
    """
    orden = sorted(
        range(len(lotes)), key=lambda i: densidad(lotes[i]), reverse=True
    )
    libre = capacidad_kg
    valor = 0
    elegidos: list[int] = []
    revisados = 0
    for i in orden:
        revisados += 1
        peso, valor_lote, _ = lotes[i]
        if peso <= libre:
            libre -= peso
            valor += valor_lote
            elegidos.append(i)
    return valor, sorted(elegidos), revisados


def cargar_por_densidad(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int]]:
    """Carga por mayor valor por kilogramo; no garantiza el óptimo.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.

    Returns:
        El valor nutricional cargado y los índices de los lotes cargados.
    """
    valor, elegidos, _ = cargar_por_densidad_con_conteo(lotes, capacidad_kg)
    return valor, elegidos
