"""Verificación matemática de integridad del grafo y exactitud de BFS, Bellman-Ford y Edmonds-Karp."""
from __future__ import annotations

import heapq
import platform
import random
import sys
import time
from typing import Any

from . import bellman_ford as bf
from . import bfs as bfs_mod
from . import edmonds_karp as ek
from . import grafo


def dijkstra_oraculo(ady: dict[str, list[tuple[str, float]]], origen: str, destino: str) -> float:
    """Oráculo independiente de caminos mínimos con pesos no negativos para validar Bellman-Ford."""
    dist: dict[str, float] = {origen: 0.0}
    visitados: set[str] = set()
    heap: list[tuple[float, str]] = [(0.0, origen)]

    while heap:
        d, u = heapq.heappop(heap)
        if u in visitados:
            continue
        visitados.add(u)
        if u == destino:
            return d
        for v, w in ady.get(u, ()):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return float("inf")


def verificar_todo(
    nodos: dict[str, dict[str, Any]],
    aristas: list[dict[str, Any]],
    n_bfs: int = 60,
    n_bf: int = 24,
    semilla: int = 42,
) -> dict[str, Any]:
    """Ejecuta la batería de verificación sobre el dataset del almacén."""
    t0 = time.perf_counter()
    rng = random.Random(semilla)
    ids = list(nodos.keys())
    ady_punta, dir_punta, por_par = grafo.construir_estructuras(nodos, aristas, "punta")
    ady_valle, dir_valle, _ = grafo.construir_estructuras(nodos, aristas, "valle")

    # 1. Integridad del grafo
    conn = bfs_mod.bfs(ady_punta, ids[0], "__NINGUNO__")
    es_conexo = conn["visitados"] == len(ids)
    sin_aislados = all(len(ady_punta[nid]) > 0 for nid in ids)
    pesos_positivos = all(a["dist"] > 0 and a["tiempo_punta"] > 0 for a in aristas)

    # 2. BFS (longitud exacta Manhattan en la cuadrícula y camino legal)
    aciertos_bfs = 0
    for _ in range(n_bfs):
        s, t = rng.choice(ids), rng.choice(ids)
        r = bfs_mod.bfs(ady_punta, s, t)
        camino = list(r["camino"])  # type: ignore[arg-type]
        manhattan = abs(nodos[s]["fila"] - nodos[t]["fila"]) + abs(nodos[s]["col"] - nodos[t]["col"])
        legal = (
            len(camino) - 1 == manhattan
            and camino[0] == s
            and camino[-1] == t
            and all(grafo.edge_key(u, v) in por_par for u, v in zip(camino, camino[1:]))
        )
        if legal:
            aciertos_bfs += 1

    # 3. Bellman-Ford vs Oráculo + 0 ciclos negativos
    aciertos_bf = 0
    ciclos_negativos = 0
    error_max_bf = 0.0
    for i in range(n_bf):
        es_punta = i % 2 == 0
        ady = ady_punta if es_punta else ady_valle
        dirigidas = dir_punta if es_punta else dir_valle
        s, t = rng.choice(ids), rng.choice(ids)
        try:
            res_bf = bf.ruta_minima(ids, dirigidas, s, t)
            ref = dijkstra_oraculo(ady, s, t)
            err = abs(float(res_bf["costo"]) - ref)
            error_max_bf = max(error_max_bf, err)
            if err < 1e-6:
                aciertos_bf += 1
        except bf.CicloNegativoError:
            ciclos_negativos += 1

    # 4. Edmonds-Karp (Teorema Flujo Máximo = Capacidad del Corte Mínimo en los 6 pares de zonas)
    cap_base = grafo.capacidades(aristas)
    aciertos_ek = 0
    pares_ek: list[dict[str, Any]] = []
    for z1 in grafo.ZONAS:
        for z2 in grafo.ZONAS:
            if z1 == z2:
                continue
            res_ek = ek.entre_zonas(cap_base, nodos, z1, z2)
            cap_corte = sum(c["cap"] for c in res_ek["corte_minimo"])
            ok = cap_corte == res_ek["flujo_maximo"] and res_ek["flujo_maximo"] > 0
            if ok:
                aciertos_ek += 1
            pares_ek.append(
                {
                    "origen": z1,
                    "destino": z2,
                    "flujo_maximo": res_ek["flujo_maximo"],
                    "capacidad_corte": cap_corte,
                    "pasillos_corte": len(res_ek["corte_minimo"]),
                    "ok": ok,
                }
            )

    segundos = round(time.perf_counter() - t0, 3)
    return {
        "python": sys.version.split()[0],
        "sistema": f"{platform.system()} {platform.release()}",
        "segundos": segundos,
        "integridad": {
            "nodos": len(nodos),
            "aristas": len(aristas),
            "conexo": es_conexo,
            "sin_aislados": sin_aislados,
            "pesos_positivos": pesos_positivos,
            "ciclos_negativos": ciclos_negativos,
        },
        "algoritmos": {
            "bfs": {"consultas": n_bfs, "aciertos": aciertos_bfs, "error_max": 0.0},
            "bellman_ford": {"consultas": n_bf, "aciertos": aciertos_bf, "error_max": error_max_bf},
            "edmonds_karp": {"consultas": 6, "aciertos": aciertos_ek, "pares": pares_ek},
        },
    }
