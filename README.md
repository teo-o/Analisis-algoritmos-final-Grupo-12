# Análisis de algoritmos — Proyecto final — Grupo 12

**Caso asignado:** Caso de estudio 3 — Planeación diaria de despachos de un banco de alimentos.

**Integrantes:**

- Mateo Orozco Oquendo
- Cristian Jose Mendez
- Jhon Alejandro Isaza Pérez
- Samuel Arango Montoya

**Estado:** entrega del Laboratorio 4 (18 de noviembre de 2026): operación 3, cargue de los vehículos (mochila 0/1 por programación dinámica). Lo marcado como pendiente se completa para la entrega del 23 de noviembre.

---

## 1. Análisis del problema

### 1.1 Descripción del problema computacional

> Pendiente para la entrega del 23 de noviembre (proceso completo de las cuatro operaciones).

### 1.2 Operación 3 — Cargue de los vehículos: entradas, salida y restricciones

Hoy en día, para cada ruta, el coordinador toma los lotes candidatos, los ordena por fecha de vencimiento y los va metiendo al vehículo uno por uno. Cuando llega a un lote que ya no cabe, se detiene y no sigue mirando. Ese procedimiento tiene dos fallas claras: primero, no tiene en cuenta el valor nutricional de los lotes, solo la fecha; segundo, se detiene en el primer lote que no cabe aunque más adelante haya lotes más livianos que sí entrarían. Es como empacar una maleta por orden de fecha y parar en la primera prenda que no cabe, aunque las medias sí cabrían. Según el banco, los vehículos salen en promedio al 78 % de su capacidad, y esta regla explica buena parte de ese espacio perdido. Nuestro objetivo en esta operación es decidir qué lotes subir a cada vehículo para llevar la mayor cantidad de valor nutricional posible sin pasarnos de la capacidad en kilos.

| Elemento | Detalle | Unidades / límites del caso |
|---|---|---|
| Entrada 1 | Lista de lotes candidatos de una ruta; cada lote = (peso, valor nutricional, días para vencer) | peso entero en kg; 300 a 600 lotes por ruta |
| Entrada 2 | Capacidad máxima del vehículo `W` | entero en kg; entre 2.500 y 4.000 kg; 14 vehículos |
| Salida | Valor nutricional máximo cargado y los índices de los lotes que suben | raciones ponderadas por prioridad (proteína, frutas y verduras, otros) |
| Restricción 1 | La suma de pesos de los lotes cargados ≤ `W` | ningún vehículo supera su capacidad |
| Restricción 2 | Un lote sube completo o no sube (0/1) | no se fracciona |
| Restricción 3 | El valor es el **máximo**, no una aproximación | exactitud |
| Restricción 4 | Termina dentro de la ventana de planeación compartida por las operaciones 1 a 3 | 2 h (03:00–05:00), PC de 150 W |
| Restricción 5 | El registro original de cada lote no se modifica | trazabilidad sanitaria |

En vez de devolver lotes nuevos o modificados, lo que entregamos son las posiciones (índices) de los lotes que van en el vehículo. Esto es importante porque la lista original queda tal cual y, si hay que hacer un retiro de producto, cada lote se puede rastrear con el registro con el que llegó a la bodega. Es una restricción de trazabilidad sanitaria que exige el caso.

### 1.3 Operaciones críticas del proceso y costo energético actual (línea base)

> Pendiente para la entrega del 23 de noviembre.

### 1.4 Supuestos

- Partimos de que los lotes candidatos de cada ruta ya vienen sin vencidos: todos tienen al menos un día para vencer. La tarea de sacar los vencidos le corresponde al ordenamiento FEFO de la operación 2, no a esta.
- El valor nutricional de un lote lo manejamos como un entero: las raciones que aporta multiplicadas por la prioridad de su categoría (proteína 3, frutas y verduras 2, otros 1). El caso dice "raciones ponderadas por prioridad" pero no dice cuánto vale cada prioridad, entonces esos números los definimos nosotros.
- Cada vehículo lo resolvemos por separado: los lotes candidatos de una ruta no compiten con los de otra.
- No trabajamos con el volumen real. Generamos datos sintéticos con [`datos.py`](src/cargue_vehiculos/datos.py) (pesos enteros de 5 a 300 kg, semilla fija 2026), medimos con tamaños que van creciendo y extrapolamos al volumen del banco.
- Solo consideramos el peso. No modelamos el volumen de las cajas ni si un lote requiere refrigeración. Por eso con nuestros datos la regla actual llena cerca del 97 % del vehículo y no el 78 % que reporta el banco: en la realidad hay restricciones físicas que no estamos simulando. Lo que sí se mantiene es que esa regla lleva mucho menos valor nutricional que el óptimo.

## 2. Diseño de la solución

### 2.1 Estructuras de datos seleccionadas

> Pendiente para la entrega del 23 de noviembre.

### 2.2 Operación 3 — Cargue de los vehículos: programación dinámica (mochila 0/1)

#### Por qué el problema admite programación dinámica

Para cargar un vehículo hay que ir decidiendo, lote por lote, si sube o no sube. Si nos fijamos en el último lote (el lote `i`), solo hay dos caminos posibles, y cada uno nos deja un problema igual pero más pequeño:

- Si el lote `i` **no sube**, lo mejor que podemos hacer es la mejor carga con los primeros `i − 1` lotes y la misma capacidad `c`.
- Si el lote `i` **sube**, gastamos `peso_i` kilos y ganamos `valor_i`; lo que queda es la mejor carga de los primeros `i − 1` lotes con capacidad `c − peso_i`.

Ahí está la **subestructura óptima**: la mejor carga se arma con la mejor solución de un problema más chico. Si esa parte no fuera la mejor, podríamos reemplazarla por una mejor y la carga completa también mejoraría, lo cual no puede pasar si ya era la óptima.

Y también se cumplen los **subproblemas repetidos**. Muchas combinaciones distintas de "sube / no sube" terminan en el mismo punto: los mismos lotes por decidir y la misma capacidad libre. En el ejemplo de abajo, llevar L0 y L1 (2 + 3 kg) o llevar solo L3 (5 kg) deja en los dos casos 5 kg libres para decidir sobre L4. La búsqueda exhaustiva vuelve a calcular cada uno de esos casos; la tabla los calcula una sola vez y los reutiliza.

Una regla voraz no sirve aquí porque el lote no se puede partir: escoger el lote que parece mejor en el momento puede dejar un hueco que después no se llena (el contraejemplo está en la sección 5.1).

#### Recurrencia

```text
mejor[0][c] = 0                                         para c = 0..W
mejor[i][c] = mejor[i-1][c]                             si peso_i > c
mejor[i][c] = max( mejor[i-1][c],                       (el lote i no sube)
                   mejor[i-1][c - peso_i] + valor_i )   (el lote i sube)
                                                        si peso_i <= c
Respuesta: mejor[n][W]
```

`mejor[i][c]` es el mayor valor nutricional que se puede cargar usando solo los primeros `i` lotes en un vehículo de `c` kg. El caso base es la fila 0: sin lotes, el valor es 0 para cualquier capacidad. Para cada lote hay dos opciones. Si pesa más que `c`, no puede subir y nos quedamos con el valor de la fila anterior. Si cabe, comparamos no subirlo (`mejor[i-1][c]`) contra subirlo (su valor más lo mejor que se podía hacer con los kilos que sobran, `mejor[i-1][c - peso_i]`) y nos quedamos con el mayor.

La tabla se llena fila por fila, de `i = 1` a `n`, y en cada fila de `c = 0` a `W`. Como cada celda solo usa valores de la fila anterior, cuando la calculamos ya tenemos todo lo que necesita. La respuesta queda en la última celda, `mejor[n][W]`.

Para saber qué lotes subieron recorremos la tabla al revés, desde `(n, W)`: si `mejor[i][c]` es distinto de `mejor[i-1][c]`, el lote `i` tuvo que subir, así que lo anotamos y le restamos su peso a `c`; si es igual, el lote `i` no subió. Seguimos así hasta llegar a la fila 0.

Código: [`estrategia.py`](src/cargue_vehiculos/estrategia.py).

#### Ejemplo resuelto a mano (5 lotes, W = 10 kg)

| Lote | Peso (kg) | Valor | Días para vencer |
|---|---:|---:|---:|
| L0 | 2 | 6 | 4 |
| L1 | 3 | 10 | 1 |
| L2 | 4 | 12 | 2 |
| L3 | 5 | 18 | 3 |
| L4 | 6 | 20 | 5 |

Tabla `mejor[i][c]` (filas = lotes considerados, columnas = capacidad en kg):

| i \ c | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 (ninguno) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 (+L0) | 0 | 0 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| 2 (+L1) | 0 | 0 | 6 | 10 | 10 | 16 | 16 | 16 | 16 | 16 | 16 |
| 3 (+L2) | 0 | 0 | 6 | 10 | 12 | 16 | 18 | 22 | 22 | 28 | 28 |
| 4 (+L3) | 0 | 0 | 6 | 10 | 12 | 18 | 18 | 24 | 28 | 30 | **34** |
| 5 (+L4) | 0 | 0 | 6 | 10 | 12 | 18 | 20 | 24 | 28 | 30 | **34** |

Celdas calculadas paso a paso:

- `mejor[2][5] = max(mejor[1][5], mejor[1][2] + 10) = max(6, 16) = 16` → L0 + L1.
- `mejor[3][9] = max(mejor[2][9], mejor[2][5] + 12) = max(16, 28) = 28` → L0 + L1 + L2.
- `mejor[4][10] = max(mejor[3][10], mejor[3][5] + 18) = max(28, 34) = 34`.
- `mejor[5][10] = max(mejor[4][10], mejor[4][4] + 20) = max(34, 32) = 34` → L4 no mejora.

Reconstrucción desde `(5, 10)`:

1. `mejor[5][10] = 34 = mejor[4][10]` → L4 **no** sube.
2. `mejor[4][10] = 34 ≠ mejor[3][10] = 28` → L3 **sube**; capacidad restante 10 − 5 = 5.
3. `mejor[3][5] = 16 = mejor[2][5]` → L2 **no** sube.
4. `mejor[2][5] = 16 ≠ mejor[1][5] = 6` → L1 **sube**; restante 5 − 3 = 2.
5. `mejor[1][2] = 6 ≠ mejor[0][2] = 0` → L0 **sube**; restante 0.

**Resultado óptimo:** L0 + L1 + L3 = 10 kg, valor **34**. La regla actual (por vencimiento: L1, L2, y se detiene en L3 porque 7 + 5 > 10) carga **22**.

Con este ejemplo se ve que la tabla llega al mismo resultado que probar las 2⁵ = 32 combinaciones posibles. Con tan pocos lotes la tabla no ahorra trabajo (55 celdas contra 32 combinaciones de hasta 5 sumas cada una), pero la ventaja aparece cuando n crece: con 600 lotes son unos 2,4 millones de celdas contra 2⁶⁰⁰ combinaciones. El ejemplo también muestra que la regla por vencimiento deja por fuera a L0 (2 kg), que todavía cabía.

### 2.3 Segunda operación

> Pendiente para la entrega del 23 de noviembre.

## 3. Implementación

### 3.1 Operación 3 — Cargue de los vehículos

<!-- SECCION-JHON-IMPLEMENTACION: Jhon reemplaza este comentario con su sección -->

### 3.2 Segunda operación

> Pendiente para la entrega del 23 de noviembre.

## 4. Evaluación del desempeño

### 4.1 Operación 3 — Complejidad temporal y espacial

| Estrategia | Tiempo | Espacio | Comentario |
|---|---|---|---|
| Programación dinámica (mochila 0/1) | Θ(n·W) | Θ(n·W) | tabla de (n+1)·(W+1) celdas; se guarda completa para reconstruir los lotes |
| Exhaustiva (todos los subconjuntos) | Θ(n·2ⁿ) | Θ(n) | 2ⁿ subconjuntos, cada uno suma hasta n pesos |
| Regla actual (vencimiento) | Θ(n log n) | Θ(n) | domina el ordenamiento; el recorrido es O(n) |
| Voraz por densidad | Θ(n log n) | Θ(n) | igual que la anterior, pero no se detiene en el primer lote que no cabe |

Peor caso real por vehículo: n = 600, W = 4.000 → 601 × 4.001 ≈ 2,4 millones de celdas; 14 vehículos ≈ 33,6 millones de celdas. Exhaustiva: 2⁶⁰⁰ ≈ 4 × 10¹⁸⁰ subconjuntos por vehículo.

El tiempo de la programación dinámica (PD) es Θ(n·W) porque la tabla tiene (n + 1)·(W + 1) celdas y cada una se calcula en tiempo constante: una resta, una suma y una comparación. Hay que aclarar que esto no la vuelve polinomial en el tamaño de la entrada, porque W es un número y no una cantidad de datos; por eso se dice que es **pseudopolinomial**. Si W se duplica, la tabla tiene el doble de columnas y el tiempo se duplica aunque el número de lotes sea el mismo (esto se ve en la gráfica de tiempo contra capacidad, sección 4.3).

Por ejemplo, si el banco empezara a registrar los pesos en gramos, W pasaría de 4.000 a 4.000.000 y la tabla sería 1.000 veces más grande, tanto en tiempo como en memoria. Por eso conviene trabajar con kilogramos enteros, como ya lo hace el caso.

En espacio también es Θ(n·W) porque guardamos la tabla completa. Si solo nos interesara el valor máximo, con una fila bastaría (Θ(W)), pero como el banco necesita saber qué lotes suben, para reconstruirlos hacen falta todas las filas.

La exhaustiva, en cambio, usa muy poca memoria (Θ(n)), pero su tiempo es Θ(n·2ⁿ): cada lote que se agrega duplica las combinaciones por revisar. Las reglas voraces cuestan Θ(n log n) por el ordenamiento; son muy rápidas, pero no garantizan el máximo.

### 4.2 Operación 3 — Verificación de las implementaciones

<!-- SECCION-JHON-VERIFICACION: Jhon reemplaza este comentario con su sección -->

### 4.3 Operación 3 — Experimentos, gráficas y contraste con la teoría

<!-- SECCION-SAMUEL-EVALUACION: Samuel reemplaza este comentario con su sección -->

### 4.4 Segunda operación

> Pendiente para la entrega del 23 de noviembre.

## 5. Análisis comparativo

### 5.1 Operación 3 — Limitación de la regla actual: contraejemplo

<!-- SECCION-CRISTIAN-CONTRAEJEMPLO: Cristian reemplaza este comentario con su sección -->

### 5.2 Operación 3 — Condición contraria

<!-- SECCION-CRISTIAN-CONDICION: Cristian reemplaza este comentario con su sección -->

### 5.3 Operación 3 — Recomendación

<!-- SECCION-SAMUEL-RECOMENDACION: Samuel reemplaza este comentario con su sección -->

### 5.4 Comparación entre las estrategias de las dos operaciones

> Pendiente para la entrega del 23 de noviembre.

## 6. Implicaciones éticas, sociales y ambientales

### 6.1 Consumo energético — Operación 3

<!-- SECCION-SAMUEL-ENERGIA: Samuel reemplaza este comentario con su sección -->

### 6.2 Preguntas de impacto del caso (personas, normativa, crecimiento)

> Pendiente para la entrega del 23 de noviembre.

### 6.3 Consecuencias sobre las personas, marco normativo y sostenibilidad

> Pendiente para la entrega del 23 de noviembre.

## 7. Conclusiones

> Pendiente para la entrega del 23 de noviembre.

## 8. Reproducción de los datos y los experimentos

<!-- SECCION-JHON-REPRODUCCION: Jhon reemplaza este comentario con su sección -->