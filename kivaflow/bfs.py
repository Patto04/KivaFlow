"""Búsqueda en Anchura (BFS): línea base para hallar la ruta con menor número de pasillos.

Complejidad temporal: O(V + E)
Complejidad espacial: O(V)
"""
from __future__ import annotations

from collections import deque
from typing import Iterable


def reconstruir(padre: dict[str, str | None], destino: str) -> list[str]:
    camino: list[str] = []
    actual: str | None = destino
    while actual is not None:
        camino.append(actual)
        actual = padre.get(actual)
    camino.reverse()
    return camino


def bfs(
    ady: dict[str, list[tuple[str, float]]],
    origen: str,
    destino: str | Iterable[str],
    pasos: list[tuple[str, int]] | None = None,
    bloqueados: set[str] | None = None,
) -> dict[str, object]:
    """Ejecuta BFS desde `origen` hasta alcanzar `destino` (o el más cercano si es un conjunto).

    Devuelve {"camino", "alcanzado", "visitados", "aristas_revisadas"}.
    """
    destinos = {destino} if isinstance(destino, str) else set(destino)
    padre: dict[str, str | None] = {origen: None}
    nivel: dict[str, int] = {origen: 0}
    cola: deque[str] = deque([origen])
    visitados = 0
    aristas_revisadas = 0

    while cola:
        u = cola.popleft()
        visitados += 1
        lv = nivel[u]
        if pasos is not None:
            pasos.append((u, lv))

        if u in destinos:
            return {
                "camino": reconstruir(padre, u),
                "alcanzado": u,
                "visitados": visitados,
                "aristas_revisadas": aristas_revisadas,
            }

        for v, _ in ady.get(u, ()):
            aristas_revisadas += 1
            if bloqueados and v in bloqueados:
                continue
            if v not in padre:
                padre[v] = u
                nivel[v] = lv + 1
                cola.append(v)

    return {
        "camino": [],
        "alcanzado": None,
        "visitados": visitados,
        "aristas_revisadas": aristas_revisadas,
    }
