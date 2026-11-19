
"""Experimentos, gráficas y extrapolación del cargue de vehículos.

Responsable: Samuel Arango Montoya.

Ejecución, desde la raíz del repositorio:
    python src/cargue_vehiculos/medicion.py

Genera en ``graficas/cargue_vehiculos/``: ``tiempo_vs_n.png``,
``operaciones_vs_n.png``, ``tiempo_vs_capacidad.png``, ``mediciones.csv`` y
``resumen_mediciones.md`` (las tablas en Markdown que se copian al informe).
"""

import contextlib
import csv
import io
import math
import sys
import time
from collections.abc import Callable
from pathlib import Path

import matplotlib.pyplot as plt

from datos import (
    generar_instancia_pequena,
    generar_instancia_real,
    generar_lotes,
)
from estrategia import cargar_vehiculo_con_conteo
from exhaustivo import cargar_exhaustivo_con_conteo
from regla_actual import (
    cargar_por_densidad_con_conteo,
    cargar_por_vencimiento_con_conteo,
)

Lote = tuple[int, int, int]  # (peso_kg, valor_nutricional, dias_para_vencer)
Contador = Callable[[list[Lote], int], tuple[int, list[int], int]]
Fila = dict[str, float | int | str]

SEMILLA = 2026
REPETICIONES = 5
TAMANOS_PEQUENOS = [4, 6, 8, 10, 12, 14, 16, 18, 20]
TAMANOS_GRANDES = [50, 100, 150, 200, 300, 400, 600, 800]
CAPACIDAD_FIJA_KG = 3000
LOTES_FIJOS = 300
CAPACIDADES_KG = [500, 1000, 2000, 3000, 4000, 6000, 8000]

# Volumen real del caso 3.
VEHICULOS = 14
LOTES_MAX_RUTA = 600
CAPACIDAD_MAX_KG = 4000
VENTANA_H = 2.0
POTENCIA_KW = 0.150
DIAS_OPERACION_ANIO = 300

PD = "Programación dinámica"
EXHAUSTIVA = "Exhaustiva"
REGLA = "Regla actual (vencimiento)"
DENSIDAD = "Voraz por densidad"

SOLUCIONES: dict[str, Contador] = {
    PD: cargar_vehiculo_con_conteo,
    EXHAUSTIVA: cargar_exhaustivo_con_conteo,
    REGLA: cargar_por_vencimiento_con_conteo,
    DENSIDAD: cargar_por_densidad_con_conteo,
}
COLORES: dict[str, str] = {
    PD: "tab:blue",
    EXHAUSTIVA: "tab:orange",
    REGLA: "tab:green",
    DENSIDAD: "tab:red",
}

RAIZ = Path(__file__).resolve().parents[2]
CARPETA_GRAFICAS = RAIZ / "graficas" / "cargue_vehiculos"


def medir(
    cargar: Contador, lotes: list[Lote], capacidad_kg: int
) -> tuple[float, int, int]:
    """Cronometra una solución varias veces sobre la misma instancia.

    Solo se cronometra la llamada a la solución, nunca la generación de
    los datos.

    Args:
        cargar: solución que devuelve (valor, elegidos, operaciones).
        lotes: lotes candidatos de la instancia.
        capacidad_kg: capacidad del vehículo en kilogramos.

    Returns:
        El tiempo medio en segundos, el valor obtenido y las operaciones.
    """
    tiempos: list[float] = []
    valor = operaciones = 0
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        valor, _, operaciones = cargar(lotes, capacidad_kg)
        tiempos.append(time.perf_counter() - inicio)
    return sum(tiempos) / len(tiempos), valor, operaciones


def crear_fila(
    experimento: str,
    solucion: str,
    n: int,
    capacidad_kg: int,
    medicion: tuple[float, int, int],
) -> Fila:
    """Arma una fila de resultados.

    Args:
        experimento: nombre del experimento.
        solucion: nombre de la solución medida.
        n: número de lotes de la instancia.
        capacidad_kg: capacidad del vehículo en kilogramos.
        medicion: (tiempo en segundos, valor, operaciones).

    Returns:
        La fila con todas las columnas del CSV.
    """
    tiempo, valor, operaciones = medicion
    return {
        "experimento": experimento,
        "solucion": solucion,
        "n": n,
        "capacidad_kg": capacidad_kg,
        "tiempo_s": tiempo,
        "operaciones": operaciones,
        "valor": valor,
    }


def experimento_tamanos_pequenos() -> list[Fila]:
    """Mide las cuatro soluciones con n pequeño y verifica PD = exhaustiva.

    La capacidad es el 40 % del peso total, así que también crece con n.

    Returns:
        Una fila por solución y tamaño.
    """
    filas: list[Fila] = []
    for n in TAMANOS_PEQUENOS:
        lotes, capacidad = generar_instancia_pequena(n, SEMILLA + n)
        valores: dict[str, int] = {}
        for nombre, cargar in SOLUCIONES.items():
            medicion = medir(cargar, lotes, capacidad)
            valores[nombre] = medicion[1]
            filas.append(crear_fila("n_pequeno", nombre, n, capacidad,
                                    medicion))
        assert valores[PD] == valores[EXHAUSTIVA], f"n={n}"
        print(f"n={n:>3} W={capacidad:>5} kg  PD = exhaustiva = "
              f"{valores[EXHAUSTIVA]}")
    return filas


def experimento_tamanos_grandes() -> list[Fila]:
    """Mide la PD y las reglas voraces con n grande y capacidad fija.

    Returns:
        Una fila por solución y tamaño.
    """
    filas: list[Fila] = []
    for n in TAMANOS_GRANDES:
        lotes = generar_lotes(n, SEMILLA + n)
        for nombre, cargar in SOLUCIONES.items():
            if nombre == EXHAUSTIVA:
                continue
            medicion = medir(cargar, lotes, CAPACIDAD_FIJA_KG)
            filas.append(crear_fila("n_grande", nombre, n, CAPACIDAD_FIJA_KG,
                                    medicion))
    return filas


def experimento_capacidad() -> list[Fila]:
    """Mide la PD con n fijo y capacidad W creciente.

    Returns:
        Una fila por capacidad.
    """
    filas: list[Fila] = []
    lotes = generar_lotes(LOTES_FIJOS, SEMILLA)
    for capacidad in CAPACIDADES_KG:
        medicion = medir(cargar_vehiculo_con_conteo, lotes, capacidad)
        filas.append(crear_fila("capacidad", PD, LOTES_FIJOS, capacidad,
                                medicion))
    return filas


def experimento_volumen_real() -> list[Fila]:
    """Resuelve 14 rutas con el volumen real y compara la calidad del cargue.

    Returns:
        Una fila por solución y ruta, con el porcentaje de capacidad usada.
    """
    filas: list[Fila] = []
    for ruta in range(VEHICULOS):
        lotes, capacidad = generar_instancia_real(SEMILLA + 1000 * ruta)
        for nombre, cargar in SOLUCIONES.items():
            if nombre == EXHAUSTIVA:
                continue
            inicio = time.perf_counter()
            valor, elegidos, ops = cargar(lotes, capacidad)
            tiempo = time.perf_counter() - inicio
            fila = crear_fila("real", nombre, len(lotes), capacidad,
                              (tiempo, valor, ops))
            peso = sum(lotes[i][0] for i in elegidos)
            fila["uso_capacidad_pct"] = round(100 * peso / capacidad, 2)
            filas.append(fila)
    return filas


def serie(
    filas: list[Fila], experimento: str, solucion: str, eje: str = "n"
) -> tuple[list[float], list[float], list[float]]:
    """Extrae una serie (x, tiempo, operaciones) de las filas medidas.

    Args:
        filas: todas las filas medidas.
        experimento: nombre del experimento.
        solucion: nombre de la solución.
        eje: columna que se usa como eje x.

    Returns:
        Las listas de x, tiempos en segundos y operaciones.
    """
    sel = [f for f in filas
           if f["experimento"] == experimento and f["solucion"] == solucion]
    return ([float(f[eje]) for f in sel],
            [float(f["tiempo_s"]) for f in sel],
            [float(f["operaciones"]) for f in sel])


def graficar_vs_n(
    filas: list[Fila],
    indice: int,
    nombre_archivo: str,
    etiqueta_y: str,
    titulo: str,
) -> None:
    """Dibuja tiempo u operaciones frente a n, en dos paneles.

    Panel izquierdo: n pequeño, las cuatro soluciones.
    Panel derecho: n grande con W fija, sin la exhaustiva.

    Args:
        filas: todas las filas medidas.
        indice: 1 para tiempo, 2 para operaciones (posición en ``serie``).
        nombre_archivo: archivo PNG de salida.
        etiqueta_y: rótulo del eje y con unidades.
        titulo: título general de la figura.
    """
    fig, (izq, der) = plt.subplots(1, 2, figsize=(13, 5))
    for nombre in SOLUCIONES:
        datos = serie(filas, "n_pequeno", nombre)
        izq.plot(datos[0], datos[indice], marker="o", label=nombre,
                 color=COLORES[nombre])
        if nombre != EXHAUSTIVA:
            datos = serie(filas, "n_grande", nombre)
            der.plot(datos[0], datos[indice], marker="o", label=nombre,
                     color=COLORES[nombre])
    izq.set_title("n pequeño (W = 40 % del peso total)")
    der.set_title(f"n grande, W fija = {CAPACIDAD_FIJA_KG} kg")
    for eje in (izq, der):
        eje.set_yscale("log")
        eje.set_xlabel("Número de lotes candidatos n")
        eje.set_ylabel(etiqueta_y)
        eje.legend()
        eje.grid(True, alpha=0.3)
    fig.suptitle(titulo)
    fig.tight_layout()
    fig.savefig(CARPETA_GRAFICAS / nombre_archivo, dpi=120)
    plt.close(fig)


def graficar_capacidad(filas: list[Fila]) -> None:
    """Dibuja el tiempo de la PD frente a la capacidad W con n fijo.

    Args:
        filas: todas las filas medidas.
    """
    x, tiempos, _ = serie(filas, "capacidad", PD, eje="capacidad_kg")
    fig, eje = plt.subplots(figsize=(7, 5))
    eje.plot(x, tiempos, marker="o", color=COLORES[PD],
             label=f"{PD}, n = {LOTES_FIJOS} lotes")
    eje.set_title("Mochila 0/1: tiempo frente a la capacidad del vehículo")
    eje.set_xlabel("Capacidad del vehículo W (kg)")
    eje.set_ylabel("Tiempo medio (s)")
    eje.legend()
    eje.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(CARPETA_GRAFICAS / "tiempo_vs_capacidad.png", dpi=120)
    plt.close(fig)


def guardar_csv(filas: list[Fila]) -> None:
    """Guarda todas las mediciones en ``mediciones.csv``.

    Args:
        filas: todas las filas medidas.
    """
    columnas = ["experimento", "solucion", "n", "capacidad_kg", "tiempo_s",
                "operaciones", "valor", "uso_capacidad_pct"]
    ruta = CARPETA_GRAFICAS / "mediciones.csv"
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)


def imprimir_tabla(
    filas: list[Fila], experimento: str, eje: str = "n"
) -> None:
    """Imprime en Markdown la tabla de un experimento.

    Args:
        filas: todas las filas medidas.
        experimento: nombre del experimento.
        eje: columna que identifica el tamaño.
    """
    print(f"\n### Experimento {experimento}\n")
    print(f"| Solución | {eje} | Tiempo medio (s) | Operaciones | Valor |")
    print("|---|---:|---:|---:|---:|")
    for f in filas:
        if f["experimento"] == experimento:
            print(f"| {f['solucion']} | {f[eje]} "
                  f"| {float(f['tiempo_s']):.6f} "
                  f"| {f['operaciones']} | {f['valor']} |")


def imprimir_factores(filas: list[Fila]) -> None:
    """Imprime cuánto se multiplican tiempo y operaciones al duplicar n.

    Args:
        filas: todas las filas medidas.
    """
    print("\n### Factor de crecimiento al duplicar n\n")
    print("| Solución | Experimento | n → 2n | Factor tiempo "
          "| Factor operaciones |")
    print("|---|---|---|---:|---:|")
    parejas = [("n_pequeno", 8, 16), ("n_pequeno", 10, 20),
               ("n_grande", 100, 200), ("n_grande", 300, 600),
               ("n_grande", 400, 800)]
    for experimento, a, b in parejas:
        for nombre in SOLUCIONES:
            x, t, o = serie(filas, experimento, nombre)
            if a in x and b in x:
                i, j = x.index(a), x.index(b)
                print(f"| {nombre} | {experimento} | {a} → {b} "
                      f"| {t[j] / t[i]:.2f} | {o[j] / o[i]:.2f} |")


def total_real(filas: list[Fila], solucion: str, columna: str) -> float:
    """Suma una columna del experimento con volumen real para una solución.

    Args:
        filas: todas las filas medidas.
        solucion: nombre de la solución.
        columna: columna que se suma.

    Returns:
        La suma de la columna sobre las 14 rutas.
    """
    return sum(float(f[columna]) for f in filas
               if f["experimento"] == "real" and f["solucion"] == solucion)


def imprimir_volumen_real(filas: list[Fila]) -> None:
    """Imprime tiempo, valor y uso de capacidad en las 14 rutas reales.

    Args:
        filas: todas las filas medidas.
    """
    print("\n### Volumen real medido (14 rutas de 300 a 600 lotes)\n")
    print("| Solución | Tiempo total 14 rutas (s) | Valor total "
          "| Uso medio de capacidad (%) |")
    print("|---|---:|---:|---:|")
    for nombre in (PD, REGLA, DENSIDAD):
        tiempo = total_real(filas, nombre, "tiempo_s")
        valor = int(total_real(filas, nombre, "valor"))
        uso = total_real(filas, nombre, "uso_capacidad_pct") / VEHICULOS
        print(f"| {nombre} | {tiempo:.3f} | {valor} | {uso:.1f} |")
    optimo = total_real(filas, PD, "valor")
    for nombre in (REGLA, DENSIDAD):
        porcentaje = 100 * total_real(filas, nombre, "valor") / optimo
        print(f"- {nombre}: {porcentaje:.1f} % del valor óptimo")


def imprimir_extrapolacion(filas: list[Fila]) -> None:
    """Extrapola al peor caso real del caso y estima la energía.

    La PD se extrapola con el tiempo por celda medido, porque su costo es
    Θ(n·W); la exhaustiva con el tiempo por subconjunto y lote, porque su
    costo es Θ(n·2ⁿ); la regla actual se toma de la medición con volumen
    real.

    Args:
        filas: todas las filas medidas.
    """
    _, t, o = serie(filas, "n_grande", PD)
    seg_por_celda = t[-1] / o[-1]
    celdas = VEHICULOS * LOTES_MAX_RUTA * (CAPACIDAD_MAX_KG + 1)
    t_pd = seg_por_celda * celdas

    xe, te, _ = serie(filas, "n_pequeno", EXHAUSTIVA)
    seg_por_paso = te[-1] / (xe[-1] * 2 ** xe[-1])
    pasos = VEHICULOS * LOTES_MAX_RUTA
    log10_t_ex = (math.log10(seg_por_paso * pasos)
                  + LOTES_MAX_RUTA * math.log10(2))

    t_regla = total_real(filas, REGLA, "tiempo_s")
    e_pd = POTENCIA_KW * t_pd / 3600
    e_regla = POTENCIA_KW * t_regla / 3600

    print("\n### Extrapolación al peor caso real "
          "(14 vehículos × 600 lotes × 4.000 kg)\n")
    print(f"- PD: {seg_por_celda:.3e} s/celda × {celdas:,} celdas = "
          f"{t_pd:.1f} s = {t_pd / 3600:.4f} h (ventana {VENTANA_H} h)")
    print(f"- Exhaustiva: ≈ 10^{log10_t_ex:.0f} s; no termina")
    print(f"- Energía PD por día: {e_pd:.6f} kWh; al año "
          f"({DIAS_OPERACION_ANIO} días): "
          f"{e_pd * DIAS_OPERACION_ANIO:.3f} kWh")
    print(f"- Energía regla actual por día: {e_regla:.8f} kWh; al año: "
          f"{e_regla * DIAS_OPERACION_ANIO:.5f} kWh")
    print(f"- Diferencia anual PD - regla: "
          f"{(e_pd - e_regla) * DIAS_OPERACION_ANIO:.3f} kWh")


def main() -> None:
    """Ejecuta los experimentos, guarda las gráficas y muestra las tablas."""
    sys.stdout.reconfigure(encoding="utf-8")  # consola de Windows
    plt.switch_backend("Agg")  # solo archivos PNG, sin ventanas
    CARPETA_GRAFICAS.mkdir(parents=True, exist_ok=True)
    filas = experimento_tamanos_pequenos()
    filas += experimento_tamanos_grandes()
    filas += experimento_capacidad()
    filas += experimento_volumen_real()
    guardar_csv(filas)
    graficar_vs_n(filas, 1, "tiempo_vs_n.png", "Tiempo medio (s, escala log)",
                  "Cargue de vehículos: tiempo frente al número de lotes")
    graficar_vs_n(filas, 2, "operaciones_vs_n.png",
                  "Operaciones elementales (escala log)",
                  "Cargue de vehículos: operaciones frente al número de "
                  "lotes (PD: celdas; exhaustiva: subconjuntos; "
                  "voraces: lotes revisados)")
    graficar_capacidad(filas)
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        imprimir_tabla(filas, "n_pequeno")
        imprimir_tabla(filas, "n_grande")
        imprimir_tabla(filas, "capacidad", eje="capacidad_kg")
        imprimir_factores(filas)
        imprimir_volumen_real(filas)
        imprimir_extrapolacion(filas)
    resumen = salida.getvalue()
    print(resumen)
    ruta = CARPETA_GRAFICAS / "resumen_mediciones.md"
    ruta.write_text("# Resumen de mediciones\n" + resumen, encoding="utf-8")
    print(f"Gráficas, CSV y resumen en {CARPETA_GRAFICAS}")


if __name__ == "__main__":
    main()
