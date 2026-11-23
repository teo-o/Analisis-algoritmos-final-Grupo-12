"""Generador de series sintéticas de cambio neto del inventario por hora.

Responsable: Jhon Alejandro Isaza Pérez.

Cada valor es lo que entró menos lo que salió o se descartó en una hora de
operación, en kilogramos (puede ser negativo). La semilla fija permite
reproducir exactamente las mismas series.
"""

import math
import random

HORAS_POR_DIA = 12
DIAS_POR_ANIO = 300
HORAS_POR_ANIO = HORAS_POR_DIA * DIAS_POR_ANIO  # 3.600 registros por año
CAMBIO_MAX_KG = 300
AMPLITUD_TEMPORADA_KG = 40
DERIVA_KG = 5  # en promedio sale un poco más de lo que entra


def cambio_por_hora(rng: random.Random, hora: int) -> int:
    """Genera el cambio neto de una hora, con un efecto de temporada.

    El ruido es simétrico entre -300 y 300 kg; la temporada suma o resta
    hasta 40 kg según la época del año, y una deriva de -5 kg por hora
    representa que, fuera de temporada, sale un poco más de lo que entra.
    Así el tramo de mayor crecimiento cae dentro de una temporada.

    Args:
        rng: generador de números aleatorios ya inicializado.
        hora: número de la hora dentro de la serie (desde 0).

    Returns:
        El cambio neto del inventario en esa hora, en kilogramos (entero).
    """
    fase = 2 * math.pi * hora / HORAS_POR_ANIO
    temporada = AMPLITUD_TEMPORADA_KG * math.sin(fase)
    ruido = rng.randint(-CAMBIO_MAX_KG, CAMBIO_MAX_KG)
    return round(ruido + temporada - DERIVA_KG)


def generar_serie(n: int, semilla: int) -> list[int]:
    """Genera la serie de cambios de una categoría para ``n`` horas.

    Args:
        n: número de horas de la serie.
        semilla: semilla fija del generador.

    Returns:
        La lista de cambios netos por hora, en kilogramos.
    """
    rng = random.Random(semilla)
    return [cambio_por_hora(rng, hora) for hora in range(n)]
