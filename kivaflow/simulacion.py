"""Simulación de un turno con múltiples operarios, congestión dinámica acumulativa y flujo máximo."""
from __future__ import annotations

import random
from collections import Counter
from typing import Any

from . import edmonds_karp as ek
from . import grafo, pedido


def simular_turno(
    nodos: dict[str, dict[str, Any]],
    aristas: list[dict[str, Any]],
    n_operarios: int = 24,
    max_productos: int = 3,
    algoritmo: str = "bfs",
    perfil: str = "punta",
    zona_origen: str = "Recepción y Almacenamiento",
    zona_destino: str = "Empaque y Despacho",
    semilla: int = 1,
) -> dict[str, Any]:
    """Simula un turno de operarios y evalúa el impacto de sus cruces sobre el flujo máximo entre zonas."""
    rng = random.Random(semilla)
    ady, dirigidas, _ = grafo.construir_estructuras(nodos, aristas, perfil)
    ids = list(nodos.keys())
    muelles = [nid for nid, d in nodos.items() if d["es_estacion"] and d["zona"] == "Empaque y Despacho"]
    if not muelles:
        muelles = [nid for nid, d in nodos.items() if d["es_estacion"]]
    racks = [nid for nid, d in nodos.items() if not d["es_estacion"]]

    operarios: list[dict[str, Any]] = []
    uso: Counter[tuple[str, str]] = Counter()

    for i in range(n_operarios):
        inicio = rng.choice(muelles)
        k = rng.randint(1, max_productos)
        destinos = rng.sample(racks, k)
        r = pedido.ruta_pedido(ids, ady, dirigidas, inicio, destinos, algoritmo, regresar=True)
        camino = r["camino"]
        operarios.append({"id": i + 1, "muelle": inicio, "racks": destinos, "camino": camino})
        for u, v in zip(camino, camino[1:]):
            uso[grafo.edge_key(u, v)] += 1

    conteos = sorted(uso.values())
    t1 = conteos[len(conteos) // 3] if conteos else 1
    t2 = conteos[(2 * len(conteos)) // 3] if conteos else 2
    rango = {"Baja": 0, "Media": 1, "Alta": 2}
    por_rango = ["Baja", "Media", "Alta"]

    niveles_dinamicos: dict[tuple[str, str], str] = {}
    for a in aristas:
        k = a["key"]
        c = uso.get(k, 0)
        nivel_turno = "Baja"
        if c > t2 and c >= 2:
            nivel_turno = "Alta"
        elif c > t1 and c >= 1:
            nivel_turno = "Media"
        idx = min(2, max(rango.get(a["frec"], 0), rango[nivel_turno]) + (1 if c > t2 else 0))
        niveles_dinamicos[k] = por_rango[idx]

    cap_turno = grafo.capacidades(aristas, niveles_dinamicos)
    res_flujo = ek.entre_zonas(cap_turno, nodos, zona_origen, zona_destino)

    cap_base = grafo.capacidades(aristas, None)
    flujo_base = ek.entre_zonas(cap_base, nodos, zona_origen, zona_destino)["flujo_maximo"]

    return {
        "operarios": len(operarios),
        "pasillos_usados": len(uso),
        "max_cruces": max(uso.values()) if uso else 0,
        "flujo_maximo": res_flujo["flujo_maximo"],
        "flujo_base": flujo_base,
        "corte_minimo_pasillos": len(res_flujo["corte_minimo"]),
        "caminos_aumento": res_flujo["caminos_aumento"],
    }
