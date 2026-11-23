"""Generador de hojas de estilo CSS desde Python para KivaFlow.

Permite centralizar los colores, fuentes y reglas visuales en Python (`kivaflow/paleta.py` y `kivaflow/estilos.py`),
sirviendo el CSS dinámicamente desde `app.py` o exportándolo a `css/styles.css`.
"""
from __future__ import annotations

from pathlib import Path
from . import paleta

RAIZ = Path(__file__).resolve().parent.parent
CSS_PATH = RAIZ / "css" / "styles.css"


def Variables_Root() -> str:
    return f""":root {{
  --imperial: {paleta.IMPERIAL};
  --baltic: {paleta.BALTIC};
  --cream: {paleta.CREAM};
  --bus-yellow: {paleta.BUS_YELLOW};
  --royal-gold: {paleta.ROYAL_GOLD};

  --paper: {paleta.PAPEL};
  --paper-alt: {paleta.PAPEL_ALT};
  --card: {paleta.TARJETA};
  --border: {paleta.BORDE};
  --border-strong: {paleta.BORDE_FUERTE};
  --ink: {paleta.TINTA};
  --muted: {paleta.SUAVE};
  --grid: {paleta.REJILLA};

  --primary: {paleta.IMPERIAL};
  --primary-hover: #001d4d;
  --primary-light: {paleta.BALTIC};
  --primary-tint: {paleta.CREAM};

  --bfs: {paleta.ALGORITMO["bfs"]};
  --bfs-soft: {paleta.ALGORITMO_CLARO["bfs"]};
  --bf: {paleta.ALGORITMO["bellman_ford"]};
  --bf-soft: {paleta.ALGORITMO_CLARO["bellman_ford"]};
  --ek: {paleta.ALGORITMO["edmonds_karp"]};
  --ek-soft: {paleta.ALGORITMO_CLARO["edmonds_karp"]};
  --front: {paleta.FRENTE};

  --warm-bg: {paleta.CREAM};
  --warm-border: #e3d3ab;

  --z-rec: {paleta.ZONA["Recepción y Almacenamiento"]};
  --z-pick: {paleta.ZONA["Picking"]};
  --z-emp: {paleta.ZONA["Empaque y Despacho"]};

  --serif: {paleta.FONT_TITULOS};
  --sans: {paleta.FONT_CUERPO};
  --mono: {paleta.FONT_MONO};

  --radius: 16px;
  --radius-sm: 10px;
  --sidebar-w: 248px;
}}"""

REGLAS_BASE = r'''
*,
*::before,
*::after {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: var(--sans);
  font-size: 15.5px;
  font-weight: 500;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

h1,
h2,
h3,
.serif {
  font-family: var(--serif);
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
}

h1 {
  font-size: clamp(1.8rem, 2.8vw, 2.35rem);
  line-height: 1.15;
}

h2 {
  font-size: 1.5rem;
  line-height: 1.22;
}

h3 {
  font-size: 1.18rem;
  line-height: 1.28;
}

/* Reemplazo total de cursiva por pastilla de acento visual recta (sin inclinación) */
em,
.title-accent,
.brand-accent {
  font-style: normal !important;
}

.title-accent,
h1 em,
h2 em,
h3 em,
.canvas-title em {
  font-style: normal !important;
  font-weight: 700;
  color: var(--baltic);
  background: none;
  border: none;
  padding: 0;
}

.brand-accent,
.brand-title em {
  font-style: normal !important;
  font-weight: 800;
  color: var(--imperial);
  background: var(--bus-yellow);
  padding: 1px 7px;
  margin-left: 4px;
  border-radius: 6px;
  display: inline-block;
  font-size: 0.92em;
  line-height: 1.1;
}

.conclusion-box em,
.card-note em {
  font-style: normal;
  font-weight: 600;
  color: var(--imperial);
  background: rgba(253, 197, 0, 0.22);
  padding: 1px 6px;
  border-radius: 5px;
}

a {
  color: var(--bfs);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

button,
input,
select {
  font-family: inherit;
  font-size: inherit;
  color: inherit;
}

button:focus-visible,
a:focus-visible,
input:focus-visible,
select:focus-visible {
  outline: 2px solid var(--bfs);
  outline-offset: 2px;
}

.skip-link {
  position: fixed;
  top: -100px;
  left: 16px;
  z-index: 200;
  background: var(--bus-yellow);
  color: var(--imperial);
  font-weight: 600;
  padding: 10px 16px;
  border-radius: 10px;
  box-shadow: 0 4px 14px rgba(0, 41, 107, 0.25);
  transition: top 0.15s ease;
}

.skip-link:focus {
  top: 14px;
  text-decoration: none;
}

.chip-remove {
  border: none;
  background: transparent;
  color: inherit;
  font-weight: 700;
  cursor: pointer;
  padding: 0 2px;
  margin-left: 2px;
  opacity: 0.65;
  line-height: 1;
}

.chip-remove:hover {
  opacity: 1;
}

.pb-hint {
  font-size: 12px;
  color: var(--muted);
  margin-left: 4px;
}

/* ---------- Layout ---------- */
.app-shell {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 268px;
  flex-shrink: 0;
  background: var(--imperial);
  color: #ffffff;
  border-right: 1px solid #001d4d;
  padding: 24px 16px 16px;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  z-index: 30;
  transition: width 0.22s ease, padding 0.22s ease;
}

.sidebar-header {
  padding: 4px 6px 20px;
  margin-bottom: 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #ffffff;
  text-decoration: none;
}

.brand:hover {
  text-decoration: none;
}

.brand-logo {
  width: 40px;
  height: 40px;
  object-fit: contain;
  flex-shrink: 0;
  transition: width 0.22s ease, height 0.22s ease;
}

.brand-text {
  min-width: 0;
}

.brand-title {
  display: block;
  font-family: var(--serif);
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.05;
}

.brand-title em {
  font-style: normal;
  font-weight: 800;
  color: var(--bus-yellow);
  background: none;
  padding: 0;
}

.brand-sub {
  display: block;
  font-size: 13px;
  color: rgba(242, 232, 207, 0.78);
  margin-top: 3px;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 8px;
}

.nav-section-label {
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(242, 232, 207, 0.62);
  margin: 20px 0 6px 12px;
  font-weight: 600;
}

.nav-section-label:first-child {
  margin-top: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 13px;
  min-height: 44px;
  padding: 10px 14px;
  border-radius: 11px;
  color: rgba(255, 255, 255, 0.88);
  font-size: 16.5px;
  font-weight: 500;
  transition: background 0.15s ease, color 0.15s ease;
}

.nav-link svg {
  width: 21px;
  height: 21px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0.88;
  flex-shrink: 0;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.11);
  color: #ffffff;
  text-decoration: none;
}

.nav-link.active {
  background: var(--baltic);
  color: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.22);
  font-weight: 600;
}

.nav-link.active svg {
  opacity: 1;
}

.sidebar-footer {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-card {
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 12px;
  padding: 10px 12px;
  color: #ffffff;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.status-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--bus-yellow);
  flex-shrink: 0;
}

.status-meta {
  font-size: 13px;
  color: rgba(242, 232, 207, 0.78);
  margin-top: 2px;
}

.sidebar-collapse-btn {
  width: 100%;
  min-height: 44px;
  padding: 9px 14px;
  border-radius: 11px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: rgba(255, 255, 255, 0.06);
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.sidebar-collapse-btn:hover {
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(255, 255, 255, 0.3);
}

.sidebar-collapse-btn svg {
  width: 22px;
  height: 22px;
  fill: none;
  stroke: #ffffff;
  stroke-width: 1.9;
  stroke-linecap: round;
  stroke-linejoin: round;
  flex-shrink: 0;
}

.sidebar-collapse-btn .chevron {
  transform-box: fill-box;
  transform-origin: center;
  transition: transform 0.22s ease;
}

/* Estado retraído (desktop) */
.sidebar.collapsed {
  width: 84px;
  padding: 20px 12px 16px;
}

.sidebar.collapsed .sidebar-header {
  padding: 2px 0 18px;
}

.sidebar.collapsed .brand {
  justify-content: center;
}

.sidebar.collapsed .brand-logo {
  width: 48px;
  height: 48px;
}

.sidebar.collapsed .brand-text,
.sidebar.collapsed .nav-section-label,
.sidebar.collapsed .nav-link span,
.sidebar.collapsed .status-row strong,
.sidebar.collapsed .status-meta,
.sidebar.collapsed .collapse-label {
  display: none;
}

.sidebar.collapsed .nav-link {
  justify-content: center;
  padding: 11px;
}

.sidebar.collapsed .nav-link svg {
  width: 24px;
  height: 24px;
}

.sidebar.collapsed .status-card {
  padding: 10px 0;
  display: flex;
  justify-content: center;
}

.sidebar.collapsed .status-row {
  justify-content: center;
}

.sidebar.collapsed .sidebar-collapse-btn {
  justify-content: center;
  padding: 10px;
}

.sidebar.collapsed .sidebar-collapse-btn .chevron {
  transform: scaleX(-1);
}

.main-content {
  flex: 1;
  min-width: 0;
  padding: 32px clamp(20px, 3.5vw, 48px) 64px;
  max-width: 1360px;
  margin: 0 auto;
}

.view-enter {
  animation: kfFadeIn 0.2s ease-out both;
}

@keyframes kfFadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ---------- Skeleton Loaders (bloques en gris con shimmer) ---------- */
.sk {
  position: relative;
  overflow: hidden;
  background: #e2e6ec;
  border-radius: 8px;
}

.sk::after {
  content: "";
  position: absolute;
  inset: 0;
  transform: translateX(-100%);
  background: linear-gradient(90deg,
      rgba(255, 255, 255, 0) 0%,
      rgba(255, 255, 255, 0.55) 50%,
      rgba(255, 255, 255, 0) 100%);
  animation: kfShimmer 1.35s ease-in-out infinite;
}

@keyframes kfShimmer {
  100% {
    transform: translateX(100%);
  }
}

.sk-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 24px;
}

.sk-title {
  height: 34px;
  width: 280px;
  max-width: 70%;
  border-radius: 10px;
}

.sk-sub {
  height: 18px;
  width: 520px;
  max-width: 92%;
}

.sk-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sk-kpi {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 118px;
}

.sk-line {
  height: 14px;
}

.sk-heading {
  height: 28px;
}

.sk-num {
  height: 34px;
  width: 45%;
}

.sk-btn {
  height: 38px;
  width: 148px;
  border-radius: 10px;
}

.sk-canvas {
  flex: 1;
  min-height: 240px;
  border-radius: 10px;
}

.sk-table-row {
  height: 38px;
  width: 100%;
  border-radius: 8px;
}

.w-30 {
  width: 30%;
}

.w-40 {
  width: 40%;
}

.w-45 {
  width: 45%;
}

.w-60 {
  width: 60%;
}

.w-75 {
  width: 75%;
}

.w-80 {
  width: 80%;
}

.w-85 {
  width: 85%;
}

.w-90 {
  width: 90%;
}

.w-100 {
  width: 100%;
}

/* ---------- Page Header ---------- */
.page-header {
  margin-bottom: 24px;
}

.page-sub {
  color: var(--muted);
  margin-top: 8px;
  max-width: 74ch;
  font-size: 16px;
}

/* ---------- Cards & Grids ---------- */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 24px;
  box-shadow: 0 1px 2px rgba(0, 41, 107, 0.04), 0 4px 14px rgba(0, 41, 107, 0.025);
}

.card-warm {
  background: var(--warm-bg);
  border-color: var(--warm-border);
}

/* ---------- Hero Card rediseñada (Inicio) ---------- */
.hero-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-top: 4px solid var(--bus-yellow);
  border-radius: var(--radius);
  padding: 26px 28px;
  box-shadow: 0 2px 6px rgba(0, 41, 107, 0.05), 0 10px 26px rgba(0, 41, 107, 0.04);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 18px;
  height: 100%;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 11px;
  border-radius: 999px;
  background: rgba(0, 41, 107, 0.06);
  color: var(--imperial);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.hero-badge-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--bus-yellow);
  box-shadow: 0 0 0 2px rgba(253, 197, 0, 0.35);
}

.hero-title {
  font-size: clamp(1.85rem, 2.5vw, 2.3rem);
  line-height: 1.14;
  margin: 12px 0 10px;
  color: var(--imperial);
}

.hero-lead {
  font-size: 15.5px;
  color: var(--muted);
  margin: 0;
  line-height: 1.5;
}

.hero-alg-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 2px 0;
}

.hero-alg-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 12px;
  background: var(--paper);
  border: 1px solid var(--border);
  border-left: 4px solid var(--imperial);
  transition: transform 0.14s ease, background 0.14s ease;
}

.hero-alg-item:hover {
  background: #eef3f9;
  transform: translateX(2px);
}

.hero-alg-name {
  font-weight: 700;
  font-size: 15px;
  color: var(--imperial);
  min-width: 106px;
}

.hero-alg-desc {
  font-size: 14px;
  color: var(--muted);
  line-height: 1.35;
}

.hero-telemetry {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  padding: 11px 14px;
  border-radius: 12px;
  background: rgba(242, 232, 207, 0.42);
  border: 1px solid var(--warm-border);
}

.hero-tel-lbl {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  font-weight: 600;
}

.hero-tel-val {
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 600;
  color: var(--imperial);
  margin-top: 2px;
}

/* Tarjetas KPI unificadas: blanco con franja superior #FDC500 */
.kpi-1,
.kpi-2,
.kpi-3,
.kpi-4 {
  background: #ffffff;
  border-color: var(--border);
  border-top: 4px solid var(--bus-yellow);
  color: var(--imperial);
}

.kpi-1 .card-label,
.kpi-1 .card-note,
.kpi-1 .card-num small,
.kpi-2 .card-label,
.kpi-2 .card-note,
.kpi-2 .card-num small,
.kpi-3 .card-label,
.kpi-3 .card-note,
.kpi-3 .card-num small,
.kpi-4 .card-label,
.kpi-4 .card-note,
.kpi-4 .card-num small {
  color: var(--muted);
}

.card-label {
  font-size: 12px;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--muted);
  font-weight: 600;
}

.card-num {
  font-family: var(--serif);
  font-size: 2.05rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.12;
  margin: 6px 0 6px;
  font-variant-numeric: tabular-nums;
}

.card-num small {
  font-size: 1rem;
  font-weight: 600;
  color: var(--muted);
  margin-left: 5px;
}

.card-note {
  font-size: 14.5px;
  color: var(--muted);
  line-height: 1.45;
}

.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.grid-hero {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 3fr);
  gap: 24px;
  align-items: stretch;
}

.grid-explore {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(320px, 1fr);
  gap: 20px;
  align-items: start;
}

.grid-compare {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(320px, 1fr);
  gap: 20px;
  align-items: start;
}

.stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.row-between {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

/* ---------- Buttons & Controls ---------- */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 9px 18px;
  border-radius: 10px;
  border: 1.5px solid var(--bus-yellow);
  background: #fffdf2;
  color: var(--imperial);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.14s ease, border-color 0.14s ease, box-shadow 0.14s ease, transform 0.08s ease;
}

.btn:hover {
  background: var(--bus-yellow);
  border-color: #d9a700;
  text-decoration: none;
}

.btn:active {
  transform: translateY(1px);
}

.btn-primary {
  background: var(--bus-yellow);
  border-color: #d9a700;
  color: var(--imperial);
  box-shadow: 0 2px 6px rgba(253, 197, 0, 0.28);
}

.btn-primary:hover {
  background: var(--royal-gold);
  border-color: var(--bus-yellow);
  box-shadow: 0 4px 10px rgba(253, 197, 0, 0.35);
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12.5px;
  border-radius: 8px;
}

.btn[disabled] {
  opacity: 0.55;
  cursor: not-allowed;
}

.segmented {
  display: inline-flex;
  background: var(--paper-alt);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 3px;
  gap: 2px;
}

.segmented button {
  border: none;
  background: transparent;
  padding: 7px 14px;
  border-radius: 7px;
  font-size: 14.5px;
  font-weight: 500;
  color: var(--muted);
  cursor: pointer;
  transition: background 0.14s ease, color 0.14s ease;
}

.segmented button:hover {
  color: var(--ink);
}

.segmented button.active {
  background: var(--imperial);
  color: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 41, 107, 0.22);
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.control-label {
  font-size: 13px;
  color: var(--muted);
  font-weight: 600;
}

.select,
.input {
  background: var(--card);
  border: 1px solid var(--border-strong);
  border-radius: 9px;
  padding: 7px 12px;
  font-size: 15px;
  min-height: 38px;
}

.toggle-wrap {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13.5px;
  user-select: none;
  padding: 6px 0;
}

.toggle-wrap input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--ink);
  cursor: pointer;
}

.range-slider {
  accent-color: var(--ink);
  cursor: pointer;
}

/* ---------- Chips & Badges ---------- */
.chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 9px;
  border-radius: 999px;
  font-size: 12px;
  background: var(--grid);
  color: var(--ink);
  font-family: var(--mono);
}

.chip-dark {
  background: var(--ink);
  color: #ffffff;
}

.chip-sans {
  font-family: var(--sans);
}

.step-num {
  font-family: var(--serif);
  font-size: 2rem;
  line-height: 1;
  color: var(--border-strong);
  float: right;
}

/* ---------- Conclusion & Metric Bars ---------- */
.conclusion-box {
  background: var(--warm-bg);
  border: 1px solid var(--warm-border);
  border-radius: 12px;
  padding: 13px 16px;
  font-size: 14px;
  line-height: 1.5;
}

.bar-block {
  margin-bottom: 14px;
}

.bar-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 6px;
}

.bar-header b {
  font-size: 13.5px;
}

.bar-row {
  display: grid;
  grid-template-columns: 105px 1fr 80px;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  margin: 6px 0;
}

.bar-track {
  background: var(--grid);
  border-radius: 4px;
  height: 8px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.25s ease;
}

.bar-val {
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-family: var(--mono);
  font-size: 12.5px;
}

.mini-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.mini-metric {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 11px;
  padding: 10px 12px;
}

.mini-metric .card-num {
  font-size: 1.38rem;
  margin: 3px 0 0;
}

/* ---------- Canvas Stage & Playback ---------- */
.canvas-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px 20px;
  box-shadow: 0 1px 2px rgba(0, 41, 107, 0.04), 0 4px 14px rgba(0, 41, 107, 0.025);
}

.canvas-title {
  font-family: var(--serif);
  font-size: 1.25rem;
  margin-bottom: 4px;
}

.canvas-subtitle {
  font-size: 14.5px;
  color: var(--muted);
  margin-bottom: 12px;
}

.canvas-wrap {
  position: relative;
  width: 100%;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
}

.canvas-wrap canvas {
  display: block;
  width: 100%;
  height: auto;
  cursor: crosshair;
}

.canvas-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 10px;
  font-size: 12px;
  color: var(--muted);
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend-swatch {
  width: 12px;
  height: 4px;
  border-radius: 2px;
  display: inline-block;
}

.legend-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  display: inline-block;
}

.playback-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.playback-btns {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.pb-btn {
  border: 1px solid var(--border);
  background: var(--paper);
  color: var(--ink);
  border-radius: 8px;
  padding: 5px 9px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  min-width: 34px;
}

.pb-btn:hover {
  background: var(--paper-alt);
}

.pb-btn.active {
  background: var(--bus-yellow);
  border-color: #d9a700;
  color: var(--imperial);
  font-weight: 600;
}

.playback-slider {
  flex: 1;
  min-width: 140px;
  accent-color: var(--primary);
  cursor: pointer;
}

.playback-counter {
  font-family: var(--mono);
  font-size: 12px;
  color: var(--muted);
  min-width: 90px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

/* ---------- Pseudocode Panel ---------- */
.pseudo-panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 18px;
}

.pseudo-narration {
  background: var(--paper);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 11px 13px;
  font-size: 13.5px;
  margin: 10px 0 12px;
  min-height: 54px;
}

.pseudo-code {
  font-family: var(--mono);
  font-size: 12.2px;
  line-height: 1.65;
  margin: 0;
  padding: 8px 0;
  background: var(--paper);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow-x: auto;
}

.pseudo-line {
  display: flex;
  gap: 10px;
  padding: 2px 12px;
  border-left: 3px solid transparent;
  white-space: pre;
  color: var(--muted);
  transition: background 0.12s ease, color 0.12s ease;
}

.pseudo-line .ln {
  width: 18px;
  text-align: right;
  opacity: 0.55;
  user-select: none;
  flex-shrink: 0;
}

.pseudo-line.active {
  background: var(--warm-bg);
  border-left-color: var(--front);
  color: var(--ink);
  font-weight: 500;
}

.pseudo-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 12px;
}

.pseudo-stat {
  background: var(--paper);
  border: 1px solid var(--border);
  border-radius: 9px;
  padding: 8px 10px;
}

.pseudo-stat .val {
  font-family: var(--mono);
  font-size: 1rem;
  font-weight: 600;
  margin-top: 2px;
}

/* ---------- Tables ---------- */
.table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
}

table.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 15px;
}

table.data-table th,
table.data-table td {
  padding: 11px 14px;
  text-align: left;
  border-bottom: 1px solid var(--border);
  font-variant-numeric: tabular-nums;
}

table.data-table tbody tr:hover {
  background: rgba(242, 232, 207, 0.28);
}

table.data-table tbody tr.exp-row {
  cursor: pointer;
  transition: background 0.14s ease;
}

table.data-table tbody tr.exp-row.active {
  background: rgba(253, 197, 0, 0.18);
  font-weight: 600;
}

table.data-table tbody tr.exp-row.active td:first-child {
  border-left: 4px solid var(--bus-yellow);
}

table.data-table th {
  background: var(--paper-alt);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  font-weight: 600;
  white-space: nowrap;
}

table.data-table tr:last-child td {
  border-bottom: none;
}

table.data-table td.num,
table.data-table th.num {
  text-align: right;
  font-family: var(--mono);
  font-size: 12.8px;
}

.badge-ok {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--bf-soft);
  color: var(--bf);
  font-size: 12px;
  font-weight: 600;
}

.badge-warn {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--warm-bg);
  color: #8a5a12;
  font-size: 12px;
  font-weight: 600;
}

/* ---------- Expander ---------- */
details.kf-details {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 16px;
}

details.kf-details summary {
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  list-style: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

details.kf-details summary::after {
  content: "Cambiar ▾";
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  border-radius: 9px;
  border: 1px solid #d9a700;
  background: var(--bus-yellow);
  color: var(--imperial);
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(253, 197, 0, 0.25);
  transition: background 0.14s ease, box-shadow 0.14s ease;
}

details.kf-details summary:hover::after {
  background: var(--royal-gold);
  box-shadow: 0 3px 9px rgba(253, 197, 0, 0.35);
}

details.kf-details[open] summary::after {
  content: "Ocultar ▴";
  background: #fffdf2;
  border: 1.5px solid var(--bus-yellow);
  box-shadow: none;
}

details.kf-details[open] summary {
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}

/* ---------- Progress Bar ---------- */
.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--grid);
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary);
  width: 0%;
  transition: width 0.12s linear;
}

/* ---------- Tooltip ---------- */
.map-tooltip {
  position: fixed;
  z-index: 100;
  pointer-events: none;
  background: var(--card);
  border: 1px solid var(--border-strong);
  box-shadow: 0 6px 18px rgba(31, 35, 40, 0.12);
  border-radius: 9px;
  padding: 7px 10px;
  font-size: 12.5px;
  line-height: 1.4;
  color: var(--ink);
  max-width: 260px;
}

.map-tooltip strong {
  font-family: var(--mono);
  font-size: 12px;
}

/* ---------- Mobile ---------- */
.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 45;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: 1px solid var(--border-strong);
  background: var(--card);
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.mobile-menu-btn span {
  width: 18px;
  height: 2px;
  background: var(--ink);
  border-radius: 2px;
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(31, 35, 40, 0.35);
  z-index: 25;
}

@media (max-width: 1040px) {

  .grid-hero,
  .grid-explore,
  .grid-compare {
    grid-template-columns: 1fr;
  }

  .grid-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .grid-3 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 820px) {
  .mobile-menu-btn {
    display: flex;
  }

  .sidebar-collapse-btn {
    display: none;
  }

  .sidebar.collapsed {
    width: var(--sidebar-w);
    padding: 26px 16px 18px;
  }

  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.14);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .main-content {
    padding-top: 64px;
  }

  .grid-2,
  .mini-metrics {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {

  .sk::after,
  .view-enter {
    animation: none !important;
  }
}
'''

def generar_css() -> str:
    """Devuelve la hoja de estilos CSS completa armada desde Python."""
    return "/* KivaFlow · CSS generado desde Python (kivaflow.estilos + kivaflow.paleta) */\n" + Variables_Root() + "\n\n" + REGLAS_BASE.strip() + "\n"


def exportar_css(ruta: Path | None = None) -> Path:
    """Escribe el archivo css/styles.css a partir de las definiciones en Python."""
    destino = ruta or CSS_PATH
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(generar_css(), encoding="utf-8")
    return destino


if __name__ == "__main__":
    p = exportar_css()
    print(f"CSS generado desde Python en: {p}")