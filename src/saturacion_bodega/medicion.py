"""Experimentos, gráficas y extrapolación del análisis de saturación.

Responsable: Samuel Arango Montoya.

Ejecución, desde la raíz del repositorio:
    python src/saturacion_bodega/medicion.py

Genera en ``graficas/saturacion_bodega/``: ``tiempo_vs_n.png``,
``operaciones_vs_n.png``, ``mediciones.csv`` y ``resumen_mediciones.md``
(las tablas en Markdown que se copian al informe).
"""

import contextlib
import csv
import io
import statistics
import sys
import time
from collections.abc import Callable
from pathlib import Path

import matplotlib.pyplot as plt

from datos import generar_serie
from divide_y_venceras import tramo_dyv_con_conteo
from kadane import tramo_kadane_con_conteo
from regla_actual import tramo_cubico_con_conteo, tramo_cuadratico_con_conteo

Tramo = tuple[int, int, int]  # (crecimiento_kg, hora_inicio, hora_fin)
Contador = Callable[[list[int]], tuple[Tramo, int]]
Fila = dict[str, float | int | str]

SEMILLA = 2026
REPETICIONES = 7

CUBICO = "Fuerza bruta Θ(n³) (actual)"
CUADRATICO = "Fuerza bruta Θ(n²)"
DYV = "Dividir y vencer Θ(n log n)"
KADANE = "Kadane Θ(n)"

SOLUCIONES: dict[str, Contador] = {
    CUBICO: tramo_cubico_con_conteo,
    CUADRATICO: tramo_cuadratico_con_conteo,
    DYV: tramo_dyv_con_conteo,
    KADANE: tramo_kadane_con_conteo,
}
COLORES: dict[str, str] = {
    CUBICO: "tab:orange",
    CUADRATICO: "tab:green",
    DYV: "tab:purple",
    KADANE: "tab:blue",
}
# Hasta qué tamaño corre cada solución (las lentas no alcanzan los grandes).
TAMANOS: list[int] = [25, 50, 100, 200, 400, 800, 1600, 3200, 6400, 12800,
                      25600, 51200, 102400, 204800]
LIMITE_N: dict[str, int] = {CUBICO: 400, CUADRATICO: 3200, DYV: 204800,
                            KADANE: 204800}

# Volumen real del caso 3.
CATEGORIAS = 40
HORAS_REALES = 36_000  # 10 años × 300 días × 12 horas
POTENCIA_KW = 0.150

RAIZ = Path(__file__).resolve().parents[2]
CARPETA_GRAFICAS = RAIZ / "graficas" / "saturacion_bodega"


def medir(contar: Contador, cambios: list[int]) -> tuple[float, int, int]:
    """Cronometra una solución varias veces sobre la misma serie.

    Se usa la mediana de las repeticiones y no el promedio, para que una
    interrupción del sistema operativo en una sola repetición no distorsione
    la medición.

    Args:
        contar: solución que devuelve (tramo, operaciones).
        cambios: serie de cambios por hora.

    Returns:
        El tiempo mediano en segundos, el crecimiento hallado y las
        operaciones contadas.
    """
    tiempos: list[float] = []
    tramo: Tramo = (0, 0, 0)
    operaciones = 0
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        tramo, operaciones = contar(cambios)
        tiempos.append(time.perf_counter() - inicio)
    return statistics.median(tiempos), tramo[0], operaciones


def experimento_tamanos() -> list[Fila]:
    """Mide cada solución en tamaños crecientes y verifica que coincidan.

    Returns:
        Una fila por solución y tamaño.
    """
    filas: list[Fila] = []
    for n in TAMANOS:
        cambios = generar_serie(n, SEMILLA + n)
        valores: dict[str, int] = {}
        for nombre, contar in SOLUCIONES.items():
            if n > LIMITE_N[nombre]:
                continue
            tiempo, crecimiento, ops = medir(contar, cambios)
            valores[nombre] = crecimiento
            filas.append({"experimento": "tamanos", "solucion": nombre,
                          "n": n, "tiempo_s": tiempo, "operaciones": ops,
                          "crecimiento_kg": crecimiento})
        assert len(set(valores.values())) == 1, f"n={n}: {valores}"
        print(f"n={n:>6}: {len(valores)} soluciones coinciden "
              f"({next(iter(valores.values()))} kg)")
    return filas


def experimento_volumen_real() -> list[Fila]:
    """Corre DyV y Kadane sobre las 40 categorías con 36.000 horas cada una.

    Returns:
        Una fila por solución con el tiempo total de las 40 categorías.
    """
    filas: list[Fila] = []
    series = [generar_serie(HORAS_REALES, SEMILLA + 10_000 + categoria)
              for categoria in range(CATEGORIAS)]
    for nombre in (DYV, KADANE):
        inicio = time.perf_counter()
        resultados = [SOLUCIONES[nombre](serie)[0][0] for serie in series]
        tiempo = time.perf_counter() - inicio
        filas.append({"experimento": "real", "solucion": nombre,
                      "n": HORAS_REALES, "tiempo_s": tiempo,
                      "operaciones": 0, "crecimiento_kg": max(resultados)})
    return filas


def serie_de(
    filas: list[Fila], solucion: str
) -> tuple[list[float], list[float], list[float]]:
    """Extrae (n, tiempo, operaciones) del experimento de tamaños.

    Args:
        filas: todas las filas medidas.
        solucion: nombre de la solución.

    Returns:
        Las listas de tamaños, tiempos en segundos y operaciones.
    """
    sel = [f for f in filas
           if f["experimento"] == "tamanos" and f["solucion"] == solucion]
    return ([float(f["n"]) for f in sel],
            [float(f["tiempo_s"]) for f in sel],
            [float(f["operaciones"]) for f in sel])


def graficar(filas: list[Fila], indice: int, archivo: str,
             etiqueta_y: str, titulo: str) -> None:
    """Dibuja tiempo u operaciones frente a n en escala log-log.

    Args:
        filas: todas las filas medidas.
        indice: 1 para tiempo, 2 para operaciones.
        archivo: nombre del PNG de salida.
        etiqueta_y: rótulo del eje y con unidades.
        titulo: título de la figura.
    """
    fig, eje = plt.subplots(figsize=(9, 6))
    for nombre in SOLUCIONES:
        datos = serie_de(filas, nombre)
        eje.plot(datos[0], datos[indice], marker="o", label=nombre,
                 color=COLORES[nombre])
    eje.set_xscale("log")
    eje.set_yscale("log")
    eje.set_title(titulo)
    eje.set_xlabel("Número de horas de la serie n (escala log)")
    eje.set_ylabel(etiqueta_y)
    eje.legend()
    eje.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(CARPETA_GRAFICAS / archivo, dpi=120)
    plt.close(fig)


def guardar_csv(filas: list[Fila]) -> None:
    """Guarda las mediciones en ``mediciones.csv``.

    Args:
        filas: todas las filas medidas.
    """
    columnas = ["experimento", "solucion", "n", "tiempo_s", "operaciones",
                "crecimiento_kg"]
    ruta = CARPETA_GRAFICAS / "mediciones.csv"
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)


def imprimir_tabla(filas: list[Fila]) -> None:
    """Imprime en Markdown la tabla del experimento de tamaños.

    Args:
        filas: todas las filas medidas.
    """
    print("\n### Experimento de tamaños\n")
    print("| Solución | n | Tiempo mediano (s) | Operaciones "
          "| Crecimiento (kg) |")
    print("|---|---:|---:|---:|---:|")
    for f in filas:
        if f["experimento"] == "tamanos":
            print(f"| {f['solucion']} | {f['n']} "
                  f"| {float(f['tiempo_s']):.6f} | {f['operaciones']} "
                  f"| {f['crecimiento_kg']} |")


def imprimir_factores(filas: list[Fila]) -> None:
    """Imprime cuánto se multiplican tiempo y operaciones al duplicar n.

    Como todos los tamaños son el doble del anterior, cada pareja de tamaños
    consecutivos es una duplicación. Se reporta la última pareja y la
    mediana de todas las parejas en que el tiempo pasa de 1 ms (por debajo
    de eso el ruido del sistema domina).

    Args:
        filas: todas las filas medidas.
    """
    print("\n### Factor de crecimiento al duplicar n\n")
    print("| Solución | Última pareja n → 2n | Factor tiempo (última) "
          "| Factor tiempo (mediana) | Factor operaciones (última) |")
    print("|---|---|---:|---:|---:|")
    for nombre in SOLUCIONES:
        x, t, o = serie_de(filas, nombre)
        factores = [t[k + 1] / t[k] for k in range(len(t) - 1)
                    if t[k] > 1e-3]
        mediana = statistics.median(factores) if factores else t[-1] / t[-2]
        print(f"| {nombre} | {int(x[-2])} → {int(x[-1])} "
              f"| {t[-1] / t[-2]:.2f} | {mediana:.2f} "
              f"| {o[-1] / o[-2]:.2f} |")


def segundos_legibles(segundos: float) -> str:
    """Convierte segundos a la unidad más legible.

    Args:
        segundos: duración en segundos.

    Returns:
        La duración como texto en s, h o días.
    """
    if segundos < 3600:
        return f"{segundos:.2f} s"
    if segundos < 86_400:
        return f"{segundos / 3600:.2f} h"
    return f"{segundos / 86_400:.1f} días"


def imprimir_extrapolacion(filas: list[Fila]) -> None:
    """Extrapola al volumen real (40 × 36.000 horas) y estima la energía.

    Cada solución lenta se extrapola con su tiempo por operación medido en
    el tamaño más grande que alcanzó, multiplicado por las operaciones que
    haría con 36.000 horas según su fórmula exacta de conteo.

    Args:
        filas: todas las filas medidas.
    """
    n = HORAS_REALES
    ops_reales = {
        CUBICO: n * (n + 1) * (n + 2) // 6,
        CUADRATICO: n * (n + 1) // 2,
    }
    print("\n### Volumen real: 40 categorías × 36.000 horas\n")
    print("| Solución | Cómo se obtiene | Tiempo (40 categorías) "
          "| Energía por corrida (kWh) |")
    print("|---|---|---:|---:|")
    for nombre, ops in ops_reales.items():
        _, t, o = serie_de(filas, nombre)
        seg_por_op = t[-1] / o[-1]
        total = seg_por_op * ops * CATEGORIAS
        energia = POTENCIA_KW * total / 3600
        print(f"| {nombre} | {seg_por_op:.2e} s/op × {ops:,} ops × 40 "
              f"| {segundos_legibles(total)} | {energia:.3f} |")
    for f in filas:
        if f["experimento"] == "real":
            total = float(f["tiempo_s"])
            energia = POTENCIA_KW * total / 3600
            print(f"| {f['solucion']} | medición directa "
                  f"| {segundos_legibles(total)} | {energia:.6f} |")


def main() -> None:
    """Ejecuta los experimentos, guarda las gráficas y muestra las tablas."""
    sys.stdout.reconfigure(encoding="utf-8")  # consola de Windows
    plt.switch_backend("Agg")
    CARPETA_GRAFICAS.mkdir(parents=True, exist_ok=True)
    filas = experimento_tamanos()
    filas += experimento_volumen_real()
    guardar_csv(filas)
    graficar(filas, 1, "tiempo_vs_n.png", "Tiempo mediano (s, escala log)",
             "Saturación de la bodega: tiempo frente al número de horas")
    graficar(filas, 2, "operaciones_vs_n.png",
             "Operaciones elementales (sumas, escala log)",
             "Saturación de la bodega: operaciones frente al número "
             "de horas")
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        imprimir_tabla(filas)
        imprimir_factores(filas)
        imprimir_extrapolacion(filas)
    resumen = salida.getvalue()
    print(resumen)
    ruta = CARPETA_GRAFICAS / "resumen_mediciones.md"
    ruta.write_text("# Resumen de mediciones\n" + resumen, encoding="utf-8")
    print(f"Gráficas, CSV y resumen en {CARPETA_GRAFICAS}")


if __name__ == "__main__":
    main()
