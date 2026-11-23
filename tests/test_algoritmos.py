"""Pruebas unitarias con unittest / pytest para el paquete Python `kivaflow`."""
from __future__ import annotations

import unittest

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
        cls.ady, cls.dirigidas, cls.por_par = grafo.construir_estructuras(cls.nodos, cls.aristas, "punta")

    def test_dimensiones_dataset(self) -> None:
        self.assertEqual(len(self.nodos), 1800)
        self.assertEqual(len(self.aristas), 3515)

    def test_bfs_manhattan(self) -> None:
        r = bfs_mod.bfs(self.ady, "F00_C00", "F10_C15")
        self.assertEqual(len(r["camino"]) - 1, 25)

    def test_bellman_ford_vs_dijkstra(self) -> None:
        res_bf = bf.ruta_minima(self.ids, self.dirigidas, "F22_C39", "F08_C03")
        costo_ref = verificacion.dijkstra_oraculo(self.ady, "F22_C39", "F08_C03")
        self.assertAlmostEqual(float(res_bf["costo"]), costo_ref, places=6)

    def test_bellman_ford_mejora_tiempo_frente_a_bfs(self) -> None:
        rb = pedido.ruta_pedido(self.ids, self.ady, self.dirigidas, "F22_C39", ["F05_C05", "F39_C10"], "bfs", True)
        rf = pedido.ruta_pedido(self.ids, self.ady, self.dirigidas, "F22_C39", ["F05_C05", "F39_C10"], "bellman_ford", True)
        mb = pedido.medir_ruta(rb["camino"], self.por_par, "punta")
        mf = pedido.medir_ruta(rf["camino"], self.por_par, "punta")
        self.assertLessEqual(mf["tiempo_s"], mb["tiempo_s"])

    def test_edmonds_karp_teorema_corte_minimo(self) -> None:
        cap = grafo.capacidades(self.aristas)
        res = ek.entre_zonas(cap, self.nodos, "Recepción y Almacenamiento", "Empaque y Despacho")
        cap_corte = sum(c["cap"] for c in res["corte_minimo"])
        self.assertEqual(res["flujo_maximo"], cap_corte)
        self.assertGreater(res["flujo_maximo"], 0)


if __name__ == "__main__":
    unittest.main()
