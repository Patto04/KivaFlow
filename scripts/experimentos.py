"""Script de experimentos comparativos en Python (BFS vs. Bellman-Ford y Edmonds-Karp).

Genera `resultados/experimentos.csv` con escenarios de 1, 5 y 10 productos en hora valle y hora punta.
"""
from __future__ import annotations

import csv
import random
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from kivaflow import edmonds_karp as ek  # noqa: E402
from kivaflow import grafo, pedido  # noqa: E402


def ejecutar_experimentos(pedidos_por_escenario: int = 10, semilla: int = 42) -> list[dict[str, object]]:
    nodos = grafo.leer_nodos()
    aristas = grafo.leer_aristas()
    ids = list(nodos.keys())
    muelles = [nid for nid, d in nodos.items() if d["es_estacion"] and d["zona"] == "Empaque y Despacho"]
    racks = [nid for nid, d in nodos.items() if not d["es_estacion"]]
    rng = random.Random(semilla)

    filas: list[dict[str, object]] = []
    escenarios = [("valle", 1), ("valle", 5), ("valle", 10), ("punta", 1), ("punta", 5), ("punta", 10)]

    print(f"{'Hora':8s} | {'Prod':4s} | {'Pas.BFS':7s} | {'Pas.BF':7s} | {'T.BFS(s)':8s} | {'T.BF(s)':8s} | {'Ahorro':7s}")
    print("-" * 68)

    for hora, n_prod in escenarios:
        ady, dirigidas, por_par = grafo.construir_estructuras(nodos, aristas, hora)
        pas_bfs = pas_bf = dist_bfs = dist_bf = t_bfs = t_bf = vis_bfs = rel_bf = ms_bfs = ms_bf = 0.0

        for _ in range(pedidos_por_escenario):
            inicio = rng.choice(muelles)
            destinos = rng.sample(racks, n_prod)

            t0 = time.perf_counter()
            rb = pedido.ruta_pedido(ids, ady, dirigidas, inicio, destinos, "bfs", regresar=True)
            ms_bfs += (time.perf_counter() - t0) * 1000
            mb = pedido.medir_ruta(rb["camino"], por_par, hora)

            t1 = time.perf_counter()
            rf = pedido.ruta_pedido(ids, ady, dirigidas, inicio, destinos, "bellman_ford", regresar=True)
            ms_bf += (time.perf_counter() - t1) * 1000
            mf = pedido.medir_ruta(rf["camino"], por_par, hora)

            pas_bfs += mb["pasillos"]
            pas_bf += mf["pasillos"]
            dist_bfs += mb["dist_ajustada_m"]
            dist_bf += mf["dist_ajustada_m"]
            t_bfs += mb["tiempo_s"]
            t_bf += mf["tiempo_s"]
            vis_bfs += rb["stats"]["visitados"]
            rel_bf += rf["stats"]["relajaciones"]

        n = float(pedidos_por_escenario)
        ahorro_pct = ((t_bfs - t_bf) / t_bfs) * 100 if t_bfs > 0 else 0.0
        fila = {
            "Escenario": hora,
            "Productos": n_prod,
            "Pasillos_BFS": round(pas_bfs / n, 2),
            "Pasillos_BF": round(pas_bf / n, 2),
            "Distancia_Ajustada_BFS_m": round(dist_bfs / n, 2),
            "Distancia_Ajustada_BF_m": round(dist_bf / n, 2),
            "Tiempo_BFS_s": round(t_bfs / n, 2),
            "Tiempo_BF_s": round(t_bf / n, 2),
            "Ahorro_BF_pct": round(ahorro_pct, 2),
            "Visitados_BFS": round(vis_bfs / n),
            "Relajaciones_BF": round(rel_bf / n),
            "ms_BFS": round(ms_bfs / n, 3),
            "ms_BF": round(ms_bf / n, 2),
        }
        filas.append(fila)
        print(
            f"{hora:8s} | {n_prod:4d} | {fila['Pasillos_BFS']:7.1f} | {fila['Pasillos_BF']:7.1f} | "
            f"{fila['Tiempo_BFS_s']:8.1f} | {fila['Tiempo_BF_s']:8.1f} | {fila['Ahorro_BF_pct']:6.1f}%"
        )

    out_dir = RAIZ / "resultados"
    out_dir.mkdir(exist_ok=True)
    csv_path = out_dir / "experimentos.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        writer.writeheader()
        writer.writerows(filas)

    res_ek = ek.entre_zonas(grafo.capacidades(aristas), nodos, "Recepción y Almacenamiento", "Empaque y Despacho")
    print("-" * 68)
    print(f"Edmonds-Karp (Recepción -> Despacho): flujo máximo = {res_ek['flujo_maximo']} op/min, corte = {len(res_ek['corte_minimo'])} pasillos")
    print(f"Resultados exportados en: {csv_path}")
    return filas


if __name__ == "__main__":
    ejecutar_experimentos()
