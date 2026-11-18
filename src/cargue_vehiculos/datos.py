"""Generador de instancias sintéticas para el cargue de vehículos.

Responsable: Jhon Alejandro Isaza Pérez.

Todas las funciones reciben una semilla para que cualquier persona obtenga
exactamente las mismas instancias y pueda reproducir las mediciones.
"""

import random

Lote = tuple[int, int, int]  # (peso_kg, valor_nutricional, dias_para_vencer)

# Prioridad de cada familia de categorías, según el caso: proteína, frutas y
# verduras, otros. El valor nutricional es raciones x prioridad.
PRIORIDADES: dict[str, int] = {"proteina": 3, "frutas_verduras": 2, "otros": 1}

PESO_MIN_KG = 5
PESO_MAX_KG = 300
DIAS_MAX_VENCER = 30
CAPACIDAD_MIN_KG = 2500
CAPACIDAD_MAX_KG = 4000


def generar_lote(rng: random.Random) -> Lote:
    """Genera un lote con peso entero, valor nutricional y días para vencer.

    Args:
        rng: generador de números aleatorios ya inicializado con la semilla.

    Returns:
        Un lote (peso_kg, valor_nutricional, dias_para_vencer). Los días para
        vencer son al menos 1: los lotes vencidos no son candidatos.
    """
    peso = rng.randint(PESO_MIN_KG, PESO_MAX_KG)
    categoria = rng.choice(list(PRIORIDADES))
    raciones = round(peso * rng.uniform(1.5, 6.0))
    valor = raciones * PRIORIDADES[categoria]
    dias = rng.randint(1, DIAS_MAX_VENCER)
    return peso, valor, dias


def generar_lotes(n: int, semilla: int) -> list[Lote]:
    """Genera ``n`` lotes candidatos de una ruta.

    Args:
        n: número de lotes candidatos.
        semilla: semilla fija del generador.

    Returns:
        La lista de lotes generados.
    """
    rng = random.Random(semilla)
    return [generar_lote(rng) for _ in range(n)]


def generar_instancia_pequena(
    n: int, semilla: int, fraccion: float = 0.4
) -> tuple[list[Lote], int]:
    """Genera una instancia pequeña cuya capacidad obliga a escoger lotes.

    La capacidad es una fracción del peso total de los lotes, para que no
    quepan todos y la decisión no sea trivial.

    Args:
        n: número de lotes.
        semilla: semilla fija del generador.
        fraccion: fracción del peso total que admite el vehículo.

    Returns:
        Los lotes y la capacidad del vehículo en kilogramos.
    """
    lotes = generar_lotes(n, semilla)
    capacidad = int(sum(peso for peso, _, _ in lotes) * fraccion)
    return lotes, capacidad


def generar_instancia_real(semilla: int) -> tuple[list[Lote], int]:
    """Genera una ruta con el volumen real del caso.

    Entre 300 y 600 lotes candidatos y un vehículo de 2.500 a 4.000 kg.

    Args:
        semilla: semilla fija del generador.

    Returns:
        Los lotes y la capacidad del vehículo en kilogramos.
    """
    rng = random.Random(semilla)
    n = rng.randint(300, 600)
    capacidad = rng.randint(CAPACIDAD_MIN_KG, CAPACIDAD_MAX_KG)
    return generar_lotes(n, semilla + 1), capacidad
