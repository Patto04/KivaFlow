"""Paleta de colores y tipografía de KivaFlow definida en Python.

Colores principales:
- Imperial Blue     (#00296B): barra lateral, tinta principal y Bellman-Ford
- Baltic Blue       (#3365A0): enlaces activos, acentos de título y BFS
- Vanilla Cream     (#F2E8CF): bloques cálidos de conclusión y telemetría
- School Bus Yellow (#FDC500): botones primarios, franja superior KPI y frente activo
- Royal Gold        (#FFE45C): estado hover de botones
- Carmesí Alerta    (#C1121F): tramo bloqueado / avería (×) y corte mínimo (Edmonds-Karp)
- Terracota         (#E05A2B): congestión alta
- Ámbar             (#EAB308): congestión media
"""
from __future__ import annotations

IMPERIAL = "#00296B"
BALTIC = "#3365A0"
CREAM = "#F2E8CF"
BUS_YELLOW = "#FDC500"
ROYAL_GOLD = "#FFE45C"

PAPEL = "#F3F4F6"
PAPEL_ALT = "#E8EDF3"
TARJETA = "#FFFFFF"
BORDE = "#DFE6EF"
BORDE_FUERTE = "#C5D1E0"
TINTA = IMPERIAL
SUAVE = "#516682"
REJILLA = "#E3E9F1"

ALGORITMO = {
    "bfs": BALTIC,
    "bellman_ford": IMPERIAL,
    "edmonds_karp": "#C1121F",
}

ALGORITMO_CLARO = {
    "bfs": "#CDE0F5",
    "bellman_ford": "#BCCFE8",
    "edmonds_karp": "#F7CFD2",
}

FRENTE = BUS_YELLOW
AVERIA = "#C1121F"

CONGESTION = {
    "Baja": "#DCE4EE",
    "Media": "#EAB308",
    "Alta": "#E05A2B",
}

CONGESTION_SUAVE = {
    "Baja": "#E3EAF2",
    "Media": "#E8C65A",
    "Alta": "#E67E53",
}

ZONA = {
    "Recepción y Almacenamiento": IMPERIAL,
    "Picking": BALTIC,
    "Empaque y Despacho": "#D49B00",
}

FONT_TITULOS = 'Arial, "Helvetica Neue", Calibri, sans-serif'
FONT_CUERPO = 'Calibri, "Segoe UI", Arial, sans-serif'
FONT_MONO = '"JetBrains Mono", Consolas, "Courier New", monospace'
