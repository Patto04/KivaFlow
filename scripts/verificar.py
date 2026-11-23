"""Script de verificación completa de los algoritmos en Python (guarda resultados/verificacion.json)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from kivaflow import grafo, verificacion  # noqa: E402


def main() -> None:
    nodos = grafo.leer_nodos()
    aristas = grafo.leer_aristas()
    res = verificacion.verificar_todo(nodos, aristas, n_bfs=100, n_bf=40, semilla=42)

    out_dir = RAIZ / "resultados"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "verificacion.json"
    out_file.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Verificación completada en {res['segundos']} s -> {out_file}")
    for nombre, d in res["algoritmos"].items():
        print(f" • {nombre:14s}: {d['aciertos']}/{d['consultas']} aciertos")


if __name__ == "__main__":
    main()
