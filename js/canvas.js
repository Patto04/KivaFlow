/* =========================================================
   KivaFlow · Motor gráfico Canvas HiDPI + Reproductor
   Renderizado en 2 capas (base cacheada + capa dinámica 60fps)
   ========================================================= */
(function (global) {
  "use strict";

  const KF = (global.KF = global.KF || {});

  class WarehouseCanvas {
    constructor(canvas, data, opts = {}) {
      this.canvas = canvas;
      this.ctx = canvas.getContext("2d");
      this.data = data;
      this.opts = Object.assign(
        {
          width: 760,
          height: 510,
          padTop: 28,
          padBottom: 16,
          padLeft: 18,
          padRight: 18,
          strongCongestion: false,
          customLevels: null,
          interactive: false,
          onNodeClick: null,
        },
        opts
      );

      this.dpr = Math.min(window.devicePixelRatio || 1, 2);
      this.canvas.width = Math.round(this.opts.width * this.dpr);
      this.canvas.height = Math.round(this.opts.height * this.dpr);
      this.canvas.style.aspectRatio = `${this.opts.width} / ${this.opts.height}`;

      this.innerW = this.opts.width - this.opts.padLeft - this.opts.padRight;
      this.innerH = this.opts.height - this.opts.padTop - this.opts.padBottom;
      this.cellW = this.innerW / (data.cols - 1);
      this.cellH = this.innerH / (data.rows - 1);

      this.pos = {};
      for (const n of data.nodeList) {
        this.pos[n.id] = {
          x: this.opts.padLeft + n.col * this.cellW,
          y: this.opts.padTop + n.fila * this.cellH,
        };
      }

      this._baseCanvas = document.createElement("canvas");
      this._baseCanvas.width = this.canvas.width;
      this._baseCanvas.height = this.canvas.height;
      this._buildBaseLayer();

      this._hoverNode = null;
      this._bindEvents();
    }

    _buildBaseLayer() {
      const ctx = this._baseCanvas.getContext("2d");
      ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
      ctx.fillStyle = KF.PALETA.TARJETA;
      ctx.fillRect(0, 0, this.opts.width, this.opts.height);

      // Bandas sutiles por zona + etiquetas arriba
      const bands = [
        { name: "Recepción y Almacenamiento", c0: 0, c1: 12, bg: "rgba(0,41,107,0.045)" },
        { name: "Picking", c0: 13, c1: 26, bg: "rgba(51,101,160,0.055)" },
        { name: "Empaque y Despacho", c0: 27, c1: 39, bg: "rgba(242,232,207,0.45)" },
      ];
      for (const b of bands) {
        const x0 = this.opts.padLeft + (b.c0 - 0.4) * this.cellW;
        const x1 = this.opts.padLeft + (b.c1 + 0.4) * this.cellW;
        ctx.fillStyle = b.bg;
        ctx.fillRect(x0, this.opts.padTop - 4, x1 - x0, this.innerH + 8);
        ctx.fillStyle = KF.PALETA.SUAVE;
        ctx.font = "500 11.5px 'EB Garamond', Garamond, Georgia, serif";
        ctx.textAlign = "center";
        ctx.fillText(b.name, (x0 + x1) / 2, 14);
      }

      // Pasillos (3 niveles de congestión)
      const palette = this.opts.strongCongestion
        ? KF.PALETA.CONGESTION
        : KF.PALETA.CONGESTION_SUAVE;
      const custom = this.opts.customLevels;

      for (const level of ["Baja", "Media", "Alta"]) {
        ctx.beginPath();
        ctx.strokeStyle = palette[level];
        ctx.lineWidth = level === "Alta" ? 1.85 : level === "Media" ? 1.3 : 1.0;
        for (const e of this.data.aristas) {
          const lvl = custom ? custom.get(e.key) || "Baja" : e.frec;
          if (lvl !== level) continue;
          const p1 = this.pos[e.u];
          const p2 = this.pos[e.v];
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
        }
        ctx.stroke();
      }

      // Nodos (estaciones cuadradas, racks circulares)
      for (const n of this.data.nodeList) {
        const p = this.pos[n.id];
        ctx.fillStyle = KF.PALETA.ZONA[n.zona] || KF.PALETA.SUAVE;
        ctx.globalAlpha = n.esEstacion ? 0.85 : 0.42;
        if (n.esEstacion) {
          ctx.fillRect(p.x - 2.3, p.y - 2.3, 4.6, 4.6);
        } else {
          ctx.beginPath();
          ctx.arc(p.x, p.y, 1.8, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      ctx.globalAlpha = 1;
    }

    updateCustomLevels(levels, strong = true) {
      this.opts.customLevels = levels;
      this.opts.strongCongestion = strong;
      this._buildBaseLayer();
    }

    _nearestNode(clientX, clientY) {
      const rect = this.canvas.getBoundingClientRect();
      const x = ((clientX - rect.left) / rect.width) * this.opts.width;
      const y = ((clientY - rect.top) / rect.height) * this.opts.height;
      const col = Math.round((x - this.opts.padLeft) / this.cellW);
      const row = Math.round((y - this.opts.padTop) / this.cellH);
      if (row < 0 || row >= this.data.rows || col < 0 || col >= this.data.cols) {
        return null;
      }
      const id = `F${String(row).padStart(2, "0")}_C${String(col).padStart(2, "0")}`;
      return this.data.nodos[id] || null;
    }

    _bindEvents() {
      const tooltip = document.getElementById("map-tooltip");

      this._onMove = (ev) => {
        const node = this._nearestNode(ev.clientX, ev.clientY);
        this._hoverNode = node;
        if (node && tooltip) {
          const skuLine = node.sku ? `<br>SKU: <strong>${node.sku}</strong>` : "";
          tooltip.innerHTML = `<strong>${node.id}</strong> · ${node.zona}<br>${node.tipo}${skuLine}`;
          tooltip.hidden = false;
          const left = Math.min(window.innerWidth - 270, ev.clientX + 14);
          const top = Math.min(window.innerHeight - 90, ev.clientY + 14);
          tooltip.style.left = `${left}px`;
          tooltip.style.top = `${top}px`;
        } else if (tooltip) {
          tooltip.hidden = true;
        }
      };

      this._onLeave = () => {
        this._hoverNode = null;
        if (tooltip) tooltip.hidden = true;
      };

      this._onClick = (ev) => {
        if (!this.opts.interactive || !this.opts.onNodeClick) return;
        const node = this._nearestNode(ev.clientX, ev.clientY);
        if (node) this.opts.onNodeClick(node.id);
      };

      this.canvas.addEventListener("mousemove", this._onMove);
      this.canvas.addEventListener("mouseleave", this._onLeave);
      this.canvas.addEventListener("click", this._onClick);
    }

    destroy() {
      this.canvas.removeEventListener("mousemove", this._onMove);
      this.canvas.removeEventListener("mouseleave", this._onLeave);
      this.canvas.removeEventListener("click", this._onClick);
      const tooltip = document.getElementById("map-tooltip");
      if (tooltip) tooltip.hidden = true;
    }

    render(overlay = {}) {
      const ctx = this.ctx;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.drawImage(this._baseCanvas, 0, 0);
      ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);

      // 1. Mapa de calor de uso (en simulación)
      if (overlay.usageMap && overlay.maxUsage > 0) {
        for (const [key, count] of overlay.usageMap.entries()) {
          if (count <= 0) continue;
          const e = this.data.edgeMap.get(key);
          if (!e) continue;
          const ratio = Math.min(1, count / overlay.maxUsage);
          const p1 = this.pos[e.u];
          const p2 = this.pos[e.v];
          ctx.beginPath();
          ctx.strokeStyle =
            ratio > 0.66
              ? "rgba(253, 197, 0, 0.95)"
              : ratio > 0.33
              ? "rgba(0, 41, 107, 0.78)"
              : "rgba(51, 101, 160, 0.45)";
          ctx.lineWidth = 1.4 + ratio * 2.6;
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      }

      // 2. Nodos visitados / relajados
      if (overlay.visited && overlay.visited.size > 0) {
        ctx.fillStyle = overlay.visitedColor || KF.PALETA.ALGORITMO_CLARO.bfs;
        for (const id of overlay.visited) {
          const p = this.pos[id];
          if (!p) continue;
          ctx.beginPath();
          ctx.arc(p.x, p.y, 3.1, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // 3. Frontera actual (ocre)
      if (overlay.frontier && overlay.frontier.size > 0) {
        ctx.fillStyle = KF.PALETA.FRENTE;
        for (const id of overlay.frontier) {
          const p = this.pos[id];
          if (!p) continue;
          ctx.beginPath();
          ctx.arc(p.x, p.y, 4.1, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // 4. Flujo acumulado / camino de aumento (Edmonds-Karp)
      if (overlay.flowEdges && overlay.flowEdges.size > 0) {
        ctx.lineCap = "round";
        for (const [key, amt] of overlay.flowEdges.entries()) {
          const e = this.data.edgeMap.get(key);
          if (!e) continue;
          const p1 = this.pos[e.u];
          const p2 = this.pos[e.v];
          ctx.beginPath();
          ctx.strokeStyle = "rgba(0, 41, 107, 0.55)";
          ctx.lineWidth = Math.min(4.2, 1.2 + amt * 0.9);
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      }

      if (overlay.augmentingPath && overlay.augmentingPath.length > 1) {
        this._drawPolyline(ctx, overlay.augmentingPath, KF.PALETA.FRENTE, 3.4, false);
      }

      // 5. Corte mínimo (cuellos de botella)
      if (overlay.minCut && overlay.minCut.length > 0) {
        ctx.lineCap = "round";
        for (const c of overlay.minCut) {
          const p1 = this.pos[c.u];
          const p2 = this.pos[c.v];
          if (!p1 || !p2) continue;
          ctx.beginPath();
          ctx.strokeStyle = KF.PALETA.ALGORITMO.edmonds_karp;
          ctx.lineWidth = 4.2;
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      }

      // 6. Rutas secundarias (ej. ruta original en historia)
      if (overlay.secondaryPath && overlay.secondaryPath.length > 1) {
        this._drawPolyline(
          ctx,
          overlay.secondaryPath,
          overlay.secondaryColor || "#A2412E",
          2.6,
          true
        );
      }

      // 7. Ruta principal
      if (overlay.path && overlay.path.length > 1) {
        this._drawPolyline(
          ctx,
          overlay.path,
          overlay.pathColor || KF.PALETA.ALGORITMO.bfs,
          3.4,
          false
        );
      }

      // 8. Operarios en movimiento (simulación o historia)
      if (overlay.workers && overlay.workers.length > 0) {
        for (const w of overlay.workers) {
          const p = this.pos[w.node];
          if (!p) continue;
          ctx.beginPath();
          ctx.fillStyle = w.color || KF.PALETA.TINTA;
          ctx.arc(p.x, p.y, w.radius || 4.8, 0, Math.PI * 2);
          ctx.fill();
          ctx.lineWidth = 1.6;
          ctx.strokeStyle = "#FFFFFF";
          ctx.stroke();
        }
      }

      // 9. Nodo averiado / bloqueado
      if (overlay.blockedNode && this.pos[overlay.blockedNode]) {
        const p = this.pos[overlay.blockedNode];
        ctx.beginPath();
        ctx.fillStyle = KF.PALETA.ALGORITMO.edmonds_karp;
        ctx.arc(p.x, p.y, 7.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#FFFFFF";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(p.x - 3.2, p.y - 3.2);
        ctx.lineTo(p.x + 3.2, p.y + 3.2);
        ctx.moveTo(p.x + 3.2, p.y - 3.2);
        ctx.lineTo(p.x - 3.2, p.y + 3.2);
        ctx.stroke();
      }

      // 10. Destinos
      if (overlay.destinations && overlay.destinations.length > 0) {
        for (let i = 0; i < overlay.destinations.length; i++) {
          const p = this.pos[overlay.destinations[i]];
          if (!p) continue;
          ctx.beginPath();
          ctx.fillStyle = "#FFFFFF";
          ctx.arc(p.x, p.y, 6.2, 0, Math.PI * 2);
          ctx.fill();
          ctx.lineWidth = 2.4;
          ctx.strokeStyle = KF.PALETA.TINTA;
          ctx.stroke();
        }
      }

      // 11. Inicio
      if (overlay.start && this.pos[overlay.start]) {
        const p = this.pos[overlay.start];
        ctx.beginPath();
        ctx.fillStyle = KF.PALETA.TINTA;
        ctx.arc(p.x, p.y, 6.8, 0, Math.PI * 2);
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = "#FFFFFF";
        ctx.stroke();
      }
    }

    _drawPolyline(ctx, nodes, color, width, dashed) {
      ctx.save();
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.lineJoin = "round";
      ctx.lineCap = "round";
      if (dashed) ctx.setLineDash([5, 5]);
      for (let i = 0; i < nodes.length; i++) {
        const p = this.pos[nodes[i]];
        if (!p) continue;
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      }
      ctx.stroke();
      ctx.restore();
    }
  }

  /* ---------- Controlador de reproducción reutilizable ---------- */
  class PlaybackController {
    constructor(container, totalFrames, onFrame, baseMs = 140) {
      this.container = container;
      this.total = Math.max(1, totalFrames);
      this.onFrame = onFrame;
      this.baseMs = baseMs;
      this.index = 0;
      this.speed = 1;
      this.playing = false;
      this.timer = null;

      this._renderUI();
      this.goTo(0);
    }

    _renderUI() {
      this.container.innerHTML = `
        <div class="playback-bar">
          <div class="playback-btns">
            <button type="button" class="pb-btn" data-act="reset" title="Reiniciar">⟲</button>
            <button type="button" class="pb-btn" data-speed="0.5">▶ 0.5×</button>
            <button type="button" class="pb-btn" data-speed="1">▶ 1×</button>
            <button type="button" class="pb-btn" data-speed="2">▶ 2×</button>
            <button type="button" class="pb-btn" data-speed="4">▶ 4×</button>
            <button type="button" class="pb-btn" data-act="pause" title="Pausar">❚❚</button>
          </div>
          <input type="range" class="playback-slider" min="0" max="${this.total - 1}" value="0" aria-label="Progreso de animación" />
          <span class="playback-counter">1 / ${this.total}</span>
        </div>
      `;
      this.slider = this.container.querySelector(".playback-slider");
      this.counter = this.container.querySelector(".playback-counter");
      this.speedBtns = Array.from(this.container.querySelectorAll("[data-speed]"));

      this.container.querySelector('[data-act="reset"]').addEventListener("click", () => {
        this.pause();
        this.goTo(0);
      });
      this.container.querySelector('[data-act="pause"]').addEventListener("click", () => {
        this.pause();
      });
      this.speedBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
          this.play(parseFloat(btn.dataset.speed));
        });
      });
      this.slider.addEventListener("input", () => {
        this.pause();
        this.goTo(parseInt(this.slider.value, 10));
      });
    }

    goTo(idx) {
      this.index = Math.max(0, Math.min(this.total - 1, idx));
      this.slider.value = String(this.index);
      this.counter.textContent = `${this.index + 1} / ${this.total}`;
      this.onFrame(this.index);
    }

    play(speed = 1) {
      this.pause();
      this.speed = speed;
      this.playing = true;
      if (this.index >= this.total - 1) this.index = 0;
      this.speedBtns.forEach((b) =>
        b.classList.toggle("active", parseFloat(b.dataset.speed) === speed)
      );
      const tick = () => {
        if (!this.playing) return;
        this.goTo(this.index);
        if (this.index >= this.total - 1) {
          this.pause();
          return;
        }
        this.index++;
        this.timer = setTimeout(tick, Math.max(16, this.baseMs / this.speed));
      };
      tick();
    }

    pause() {
      this.playing = false;
      if (this.timer) {
        clearTimeout(this.timer);
        this.timer = null;
      }
      this.speedBtns.forEach((b) => b.classList.remove("active"));
    }

    destroy() {
      this.pause();
    }
  }

  KF.WarehouseCanvas = WarehouseCanvas;
  KF.PlaybackController = PlaybackController;
})(window);
