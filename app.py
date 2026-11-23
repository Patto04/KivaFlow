"""KivaFlow · Programa principal en Python (Servidor Web Multihilo + API REST + Modo Consola CLI).

Formas de ejecutarlo:
1. Iniciar la aplicación web interactiva (en http://localhost:8501):
       python app.py
2. Ejecutar únicamente la verificación y demostración en consola:
       python app.py --cli
3. Ejecutar el experimento comparativo (60 pedidos) desde Python:
       python scripts/experimentos.py
"""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import threading
import time
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Any

from kivaflow import edmonds_karp as ek
from kivaflow import grafo, paleta, pedido, simulacion, verificacion

RAIZ = Path(__file__).resolve().parent
PUERTO_DEFAULT = 8501


class KivaFlowAPI:
    """Estado del grafo en memoria para responder consultas desde Python."""

    def __init__(self) -> None:
        self.nodos = grafo.leer_nodos()
        self.aristas = grafo.leer_aristas()
        self.ids = list(self.nodos.keys())
        self.skus = grafo.indice_skus(self.nodos)
        self.estructuras = {
            "punta": grafo.construir_estructuras(self.nodos, self.aristas, "punta"),
            "valle": grafo.construir_estructuras(self.nodos, self.aristas, "valle"),
        }
        self.cap_base = grafo.capacidades(self.aristas)
        self.muelles = [nid for nid, d in self.nodos.items() if d["es_estacion"] and d["zona"] == "Empaque y Despacho"]
        self.racks_picking = [nid for nid, d in self.nodos.items() if not d["es_estacion"] and d["zona"] == "Picking"]

    def calcular_comparacion(
        self,
        inicio: str = "F22_C39",
        destinos: list[str] | None = None,
        perfil: str = "punta",
        regresar: bool = False,
        bloqueados: list[str] | None = None,
    ) -> dict[str, Any]:
        dests = [d for d in (destinos or ["F05_C05", "F39_C10", "F11_C29"]) if d]
        bloq = set(bloqueados or [])
        ady, dirigidas, por_par = self.estructuras[perfil]
        salida: dict[str, Any] = {}
        for alg in ("bfs", "bellman_ford"):
            r = pedido.ruta_pedido(self.ids, ady, dirigidas, inicio, dests, alg, regresar, bloq)
            m = pedido.medir_ruta(r["camino"], por_par, perfil)
            salida[alg] = {"ruta": r, "metricas": m}
        return salida

    def calcular_flujo(
        self,
        zona_origen: str = "Recepción y Almacenamiento",
        zona_destino: str = "Empaque y Despacho",
    ) -> dict[str, Any]:
        res = ek.entre_zonas(self.cap_base, self.nodos, zona_origen, zona_destino)
        return {
            "zona_origen": zona_origen,
            "zona_destino": zona_destino,
            "flujo_maximo": res["flujo_maximo"],
            "unidades": "unidades de flujo",
            "caminos_aumento": res["caminos_aumento"],
            "corte_minimo": res["corte_minimo"],
        }

    def ejecutar_experimentos(self, por_escenario: int = 10, semilla: int = 42) -> dict[str, Any]:
        rng = grafo.mulberry32(semilla)
        racks = self.racks_picking or [nid for nid, d in self.nodos.items() if not d["es_estacion"]]
        escenarios = [("valle", 1), ("valle", 5), ("valle", 10), ("punta", 1), ("punta", 5), ("punta", 10)]
        filas: list[dict[str, Any]] = []

        for idx, (hora, n_prod) in enumerate(escenarios):
            ady, dirigidas, por_par = self.estructuras[hora]
            pas_bfs = pas_bf = dist_bfs = dist_bf = t_bfs = t_bf = vis_bfs = rel_bf = ms_bfs = ms_bf = 0.0
            mejor_muestra = None

            for _ in range(por_escenario):
                inicio = self.muelles[int(rng() * len(self.muelles))]
                destinos: list[str] = []
                vistos = {inicio}
                while len(destinos) < n_prod:
                    cand = racks[int(rng() * len(racks))]
                    if cand not in vistos:
                        vistos.add(cand)
                        destinos.append(cand)

                t0 = time.perf_counter()
                rb = pedido.ruta_pedido(self.ids, ady, dirigidas, inicio, destinos, "bfs", regresar=True)
                ms_bfs += (time.perf_counter() - t0) * 1000
                mb = pedido.medir_ruta(rb["camino"], por_par, hora)

                t1 = time.perf_counter()
                rf = pedido.ruta_pedido(self.ids, ady, dirigidas, inicio, destinos, "bellman_ford", regresar=True)
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

                diff = mb["tiempo_s"] - mf["tiempo_s"]
                if mejor_muestra is None or diff > mejor_muestra["diff"]:
                    mejor_muestra = {
                        "start": inicio,
                        "picks": list(destinos),
                        "bfsPath": rb["camino"],
                        "bfPath": rf["camino"],
                        "bfOrder": rf["orden"],
                        "mb": {"tiempoS": mb["tiempo_s"], "pasillos": mb["pasillos"], "distAjustada": mb["dist_ajustada_m"]},
                        "mf": {"tiempoS": mf["tiempo_s"], "pasillos": mf["pasillos"], "distAjustada": mf["dist_ajustada_m"]},
                        "diff": round(diff, 2),
                    }

            n = float(por_escenario)
            avg_t_bfs = t_bfs / n
            avg_t_bf = t_bf / n
            filas.append(
                {
                    "idx": idx,
                    "hora": hora,
                    "prod": n_prod,
                    "pasBfs": round(pas_bfs / n, 2),
                    "pasBf": round(pas_bf / n, 2),
                    "distAdjBfs": round(dist_bfs / n, 2),
                    "distAdjBf": round(dist_bf / n, 2),
                    "tBfs": round(avg_t_bfs, 2),
                    "tBf": round(avg_t_bf, 2),
                    "ahorro": round(((avg_t_bfs - avg_t_bf) / avg_t_bfs) * 100, 2) if avg_t_bfs > 0 else 0.0,
                    "visBfs": round(vis_bfs / n),
                    "relBf": round(rel_bf / n),
                    "msBfs": round(ms_bfs / n, 3),
                    "msBf": round(ms_bf / n, 2),
                    "sample": mejor_muestra,
                }
            )

        return {"rows": filas, "perScenario": por_escenario, "seed": semilla, "motor": "Python"}


class KivaFlowHandler(http.server.SimpleHTTPRequestHandler):
    """Sirve la interfaz web de KivaFlow y expone endpoints JSON en /api/* con validación HTTP 400."""

    def __init__(self, *args: Any, api: KivaFlowAPI, **kwargs: Any) -> None:
        self.api = api
        super().__init__(*args, directory=str(RAIZ), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        if self.path.startswith("/api/"):
            super().log_message(format, *args)

    def _enviar_json(self, datos: Any, codigo: int = 200) -> None:
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _error_400(self, mensaje: str) -> None:
        self._enviar_json({"error": mensaje}, codigo=400)

    def _leer_entero(self, params: dict[str, list[str]], nombre: str, defecto: int, minimo: int, maximo: int) -> int | None:
        crudo = params.get(nombre, [str(defecto)])[0]
        try:
            valor = int(crudo)
        except ValueError:
            self._error_400(f"El parámetro '{nombre}' debe ser un número entero válido.")
            return None
        if not (minimo <= valor <= maximo):
            self._error_400(f"El parámetro '{nombre}' debe estar entre {minimo} y {maximo}.")
            return None
        return valor

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/api/paleta":
            self._enviar_json(
                {
                    "imperial": paleta.IMPERIAL,
                    "baltic": paleta.BALTIC,
                    "cream": paleta.CREAM,
                    "bus_yellow": paleta.BUS_YELLOW,
                    "royal_gold": paleta.ROYAL_GOLD,
                    "algoritmo": paleta.ALGORITMO,
                    "congestion": paleta.CONGESTION,
                }
            )
            return

        if parsed.path == "/api/estado":
            self._enviar_json(
                {
                    "motor": "Python (kivaflow)",
                    "nodos": len(self.api.nodos),
                    "aristas": len(self.api.aristas),
                    "skus_unicos": len(self.api.skus),
                }
            )
            return

        if parsed.path == "/api/comparar":
            inicio = params.get("inicio", ["F22_C39"])[0].strip()
            if inicio not in self.api.nodos:
                self._error_400(f"El nodo de inicio '{inicio}' no existe en el almacén.")
                return
            destinos = [d.strip() for d in params.get("destinos", ["F05_C05,F39_C10,F11_C29"])[0].split(",") if d.strip()]
            if not destinos or any(d not in self.api.nodos for d in destinos):
                self._error_400("Uno o más nodos de destino no existen en el almacén.")
                return
            bloqueados = [b.strip() for b in params.get("bloqueados", [""])[0].split(",") if b.strip()]
            if any(b not in self.api.nodos for b in bloqueados):
                self._error_400("Uno o más nodos bloqueados no existen en el almacén.")
                return
            perfil = params.get("perfil", ["punta"])[0].strip()
            if perfil not in ("punta", "valle"):
                self._error_400("El parámetro 'perfil' debe ser 'punta' o 'valle'.")
                return
            regresar = params.get("regresar", ["0"])[0] in ("1", "true", "True")
            self._enviar_json(self.api.calcular_comparacion(inicio, destinos, perfil, regresar, bloqueados))
            return

        if parsed.path == "/api/flujo":
            zo = params.get("origen", ["Recepción y Almacenamiento"])[0].strip()
            zd = params.get("destino", ["Empaque y Despacho"])[0].strip()
            if zo not in grafo.ZONAS or zd not in grafo.ZONAS or zo == zd:
                self._error_400("Las zonas 'origen' y 'destino' deben ser zonas válidas y distintas.")
                return
            self._enviar_json(self.api.calcular_flujo(zo, zd))
            return

        if parsed.path == "/api/turno":
            n_ops = self._leer_entero(params, "operarios", 12, 1, 60)
            max_prod = self._leer_entero(params, "max_prod", 3, 1, 10)
            semilla = self._leer_entero(params, "semilla", 1, 0, 999999)
            if n_ops is None or max_prod is None or semilla is None:
                return
            alg = params.get("alg", ["bfs"])[0].strip()
            if alg not in ("bfs", "bellman_ford", "edmonds_karp"):
                self._error_400("El parámetro 'alg' debe ser 'bfs', 'bellman_ford' o 'edmonds_karp'.")
                return
            perfil = params.get("perfil", params.get("hora", ["punta"]))[0].strip()
            if perfil not in ("punta", "valle"):
                self._error_400("El parámetro 'perfil' debe ser 'punta' o 'valle'.")
                return
            zo = params.get("origen", ["Recepción y Almacenamiento"])[0].strip()
            zd = params.get("destino", ["Empaque y Despacho"])[0].strip()
            if zo not in grafo.ZONAS or zd not in grafo.ZONAS or zo == zd:
                self._error_400("Las zonas 'origen' y 'destino' deben ser zonas válidas y distintas.")
                return
            self._enviar_json(
                simulacion.simular_turno(
                    self.api.nodos,
                    self.api.aristas,
                    n_operarios=n_ops,
                    max_productos=max_prod,
                    algoritmo=alg,
                    perfil=perfil,
                    zona_origen=zo,
                    zona_destino=zd,
                    semilla=semilla,
                )
            )
            return

        if parsed.path == "/api/experimentos":
            por_esc = self._leer_entero(params, "pedidos", 10, 1, 60)
            semilla = self._leer_entero(params, "semilla", 42, 0, 999999)
            if por_esc is None or semilla is None:
                return
            self._enviar_json(self.api.ejecutar_experimentos(por_esc, semilla))
            return

        if parsed.path == "/api/verificar":
            semilla = self._leer_entero(params, "semilla", 42, 0, 999999)
            if semilla is None:
                return
            self._enviar_json(verificacion.verificar_todo(self.api.nodos, self.api.aristas, semilla=semilla))
            return

        super().do_GET()


def resumen_consola(api: KivaFlowAPI) -> None:
    print("=" * 74)
    print(" KivaFlow · Sistema de Optimización de Picking en Almacenes (Python)")
    print(" Curso: 1ACC0184 Complejidad Algorítmica · UPC · Sección 4834")
    print("=" * 74)
    print(f" • Grafo cargado : {len(api.nodos)} nodos (45×40) y {len(api.aristas)} aristas")
    print(f" • Inventario    : {len(api.skus)} SKUs únicos en racks de almacenamiento")

    cmp_res = api.calcular_comparacion("F22_C39", ["F05_C05", "F39_C10", "F11_C29"], "punta", True)
    mb = cmp_res["bfs"]["metricas"]
    mf = cmp_res["bellman_ford"]["metricas"]
    ahorro = mb["tiempo_s"] - mf["tiempo_s"]
    print("\n [1] Pedido de prueba (F22_C39 -> F05_C05, F39_C10, F11_C29 + retorno):")
    print(f"     • BFS          O(V + E) : {mb['tiempo_s']:6.1f} s | {mb['pasillos']:3d} pasillos | {mb['dist_ajustada_m']:6.1f} m ajustados")
    print(f"     • Bellman-Ford O(V · E) : {mf['tiempo_s']:6.1f} s | {mf['pasillos']:3d} pasillos | {mf['dist_ajustada_m']:6.1f} m ajustados")
    print(f"     • Ahorro Bellman-Ford   : {ahorro:6.1f} s ({100 * ahorro / mb['tiempo_s']:.1f} % menos tiempo de caminata)")

    flujo = api.calcular_flujo("Recepción y Almacenamiento", "Empaque y Despacho")
    print("\n [2] Flujo Máximo Edmonds-Karp O(V · E²) (Recepción -> Despacho):")
    print(f"     • Flujo máximo          : {flujo['flujo_maximo']} unidades de flujo ({flujo['caminos_aumento']} caminos de aumento)")
    print(f"     • Corte mínimo (cuellos): {len(flujo['corte_minimo'])} pasillos saturados")

    v = verificacion.verificar_todo(api.nodos, api.aristas, n_bfs=30, n_bf=12)
    alg_v = v["algoritmos"]
    print("\n [3] Verificación por Certificado de Optimalidad:")
    print(
        f"     • Integridad: conexo={v['integridad']['conexo']}, "
        f"0 aislados={v['integridad']['sin_aislados']}, "
        f"ciclos negativos={v['integridad']['ciclos_negativos']}"
    )
    print(
        f"     • BFS: {alg_v['bfs']['aciertos']}/{alg_v['bfs']['consultas']} | "
        f"Bellman-Ford: {alg_v['bellman_ford']['aciertos']}/{alg_v['bellman_ford']['consultas']} | "
        f"Edmonds-Karp: {alg_v['edmonds_karp']['aciertos']}/{alg_v['edmonds_karp']['consultas']}"
    )
    print("=" * 74)


def main() -> None:
    parser = argparse.ArgumentParser(description="KivaFlow · Simulador en Python de rutas de picking")
    parser.add_argument("--cli", action="store_true", help="Ejecutar solo demostración y verificación en consola")
    parser.add_argument("--port", type=int, default=PUERTO_DEFAULT, help="Puerto local para la interfaz web")
    parser.add_argument("--no-browser", action="store_true", help="No abrir el navegador automáticamente")
    args = parser.parse_args()

    api = KivaFlowAPI()
    resumen_consola(api)

    if args.cli:
        return

    handler = functools.partial(KivaFlowHandler, api=api)
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler) as httpd:
        url = f"http://localhost:{args.port}"
        print(f"\n Interfaz gráfica KivaFlow activa en: {url}")
        print(" Endpoints Python activos: /api/estado, /api/comparar, /api/flujo, /api/turno, /api/experimentos, /api/verificar")
        print(" Presiona Ctrl+C para detener el servidor.\n")
        if not args.no_browser:
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor KivaFlow detenido.")


if __name__ == "__main__":
    main()
