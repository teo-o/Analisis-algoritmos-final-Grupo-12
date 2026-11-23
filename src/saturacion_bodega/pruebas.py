"""Pruebas con assert del tramo de mayor crecimiento del inventario.

Responsable: Jhon Alejandro Isaza Pérez.

Ejecución, desde la raíz del repositorio:
    python src/saturacion_bodega/pruebas.py
"""

from collections.abc import Callable

from datos import generar_serie
from divide_y_venceras import tramo_dyv
from kadane import tramo_kadane
from regla_actual import tramo_cubico, tramo_cuadratico

Tramo = tuple[int, int, int]  # (crecimiento_kg, hora_inicio, hora_fin)
Solucion = Callable[[list[int]], Tramo]

TODAS: list[Solucion] = [tramo_cubico, tramo_cuadratico, tramo_dyv,
                         tramo_kadane]

# Ejemplo resuelto a mano en el informe (Diseño de la solución, 2.3).
EJEMPLO_MANO = [3, -5, 4, -1, 2, 6, -7, 2]

INSTANCIAS_ALEATORIAS = 30
SEMILLA_BASE = 4040


def es_tramo_valido(cambios: list[int], tramo: Tramo) -> bool:
    """Verifica que el tramo exista y que su crecimiento sea el reportado.

    Args:
        cambios: serie de cambios por hora.
        tramo: (crecimiento, inicio, fin) devuelto por una solución.

    Returns:
        True si 0 <= inicio <= fin < n y la suma del tramo coincide.
    """
    crecimiento, inicio, fin = tramo
    if not 0 <= inicio <= fin < len(cambios):
        return False
    return sum(cambios[inicio:fin + 1]) == crecimiento


def probar_casos_limite() -> None:
    """Serie vacía, una hora, todo negativo, todo positivo y ceros."""
    for solucion in TODAS:
        try:
            solucion([])
            raise AssertionError("una serie vacía debe rechazarse")
        except ValueError:
            pass
        assert solucion([7]) == (7, 0, 0)
        assert solucion([-7]) == (-7, 0, 0)
        assert solucion([-4, -2, -7, -1])[0] == -1  # la hora que menos baja
        assert solucion([2, 3, 1]) == (6, 0, 2)  # todo crece: la serie entera
        assert solucion([0, 0, 0])[0] == 0


def probar_ejemplo_a_mano() -> None:
    """Prueba el ejemplo de 8 horas resuelto a mano en el informe."""
    for solucion in TODAS:
        assert solucion(EJEMPLO_MANO) == (11, 2, 5)


def probar_aleatorias() -> None:
    """Las estrategias rápidas dan el mismo crecimiento que la exacta."""
    for k in range(INSTANCIAS_ALEATORIAS):
        n = 1 + 7 * k  # de 1 a 204 horas
        cambios = generar_serie(n, SEMILLA_BASE + k)
        exacto = tramo_cubico(cambios)[0]
        for solucion in TODAS:
            tramo = solucion(cambios)
            assert tramo[0] == exacto, f"{solucion.__name__}, instancia {k}"
            assert es_tramo_valido(cambios, tramo)


def probar_registro_original() -> None:
    """Ninguna solución modifica la serie original (trazabilidad)."""
    cambios = generar_serie(150, SEMILLA_BASE + 999)
    copia = list(cambios)
    for solucion in TODAS:
        solucion(cambios)
        assert cambios == copia, f"{solucion.__name__} modificó la serie"


def main() -> None:
    """Ejecuta todas las pruebas e informa el resultado."""
    probar_casos_limite()
    probar_ejemplo_a_mano()
    probar_aleatorias()
    probar_registro_original()
    print("Todas las pruebas pasaron.")


if __name__ == "__main__":
    main()
