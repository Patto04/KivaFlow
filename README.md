# KivaFlow · Sistema de Optimización de Rutas de Picking (Python + Web UI)

Simulador interactivo basado en grafos para la optimización de rutas de *picking* y detección de cuellos de botella en un almacén inteligente tipo Amazon modelado como un grafo ponderado de **1 800 nodos y 3 515 aristas**.

Proyecto del curso **1ACC0184 - Complejidad Algorítmica** (Sección 4834), Universidad Peruana de Ciencias Aplicadas (UPC).

## Estructura del proyecto

```text
KivaFlow/
├── app.py                     # Programa principal Python (Servidor Web Multihilo + API REST + CLI)
├── requirements.txt           # Dependencias opcionales (NetworkX, NumPy, Pandas, Pytest)
├── kivaflow/                  # Paquete de algoritmos en Python
│   ├── __init__.py
│   ├── grafo.py               # Carga de nodos.csv y aristas.csv (utf-8-sig), adyacencia, capacidades y Mulberry32
│   ├── bfs.py                 # Búsqueda en Anchura (BFS) — O(V + E)
│   ├── bellman_ford.py        # Bellman-Ford (con salida anticipada y ciclos negativos) — O(V · E)
│   ├── edmonds_karp.py        # Flujo Máximo y Corte Mínimo (Edmonds-Karp) — O(V · E²)
│   ├── pedido.py              # Ruteo multi-producto (vecino más cercano) y métricas
│   ├── simulacion.py          # Simulación de turno con múltiples operarios y congestión progresiva
│   ├── verificacion.py        # Verificación matemática por Certificado de Optimalidad
│   └── paleta.py              # Constantes de paleta de colores y tipografía
├── scripts/
│   ├── generar_dataset.py     # Generador reproducible del dataset (NetworkX + NumPy + Pandas)
│   ├── experimentos.py        # Ejecuta el experimento comparativo y exporta resultados/experimentos.csv
│   └── verificar.py           # Ejecuta la verificación completa y guarda resultados/verificacion.json
├── tests/
│   └── test_algoritmos.py     # Suite de 11 pruebas unitarias (unittest / pytest + NetworkX opcional)
├── data/
│   ├── nodos.csv              # 1 800 ubicaciones (45 × 40) en 3 zonas (585 / 630 / 585)
│   ├── aristas.csv            # 3 515 pasillos con distancias, congestión y tiempos
│   └── dataset.js             # Empaquetado offline para la interfaz gráfica
└── index.html, js/            # Interfaz gráfica interactiva conectada a Python (/api/*)
```

## Cómo ejecutar el programa en Python

Funciona directamente con la librería estándar de Python 3.10+ (y usa `networkx`/`pytest` opcionalmente si están instalados):

```bash
# 1. Levantar la aplicación completa (consola + servidor en http://localhost:8501 + abre el navegador)
python app.py

# 2. Ejecutar solo en consola (demostración + verificación por certificado de optimalidad)
python app.py --cli

# 3. Correr los experimentos comparativos (genera resultados/experimentos.csv)
python scripts/experimentos.py

# 4. Correr la suite de 11 pruebas unitarias
python -m unittest discover -s tests
```
