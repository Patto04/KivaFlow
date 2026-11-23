"""Algoritmo de Bellman-Ford: ruta de menor costo ponderado considerando la congestión.

Incluye optimización de salida anticipada (early termination) y verificación de ciclos negativos.
Complejidad temporal: O(V · E)
Complejidad espacial: O(V)
"""
from __future__ import annotations

from math import inf, isfinite
from typing import Iterable

from .bfs import reconstruir
from .grafo import edge_key


class CicloNegativoError(Exception):
    """Excepción lanzada si se detecta un ciclo de peso negativo alcanzable."""


def bellman_ford(
    nodos: Iterable[str],
    aristas_dirigidas: list[tuple[str, str, float]],
    origen: str,
    pasos: list[list[str]] | None = None,
    aristas_bloqueadas: set[tuple[str, str]] | None = None,
) -> tuple[dict[str, float], dict[str, str | None], dict[str, int]]:
    """Calcula distancias mínimas desde `origen` hacia todos los nodos.

    Devuelve (dist, padre, stats) con stats = {"rondas", "relajaciones", "aristas_revisadas"}.
    """
    dist: dict[str, float] = {n: inf for n in nodos}
    padre: dict[str, str | None] = {n: None for n in dist}
    dist[origen] = 0.0

    rondas = 0
    relajaciones = 0
    aristas_revisadas = 0
    total_nodos = len(dist)

    for _ in range(total_nodos - 1):
        rondas += 1
        cambio = False
        mejorados: list[str] = []

        for u, v, w in aristas_dirigidas:
            aristas_revisadas += 1
            if aristas_bloqueadas and edge_key(u, v) in aristas_bloqueadas:
                continue
            du = dist[u]
            if du != inf and du + w < dist[v] - 1e-12:
                dist[v] = du + w
                padre[v] = u
                relajaciones += 1
                cambio = True
                if pasos is not None:
                    mejorados.append(v)

        if pasos is not None:
            pasos.append(list(dict.fromkeys(mejorados)))
        if not cambio:
            break
    else:
        for u, v, w in aristas_dirigidas:
            if aristas_bloqueadas and edge_key(u, v) in aristas_bloqueadas:
                continue
            if dist[u] != inf and dist[u] + w < dist[v] - 1e-12:
                raise CicloNegativoError(f"Ciclo negativo detectado en la arista {u} -> {v}")

    return dist, padre, {
        "rondas": rondas,
        "relajaciones": relajaciones,
        "aristas_revisadas": aristas_revisadas,
    }


def ruta_minima(
    nodos: Iterable[str],
    aristas_dirigidas: list[tuple[str, str, float]],
    origen: str,
    destino: str,
    aristas_bloqueadas: set[tuple[str, str]] | None = None,
) -> dict[str, object]:
    """Calcula el camino óptimo entre `origen` y `destino` usando Bellman-Ford."""
    dist, padre, stats = bellman_ford(nodos, aristas_dirigidas, origen, None, aristas_bloqueadas)
    costo = dist.get(destino, inf)
    if not isfinite(costo):
        return {"camino": [], "costo": inf, "stats": stats}
    return {"camino": reconstruir(padre, destino), "costo": costo, "stats": stats}
