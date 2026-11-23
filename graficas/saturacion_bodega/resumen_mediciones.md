# Resumen de mediciones

### Experimento de tamaños

| Solución | n | Tiempo mediano (s) | Operaciones | Crecimiento (kg) |
|---|---:|---:|---:|---:|
| Fuerza bruta Θ(n³) (actual) | 25 | 0.000126 | 2925 | 1139 |
| Fuerza bruta Θ(n²) | 25 | 0.000016 | 325 | 1139 |
| Dividir y vencer Θ(n log n) | 25 | 0.000021 | 143 | 1139 |
| Kadane Θ(n) | 25 | 0.000002 | 25 | 1139 |
| Fuerza bruta Θ(n³) (actual) | 50 | 0.000802 | 22100 | 1111 |
| Fuerza bruta Θ(n²) | 50 | 0.000066 | 1275 | 1111 |
| Dividir y vencer Θ(n log n) | 50 | 0.000042 | 336 | 1111 |
| Kadane Θ(n) | 50 | 0.000002 | 50 | 1111 |
| Fuerza bruta Θ(n³) (actual) | 100 | 0.005533 | 171700 | 1705 |
| Fuerza bruta Θ(n²) | 100 | 0.000229 | 5050 | 1705 |
| Dividir y vencer Θ(n log n) | 100 | 0.000087 | 772 | 1705 |
| Kadane Θ(n) | 100 | 0.000005 | 100 | 1705 |
| Fuerza bruta Θ(n³) (actual) | 200 | 0.047629 | 1353400 | 1936 |
| Fuerza bruta Θ(n²) | 200 | 0.000889 | 20100 | 1936 |
| Dividir y vencer Θ(n log n) | 200 | 0.000196 | 1744 | 1936 |
| Kadane Θ(n) | 200 | 0.000010 | 200 | 1936 |
| Fuerza bruta Θ(n³) (actual) | 400 | 0.395318 | 10746800 | 8436 |
| Fuerza bruta Θ(n²) | 400 | 0.004043 | 80200 | 8436 |
| Dividir y vencer Θ(n log n) | 400 | 0.000422 | 3888 | 8436 |
| Kadane Θ(n) | 400 | 0.000019 | 400 | 8436 |
| Fuerza bruta Θ(n²) | 800 | 0.017579 | 320400 | 21173 |
| Dividir y vencer Θ(n log n) | 800 | 0.000995 | 8576 | 21173 |
| Kadane Θ(n) | 800 | 0.000045 | 800 | 21173 |
| Fuerza bruta Θ(n²) | 1600 | 0.065901 | 1280800 | 38956 |
| Dividir y vencer Θ(n log n) | 1600 | 0.001851 | 18752 | 38956 |
| Kadane Θ(n) | 1600 | 0.000086 | 1600 | 38956 |
| Fuerza bruta Θ(n²) | 3200 | 0.285002 | 5121600 | 37859 |
| Dividir y vencer Θ(n log n) | 3200 | 0.004357 | 40704 | 37859 |
| Kadane Θ(n) | 3200 | 0.000217 | 3200 | 37859 |
| Dividir y vencer Θ(n log n) | 6400 | 0.008373 | 87808 | 48789 |
| Kadane Θ(n) | 6400 | 0.000308 | 6400 | 48789 |
| Dividir y vencer Θ(n log n) | 12800 | 0.017959 | 188416 | 43433 |
| Kadane Θ(n) | 12800 | 0.000605 | 12800 | 43433 |
| Dividir y vencer Θ(n log n) | 25600 | 0.036992 | 402432 | 48656 |
| Kadane Θ(n) | 25600 | 0.001199 | 25600 | 48656 |
| Dividir y vencer Θ(n log n) | 51200 | 0.076380 | 856064 | 51041 |
| Kadane Θ(n) | 51200 | 0.002656 | 51200 | 51041 |
| Dividir y vencer Θ(n log n) | 102400 | 0.159002 | 1814528 | 53601 |
| Kadane Θ(n) | 102400 | 0.005199 | 102400 | 53601 |
| Dividir y vencer Θ(n log n) | 204800 | 0.319463 | 3833856 | 61660 |
| Kadane Θ(n) | 204800 | 0.010855 | 204800 | 61660 |

### Factor de crecimiento al duplicar n

| Solución | Última pareja n → 2n | Factor tiempo (última) | Factor tiempo (mediana) | Factor operaciones (última) |
|---|---|---:|---:|---:|
| Fuerza bruta Θ(n³) (actual) | 200 → 400 | 8.30 | 8.45 | 7.94 |
| Fuerza bruta Θ(n²) | 1600 → 3200 | 4.32 | 4.32 | 4.00 |
| Dividir y vencer Θ(n log n) | 102400 → 204800 | 2.01 | 2.06 | 2.11 |
| Kadane Θ(n) | 102400 → 204800 | 2.09 | 2.09 | 2.00 |

### Volumen real: 40 categorías × 36.000 horas

| Solución | Cómo se obtiene | Tiempo (40 categorías) | Energía por corrida (kWh) |
|---|---|---:|---:|
| Fuerza bruta Θ(n³) (actual) | 3.68e-08 s/op × 7,776,648,012,000 ops × 40 | 132.4 días | 476.769 |
| Fuerza bruta Θ(n²) | 5.56e-08 s/op × 648,018,000 ops × 40 | 1442.41 s | 0.060 |
| Dividir y vencer Θ(n log n) | medición directa | 2.33 s | 0.000097 |
| Kadane Θ(n) | medición directa | 0.07 s | 0.000003 |
