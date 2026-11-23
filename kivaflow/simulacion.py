"""Simulación de un turno con múltiples operarios, congestión progresiva entre operarios y flujo máximo."""
from __future__ import annotations

from collections import Counter
from typing import Any

from . import edmonds_karp as ek
from . import grafo, pedido


def simular_turno(
    nodos: dict[str, dict[str, Any]],
    aristas: list[dict[str, Any]],
    n_operarios: int = 12,
    max_productos: int = 3,
    algoritmo: str = "bfs",
    perfil: str = "punta",
    zona_origen: str = "Recepción y Almacenamiento",
    zona_destino: str = "Empaque y Despacho",
    semilla: int = 1,
) -> dict[str, Any]:
    """Simula un turno de operarios donde la congestión acumulada afecta progresivamente el ruteo."""
    rng = grafo.mulberry32(semilla)
    ady, dirigidas_base, por_par = grafo.construir_estructuras(nodos, aristas, perfil)
    ids = list(nodos.keys())
    muelles = [nid for nid, d in nodos.items() if d["es_estacion"] and d["zona"] == "Empaque y Despacho"]
    if not muelles:
        muelles = [nid for nid, d in nodos.items() if d["es_estacion"]]
    racks_picking = [nid for nid, d in nodos.items() if not d["es_estacion"] and d["zona"] == "Picking"]
    racks = racks_picking if racks_picking else [nid for nid, d in nodos.items() if not d["es_estacion"]]

    cap_base = grafo.capacidades(aristas, None)
    ek_base = ek.entre_zonas(cap_base, nodos, zona_origen, zona_destino)
    flujo_base = ek_base["flujo_maximo"]
    corte_keys = {grafo.edge_key(c["u"], c["v"]) for c in ek_base["corte_minimo"]}

    operarios: list[dict[str, Any]] = []
    uso: Counter[tuple[str, str]] = Counter()
    suma_tiempo = 0.0

    for i in range(n_operarios):
        inicio = muelles[int(rng() * len(muelles))]
        k = 1 + int(rng() * max_productos)
        destinos: list[str] = []
        vistos = {inicio}
        while len(destinos) < k:
            cand = racks[int(rng() * len(racks))]
            if cand not in vistos:
                vistos.add(cand)
                destinos.append(cand)

        if algoritmo in ("bellman_ford", "edmonds_karp") and uso:
            es_anti_cuello = algoritmo == "edmonds_karp"
            dirigidas_din = [
                (
                    u,
                    v,
                    w
                    * (1.45 if (es_anti_cuello and grafo.edge_key(u, v) in corte_keys) else 1.0)
                    * (1.0 + uso.get(grafo.edge_key(u, v), 0) * (0.28 if es_anti_cuello else 0.12)),
                )
                for u, v, w in dirigidas_base
            ]
            r = pedido.ruta_pedido(ids, ady, dirigidas_din, inicio, destinos, "bellman_ford", regresar=True)
        else:
            alg_real = "bfs" if algoritmo == "bfs" else "bellman_ford"
            r = pedido.ruta_pedido(ids, ady, dirigidas_base, inicio, destinos, alg_real, regresar=True)

        camino = r["camino"]
        met = pedido.medir_ruta(camino, por_par, perfil)
        suma_tiempo += met["tiempo_s"]
        operarios.append({"id": i + 1, "muelle": inicio, "racks": destinos, "camino": camino, "tiempo_s": met["tiempo_s"]})
        for u, v in zip(camino, camino[1:]):
            uso[grafo.edge_key(u, v)] += 1

    conteos = sorted(uso.values())
    t1 = conteos[len(conteos) // 3] if conteos else 1
    t2 = conteos[(2 * len(conteos)) // 3] if conteos else 2
    rango = {"Baja": 0, "Media": 1, "Alta": 2}
    por_rango = ["Baja", "Media", "Alta"]

    niveles_dinamicos: dict[tuple[str, str], str] = {}
    for a in aristas:
        k_edge = a["key"]
        c = uso.get(k_edge, 0)
        nivel_turno = "Baja"
        if c > t2 and c >= 2:
            nivel_turno = "Alta"
        elif c > t1 and c >= 1:
            nivel_turno = "Media"
        idx = min(2, max(rango.get(a["frec"], 0), rango[nivel_turno]) + (1 if c > t2 else 0))
        niveles_dinamicos[k_edge] = por_rango[idx]

    cap_turno = grafo.capacidades(aristas, niveles_dinamicos)
    res_flujo = ek.entre_zonas(cap_turno, nodos, zona_origen, zona_destino)

    return {
        "algoritmo": algoritmo,
        "operarios": len(operarios),
        "tiempo_medio_s": round(suma_tiempo / max(1, len(operarios)), 1),
        "pasillos_usados": len(uso),
        "max_cruces": max(uso.values()) if uso else 0,
        "flujo_maximo": res_flujo["flujo_maximo"],
        "flujo_base": flujo_base,
        "corte_minimo_pasillos": len(res_flujo["corte_minimo"]),
        "caminos_aumento": res_flujo["caminos_aumento"],
    }
