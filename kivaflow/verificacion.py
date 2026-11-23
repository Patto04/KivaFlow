"""Verificación matemática de integridad del grafo y exactitud de BFS, Bellman-Ford y Edmonds-Karp.

Para Bellman-Ford se emplea un Certificado de Optimalidad de Caminos Mínimos (CLRS, Lema 24.10)
sin recurrir a algoritmos externos:
1. Factibilidad dual (desigualdad triangular): para toda arista dirigida (u, v, w), dist[v] <= dist[u] + w.
2. Factibilidad primal (holgura complementaria): el camino reconstruido desde `origen` hasta `destino`
   es conexo en G y la suma exacta de los pesos de sus aristas es igual a dist[destino].
"""
from __future__ import annotations

import platform
import sys
import time
from typing import Any

from . import bellman_ford as bf
from . import bfs as bfs_mod
from . import edmonds_karp as ek
from . import grafo


def certificar_bellman_ford(
    dist: dict[str, float],
    padre: dict[str, str | None],
    aristas_dirigidas: list[tuple[str, str, float]],
    por_par: dict[tuple[str, str], dict[str, Any]],
    origen: str,
    destino: str,
    perfil: str = "punta",
) -> tuple[bool, float]:
    """Comprueba las condiciones de optimalidad de Bellman-Ford sin usar otro algoritmo.

    Devuelve (es_optimo, error_maximo).
    """
    if abs(dist.get(origen, 1.0)) > 1e-12:
        return False, abs(dist.get(origen, 1.0))

    max_violacion = 0.0
    for u, v, w in aristas_dirigidas:
        du = dist[u]
        dv = dist[v]
        if dv > du + w + 1e-9:
            max_violacion = max(max_violacion, dv - (du + w))

    camino = bfs_mod.reconstruir(padre, destino)
    if not camino or camino[0] != origen or camino[-1] != destino:
        return False, float("inf")

    campo = "tiempo_valle" if perfil == "valle" else "tiempo_punta"
    suma_camino = 0.0
    for u, v in zip(camino, camino[1:]):
        a = por_par.get(grafo.edge_key(u, v))
        if not a:
            return False, float("inf")
        suma_camino += float(a[campo])

    err_camino = abs(suma_camino - dist[destino])
    error_max = max(max_violacion, err_camino)
    return error_max < 1e-6, error_max


def verificar_todo(
    nodos: dict[str, dict[str, Any]],
    aristas: list[dict[str, Any]],
    n_bfs: int = 60,
    n_bf: int = 24,
    semilla: int = 42,
) -> dict[str, Any]:
    """Ejecuta la batería de verificación sobre el dataset del almacén usando Mulberry32."""
    t0 = time.perf_counter()
    rng = grafo.mulberry32(semilla)
    ids = list(nodos.keys())
    ady_punta, dir_punta, por_par = grafo.construir_estructuras(nodos, aristas, "punta")
    _, dir_valle, _ = grafo.construir_estructuras(nodos, aristas, "valle")

    # 1. Integridad del grafo
    conn = bfs_mod.bfs(ady_punta, ids[0], "__NINGUNO__")
    es_conexo = conn["visitados"] == len(ids)
    sin_aislados = all(len(ady_punta[nid]) > 0 for nid in ids)
    pesos_positivos = all(a["dist"] > 0 and a["tiempo_punta"] > 0 for a in aristas)

    # 2. BFS (longitud exacta Manhattan en la cuadrícula y camino legal)
    aciertos_bfs = 0
    for _ in range(n_bfs):
        s = ids[int(rng() * len(ids))]
        t = ids[int(rng() * len(ids))]
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

    # 3. Bellman-Ford: Certificado de optimalidad (dist[v] <= dist[u] + w y suma exacta del camino) + 0 ciclos negativos
    aciertos_bf = 0
    ciclos_negativos = 0
    error_max_bf = 0.0
    for i in range(n_bf):
        perfil = "punta" if i % 2 == 0 else "valle"
        dirigidas = dir_punta if perfil == "punta" else dir_valle
        s = ids[int(rng() * len(ids))]
        t = ids[int(rng() * len(ids))]
        try:
            dist, padre, _ = bf.bellman_ford(ids, dirigidas, s)
            ok, err = certificar_bellman_ford(dist, padre, dirigidas, por_par, s, t, perfil)
            error_max_bf = max(error_max_bf, err)
            if ok:
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
