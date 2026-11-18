"""Pruebas con assert del cargue de vehículos.

Responsable: Jhon Alejandro Isaza Pérez.

Ejecución, desde la raíz del repositorio:
    python src/cargue_vehiculos/pruebas.py
"""

from collections.abc import Callable

from datos import generar_instancia_pequena
from estrategia import cargar_vehiculo
from exhaustivo import cargar_exhaustivo
from regla_actual import cargar_por_densidad, cargar_por_vencimiento

Lote = tuple[int, int, int]  # (peso_kg, valor_nutricional, dias_para_vencer)
Cargador = Callable[[list[Lote], int], tuple[int, list[int]]]

TODAS: list[Cargador] = [
    cargar_vehiculo,
    cargar_exhaustivo,
    cargar_por_vencimiento,
    cargar_por_densidad,
]

# Ejemplo resuelto a mano en el informe (Diseño de la solución).
EJEMPLO_MANO: list[Lote] = [
    (2, 6, 4), (3, 10, 1), (4, 12, 2), (5, 18, 3), (6, 20, 5)
]
CAPACIDAD_MANO = 10

# Contraejemplo del informe (Análisis comparativo).
CONTRAEJEMPLO: list[Lote] = [(6, 30, 1), (5, 20, 2), (5, 20, 3)]
CAPACIDAD_CONTRA = 10

INSTANCIAS_ALEATORIAS = 30
SEMILLA_BASE = 2026


def cumple_restricciones(
    lotes: list[Lote], capacidad_kg: int, valor: int, elegidos: list[int]
) -> bool:
    """Verifica las restricciones del negocio sobre un cargue.

    Ningún vehículo supera su capacidad, ningún lote se fracciona ni se
    carga dos veces, y el valor reportado es la suma de los lotes cargados.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad máxima del vehículo en kilogramos.
        valor: valor nutricional que devolvió la solución.
        elegidos: índices de los lotes que devolvió la solución.

    Returns:
        True si el cargue cumple todas las restricciones.
    """
    if len(set(elegidos)) != len(elegidos):
        return False
    if any(i < 0 or i >= len(lotes) for i in elegidos):
        return False
    peso = sum(lotes[i][0] for i in elegidos)
    return peso <= capacidad_kg and valor == sum(lotes[i][1] for i in elegidos)


def probar_casos_limite() -> None:
    """Prueba entrada vacía, un solo lote, nada cabe y todo cabe."""
    for cargar in TODAS:
        assert cargar([], 100) == (0, [])
        assert cargar([(10, 50, 3)], 10) == (50, [0])
        assert cargar([(10, 50, 3)], 9) == (0, [])
        assert cargar([(10, 50, 3), (20, 40, 1)], 0) == (0, [])
        assert cargar([(5, 9, 1), (5, 8, 2)], 4) == (0, [])
    todo_cabe: list[Lote] = [(1, 3, 2), (2, 5, 1), (3, 4, 3)]
    assert cargar_vehiculo(todo_cabe, 6) == (12, [0, 1, 2])
    assert cargar_exhaustivo(todo_cabe, 6) == (12, [0, 1, 2])


def probar_ejemplo_a_mano() -> None:
    """Prueba el ejemplo de 5 lotes y 10 kg resuelto a mano en el informe."""
    assert cargar_vehiculo(EJEMPLO_MANO, CAPACIDAD_MANO) == (34, [0, 1, 3])
    assert cargar_exhaustivo(EJEMPLO_MANO, CAPACIDAD_MANO)[0] == 34
    assert cargar_por_vencimiento(EJEMPLO_MANO, CAPACIDAD_MANO) == (22, [1, 2])


def probar_aleatorias_contra_exhaustiva() -> None:
    """Compara la PD con la exhaustiva en instancias pequeñas aleatorias."""
    for k in range(INSTANCIAS_ALEATORIAS):
        n = 1 + k % 12
        lotes, capacidad = generar_instancia_pequena(n, SEMILLA_BASE + k)
        valor_pd, elegidos_pd = cargar_vehiculo(lotes, capacidad)
        valor_ex, _ = cargar_exhaustivo(lotes, capacidad)
        assert valor_pd == valor_ex, f"instancia {k}: {valor_pd} != {valor_ex}"
        assert cumple_restricciones(lotes, capacidad, valor_pd, elegidos_pd)


def probar_restriccion_negocio() -> None:
    """Ninguna solución supera la capacidad ni fracciona o repite lotes."""
    for k in range(INSTANCIAS_ALEATORIAS):
        semilla = SEMILLA_BASE + 100 + k
        lotes, capacidad = generar_instancia_pequena(10, semilla)
        optimo = cargar_vehiculo(lotes, capacidad)[0]
        for cargar in TODAS:
            valor, elegidos = cargar(lotes, capacidad)
            assert cumple_restricciones(lotes, capacidad, valor, elegidos)
            assert valor <= optimo


def probar_contraejemplo() -> None:
    """La regla actual y la de densidad cargan menos que la PD."""
    assert cargar_vehiculo(CONTRAEJEMPLO, CAPACIDAD_CONTRA) == (40, [1, 2])
    assert cargar_por_vencimiento(CONTRAEJEMPLO, CAPACIDAD_CONTRA) == (30, [0])
    assert cargar_por_densidad(CONTRAEJEMPLO, CAPACIDAD_CONTRA) == (30, [0])


def main() -> None:
    """Ejecuta todas las pruebas e informa el resultado."""
    probar_casos_limite()
    probar_ejemplo_a_mano()
    probar_aleatorias_contra_exhaustiva()
    probar_restriccion_negocio()
    probar_contraejemplo()
    print("Todas las pruebas pasaron.")


if __name__ == "__main__":
    main()
