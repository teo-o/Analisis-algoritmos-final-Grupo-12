"""Cargue de un vehículo por búsqueda exhaustiva de todos los subconjuntos.

Responsable: Cristian Jose Mendez.

Solo se usa con instancias pequeñas: su costo es Θ(n·2ⁿ). Es la solución
exacta con la que se verifica la programación dinámica.
"""

Lote = tuple[int, int, int]  # (peso_kg, valor_nutricional, dias_para_vencer)


def cargar_exhaustivo_con_conteo(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int], int]:
    """Prueba los 2ⁿ subconjuntos de lotes y cuenta los que explora.

    Cada número ``mascara`` entre 0 y 2ⁿ - 1 representa un subconjunto: el
    bit ``i`` encendido significa que el lote ``i`` sube al vehículo.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.

    Returns:
        El valor nutricional máximo, los índices de los lotes cargados y el
        número de subconjuntos explorados.
    """
    n = len(lotes)
    mejor_valor = 0
    mejor_mascara = 0
    explorados = 0
    for mascara in range(1 << n):
        explorados += 1
        peso_total = 0
        valor_total = 0
        for i in range(n):
            if mascara >> i & 1:
                peso_total += lotes[i][0]
                valor_total += lotes[i][1]
        if peso_total <= capacidad_kg and valor_total > mejor_valor:
            mejor_valor = valor_total
            mejor_mascara = mascara
    elegidos = [i for i in range(n) if mejor_mascara >> i & 1]
    return mejor_valor, elegidos, explorados


def cargar_exhaustivo(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int]]:
    """Calcula el mismo resultado probando todos los subconjuntos de lotes.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.

    Returns:
        El valor nutricional máximo y los índices de los lotes cargados.
    """
    valor, elegidos, _ = cargar_exhaustivo_con_conteo(lotes, capacidad_kg)
    return valor, elegidos
