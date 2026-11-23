"""Algoritmo de Edmonds-Karp (Ford-Fulkerson con BFS): flujo máximo y corte mínimo entre zonas.

Complejidad temporal: O(V · E²)
Complejidad espacial: O(V + E)
"""
from __future__ import annotations

from collections import deque
from typing import Any

FUENTE = "__FUENTE__"
SUMIDERO = "__SUMIDERO__"


def _bfs_camino_aumento(residual: dict[str, dict[str, int]], s: str, t: str) -> dict[str, str | None] | None:
    padre: dict[str, str | None] = {s: None}
    cola: deque[str] = deque([s])
    while cola:
        u = cola.popleft()
        for v, cap_res in residual.get(u, {}).items():
            if cap_res > 0 and v not in padre:
                padre[v] = u
                if v == t:
                    return padre
                cola.append(v)
    return None


def _alcanzables_residual(residual: dict[str, dict[str, int]], s: str) -> set[str]:
    vistos: set[str] = {s}
    cola: deque[str] = deque([s])
    while cola:
        u = cola.popleft()
        for v, cap_res in residual.get(u, {}).items():
            if cap_res > 0 and v not in vistos:
                vistos.add(v)
                cola.append(v)
    return vistos


def flujo_maximo(
    capacidad: dict[str, dict[str, int]],
    s: str,
    t: str,
    pasos: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Ejecuta Edmonds-Karp entre fuente `s` y sumidero `t`."""
    residual: dict[str, dict[str, int]] = {u: dict(vec) for u, vec in capacidad.items()}
    for u, vec in capacidad.items():
        for v in vec:
            residual.setdefault(v, {}).setdefault(u, 0)
    residual.setdefault(s, {})
    residual.setdefault(t, {})

    valor_flujo = 0
    caminos_aumento = 0

    while (padre := _bfs_camino_aumento(residual, s, t)) is not None:
        caminos_aumento += 1
        delta = 10**9
        v = t
        while padre[v] is not None:
            u = padre[v]  # type: ignore[assignment]
            delta = min(delta, residual[u][v])
            v = u

        if pasos is not None:
            camino: list[str] = []
            x: str | None = t
            while x is not None:
                if x not in (FUENTE, SUMIDERO):
                    camino.append(x)
                x = padre[x]
            camino.reverse()
            pasos.append({"camino": camino, "delta": delta})

        v = t
        while padre[v] is not None:
            u = padre[v]  # type: ignore[assignment]
            residual[u][v] -= delta
            residual[v][u] += delta
            v = u
        valor_flujo += delta

    lado_fuente = _alcanzables_residual(residual, s)
    corte_minimo: list[dict[str, Any]] = []
    for u in lado_fuente:
        for v, cap_orig in capacidad.get(u, {}).items():
            if v not in lado_fuente and u != FUENTE and v != SUMIDERO:
                corte_minimo.append({"u": u, "v": v, "cap": cap_orig})

    return {
        "flujo_maximo": valor_flujo,
        "caminos_aumento": caminos_aumento,
        "corte_minimo": corte_minimo,
        "lado_fuente": lado_fuente,
    }


def entre_zonas(
    capacidad: dict[str, dict[str, int]],
    nodos: dict[str, dict[str, Any]],
    zona_origen: str,
    zona_destino: str,
    pasos: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Calcula el flujo máximo y los cuellos de botella (corte mínimo) desde `zona_origen` hasta `zona_destino`."""
    infinito = sum(c for vec in capacidad.values() for c in vec.values())
    cap: dict[str, dict[str, int]] = {u: dict(vec) for u, vec in capacidad.items()}
    cap[FUENTE] = {nid: infinito for nid, d in nodos.items() if d["zona"] == zona_origen}
    for nid, d in nodos.items():
        if d["zona"] == zona_destino:
            cap.setdefault(nid, {})[SUMIDERO] = infinito

    return flujo_maximo(cap, FUENTE, SUMIDERO, pasos)
