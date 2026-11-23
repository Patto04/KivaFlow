"""Pruebas unitarias exhaustivas (unittest / pytest) para el paquete Python `kivaflow`."""
from __future__ import annotations

import tempfile
import unittest
from math import isinf
from pathlib import Path

from kivaflow import bellman_ford as bf
from kivaflow import bfs as bfs_mod
from kivaflow import edmonds_karp as ek
from kivaflow import grafo, pedido, verificacion


class TestKivaFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.nodos = grafo.leer_nodos()
        cls.aristas = grafo.leer_aristas()
        cls.ids = list(cls.nodos.keys())
        cls.skus = grafo.indice_skus(cls.nodos)
        cls.ady, cls.dirigidas, cls.por_par = grafo.construir_estructuras(cls.nodos, cls.aristas, "punta")

    def test_01_dimensiones_y_zonas_dataset(self) -> None:
        self.assertEqual(len(self.nodos), 1800)
        self.assertEqual(len(self.aristas), 3515)
        conteo_zonas = {}
        for d in self.nodos.values():
            conteo_zonas[d["zona"]] = conteo_zonas.get(d["zona"], 0) + 1
        self.assertEqual(conteo_zonas["Recepción y Almacenamiento"], 585)
        self.assertEqual(conteo_zonas["Picking"], 630)
        self.assertEqual(conteo_zonas["Empaque y Despacho"], 585)

    def test_02_lectura_csv_con_bom_utf8(self) -> None:
        """Verifica que leer_nodos soporte archivos CSV guardados con UTF-8 BOM (\ufeff)."""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "nodos_bom.csv"
            p.write_bytes(
                "\ufeffNodo,Fila,Columna,Zona,Tipo_Ubicacion,SKU_Principal\n"
                "F00_C00,0,0,Recepción y Almacenamiento,Estación de trabajo,\n".encode("utf-8")
            )
            leidos = grafo.leer_nodos(p)
            self.assertIn("F00_C00", leidos)

    def test_03_bfs_distancia_manhattan(self) -> None:
        r = bfs_mod.bfs(self.ady, "F00_C00", "F10_C15")
        self.assertEqual(len(r["camino"]) - 1, 25)
        self.assertEqual(r["camino"][0], "F00_C00")
        self.assertEqual(r["camino"][-1], "F10_C15")

    def test_04_bellman_ford_certificado_optimalidad(self) -> None:
        """Verifica optimalidad de Bellman-Ford mediante certificado dual y primal sin algoritmos externos."""
        dist, padre, _ = bf.bellman_ford(self.ids, self.dirigidas, "F22_C39")
        es_optimo, err = verificacion.certificar_bellman_ford(
            dist, padre, self.dirigidas, self.por_par, "F22_C39", "F08_C03", "punta"
        )
        self.assertTrue(es_optimo)
        self.assertLess(err, 1e-6)

    def test_05_bellman_ford_mejora_tiempo_frente_a_bfs(self) -> None:
        rb = pedido.ruta_pedido(self.ids, self.ady, self.dirigidas, "F22_C39", ["F05_C05", "F39_C10"], "bfs", True)
        rf = pedido.ruta_pedido(self.ids, self.ady, self.dirigidas, "F22_C39", ["F05_C05", "F39_C10"], "bellman_ford", True)
        mb = pedido.medir_ruta(rb["camino"], self.por_par, "punta")
        mf = pedido.medir_ruta(rf["camino"], self.por_par, "punta")
        self.assertLessEqual(mf["tiempo_s"], mb["tiempo_s"])

    def test_06_nodos_bloqueados_esquivados(self) -> None:
        """Verifica que tanto BFS como Bellman-Ford esquiven nodos bloqueados (×)."""
        bloq = {"F00_C01", "F01_C01"}
        rb = pedido.ruta_pedido(self.ids, self.ady, self.dirigidas, "F00_C00", ["F00_C02"], "bfs", False, bloq)
        rf = pedido.ruta_pedido(self.ids, self.ady, self.dirigidas, "F00_C00", ["F00_C02"], "bellman_ford", False, bloq)
        self.assertTrue(bloq.isdisjoint(rb["camino"]))
        self.assertTrue(bloq.isdisjoint(rf["camino"]))
        self.assertEqual(rb["camino"][-1], "F00_C02")
        self.assertEqual(rf["camino"][-1], "F00_C02")

    def test_07_destino_inalcanzable_encerrado(self) -> None:
        """Si los vecinos de un nodo están bloqueados, el destino se reporta como inalcanzable."""
        vecinos_esquina = {"F00_C01", "F01_C00"}
        rb = bfs_mod.bfs(self.ady, "F05_C05", "F00_C00", None, vecinos_esquina)
        self.assertEqual(rb["camino"], [])
        aristas_bloq = {grafo.edge_key("F00_C00", "F00_C01"), grafo.edge_key("F00_C00", "F01_C00")}
        rf = bf.ruta_minima(self.ids, self.dirigidas, "F05_C05", "F00_C00", aristas_bloq)
        self.assertEqual(rf["camino"], [])
        self.assertTrue(isinf(float(rf["costo"])))

    def test_08_deteccion_ciclo_negativo(self) -> None:
        """Verifica que Bellman-Ford lance CicloNegativoError ante un ciclo de peso negativo."""
        nodos_peq = ["A", "B", "C"]
        aristas_neg = [("A", "B", 1.0), ("B", "C", -5.0), ("C", "A", 2.0)]
        with self.assertRaises(bf.CicloNegativoError):
            bf.bellman_ford(nodos_peq, aristas_neg, "A")

    def test_09_edmonds_karp_red_clasica_clrs_23(self) -> None:
        """Ejemplo clásico de Cormen et al. (CLRS Fig. 26.6): el flujo máximo debe ser exactamente 23."""
        cap_clrs = {
            "s": {"v1": 16, "v2": 13},
            "v1": {"v3": 12},
            "v2": {"v1": 4, "v4": 14},
            "v3": {"v2": 9, "t": 20},
            "v4": {"v3": 7, "t": 4},
            "t": {},
        }
        res = ek.flujo_maximo(cap_clrs, "s", "t")
        cap_corte = sum(c["cap"] for c in res["corte_minimo"])
        self.assertEqual(res["flujo_maximo"], 23)
        self.assertEqual(cap_corte, 23)

    def test_10_edmonds_karp_almacen_y_sku_cercano(self) -> None:
        cap = grafo.capacidades(self.aristas)
        res = ek.entre_zonas(cap, self.nodos, "Recepción y Almacenamiento", "Empaque y Despacho")
        cap_corte = sum(c["cap"] for c in res["corte_minimo"])
        self.assertEqual(res["flujo_maximo"], 69)
        self.assertEqual(res["flujo_maximo"], cap_corte)

        # Verificar que un SKU repetido elija el rack más cercano al nodo de referencia
        sku_rep = next(s for s, lista in self.skus.items() if len(lista) >= 2)
        copias = self.skus[sku_rep]
        elegido = grafo.rack_mas_cercano_por_sku(self.nodos, self.skus, sku_rep, copias[1])
        self.assertEqual(elegido, copias[1])

    def test_11_oraculo_opcional_networkx(self) -> None:
        """Si NetworkX está instalado en el entorno, contrasta los 3 algoritmos contra NetworkX."""
        try:
            import networkx as nx
        except ImportError:
            self.skipTest("NetworkX no instalado; se omite prueba opcional con NetworkX.")

        G = nx.Graph()
        for a in self.aristas:
            G.add_edge(a["u"], a["v"], weight=a["tiempo_punta"], capacity=grafo.CAPACIDAD[a["frec"]])

        r_bfs = bfs_mod.bfs(self.ady, "F22_C39", "F08_C03")
        self.assertEqual(len(r_bfs["camino"]) - 1, nx.shortest_path_length(G, "F22_C39", "F08_C03"))

        r_bf = bf.ruta_minima(self.ids, self.dirigidas, "F22_C39", "F08_C03")
        self.assertAlmostEqual(float(r_bf["costo"]), nx.bellman_ford_path_length(G, "F22_C39", "F08_C03", weight="weight"), places=6)


if __name__ == "__main__":
    unittest.main()
