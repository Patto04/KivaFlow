"""Ruteo de pedidos multi-producto mediante estrategia voraz de vecino más cercano y medición de métricas."""
from __future__ import annotations

from math import inf, isfinite
from typing import Any, Iterable

from . import bellman_ford as bf
from . import bfs as bfs_mod
from .grafo import edge_key


def ruta_pedido(
    nodos_ids: Iterable[str],
    ady: dict[str, list[tuple[str, float]]],
    aristas_dirigidas: list[tuple[str, str, float]],
    inicio: str,
    destinos: list[str],
    algoritmo: str = "bfs",
    regresar: bool = False,
    nodos_bloqueados: set[str] | None = None,
) -> dict[str, Any]:
    """Calcula la ruta completa para recoger todos los `destinos` desde `inicio`."""
    bloqueados = nodos_bloqueados if nodos_bloqueados else set()
    aristas_bloq: set[tuple[str, str]] | None = None
    if bloqueados:
        aristas_bloq = set()
        for nid in bloqueados:
            for nb, _ in ady.get(nid, ()):
                aristas_bloq.add(edge_key(nid, nb))

    pendientes = {d for d in destinos if d != inicio and d not in bloqueados}
    actual = inicio
    camino_total: list[str] = [inicio]
    orden_visita: list[str] = []
    visitados_tot = 0
    rondas_tot = 0
    relajaciones_tot = 0
    aristas_rev_tot = 0

    while pendientes:
        if algoritmo == "bfs":
            res = bfs_mod.bfs(ady, actual, pendientes, None, bloqueados)
            tramo = list(res["camino"])  # type: ignore[arg-type]
            sig = res["alcanzado"]
            visitados_tot += int(res["visitados"])  # type: ignore[arg-type]
            aristas_rev_tot += int(res["aristas_revisadas"])  # type: ignore[arg-type]
        else:
            dist, padre, st = bf.bellman_ford(nodos_ids, aristas_dirigidas, actual, None, aristas_bloq)
            rondas_tot += st["rondas"]
            relajaciones_tot += st["relajaciones"]
            aristas_rev_tot += st["aristas_revisadas"]
            mejor_costo = inf
            sig = None
            for p in pendientes:
                if dist.get(p, inf) < mejor_costo:
                    mejor_costo = dist[p]
                    sig = p
            tramo = bfs_mod.reconstruir(padre, str(sig)) if sig is not None else []

        if not sig or not tramo:
            break
        pendientes.remove(str(sig))
        orden_visita.append(str(sig))
        camino_total.extend(tramo[1:])
        actual = str(sig)

    if regresar and actual != inicio:
        if algoritmo == "bfs":
            res = bfs_mod.bfs(ady, actual, inicio, None, bloqueados)
            tramo = list(res["camino"])  # type: ignore[arg-type]
            visitados_tot += int(res["visitados"])  # type: ignore[arg-type]
            aristas_rev_tot += int(res["aristas_revisadas"])  # type: ignore[arg-type]
        else:
            dist, padre, st = bf.bellman_ford(nodos_ids, aristas_dirigidas, actual, None, aristas_bloq)
            rondas_tot += st["rondas"]
            relajaciones_tot += st["relajaciones"]
            aristas_rev_tot += st["aristas_revisadas"]
            tramo = bfs_mod.reconstruir(padre, inicio) if isfinite(dist.get(inicio, inf)) else []
        camino_total.extend(tramo[1:])

    return {
        "camino": camino_total,
        "orden": orden_visita,
        "incompleto": len(pendientes) > 0,
        "stats": {
            "visitados": visitados_tot,
            "rondas": rondas_tot,
            "relajaciones": relajaciones_tot,
            "aristas_revisadas": aristas_rev_tot,
        },
    }


def medir_ruta(
    camino: list[str],
    por_par: dict[tuple[str, str], dict[str, Any]],
    perfil: str = "punta",
) -> dict[str, Any]:
    """Calcula distancia física, distancia ajustada, tiempo en segundos y conteo de pasillos."""
    dist_fisica = 0.0
    dist_ajustada = 0.0
    tiempo_s = 0.0
    alta = media = baja = 0

    for u, v in zip(camino, camino[1:]):
        a = por_par.get(edge_key(u, v))
        if not a:
            continue
        dist_fisica += float(a["dist"])
        dist_ajustada += float(a["dist_adj_valle"] if perfil == "valle" else a["dist_adj_punta"])
        tiempo_s += float(a["tiempo_valle"] if perfil == "valle" else a["tiempo_punta"])
        if a["frec"] == "Alta":
            alta += 1
        elif a["frec"] == "Media":
            media += 1
        else:
            baja += 1

    return {
        "pasillos": max(0, len(camino) - 1),
        "dist_fisica_m": round(dist_fisica, 2),
        "dist_ajustada_m": round(dist_ajustada, 2),
        "tiempo_s": round(tiempo_s, 2),
        "alta": alta,
        "media": media,
        "baja": baja,
    }
