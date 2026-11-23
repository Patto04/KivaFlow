"""Carga y modelado del grafo G = (V, E) del almacén KivaFlow (1 800 nodos, 3 515 aristas)."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parent.parent
DATA_DIR = RAIZ / "data"

VELOCIDAD_MS = 1.1
PENALIZACION = {
    "punta": {"Baja": 1.0, "Media": 1.5, "Alta": 2.0},
    "valle": {"Baja": 1.0, "Media": 1.2, "Alta": 1.4},
}
CAPACIDAD = {"Baja": 3, "Media": 2, "Alta": 1}
ZONAS = [
    "Recepción y Almacenamiento",
    "Picking",
    "Empaque y Despacho",
]


def edge_key(u: str, v: str) -> tuple[str, str]:
    return (u, v) if u < v else (v, u)


def leer_nodos(ruta: Path | None = None) -> dict[str, dict[str, Any]]:
    archivo = ruta or (DATA_DIR / "nodos.csv")
    nodos: dict[str, dict[str, Any]] = {}
    with open(archivo, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            nid = r["Nodo"].strip()
            tipo = r["Tipo_Ubicacion"].strip()
            nodos[nid] = {
                "id": nid,
                "fila": int(r["Fila"]),
                "col": int(r["Columna"]),
                "zona": r["Zona"].strip(),
                "tipo": tipo,
                "es_estacion": tipo == "Estación de trabajo",
                "sku": (r.get("SKU_Principal") or "").strip(),
            }
    return nodos


def leer_aristas(ruta: Path | None = None) -> list[dict[str, Any]]:
    archivo = ruta or (DATA_DIR / "aristas.csv")
    aristas: list[dict[str, Any]] = []
    with open(archivo, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            u = r["Nodo_Origen"].strip()
            v = r["Nodo_Destino"].strip()
            dist = float(r["Distancia_m"])
            frec = r["Frecuencia_Pedidos"].strip()
            dist_punta = float(r["Distancia_Ajustada_m"])
            tiempo_punta = float(r["Tiempo_Estimado_s"])
            dist_valle = round(dist * PENALIZACION["valle"].get(frec, 1.0), 3)
            tiempo_valle = round(dist_valle / VELOCIDAD_MS, 3)
            aristas.append(
                {
                    "u": u,
                    "v": v,
                    "key": edge_key(u, v),
                    "pasillo": r["Pasillo"].strip(),
                    "dist": dist,
                    "frec": frec,
                    "dist_adj_punta": dist_punta,
                    "tiempo_punta": tiempo_punta,
                    "dist_adj_valle": dist_valle,
                    "tiempo_valle": tiempo_valle,
                    "zona_origen": r["Zona_Origen"].strip(),
                    "zona_destino": r["Zona_Destino"].strip(),
                }
            )
    return aristas


def construir_estructuras(
    nodos: dict[str, dict[str, Any]],
    aristas: list[dict[str, Any]],
    perfil: str = "punta",
) -> tuple[dict[str, list[tuple[str, float]]], list[tuple[str, str, float]], dict[tuple[str, str], dict[str, Any]]]:
    """Devuelve (lista_adyacencia, aristas_dirigidas, mapa_por_par)."""
    ady: dict[str, list[tuple[str, float]]] = {nid: [] for nid in nodos}
    dirigidas: list[tuple[str, str, float]] = []
    por_par: dict[tuple[str, str], dict[str, Any]] = {}

    campo_peso = "tiempo_valle" if perfil == "valle" else "tiempo_punta"
    for a in aristas:
        u, v = a["u"], a["v"]
        w = float(a[campo_peso])
        ady[u].append((v, w))
        ady[v].append((u, w))
        dirigidas.append((u, v, w))
        dirigidas.append((v, u, w))
        por_par[a["key"]] = a

    return ady, dirigidas, por_par


def capacidades(
    aristas: list[dict[str, Any]],
    niveles_dinamicos: dict[tuple[str, str], str] | None = None,
) -> dict[str, dict[str, int]]:
    """Construye el diccionario de capacidades {u: {v: cap}} según congestión (Baja=3, Media=2, Alta=1)."""
    cap: dict[str, dict[str, int]] = {}
    for a in aristas:
        u, v, k = a["u"], a["v"], a["key"]
        nivel = niveles_dinamicos.get(k, a["frec"]) if niveles_dinamicos else a["frec"]
        c = CAPACIDAD.get(nivel, 2)
        cap.setdefault(u, {})[v] = c
        cap.setdefault(v, {})[u] = c
    return cap


def indice_skus(nodos: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    skus: dict[str, list[str]] = {}
    for nid, d in nodos.items():
        if d["sku"]:
            skus.setdefault(d["sku"], []).append(nid)
    return skus
