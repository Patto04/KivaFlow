"""Paquete KivaFlow · Algoritmos de grafos para optimización de picking en almacenes inteligentes.

Curso: 1ACC0184 - Complejidad Algorítmica (UPC, Sección 4834).
Algoritmos implementados:
- BFS (Búsqueda en Anchura)             — O(V + E)
- Bellman-Ford (con salida anticipada)  — O(V · E)
- Edmonds-Karp (Flujo Máximo / Min-Cut) — O(V · E²)
"""

from . import bellman_ford, bfs, edmonds_karp, grafo, paleta, pedido, simulacion, verificacion

__all__ = [
    "grafo",
    "bfs",
    "bellman_ford",
    "edmonds_karp",
    "pedido",
    "simulacion",
    "verificacion",
    "paleta",
]
