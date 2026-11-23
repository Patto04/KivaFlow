"""KivaFlow · Programa principal en Python (Servidor Web + API REST + Modo Consola CLI).

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
import socketserver
import threading
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Any

from kivaflow import edmonds_karp as ek
from kivaflow import estilos, grafo, paleta, pedido, simulacion, verificacion

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

    def calcular_comparacion(
        self,
        inicio: str = "F22_C39",
        destinos: list[str] | None = None,
        perfil: str = "punta",
        regresar: bool = False,
        bloqueados: list[str] | None = None,
    ) -> dict[str, Any]:
        dests = destinos or ["F05_C05", "F39_C10", "F11_C29"]
        bloq = set(bloqueados or [])
        ady, dirigidas, por_par = self.estructuras.get(perfil, self.estructuras["punta"])
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
            "caminos_aumento": res["caminos_aumento"],
            "corte_minimo": res["corte_minimo"],
        }


class KivaFlowHandler(http.server.SimpleHTTPRequestHandler):
    """Sirve la interfaz web de KivaFlow y expone endpoints JSON en /api/* calculados por Python."""

    def __init__(self, *args: Any, api: KivaFlowAPI, **kwargs: Any) -> None:
        self.api = api
        super().__init__(*args, directory=str(RAIZ), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        # Silenciar logs estáticos innecesarios para mantener limpia la consola
        if self.path.startswith("/api/"):
            super().log_message(format, *args)

    def _enviar_json(self, datos: Any, codigo: int = 200) -> None:
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/css/styles.css":
            cuerpo = estilos.generar_css().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
            return

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
            inicio = params.get("inicio", ["F22_C39"])[0]
            destinos = params.get("destinos", ["F05_C05,F39_C10,F11_C29"])[0].split(",")
            perfil = params.get("perfil", ["punta"])[0]
            regresar = params.get("regresar", ["0"])[0] in ("1", "true", "True")
            self._enviar_json(self.api.calcular_comparacion(inicio, destinos, perfil, regresar))
            return

        if parsed.path == "/api/flujo":
            zo = params.get("origen", ["Recepción y Almacenamiento"])[0]
            zd = params.get("destino", ["Empaque y Despacho"])[0]
            self._enviar_json(self.api.calcular_flujo(zo, zd))
            return

        if parsed.path == "/api/turno":
            n_ops = int(params.get("operarios", ["24"])[0])
            alg = params.get("alg", ["bfs"])[0]
            self._enviar_json(simulacion.simular_turno(self.api.nodos, self.api.aristas, n_operarios=n_ops, algoritmo=alg))
            return

        if parsed.path == "/api/verificar":
            self._enviar_json(verificacion.verificar_todo(self.api.nodos, self.api.aristas))
            return

        super().do_GET()


def resumen_consola(api: KivaFlowAPI) -> None:
    print("=" * 72)
    print(" KivaFlow · Sistema de Optimización de Picking en Almacenes (Python)")
    print(" Curso: 1ACC0184 Complejidad Algorítmica · UPC · Sección 4834")
    print("=" * 72)
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
    print(f"     • Flujo máximo          : {flujo['flujo_maximo']} operarios/min ({flujo['caminos_aumento']} caminos de aumento)")
    print(f"     • Corte mínimo (cuellos): {len(flujo['corte_minimo'])} pasillos saturados")

    v = verificacion.verificar_todo(api.nodos, api.aristas, n_bfs=30, n_bf=12)
    alg_v = v["algoritmos"]
    print("\n [3] Verificación matemática rápida:")
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
    print("=" * 72)


def main() -> None:
    parser = argparse.ArgumentParser(description="KivaFlow · Simulador en Python de rutas de picking")
    parser.add_argument("--cli", action="store_true", help="Ejecutar solo demostración y verificación en consola")
    parser.add_argument("--port", type=int, default=PUERTO_DEFAULT, help="Puerto local para la interfaz web")
    parser.add_argument("--no-browser", action="store_true", help="No abrir el navegador automáticamente")
    args = parser.parse_args()

    api = KivaFlowAPI()
    estilos.exportar_css()
    resumen_consola(api)

    if args.cli:
        return

    handler = functools.partial(KivaFlowHandler, api=api)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
        url = f"http://localhost:{args.port}"
        print(f"\n Interfaz gráfica KivaFlow activa en: {url}")
        print(" Endpoints Python activos: /api/estado, /api/comparar, /api/flujo, /api/turno, /api/verificar")
        print(" Presiona Ctrl+C para detener el servidor.\n")
        if not args.no_browser:
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor KivaFlow detenido.")


if __name__ == "__main__":
    main()
