"""Generador reproducible del dataset sintético del almacén KivaFlow (45 × 40 = 1 800 nodos, 3 515 aristas).

Utiliza NetworkX, NumPy y Pandas conforme a la metodología descrita en el informe:
- Cuadrícula de 45 filas × 40 columnas (1 800 nodos y 3 515 aristas).
- Tres zonas funcionales:
    * Recepción y Almacenamiento: columnas 0..12 (585 nodos)
    * Picking                   : columnas 13..26 (630 nodos)
    * Empaque y Despacho        : columnas 27..39 (585 nodos)
- Pasillos horizontales (PH00..PH44) de 1.5 m y verticales (PV00..PV39) de 2.5 m.
- Frecuencia de tránsito (Baja ×1.0, Media ×1.5, Alta ×2.0) y velocidad media de 1.1 m/s.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DATA_DIR = RAIZ / "data"

FILAS = 45
COLUMNAS = 40
VELOCIDAD_MS = 1.1
FACTOR_CONGESTION = {"Baja": 1.0, "Media": 1.5, "Alta": 2.0}


def zona_por_columna(col: int) -> str:
    if col <= 12:
        return "Recepción y Almacenamiento"
    if col <= 26:
        return "Picking"
    return "Empaque y Despacho"


def es_estacion_trabajo(fila: int, col: int) -> bool:
    if col in (0, 39):
        return True
    if col in (13, 26) and fila % 9 == 0:
        return True
    return False


def construir_grafo(semilla: int = 42) -> tuple[nx.Graph, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(semilla)
    G = nx.Graph()

    filas_nodos = []
    for f in range(FILAS):
        for c in range(COLUMNAS):
            nid = f"F{f:02d}_C{c:02d}"
            zona = zona_por_columna(c)
            est = es_estacion_trabajo(f, c)
            tipo = "Estación de trabajo" if est else "Rack de almacenamiento"
            sku = "" if est else f"SKU-{int(rng.integers(1, 601)):04d}"
            G.add_node(nid, Fila=f, Columna=c, Zona=zona, Tipo_Ubicacion=tipo, SKU_Principal=sku)
            filas_nodos.append(
                {
                    "Nodo": nid,
                    "Fila": f,
                    "Columna": c,
                    "Zona": zona,
                    "Tipo_Ubicacion": tipo,
                    "SKU_Principal": sku,
                }
            )

    niveles = ["Baja", "Media", "Alta"]
    probs = [0.436, 0.346, 0.218]
    filas_aristas = []

    for f in range(FILAS):
        for c in range(COLUMNAS):
            u = f"F{f:02d}_C{c:02d}"
            for df, dc, dist, pasillo in (
                (0, 1, 1.5, f"PH{f:02d}"),
                (1, 0, 2.5, f"PV{c:02d}"),
            ):
                nf, nc = f + df, c + dc
                if nf >= FILAS or nc >= COLUMNAS:
                    continue
                v = f"F{nf:02d}_C{nc:02d}"
                frec = str(rng.choice(niveles, p=probs))
                dist_adj = round(dist * FACTOR_CONGESTION[frec], 2)
                tiempo = round(dist_adj / VELOCIDAD_MS, 3)
                zu = zona_por_columna(c)
                zv = zona_por_columna(nc)
                G.add_edge(
                    u,
                    v,
                    Pasillo=pasillo,
                    Distancia_m=dist,
                    Frecuencia_Pedidos=frec,
                    Distancia_Ajustada_m=dist_adj,
                    Tiempo_Estimado_s=tiempo,
                    Zona_Origen=zu,
                    Zona_Destino=zv,
                )
                filas_aristas.append(
                    {
                        "Nodo_Origen": u,
                        "Nodo_Destino": v,
                        "Pasillo": pasillo,
                        "Distancia_m": dist,
                        "Frecuencia_Pedidos": frec,
                        "Distancia_Ajustada_m": dist_adj,
                        "Tiempo_Estimado_s": tiempo,
                        "Zona_Origen": zu,
                        "Zona_Destino": zv,
                    }
                )

    assert G.number_of_nodes() == 1800, f"Se esperaban 1800 nodos, se obtuvieron {G.number_of_nodes()}"
    assert G.number_of_edges() == 3515, f"Se esperaban 3515 aristas, se obtuvieron {G.number_of_edges()}"
    assert nx.is_connected(G), "El grafo generado debe ser conexo"

    return G, pd.DataFrame(filas_nodos), pd.DataFrame(filas_aristas)


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera nodos.csv y aristas.csv con NetworkX, NumPy y Pandas")
    parser.add_argument("--out", type=Path, default=DATA_DIR, help="Carpeta de salida (por defecto: data/)")
    parser.add_argument("--seed", type=int, default=42, help="Semilla reproducible")
    args = parser.parse_args()

    G, df_nodos, df_aristas = construir_grafo(args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    df_nodos.to_csv(args.out / "nodos.csv", index=False, encoding="utf-8")
    df_aristas.to_csv(args.out / "aristas.csv", index=False, encoding="utf-8")
    print(f"Dataset generado en {args.out}: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas (conexo={nx.is_connected(G)})")


if __name__ == "__main__":
    main()
