/* =========================================================
   KivaFlow · Aplicación SPA (7 vistas interactivas)
   ========================================================= */
(function (global) {
  "use strict";

  const KF = (global.KF = global.KF || {});

  const STATE = {
    page: "inicio",
    inicio: "F22_C39",
    destinos: ["F05_C05", "F39_C10", "F11_C29"],
    perfil: "punta",
    regresar: false,
    clickModo: "Inicio",
    exploreAlg: "bfs",
    ekOrigen: "Recepción y Almacenamiento",
    ekDestino: "Empaque y Despacho",
    sim: {
      alg: "bfs",
      nOps: 24,
      maxProd: 3,
      hora: "punta",
      zOrigen: "Recepción y Almacenamiento",
      zDestino: "Empaque y Despacho",
      semilla: 1,
      result: null,
    },
    expCache: null,
    verifCache: null,
  };

  let activeCleanups = [];

  function registerCleanup(fn) {
    activeCleanups.push(fn);
  }

  function runCleanups() {
    for (const fn of activeCleanups) {
      try {
        fn();
      } catch (_) { }
    }
    activeCleanups = [];
  }

  function pageHeader(title, italic, sub) {
    return `
      <header class="page-header">
        <h1>${title} <em>${italic}</em></h1>
        <p class="page-sub">${sub}</p>
      </header>
    `;
  }

  function renderBars(title, entries, fmt, note = "menos es mejor") {
    const maxVal = Math.max(...entries.map((e) => e.val), 0.0001);
    const rows = entries
      .map(
        (e) => `
      <div class="bar-row">
        <span>${KF.NOMBRE[e.alg]}</span>
        <div class="bar-track">
          <div class="bar-fill" style="width:${(100 * e.val) / maxVal}%;background:${KF.PALETA.ALGORITMO[e.alg]}"></div>
        </div>
        <span class="bar-val">${fmt(e.val)}</span>
      </div>`
      )
      .join("");
    return `
      <div class="bar-block">
        <div class="bar-header">
          <b>${title}</b>
          <span class="card-note">${note}</span>
        </div>
        ${rows}
      </div>
    `;
  }

  function renderLegend(items) {
    return `<div class="canvas-legend">${items
      .map((it) =>
        it.dot
          ? `<span class="legend-item"><span class="legend-dot" style="background:${it.color};${it.border ? `border:2px solid ${it.border}` : ""}"></span>${it.label}</span>`
          : `<span class="legend-item"><span class="legend-swatch" style="background:${it.color}"></span>${it.label}</span>`
      )
      .join("")}</div>`;
  }

  function renderSkeletonBlock(kpiCount = 4, showTable = true) {
    const kpis = Array.from({ length: kpiCount }, (_, i) => `
      <div class="card kpi-${(i % 4) + 1} sk-kpi">
        <div class="sk sk-line w-45"></div>
        <div class="sk sk-num"></div>
        <div class="sk sk-line w-80"></div>
      </div>`).join("");
    const table = showTable
      ? `<div class="card sk-box">
           <div class="sk sk-line w-40"></div>
           <div class="sk sk-table-row"></div>
           <div class="sk sk-table-row"></div>
           <div class="sk sk-table-row"></div>
           <div class="sk sk-table-row"></div>
         </div>`
      : `<div class="grid-2">
           <div class="card sk-box" style="min-height:340px"><div class="sk sk-line w-45"></div><div class="sk sk-canvas"></div></div>
           <div class="card sk-box" style="min-height:340px"><div class="sk sk-line w-45"></div><div class="sk sk-canvas"></div></div>
         </div>`;
    return `<div class="stack" aria-busy="true"><div class="grid-${kpiCount}">${kpis}</div>${table}</div>`;
  }

  /* =======================================================
     Selector interactivo de puntos (reutilizado en Comparar y Explorar)
     ======================================================= */
  function mountPointSelector(container, data, onChange) {
    container.innerHTML = `
      <div class="stack">
        <div class="row-between">
          <div class="row">
            <div class="control-group">
              <span class="control-label">El clic en el mapa marca</span>
              <div class="segmented" data-seg="modo">
                <button type="button" data-val="Inicio" class="${STATE.clickModo === "Inicio" ? "active" : ""}">Inicio</button>
                <button type="button" data-val="Destino" class="${STATE.clickModo === "Destino" ? "active" : ""}">Destino</button>
              </div>
            </div>

            <div class="control-group">
              <span class="control-label">Perfil horario</span>
              <div class="segmented" data-seg="perfil">
                <button type="button" data-val="punta" class="${STATE.perfil === "punta" ? "active" : ""}">Hora punta</button>
                <button type="button" data-val="valle" class="${STATE.perfil === "valle" ? "active" : ""}">Hora valle</button>
              </div>
            </div>

            <div class="control-group">
              <span class="control-label">Retorno</span>
              <label class="toggle-wrap">
                <input type="checkbox" id="sel-regresar" ${STATE.regresar ? "checked" : ""} />
                Volver al inicio
              </label>
            </div>
          </div>

          <div class="row">
            <div class="control-group">
              <span class="control-label">Cant. destinos</span>
              <input type="number" id="sel-n" class="input" min="1" max="10" value="${Math.max(1, STATE.destinos.length)}" style="width:74px" />
            </div>
            <div class="control-group">
              <span class="control-label">&nbsp;</span>
              <button type="button" id="sel-azar" class="btn">Al azar</button>
            </div>
          </div>
        </div>

        <div class="canvas-card" style="padding:10px 12px">
          <div class="canvas-wrap"><canvas id="sel-canvas"></canvas></div>
        </div>

        <div class="row" style="font-size:13px">
          <span class="card-note">Inicio:</span>
          <span class="chip chip-dark">${STATE.inicio}</span>
          <span class="card-note" style="margin-left:6px">Destinos (${STATE.destinos.length}):</span>
          ${STATE.destinos.length
        ? STATE.destinos.map((d) => `<span class="chip">${d}</span>`).join("")
        : `<span class="card-note">— haz clic en el mapa para agregar</span>`
      }
        </div>
      </div>
    `;

    const canvasEl = container.querySelector("#sel-canvas");
    const map = new KF.WarehouseCanvas(canvasEl, data, {
      width: 820,
      height: 360,
      interactive: true,
      onNodeClick: (nodeId) => {
        if (STATE.clickModo === "Inicio") {
          STATE.inicio = nodeId;
        } else {
          const idx = STATE.destinos.indexOf(nodeId);
          if (idx >= 0) STATE.destinos.splice(idx, 1);
          else if (STATE.destinos.length < 10 && nodeId !== STATE.inicio) {
            STATE.destinos.push(nodeId);
          }
        }
        onChange();
      },
    });
    map.render({ start: STATE.inicio, destinations: STATE.destinos });
    registerCleanup(() => map.destroy());

    container.querySelectorAll('[data-seg="modo"] button').forEach((btn) => {
      btn.addEventListener("click", () => {
        STATE.clickModo = btn.dataset.val;
        container
          .querySelectorAll('[data-seg="modo"] button')
          .forEach((b) => b.classList.toggle("active", b === btn));
      });
    });

    container.querySelectorAll('[data-seg="perfil"] button').forEach((btn) => {
      btn.addEventListener("click", () => {
        STATE.perfil = btn.dataset.val;
        onChange();
      });
    });

    container.querySelector("#sel-regresar").addEventListener("change", (ev) => {
      STATE.regresar = ev.target.checked;
      onChange();
    });

    container.querySelector("#sel-azar").addEventListener("click", () => {
      const n = Math.max(1, Math.min(10, parseInt(container.querySelector("#sel-n").value, 10) || 3));
      const pool = data.ids;
      STATE.inicio = data.estaciones[Math.floor(Math.random() * data.estaciones.length)];
      const chosen = new Set([STATE.inicio]);
      const dests = [];
      while (dests.length < n) {
        const c = pool[Math.floor(Math.random() * pool.length)];
        if (!chosen.has(c)) {
          chosen.add(c);
          dests.push(c);
        }
      }
      STATE.destinos = dests;
      onChange();
    });
  }

  /* =======================================================
     1. INICIO
     ======================================================= */
  function renderInicio(main, data) {
    const startId = "F22_C39";
    const destId = "F08_C03";
    const { directed } = data.graphs.punta;

    // Ruta inicial con Bellman-Ford
    const initial = KF.bellmanFordPath(data.ids, directed, startId, destId);
    const fullInitPath = initial.path;
    const midIdx = Math.floor(fullInitPath.length * 0.48);
    const fromNode = fullInitPath[midIdx];
    const blockedNode = fullInitPath[midIdx + 2] || fullInitPath[midIdx + 1];

    // Bloquear todos los pasillos incidentes al nodo averiado
    const blockedKeys = new Set();
    for (const nb of data.graphs.punta.adj[blockedNode] || []) {
      blockedKeys.add(KF.edgeKey(blockedNode, nb.to));
    }
    const recalc = KF.bellmanFordPath(data.ids, directed, fromNode, destId, blockedKeys);

    // Armar cuadros de la historia
    const frames = [];
    for (let i = 0; i <= midIdx; i++) {
      frames.push({
        phase: "walk1",
        worker: fullInitPath[i],
        walked: fullInitPath.slice(0, i + 1),
        planned: fullInitPath,
        blocked: false,
        caption: `Paso ${i + 1}: el operario avanza por la ruta óptima inicial (${startId} → ${destId}).`,
      });
    }
    // Pausa dramática: robot averiado
    for (let p = 0; p < 5; p++) {
      frames.push({
        phase: "incident",
        worker: fromNode,
        walked: fullInitPath.slice(0, midIdx + 1),
        planned: fullInitPath,
        blocked: true,
        caption: `¡Incidencia! Un robot se avería en ${blockedNode}. Bellman-Ford recalcula desde ${fromNode} sin volver al inicio.`,
      });
    }
    for (let i = 1; i < recalc.path.length; i++) {
      frames.push({
        phase: "walk2",
        worker: recalc.path[i],
        walked: fullInitPath.slice(0, midIdx + 1).concat(recalc.path.slice(1, i + 1)),
        planned: recalc.path,
        oldPlan: fullInitPath.slice(midIdx),
        blocked: true,
        caption: `Desvío activo (${i}/${recalc.path.length - 1}): nueva ruta de menor tiempo evitando ${blockedNode}.`,
      });
    }

    main.innerHTML = `
      ${pageHeader(
      "Bienvenido a",
      "KivaFlow",
      "Un laboratorio de rutas de picking sobre un almacén inteligente tipo Amazon modelado como grafo."
    )}

      <div class="grid-hero" style="margin-bottom:18px">
        <div class="stack">
          <div class="card card-warm" style="padding:26px;flex:1;display:flex;flex-direction:column;justify-content:space-between">
            <div>
              <div class="card-label">Rutas · congestión · capacidad</div>
              <h2 style="font-size:2.15rem;line-height:1.15;margin:16px 0">
                Encuentra la ruta, <em>entiende la congestión.</em>
              </h2>
              <p class="card-note" style="font-size:14px;margin:0">
                Compara <strong>BFS</strong> y <strong>Bellman-Ford</strong> sobre tu dataset de 1 800 ubicaciones,
                observa cada paso con su pseudocódigo en vivo y descubre con <strong>Edmonds-Karp</strong> dónde se
                atasca el almacén.
              </p>
            </div>
            <div class="row" style="margin-top:22px">
              <a href="#comparar" class="btn btn-primary" data-nav="comparar">Comparar algoritmos</a>
              <a href="#explorar" class="btn" data-nav="explorar">Explorar paso a paso</a>
            </div>
          </div>
        </div>

        <div class="canvas-card">
          <div class="canvas-title">El operario que recalcula</div>
          <div class="canvas-subtitle" id="story-caption">
            Dale play: un robot se avería en <strong>${blockedNode}</strong> a mitad de camino y Bellman-Ford recalcula desde <strong>${fromNode}</strong>.
          </div>
          <div class="canvas-wrap"><canvas id="story-canvas"></canvas></div>
          ${renderLegend([
      { color: KF.PALETA.ALGORITMO.bellman_ford, label: "Ruta activa (Bellman-Ford)" },
      { color: KF.PALETA.ALGORITMO.edmonds_karp, label: "Tramo bloqueado / avería" },
      { color: KF.PALETA.CONGESTION.Alta, label: "Congestión alta" },
      { color: KF.PALETA.CONGESTION.Media, label: "Congestión media" },
    ])}
          <div id="story-controls"></div>
        </div>
      </div>

      <div class="grid-4" style="margin-bottom:18px">
        <div class="card kpi-1">
          <div class="card-label">Ubicaciones (V)</div>
          <div class="card-num">1 800</div>
          <div class="card-note">45 × 40 en tres zonas (585 / 630 / 585)</div>
        </div>
        <div class="card kpi-2">
          <div class="card-label">Pasillos (E)</div>
          <div class="card-num">3 515</div>
          <div class="card-note">1.5 m horizontales · 2.5 m verticales</div>
        </div>
        <div class="card kpi-3">
          <div class="card-label">Algoritmos</div>
          <div class="card-num">3</div>
          <div class="card-note">BFS · Bellman-Ford · Edmonds-Karp</div>
        </div>
        <div class="card kpi-4">
          <div class="card-label">Inventario</div>
          <div class="card-num">${KF.formatNum(data.racks.length)}<small>racks</small></div>
          <div class="card-note">${data.estaciones.length} estaciones · ${data.skuMap.size} SKUs únicos</div>
        </div>
      </div>

      <div class="grid-3">
        <div class="card">
          <span class="step-num">01</span>
          <strong>Elige los puntos</strong>
          <p class="card-note" style="margin:6px 0 0">Clic en el mapa o al azar: estación de inicio y hasta 10 racks destino en cualquier zona.</p>
        </div>
        <div class="card">
          <span class="step-num">02</span>
          <strong>Mira al algoritmo pensar</strong>
          <p class="card-note" style="margin:6px 0 0">El pseudocódigo se ilumina línea a línea mientras el almacén se explora o relaja en vivo.</p>
        </div>
        <div class="card">
          <span class="step-num">03</span>
          <strong>Compara y decide</strong>
          <p class="card-note" style="margin:6px 0 0">Tiempo de caminata contra trabajo de cálculo: el trade-off entre BFS y Bellman-Ford, con números.</p>
        </div>
      </div>
    `;

    const canvas = new KF.WarehouseCanvas(main.querySelector("#story-canvas"), data, {
      width: 720,
      height: 410,
    });
    const captionEl = main.querySelector("#story-caption");
    const ctrl = new KF.PlaybackController(
      main.querySelector("#story-controls"),
      frames.length,
      (idx) => {
        const f = frames[idx];
        captionEl.textContent = f.caption;
        canvas.render({
          start: startId,
          destinations: [destId],
          path: f.walked,
          pathColor: KF.PALETA.ALGORITMO.bellman_ford,
          secondaryPath: f.oldPlan || null,
          secondaryColor: KF.PALETA.ALGORITMO.edmonds_karp,
          blockedNode: f.blocked ? blockedNode : null,
          workers: [{ node: f.worker, color: KF.PALETA.TINTA, radius: 6.2 }],
        });
      },
      110
    );
    registerCleanup(() => {
      ctrl.destroy();
      canvas.destroy();
    });
  }

  /* =======================================================
     2. EXPLORAR PASO A PASO
     ======================================================= */
  function renderExplorar(main, data) {
    main.innerHTML = `
      ${pageHeader(
      "Explorar",
      "paso a paso",
      "Un algoritmo a la vez, con su pseudocódigo iluminado en vivo y narración de cada operación."
    )}

      <div class="stack">
        <div class="row-between">
          <div class="segmented" id="exp-alg-seg">
            <button type="button" data-alg="bfs" class="${STATE.exploreAlg === "bfs" ? "active" : ""}">BFS</button>
            <button type="button" data-alg="bellman_ford" class="${STATE.exploreAlg === "bellman_ford" ? "active" : ""}">Bellman-Ford</button>
            <button type="button" data-alg="edmonds_karp" class="${STATE.exploreAlg === "edmonds_karp" ? "active" : ""}">Edmonds-Karp</button>
          </div>
          <div class="row">
            <span class="chip">${KF.COMPLEJIDAD[STATE.exploreAlg].tiempo} tiempo</span>
            <span class="chip">${KF.COMPLEJIDAD[STATE.exploreAlg].espacio} espacio</span>
          </div>
        </div>

        <div id="exp-config"></div>

        <div class="grid-explore">
          <div class="canvas-card">
            <div class="canvas-title" id="exp-title"></div>
            <div class="canvas-wrap"><canvas id="exp-canvas"></canvas></div>
            <div id="exp-legend"></div>
            <div id="exp-controls"></div>
          </div>

          <div class="pseudo-panel">
            <div class="row-between">
              <strong style="font-size:14px">Pseudocódigo · ${KF.NOMBRE[STATE.exploreAlg]}</strong>
              <span class="chip chip-sans" id="exp-step-badge">Paso 1</span>
            </div>
            <div class="pseudo-narration" id="exp-narration"></div>
            <div class="pseudo-code" id="exp-code"></div>
            <div class="pseudo-stats" id="exp-stats"></div>
          </div>
        </div>
      </div>
    `;

    main.querySelectorAll("#exp-alg-seg button").forEach((btn) => {
      btn.addEventListener("click", () => {
        STATE.exploreAlg = btn.dataset.alg;
        navigate("explorar");
      });
    });

    const configEl = main.querySelector("#exp-config");
    const codeEl = main.querySelector("#exp-code");
    const narrEl = main.querySelector("#exp-narration");
    const statsEl = main.querySelector("#exp-stats");
    const badgeEl = main.querySelector("#exp-step-badge");
    const titleEl = main.querySelector("#exp-title");
    const legendEl = main.querySelector("#exp-legend");

    const lines = KF.PSEUDO[STATE.exploreAlg];
    codeEl.innerHTML = lines
      .map(
        (ln, i) =>
          `<div class="pseudo-line" data-ln="${i}"><span class="ln">${i + 1}</span><span>${ln}</span></div>`
      )
      .join("");

    function highlightLine(idx) {
      codeEl.querySelectorAll(".pseudo-line").forEach((el) => {
        el.classList.toggle("active", parseInt(el.dataset.ln, 10) === idx);
      });
    }

    if (STATE.exploreAlg === "edmonds_karp") {
      const destOpts = KF.ZONAS.filter((z) => z !== STATE.ekOrigen);
      if (!destOpts.includes(STATE.ekDestino)) STATE.ekDestino = destOpts[destOpts.length - 1];

      configEl.innerHTML = `
        <div class="card">
          <div class="row">
            <div class="control-group" style="flex:1;min-width:220px">
              <span class="control-label">Desde la zona (fuente s)</span>
              <select id="ek-origen" class="select">
                ${KF.ZONAS.map((z) => `<option value="${z}" ${z === STATE.ekOrigen ? "selected" : ""}>${z}</option>`).join("")}
              </select>
            </div>
            <div class="control-group" style="flex:1;min-width:220px">
              <span class="control-label">Hasta la zona (sumidero t)</span>
              <select id="ek-destino" class="select">
                ${destOpts.map((z) => `<option value="${z}" ${z === STATE.ekDestino ? "selected" : ""}>${z}</option>`).join("")}
              </select>
            </div>
          </div>
          <p class="card-note" style="margin:10px 0 0">
            Edmonds-Karp calcula cuántos operarios por minuto pueden circular simultáneamente de una zona a otra
            (capacidad por pasillo según congestión: Baja = 3, Media = 2, Alta = 1) y marca los pasillos saturados del corte mínimo.
          </p>
        </div>
      `;

      configEl.querySelector("#ek-origen").addEventListener("change", (ev) => {
        STATE.ekOrigen = ev.target.value;
        navigate("explorar");
      });
      configEl.querySelector("#ek-destino").addEventListener("change", (ev) => {
        STATE.ekDestino = ev.target.value;
        navigate("explorar");
      });

      const caps = data.buildCapacities(null);
      const ekSteps = [];
      const res = KF.edmondsKarpBetweenZones(caps, data.nodos, STATE.ekOrigen, STATE.ekDestino, ekSteps);

      // Construir cuadros acumulativos
      const flowFrames = [];
      const accEdges = new Map();
      let accFlow = 0;
      flowFrames.push({
        edges: new Map(),
        aug: [],
        cut: [],
        flow: 0,
        delta: 0,
        line: 0,
        narration: `Red residual inicializada desde ${STATE.ekOrigen} hasta ${STATE.ekDestino}.`,
      });
      for (let i = 0; i < ekSteps.length; i++) {
        const st = ekSteps[i];
        accFlow += st.delta;
        for (let j = 0; j < st.path.length - 1; j++) {
          const k = KF.edgeKey(st.path[j], st.path[j + 1]);
          accEdges.set(k, (accEdges.get(k) || 0) + st.delta);
        }
        flowFrames.push({
          edges: new Map(accEdges),
          aug: st.path,
          cut: [],
          flow: accFlow,
          delta: st.delta,
          line: 4,
          narration: `Camino de aumento #${i + 1}: BFS halló una ruta de ${st.path.length - 1} pasillos con cuello δ = ${st.delta} op/min. Flujo acumulado = ${accFlow}.`,
        });
      }
      flowFrames.push({
        edges: new Map(accEdges),
        aug: [],
        cut: res.minCut,
        flow: res.maxFlow,
        delta: 0,
        line: 7,
        narration: `Sin más caminos en la red residual. Flujo máximo = ${res.maxFlow} op/min; corte mínimo = ${res.minCut.length} pasillos cuello de botella.`,
      });

      titleEl.textContent = `Edmonds-Karp · ${STATE.ekOrigen} → ${STATE.ekDestino}`;
      legendEl.innerHTML = renderLegend([
        { color: KF.PALETA.FRENTE, label: "Camino de aumento actual" },
        { color: KF.PALETA.ALGORITMO.bellman_ford, label: "Flujo acumulado" },
        { color: KF.PALETA.ALGORITMO.edmonds_karp, label: "Corte mínimo (cuellos de botella)" },
      ]);

      const canvas = new KF.WarehouseCanvas(main.querySelector("#exp-canvas"), data, {
        width: 760,
        height: 460,
      });

      const ctrl = new KF.PlaybackController(
        main.querySelector("#exp-controls"),
        flowFrames.length,
        (idx) => {
          const f = flowFrames[idx];
          badgeEl.textContent = `Paso ${idx + 1} / ${flowFrames.length}`;
          narrEl.textContent = f.narration;
          highlightLine(f.line);
          statsEl.innerHTML = `
            <div class="pseudo-stat"><div class="card-label">Flujo acumulado</div><div class="val">${f.flow} op/min</div></div>
            <div class="pseudo-stat"><div class="card-label">Caminos hallados</div><div class="val">${Math.min(idx, ekSteps.length)}</div></div>
            <div class="pseudo-stat"><div class="card-label">Cuello δ actual</div><div class="val">${f.delta || "—"}</div></div>
            <div class="pseudo-stat"><div class="card-label">Aristas corte mín.</div><div class="val">${f.cut.length || "—"}</div></div>
          `;
          canvas.render({
            flowEdges: f.edges,
            augmentingPath: f.aug,
            minCut: f.cut,
          });
        },
        130
      );
      registerCleanup(() => {
        ctrl.destroy();
        canvas.destroy();
      });
      return;
    }

    // BFS o Bellman-Ford
    configEl.innerHTML = `
      <details class="kf-details">
        <summary>Puntos: inicio <strong>${STATE.inicio}</strong> · ${STATE.destinos.length} destinos · hora ${STATE.perfil}</summary>
        <div id="exp-selector-inner"></div>
      </details>
    `;
    mountPointSelector(configEl.querySelector("#exp-selector-inner"), data, () => navigate("explorar"));

    if (!STATE.inicio || STATE.destinos.length === 0) {
      titleEl.textContent = "Marca un inicio y al menos un destino para explorar.";
      return;
    }

    const r = KF.rutaPedido(
      data,
      STATE.perfil,
      STATE.inicio,
      STATE.destinos,
      STATE.exploreAlg,
      true,
      STATE.regresar
    );
    const frames = KF.buildSearchFrames(r.segments, STATE.exploreAlg, data, 180);
    const met = KF.medirRuta(r.path, data.edgeMap, STATE.perfil);

    titleEl.textContent = `${KF.NOMBRE[STATE.exploreAlg]} · ${met.tiempoS} s (${met.pasillos} pasillos · ${met.distFisica} m)`;
    legendEl.innerHTML = renderLegend([
      { color: KF.PALETA.ALGORITMO[STATE.exploreAlg], label: `Ruta ${KF.NOMBRE[STATE.exploreAlg]}` },
      { color: KF.PALETA.ALGORITMO_CLARO[STATE.exploreAlg], label: "Explorados / relajados" },
      { color: KF.PALETA.FRENTE, label: "Frente activo" },
      { dot: true, color: KF.PALETA.TINTA, label: "Inicio" },
      { dot: true, color: "#FFFFFF", border: KF.PALETA.TINTA, label: "Destinos" },
    ]);

    const canvas = new KF.WarehouseCanvas(main.querySelector("#exp-canvas"), data, {
      width: 760,
      height: 460,
    });

    const ctrl = new KF.PlaybackController(
      main.querySelector("#exp-controls"),
      frames.length,
      (idx) => {
        const f = frames[idx];
        badgeEl.textContent = `Cuadro ${idx + 1} / ${frames.length}`;
        narrEl.textContent = f.narration;
        highlightLine(f.line);
        const c = f.counters;
        statsEl.innerHTML =
          STATE.exploreAlg === "bfs"
            ? `
            <div class="pseudo-stat"><div class="card-label">Tramo</div><div class="val">${c.tramo}</div></div>
            <div class="pseudo-stat"><div class="card-label">Nodos visitados</div><div class="val">${KF.formatNum(c.visitados)}</div></div>
            <div class="pseudo-stat"><div class="card-label">Nivel (pasillos)</div><div class="val">${c.nivel}</div></div>
            <div class="pseudo-stat"><div class="card-label">Aristas revisadas</div><div class="val">${KF.formatNum(c.aristas)}</div></div>
          `
            : `
            <div class="pseudo-stat"><div class="card-label">Tramo</div><div class="val">${c.tramo}</div></div>
            <div class="pseudo-stat"><div class="card-label">Ronda actual</div><div class="val">${c.ronda}</div></div>
            <div class="pseudo-stat"><div class="card-label">Relajaciones</div><div class="val">${KF.formatNum(c.relajaciones)}</div></div>
            <div class="pseudo-stat"><div class="card-label">Aristas revisadas</div><div class="val">${KF.formatNum(c.aristas)}</div></div>
          `;
        canvas.render({
          start: STATE.inicio,
          destinations: STATE.destinos,
          visited: f.visited,
          visitedColor: KF.PALETA.ALGORITMO_CLARO[STATE.exploreAlg],
          frontier: f.frontier,
          path: f.path,
          pathColor: KF.PALETA.ALGORITMO[STATE.exploreAlg],
        });
      },
      115
    );
    registerCleanup(() => {
      ctrl.destroy();
      canvas.destroy();
    });
  }

  /* =======================================================
     3. COMPARAR BFS vs BELLMAN-FORD
     ======================================================= */
  function renderComparar(main, data) {
    main.innerHTML = `
      ${pageHeader(
      "Comparar",
      "dos caminos",
      "Los mismos puntos y la misma congestión: ruta, tiempo de caminata y trabajo de cálculo sincronizados."
    )}
      <div class="stack">
        <div class="card" id="cmp-selector"></div>
        <div id="cmp-results"></div>
      </div>
    `;

    mountPointSelector(main.querySelector("#cmp-selector"), data, () => navigate("comparar"));

    const resEl = main.querySelector("#cmp-results");
    if (!STATE.inicio || STATE.destinos.length === 0) {
      resEl.innerHTML = `<div class="card">Marca un inicio y al menos un destino en el mapa para comparar BFS y Bellman-Ford.</div>`;
      return;
    }

    const results = {};
    for (const alg of ["bfs", "bellman_ford"]) {
      const t0 = performance.now();
      const r = KF.rutaPedido(data, STATE.perfil, STATE.inicio, STATE.destinos, alg, true, STATE.regresar);
      const ms = performance.now() - t0;
      const m = KF.medirRuta(r.path, data.edgeMap, STATE.perfil);
      const frames = KF.buildSearchFrames(r.segments, alg, data, 120);
      results[alg] = { r, m, ms, frames, work: frames[frames.length - 1].work };
    }

    const b = results.bfs;
    const f = results.bellman_ford;
    const ahorro = b.m.tiempoS - f.m.tiempoS;
    const pct = b.m.tiempoS > 0 ? (100 * ahorro) / b.m.tiempoS : 0;
    const veces = f.work / Math.max(1, b.work);

    const conclusion =
      ahorro > 0.05
        ? `<strong>Bellman-Ford ahorra ${ahorro.toFixed(1)} s</strong> de caminata (${pct.toFixed(1)} %) esquivando pasillos congestionados (${f.m.alta} tramos de congestión alta frente a ${b.m.alta} de BFS), pero revisa <strong>${veces.toFixed(0)}× más aristas</strong> que BFS.`
        : `Ambas rutas cuestan prácticamente lo mismo en este trayecto (el camino mínimo en pasillos no atravesaba congestión crítica), pero Bellman-Ford revisó <strong>${veces.toFixed(0)}× más aristas</strong>.`;

    // Reloj común por trabajo (aristas revisadas)
    const maxWork = Math.max(b.work, f.work, 1);
    const totalSyncFrames = 85;
    function frameAtWork(frames, targetWork) {
      let chosen = frames[0];
      for (let i = 0; i < frames.length; i++) {
        if (frames[i].work <= targetWork) chosen = frames[i];
        else break;
      }
      return chosen;
    }

    resEl.innerHTML = `
      <div class="stack">
        <div class="grid-2">
          ${["bfs", "bellman_ford"]
        .map((alg) => {
          const d = results[alg];
          return `
              <div class="stack" style="gap:10px">
                <div class="row">
                  <h3 style="color:${KF.PALETA.ALGORITMO[alg]}">${KF.NOMBRE[alg]}</h3>
                  <span class="chip">${KF.COMPLEJIDAD[alg].tiempo}</span>
                  <span class="chip">espacio ${KF.COMPLEJIDAD[alg].espacio}</span>
                </div>
                <div class="mini-metrics">
                  <div class="mini-metric"><div class="card-label">Caminata</div><div class="card-num">${d.m.tiempoS} s</div></div>
                  <div class="mini-metric"><div class="card-label">Pasillos</div><div class="card-num">${d.m.pasillos}</div></div>
                  <div class="mini-metric"><div class="card-label">Distancia</div><div class="card-num">${d.m.distFisica} m</div></div>
                  <div class="mini-metric"><div class="card-label">Cálculo</div><div class="card-num">${d.ms.toFixed(1)} ms</div></div>
                </div>
              </div>`;
        })
        .join("")}
        </div>

        <div class="grid-compare">
          <div class="canvas-card">
            <div class="row-between" style="margin-bottom:8px">
              <div class="canvas-title">Sincronizados por trabajo (aristas revisadas)</div>
              <span class="chip" id="cmp-work-chip">0 aristas</span>
            </div>
            <div class="grid-2" style="gap:10px">
              <div>
                <div class="card-label" style="margin-bottom:4px;color:${KF.PALETA.ALGORITMO.bfs}">BFS · <span id="cmp-bfs-st">en curso</span></div>
                <div class="canvas-wrap"><canvas id="cmp-bfs-canvas"></canvas></div>
              </div>
              <div>
                <div class="card-label" style="margin-bottom:4px;color:${KF.PALETA.ALGORITMO.bellman_ford}">Bellman-Ford · <span id="cmp-bf-st">en curso</span></div>
                <div class="canvas-wrap"><canvas id="cmp-bf-canvas"></canvas></div>
              </div>
            </div>
            <div id="cmp-controls"></div>
            <p class="card-note" style="margin:8px 0 0">
              En cada cuadro ambos algoritmos llevan, como mucho, la misma cantidad de aristas revisadas. Por eso BFS termina casi de inmediato mientras Bellman-Ford continúa relajando pasillos.
            </p>
          </div>

          <div class="card stack" style="gap:6px">
            ${renderBars(
          "Tiempo de caminata (s)",
          [
            { alg: "bfs", val: b.m.tiempoS },
            { alg: "bellman_ford", val: f.m.tiempoS },
          ],
          (v) => `${v.toFixed(1)} s`
        )}
            ${renderBars(
          "Aristas revisadas",
          [
            { alg: "bfs", val: b.work },
            { alg: "bellman_ford", val: f.work },
          ],
          (v) => KF.formatNum(v)
        )}
            ${renderBars(
          "Tiempo de cálculo (ms)",
          [
            { alg: "bfs", val: b.ms },
            { alg: "bellman_ford", val: f.ms },
          ],
          (v) => `${v.toFixed(1)} ms`,
          "depende de la PC"
        )}
            <div class="conclusion-box">${conclusion}</div>
          </div>
        </div>
      </div>
    `;

    const cBfs = new KF.WarehouseCanvas(resEl.querySelector("#cmp-bfs-canvas"), data, {
      width: 440,
      height: 360,
    });
    const cBf = new KF.WarehouseCanvas(resEl.querySelector("#cmp-bf-canvas"), data, {
      width: 440,
      height: 360,
    });
    const workChip = resEl.querySelector("#cmp-work-chip");
    const bfsSt = resEl.querySelector("#cmp-bfs-st");
    const bfSt = resEl.querySelector("#cmp-bf-st");

    const ctrl = new KF.PlaybackController(
      resEl.querySelector("#cmp-controls"),
      totalSyncFrames,
      (idx) => {
        const wNow = Math.round((idx / (totalSyncFrames - 1)) * maxWork);
        workChip.textContent = `${KF.formatNum(wNow)} aristas`;
        const fb = frameAtWork(b.frames, wNow);
        const ff = frameAtWork(f.frames, wNow);
        bfsSt.textContent = wNow >= b.work ? "terminado ✓" : `${KF.formatNum(fb.work)} aristas`;
        bfSt.textContent = wNow >= f.work ? "terminado ✓" : `${KF.formatNum(ff.work)} aristas`;

        cBfs.render({
          start: STATE.inicio,
          destinations: STATE.destinos,
          visited: fb.visited,
          visitedColor: KF.PALETA.ALGORITMO_CLARO.bfs,
          frontier: fb.frontier,
          path: fb.path,
          pathColor: KF.PALETA.ALGORITMO.bfs,
        });
        cBf.render({
          start: STATE.inicio,
          destinations: STATE.destinos,
          visited: ff.visited,
          visitedColor: KF.PALETA.ALGORITMO_CLARO.bellman_ford,
          frontier: ff.frontier,
          path: ff.path,
          pathColor: KF.PALETA.ALGORITMO.bellman_ford,
        });
      },
      90
    );
    // Mostrar estado final al cargar para que las rutas se aprecien de inmediato
    ctrl.goTo(totalSyncFrames - 1);

    registerCleanup(() => {
      ctrl.destroy();
      cBfs.destroy();
      cBf.destroy();
    });
  }

  /* =======================================================
     4. SIMULACIÓN DE UN TURNO
     ======================================================= */
  function renderSimular(main, data) {
    const s = STATE.sim;
    const destOpts = KF.ZONAS.filter((z) => z !== s.zOrigen);
    if (!destOpts.includes(s.zDestino)) s.zDestino = destOpts[destOpts.length - 1];

    main.innerHTML = `
      ${pageHeader(
      "Simulación",
      "de un turno",
      "Varios operarios trabajan a la vez: los pasillos más cruzados se congestionan, baja su capacidad y Edmonds-Karp encuentra el nuevo corte mínimo."
    )}

      <div class="stack">
        <div class="card stack">
          <div class="grid-4">
            <div class="control-group">
              <span class="control-label">Los operarios usan</span>
              <div class="segmented" id="sim-alg">
                <button type="button" data-val="bfs" class="${s.alg === "bfs" ? "active" : ""}">BFS</button>
                <button type="button" data-val="bellman_ford" class="${s.alg === "bellman_ford" ? "active" : ""}">Bellman-Ford</button>
              </div>
            </div>

            <div class="control-group">
              <span class="control-label">Operarios: <strong id="sim-nops-val">${s.nOps}</strong></span>
              <input type="range" id="sim-nops" class="range-slider" min="5" max="${s.alg === "bellman_ford" ? 15 : 45}" value="${Math.min(s.nOps, s.alg === "bellman_ford" ? 15 : 45)}" />
            </div>

            <div class="control-group">
              <span class="control-label">Productos máx./pedido: <strong id="sim-maxp-val">${s.maxProd}</strong></span>
              <input type="range" id="sim-maxp" class="range-slider" min="1" max="5" value="${s.maxProd}" />
            </div>

            <div class="control-group">
              <span class="control-label">Hora</span>
              <div class="segmented" id="sim-hora">
                <button type="button" data-val="punta" class="${s.hora === "punta" ? "active" : ""}">Punta</button>
                <button type="button" data-val="valle" class="${s.hora === "valle" ? "active" : ""}">Valle</button>
              </div>
            </div>
          </div>

          <div class="row-between">
            <div class="row" style="flex:1">
              <div class="control-group" style="min-width:210px;flex:1">
                <span class="control-label">Flujo Edmonds-Karp desde</span>
                <select id="sim-zo" class="select">
                  ${KF.ZONAS.map((z) => `<option value="${z}" ${z === s.zOrigen ? "selected" : ""}>${z}</option>`).join("")}
                </select>
              </div>
              <div class="control-group" style="min-width:210px;flex:1">
                <span class="control-label">hasta</span>
                <select id="sim-zd" class="select">
                  ${destOpts.map((z) => `<option value="${z}" ${z === s.zDestino ? "selected" : ""}>${z}</option>`).join("")}
                </select>
              </div>
              <div class="control-group" style="width:96px">
                <span class="control-label">Semilla</span>
                <input type="number" id="sim-seed" class="input" min="0" max="9999" value="${s.semilla}" />
              </div>
            </div>
            <div class="control-group">
              <span class="control-label">&nbsp;</span>
              <button type="button" id="sim-run" class="btn btn-primary">Simular turno</button>
            </div>
          </div>
        </div>

        <div id="sim-output"></div>
      </div>
    `;

    main.querySelectorAll("#sim-alg button").forEach((b) => {
      b.addEventListener("click", () => {
        s.alg = b.dataset.val;
        if (s.alg === "bellman_ford" && s.nOps > 15) s.nOps = 10;
        navigate("simular");
      });
    });
    main.querySelectorAll("#sim-hora button").forEach((b) => {
      b.addEventListener("click", () => {
        s.hora = b.dataset.val;
        main.querySelectorAll("#sim-hora button").forEach((x) => x.classList.toggle("active", x === b));
      });
    });
    main.querySelector("#sim-nops").addEventListener("input", (ev) => {
      s.nOps = parseInt(ev.target.value, 10);
      main.querySelector("#sim-nops-val").textContent = s.nOps;
    });
    main.querySelector("#sim-maxp").addEventListener("input", (ev) => {
      s.maxProd = parseInt(ev.target.value, 10);
      main.querySelector("#sim-maxp-val").textContent = s.maxProd;
    });
    main.querySelector("#sim-zo").addEventListener("change", (ev) => {
      s.zOrigen = ev.target.value;
      navigate("simular");
    });
    main.querySelector("#sim-zd").addEventListener("change", (ev) => {
      s.zDestino = ev.target.value;
    });
    main.querySelector("#sim-seed").addEventListener("change", (ev) => {
      s.semilla = parseInt(ev.target.value, 10) || 1;
    });

    const outEl = main.querySelector("#sim-output");

    function runAndShow() {
      outEl.innerHTML = renderSkeletonBlock(4, false);
      setTimeout(() => {
        s.result = KF.simularTurno(data, {
          alg: s.alg,
          nOps: s.nOps,
          maxProd: s.maxProd,
          hora: s.hora,
          zonaOrigen: s.zOrigen,
          zonaDestino: s.zDestino,
          semilla: s.semilla,
        });
        renderSimResult(outEl, data, s);
      }, 60);
    }

    main.querySelector("#sim-run").addEventListener("click", runAndShow);

    if (s.result) {
      renderSimResult(outEl, data, s);
    } else {
      runAndShow();
    }
  }

  function renderSimResult(outEl, data, s) {
    const r = s.result;
    outEl.innerHTML = `
      <div class="stack">
        <div class="grid-4">
          <div class="card kpi-1">
            <div class="card-label">Operarios</div>
            <div class="card-num">${r.operators.length}</div>
            <div class="card-note">un pedido cada uno (${KF.NOMBRE[s.alg]})</div>
          </div>
          <div class="card kpi-2">
            <div class="card-label">Pasillos usados</div>
            <div class="card-num">${KF.formatNum(r.usage.size)}</div>
            <div class="card-note">de ${KF.formatNum(data.aristas.length)} pasillos totales</div>
          </div>
          <div class="card kpi-3">
            <div class="card-label">Pasillo más cruzado</div>
            <div class="card-num">${r.maxUsage}</div>
            <div class="card-note">cruces acumulados en el turno</div>
          </div>
          <div class="card kpi-4">
            <div class="card-label">Flujo máximo</div>
            <div class="card-num">${r.flowRes.maxFlow}<small>op/min</small></div>
            <div class="card-note">con congestión base del dataset: ${r.baseFlow} op/min</div>
          </div>
        </div>

        <div class="grid-2">
          <div class="canvas-card">
            <div class="canvas-title">Movimiento de operarios y mapa de calor</div>
            <div class="canvas-subtitle">Los pasillos cambian de color conforme acumulan cruces durante el turno.</div>
            <div class="canvas-wrap"><canvas id="sim-turn-canvas"></canvas></div>
            ${renderLegend([
      { dot: true, color: KF.PALETA.TINTA, label: "Operario activo" },
      { color: KF.PALETA.ALGORITMO.bfs, label: "Tráfico bajo" },
      { color: KF.PALETA.FRENTE, label: "Tráfico medio" },
      { color: KF.PALETA.ALGORITMO.edmonds_karp, label: "Tráfico alto" },
    ])}
            <div id="sim-turn-ctrl"></div>
          </div>

          <div class="canvas-card">
            <div class="canvas-title">Edmonds-Karp · <em>${s.zOrigen} → ${s.zDestino}</em></div>
            <div class="canvas-subtitle">
              Corte mínimo con la congestión generada por el turno: <strong>${r.flowRes.minCut.length} pasillos</strong> saturados (${r.flowRes.maxFlow} op/min).
            </div>
            <div class="canvas-wrap"><canvas id="sim-flow-canvas"></canvas></div>
            ${renderLegend([
      { color: KF.PALETA.ALGORITMO.edmonds_karp, label: "Corte mínimo (cuellos de botella)" },
      { color: KF.PALETA.CONGESTION.Alta, label: "Congestión alta del turno" },
      { color: KF.PALETA.CONGESTION.Media, label: "Congestión media" },
    ])}
          </div>
        </div>
      </div>
    `;

    const cTurn = new KF.WarehouseCanvas(outEl.querySelector("#sim-turn-canvas"), data, {
      width: 620,
      height: 410,
    });
    const cFlow = new KF.WarehouseCanvas(outEl.querySelector("#sim-flow-canvas"), data, {
      width: 620,
      height: 410,
      customLevels: r.dynamicLevels,
      strongCongestion: true,
    });
    cFlow.render({ minCut: r.flowRes.minCut });

    const totalSteps = Math.max(1, r.maxStep);
    const ctrl = new KF.PlaybackController(
      outEl.querySelector("#sim-turn-ctrl"),
      totalSteps,
      (t) => {
        const partialUsage = new Map();
        const workers = [];
        for (const op of r.operators) {
          const lim = Math.min(t, op.path.length - 1);
          workers.push({ node: op.path[lim], color: KF.PALETA.TINTA, radius: 4.4 });
          for (let i = 0; i < lim; i++) {
            const k = KF.edgeKey(op.path[i], op.path[i + 1]);
            partialUsage.set(k, (partialUsage.get(k) || 0) + 1);
          }
        }
        cTurn.render({
          usageMap: partialUsage,
          maxUsage: Math.max(1, r.maxUsage),
          workers,
        });
      },
      75
    );
    ctrl.goTo(Math.floor(totalSteps * 0.55));

    registerCleanup(() => {
      ctrl.destroy();
      cTurn.destroy();
      cFlow.destroy();
    });
  }

  /* =======================================================
     5. RESULTADOS DE EXPERIMENTOS
     ======================================================= */
  function renderResultados(main, data) {
    main.innerHTML = `
      ${pageHeader(
      "Resultados",
      "del experimento",
      "Comparativa controlada de BFS contra Bellman-Ford en hora valle y hora punta, más el análisis de flujo máximo de Edmonds-Karp sobre tu dataset."
    )}
      <div class="stack">
        <div class="card row-between">
          <div>
            <strong>Experimento reproducible sobre el dataset (1 800 nodos · 3 515 aristas)</strong>
            <div class="card-note">Escenarios de 1, 5 y 10 productos por pedido (salida y retorno a estación de despacho).</div>
          </div>
          <div class="row">
            <button type="button" id="exp-run-btn" class="btn btn-primary">Ejecutar experimento (60 pedidos)</button>
          </div>
        </div>
        <div id="exp-progress-wrap" hidden>
          <div class="progress-bar"><div class="progress-fill" id="exp-progress-fill"></div></div>
        </div>
        <div id="exp-body"></div>
      </div>
    `;

    const bodyEl = main.querySelector("#exp-body");
    const progWrap = main.querySelector("#exp-progress-wrap");
    const progFill = main.querySelector("#exp-progress-fill");
    const runBtn = main.querySelector("#exp-run-btn");

    async function runExperiments(perScenario = 10) {
      runBtn.disabled = true;
      progWrap.hidden = false;
      progFill.style.width = "5%";
      bodyEl.innerHTML = renderSkeletonBlock(3, true);

      const scenarios = [
        { hora: "valle", prod: 1 },
        { hora: "valle", prod: 5 },
        { hora: "valle", prod: 10 },
        { hora: "punta", prod: 1 },
        { hora: "punta", prod: 5 },
        { hora: "punta", prod: 10 },
      ];

      const rng = KF.mulberry32(42);
      const muelles = data.estacionesDespacho;
      const rows = [];

      for (let sIdx = 0; sIdx < scenarios.length; sIdx++) {
        const sc = scenarios[sIdx];
        let sumPasBfs = 0,
          sumPasBf = 0,
          sumTBfs = 0,
          sumTBf = 0,
          sumVisBfs = 0,
          sumRelBf = 0,
          sumMsBfs = 0,
          sumMsBf = 0;

        for (let k = 0; k < perScenario; k++) {
          const start = muelles[Math.floor(rng() * muelles.length)];
          const picks = [];
          const seen = new Set([start]);
          while (picks.length < sc.prod) {
            const cand = data.racks[Math.floor(rng() * data.racks.length)];
            if (!seen.has(cand)) {
              seen.add(cand);
              picks.push(cand);
            }
          }

          const t0 = performance.now();
          const rb = KF.rutaPedido(data, sc.hora, start, picks, "bfs", false, true);
          sumMsBfs += performance.now() - t0;
          const mb = KF.medirRuta(rb.path, data.edgeMap, sc.hora);
          sumPasBfs += mb.pasillos;
          sumTBfs += mb.tiempoS;
          sumVisBfs += rb.stats.visited;

          const t1 = performance.now();
          const rf = KF.rutaPedido(data, sc.hora, start, picks, "bellman_ford", false, true);
          sumMsBf += performance.now() - t1;
          const mf = KF.medirRuta(rf.path, data.edgeMap, sc.hora);
          sumPasBf += mf.pasillos;
          sumTBf += mf.tiempoS;
          sumRelBf += rf.stats.relaxations;
        }

        const avgTBfs = sumTBfs / perScenario;
        const avgTBf = sumTBf / perScenario;
        rows.push({
          hora: sc.hora,
          prod: sc.prod,
          pasBfs: sumPasBfs / perScenario,
          pasBf: sumPasBf / perScenario,
          tBfs: avgTBfs,
          tBf: avgTBf,
          ahorro: ((avgTBfs - avgTBf) / avgTBfs) * 100,
          visBfs: sumVisBfs / perScenario,
          relBf: sumRelBf / perScenario,
          msBfs: sumMsBfs / perScenario,
          msBf: sumMsBf / perScenario,
        });

        progFill.style.width = `${Math.round(((sIdx + 1) / (scenarios.length + 1)) * 100)}%`;
        await new Promise((res) => setTimeout(res, 15));
      }

      const tEk = performance.now();
      const ekRes = KF.edmondsKarpBetweenZones(
        data.buildCapacities(null),
        data.nodos,
        "Recepción y Almacenamiento",
        "Empaque y Despacho"
      );
      const ekMs = performance.now() - tEk;

      const cutFreq = { Alta: 0, Media: 0, Baja: 0 };
      for (const c of ekRes.minCut) {
        const e = data.edgeMap.get(KF.edgeKey(c.u, c.v));
        if (e) cutFreq[e.frec] = (cutFreq[e.frec] || 0) + 1;
      }

      STATE.expCache = { rows, ekRes, ekMs, cutFreq, perScenario };
      progFill.style.width = "100%";
      setTimeout(() => {
        progWrap.hidden = true;
        runBtn.disabled = false;
      }, 250);
      drawExpResults(bodyEl, data, STATE.expCache);
    }

    runBtn.addEventListener("click", () => runExperiments(10));

    if (STATE.expCache) {
      drawExpResults(bodyEl, data, STATE.expCache);
    } else {
      runExperiments(6);
    }
  }

  function drawExpResults(bodyEl, data, exp) {
    const avgPuntaSave =
      exp.rows
        .filter((r) => r.hora === "punta")
        .reduce((a, r) => a + r.ahorro, 0) / 3;

    bodyEl.innerHTML = `
      <div class="stack">
        <div class="grid-3">
          <div class="card kpi-1">
            <div class="card-label">Ahorro medio en hora punta</div>
            <div class="card-num">${avgPuntaSave.toFixed(1)}<small>%</small></div>
            <div class="card-note">menos tiempo de caminata con Bellman-Ford</div>
          </div>
          <div class="card kpi-3">
            <div class="card-label">Flujo máximo (Recepción → Despacho)</div>
            <div class="card-num">${exp.ekRes.maxFlow}<small>op/min</small></div>
            <div class="card-note">${exp.ekRes.augmentingPaths} caminos de aumento (${exp.ekMs.toFixed(1)} ms)</div>
          </div>
          <div class="card kpi-4">
            <div class="card-label">Corte mínimo (cuellos de botella)</div>
            <div class="card-num">${exp.ekRes.minCut.length}<small>pasillos</small></div>
            <div class="card-note">Alta: ${exp.cutFreq.Alta} · Media: ${exp.cutFreq.Media} · Baja: ${exp.cutFreq.Baja}</div>
          </div>
        </div>

        <h3 style="margin-top:6px">Rutas de picking: BFS vs. Bellman-Ford (promedios por pedido)</h3>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Hora</th>
                <th class="num">Productos</th>
                <th class="num">Pasillos BFS</th>
                <th class="num">Pasillos B-F</th>
                <th class="num">Tiempo BFS (s)</th>
                <th class="num">Tiempo B-F (s)</th>
                <th class="num">Ahorro B-F</th>
                <th class="num">Visitados BFS</th>
                <th class="num">Relajaciones B-F</th>
                <th class="num">ms BFS</th>
                <th class="num">ms B-F</th>
              </tr>
            </thead>
            <tbody>
              ${exp.rows
        .map(
          (r) => `
                <tr>
                  <td>${r.hora}</td>
                  <td class="num">${r.prod}</td>
                  <td class="num">${r.pasBfs.toFixed(1)}</td>
                  <td class="num">${r.pasBf.toFixed(1)}</td>
                  <td class="num">${r.tBfs.toFixed(1)}</td>
                  <td class="num">${r.tBf.toFixed(1)}</td>
                  <td class="num"><span class="badge-ok">${r.ahorro.toFixed(1)} %</span></td>
                  <td class="num">${KF.formatNum(r.visBfs)}</td>
                  <td class="num">${KF.formatNum(r.relBf)}</td>
                  <td class="num">${r.msBfs.toFixed(2)}</td>
                  <td class="num">${r.msBf.toFixed(1)}</td>
                </tr>`
        )
        .join("")}
            </tbody>
          </table>
        </div>

        <div class="canvas-card">
          <div class="canvas-title">Visualización del corte mínimo · Recepción y Almacenamiento → Empaque y Despacho</div>
          <div class="canvas-subtitle">Los ${exp.ekRes.minCut.length} pasillos resaltados en ladrillo saturan la capacidad de ${exp.ekRes.maxFlow} operarios/min.</div>
          <div class="canvas-wrap"><canvas id="res-cut-canvas"></canvas></div>
        </div>
      </div>
    `;

    const cCut = new KF.WarehouseCanvas(bodyEl.querySelector("#res-cut-canvas"), data, {
      width: 820,
      height: 410,
      strongCongestion: true,
    });
    cCut.render({ minCut: exp.ekRes.minCut });
    registerCleanup(() => cCut.destroy());
  }

  /* =======================================================
     6. VERIFICACIÓN EN VIVO
     ======================================================= */
  function renderVerificar(main, data) {
    main.innerHTML = `
      ${pageHeader(
      "Resultados de",
      "la verificación",
      "Comprobación automática de integridad del grafo y corrección de BFS, Bellman-Ford y Edmonds-Karp frente a oráculos independientes y el teorema flujo máximo–corte mínimo."
    )}
      <div class="stack">
        <div class="card row-between">
          <div>
            <strong>Suite de pruebas en vivo (en tu navegador)</strong>
            <div class="card-note">Valida conectividad del grafo, 60 consultas BFS, 40 consultas Bellman-Ford contra Dijkstra y los 6 pares ordenados de zonas en Edmonds-Karp.</div>
          </div>
          <button type="button" id="verif-run" class="btn btn-primary">Ejecutar verificación ahora</button>
        </div>
        <div id="verif-prog" hidden><div class="progress-bar"><div class="progress-fill" id="verif-fill"></div></div></div>
        <div id="verif-body"></div>
      </div>
    `;

    const bodyEl = main.querySelector("#verif-body");
    const prog = main.querySelector("#verif-prog");
    const fill = main.querySelector("#verif-fill");
    const btn = main.querySelector("#verif-run");

    async function runVerification() {
      btn.disabled = true;
      prog.hidden = false;
      fill.style.width = "10%";
      bodyEl.innerHTML = renderSkeletonBlock(4, true);
      const t0 = performance.now();

      // 1. Integridad del grafo
      const bfsConn = KF.bfs(data.graphs.punta.adj, data.ids[0], "__NONE__");
      const conexo = bfsConn.visited === data.ids.length;
      const sinAislados = data.ids.every((id) => data.graphs.punta.adj[id].length > 0);
      const pesosPos = data.aristas.every((e) => e.dist > 0 && e.tiempoPunta > 0 && e.tiempoValle > 0);
      fill.style.width = "25%";
      await new Promise((r) => setTimeout(r, 15));

      // 2. BFS (60 consultas aleatorias)
      const rng = KF.mulberry32(Math.floor(Math.random() * 10000));
      let bfsOk = 0;
      const bfsN = 60;
      for (let i = 0; i < bfsN; i++) {
        const s = data.ids[Math.floor(rng() * data.ids.length)];
        const t = data.ids[Math.floor(rng() * data.ids.length)];
        const r = KF.bfs(data.graphs.punta.adj, s, t);
        const manhattan =
          Math.abs(data.nodos[s].fila - data.nodos[t].fila) +
          Math.abs(data.nodos[s].col - data.nodos[t].col);
        let legal = r.path.length - 1 === manhattan && r.path[0] === s && r.path[r.path.length - 1] === t;
        for (let j = 0; legal && j < r.path.length - 1; j++) {
          if (!data.edgeMap.has(KF.edgeKey(r.path[j], r.path[j + 1]))) legal = false;
        }
        if (legal) bfsOk++;
      }
      fill.style.width = "55%";
      await new Promise((r) => setTimeout(r, 15));

      // 3. Bellman-Ford vs Dijkstra (24 consultas: 12 punta + 12 valle)
      let bfOk = 0;
      let bfMaxErr = 0;
      const bfN = 24;
      for (let i = 0; i < bfN; i++) {
        const prof = i % 2 === 0 ? "punta" : "valle";
        const s = data.ids[Math.floor(rng() * data.ids.length)];
        const t = data.ids[Math.floor(rng() * data.ids.length)];
        const rbf = KF.bellmanFordPath(data.ids, data.graphs[prof].directed, s, t);
        const ref = KF.dijkstraOracle(data.graphs[prof].adj, s, t);
        const err = Math.abs(rbf.cost - ref);
        if (err > bfMaxErr) bfMaxErr = err;
        if (err < 1e-6) bfOk++;
      }
      fill.style.width = "85%";
      await new Promise((r) => setTimeout(r, 15));

      // 4. Edmonds-Karp en los 6 pares ordenados de zonas (Max-Flow === Min-Cut)
      const caps = data.buildCapacities(null);
      let ekOk = 0;
      const ekPairs = [];
      for (const z1 of KF.ZONAS) {
        for (const z2 of KF.ZONAS) {
          if (z1 === z2) continue;
          const r = KF.edmondsKarpBetweenZones(caps, data.nodos, z1, z2);
          const cutCap = r.minCut.reduce((a, c) => a + c.cap, 0);
          const ok = cutCap === r.maxFlow && r.maxFlow > 0;
          if (ok) ekOk++;
          ekPairs.push({ z1, z2, maxFlow: r.maxFlow, cutCap, cutEdges: r.minCut.length, ok });
        }
      }

      const elapsed = ((performance.now() - t0) / 1000).toFixed(2);
      STATE.verifCache = {
        conexo,
        sinAislados,
        pesosPos,
        bfsOk,
        bfsN,
        bfOk,
        bfN,
        bfMaxErr,
        ekOk,
        ekN: 6,
        ekPairs,
        elapsed,
      };
      fill.style.width = "100%";
      setTimeout(() => {
        prog.hidden = true;
        btn.disabled = false;
      }, 200);
      drawVerification(bodyEl, STATE.verifCache);
    }

    btn.addEventListener("click", runVerification);
    if (STATE.verifCache) drawVerification(bodyEl, STATE.verifCache);
    else runVerification();
  }

  function drawVerification(bodyEl, v) {
    bodyEl.innerHTML = `
      <div class="stack">
        <div class="grid-4">
          <div class="card kpi-1">
            <div class="card-label">BFS</div>
            <div class="card-num">${v.bfsOk}<small>/ ${v.bfsN}</small></div>
            <div class="card-note">longitud exacta (= distancia Manhattan en cuadrícula) y ruta legal</div>
          </div>
          <div class="card kpi-2">
            <div class="card-label">Bellman-Ford</div>
            <div class="card-num">${v.bfOk}<small>/ ${v.bfN}</small></div>
            <div class="card-note">exactamente igual al oráculo Dijkstra (error máx. ${v.bfMaxErr.toExponential(1)})</div>
          </div>
          <div class="card kpi-3">
            <div class="card-label">Edmonds-Karp</div>
            <div class="card-num">${v.ekOk}<small>/ ${v.ekN}</small></div>
            <div class="card-note">teorema flujo máximo = capacidad del corte mínimo en los 6 pares de zonas</div>
          </div>
          <div class="card kpi-4">
            <div class="card-label">Integridad del grafo</div>
            <div class="card-num">${v.conexo && v.sinAislados && v.pesosPos ? "100 %" : "Error"}</div>
            <div class="card-note">conexo, 0 nodos aislados, pesos positivos · ${v.elapsed} s</div>
          </div>
        </div>

        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Par de zonas (Edmonds-Karp)</th>
                <th class="num">Flujo máximo</th>
                <th class="num">Capacidad corte mínimo</th>
                <th class="num">Pasillos en el corte</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              ${v.ekPairs
        .map(
          (p) => `
                <tr>
                  <td>${p.z1} → ${p.z2}</td>
                  <td class="num">${p.maxFlow} op/min</td>
                  <td class="num">${p.cutCap} op/min</td>
                  <td class="num">${p.cutEdges}</td>
                  <td><span class="${p.ok ? "badge-ok" : "badge-warn"}">${p.ok ? "Verificado ✓" : "Revisar"}</span></td>
                </tr>`
        )
        .join("")}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  /* =======================================================
     7. ACERCA (Información académica del Informe TB1)
     ======================================================= */
  function renderAcerca(main, data) {
    const algs = [
      {
        id: "bfs",
        tag: "No considera pesos",
        tec: "Recorridos y búsquedas en grafos",
        ref: "Cormen et al. (2022); Russell y Norvig (2021)",
        desc: "Línea base: calcula la ruta con el menor número de pasillos desde el operario hasta el producto.",
      },
      {
        id: "bellman_ford",
        tag: "Óptimo con pesos",
        tec: "Caminos mínimos (Bellman-Ford)",
        ref: "Bellman (1958); Cormen et al. (2022)",
        desc: "Calcula la ruta de menor tiempo considerando distancias físicas y penalizaciones por congestión.",
      },
      {
        id: "edmonds_karp",
        tag: "Óptimo en redes",
        tec: "Flujo máximo (Ford-Fulkerson / Edmonds-Karp)",
        ref: "Edmonds y Karp (1972); Ahuja et al. (1993)",
        desc: "Determina la capacidad máxima simultánea entre zonas e identifica los pasillos cuello de botella.",
      },
    ];

    main.innerHTML = `
      ${pageHeader(
      "Un laboratorio para",
      "ver pensar a los algoritmos",
      "Universidad Peruana de Ciencias Aplicadas (UPC) · Ciencias de la Computación · 1ACC0184 Complejidad Algorítmica · Sección 4834."
    )}

      <div class="stack">
        <div class="grid-3">
          ${algs
        .map(
          (a) => `
            <div class="card" style="border-top:4px solid ${KF.PALETA.ALGORITMO[a.id]}">
              <h3>${KF.NOMBRE[a.id]}</h3>
              <span class="chip chip-sans" style="margin-top:6px">${a.tag}</span>
              <p class="card-note" style="margin:10px 0 12px">${a.desc}</p>
              <div class="card-label">Técnica del curso</div>
              <div style="margin-bottom:8px">${a.tec}</div>
              <div class="card-label">Complejidad</div>
              <div style="font-family:var(--mono);font-size:13px;margin-bottom:8px">${KF.COMPLEJIDAD[a.id].tiempo} tiempo · ${KF.COMPLEJIDAD[a.id].espacio} espacio</div>
              <div class="card-label">Referencia</div>
              <div class="card-note">${a.ref}</div>
            </div>`
        )
        .join("")}
        </div>

        <div class="grid-2">
          <div class="card">
            <h3>Equipo y curso</h3>
            <p class="card-note" style="margin:6px 0 12px">Profesor: <strong>Johann Cristian Berny Perez Rojas</strong></p>
            <div class="table-wrap">
              <table class="data-table">
                <thead>
                  <tr><th>Código</th><th>Apellidos y Nombres</th></tr>
                </thead>
                <tbody>
                  <tr><td class="num" style="text-align:left">u202412270</td><td>Avila De La Cruz, Dario Fabian</td></tr>
                  <tr><td class="num" style="text-align:left">u20231h117</td><td>Cobades Zamora, Yhoshua Hebert</td></tr>
                  <tr><td class="num" style="text-align:left">u202411521</td><td>Morocho Pinedo, Mariana</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="card">
            <h3>Dataset y reglas del modelo</h3>
            <p style="margin:8px 0">
              Almacén sintético inspirado en los sistemas robóticos Kiva de Amazon (Wurman, D'Andrea y Mountz, 2008),
              modelado como una cuadrícula de <strong>45 filas × 40 columnas</strong> (<strong>1 800 nodos</strong> y
              <strong>3 515 aristas</strong>), dividida en tres zonas funcionales:
            </p>
            <ul style="margin:8px 0 12px;padding-left:20px;color:var(--muted)">
              <li><strong>Recepción y Almacenamiento</strong>: 585 nodos (columnas 0–12)</li>
              <li><strong>Picking</strong>: 630 nodos (columnas 13–26)</li>
              <li><strong>Empaque y Despacho</strong>: 585 nodos (columnas 27–39)</li>
            </ul>
            <p class="card-note" style="margin:0">
              Pasillos horizontales: <strong>1.5 m</strong> (<code>PHxx</code>); verticales: <strong>2.5 m</strong> (<code>PVxx</code>).
              Velocidad promedio: <strong>1.1 m/s</strong>. Penalizaciones de congestión en hora punta: Baja ×1.0, Media ×1.5, Alta ×2.0
              (${data.freqCounts.Baja} Baja · ${data.freqCounts.Media} Media · ${data.freqCounts.Alta} Alta).
              Capacidades para flujo máximo: 3, 2 y 1 operarios/min respectivamente.
            </p>
          </div>
        </div>

        <div class="card">
          <h3>Pregunta de investigación</h3>
          <p style="margin:8px 0 0;font-family:var(--serif);font-size:1.18rem;color:var(--ink)">
            «¿Cómo podemos modelar la infraestructura de un almacén inteligente tipo Amazon como un grafo que permita
            encontrar la ruta de picking más conveniente entre múltiples ubicaciones, considerando la distancia recorrida
            y las condiciones de congestión del entorno?»
          </p>
        </div>
      </div>
    `;
  }

  /* =======================================================
     Router y Bootstrap
     ======================================================= */
  const ROUTES = {
    inicio: renderInicio,
    explorar: renderExplorar,
    comparar: renderComparar,
    simular: renderSimular,
    resultados: renderResultados,
    verificar: renderVerificar,
    acerca: renderAcerca,
  };

  function navigate(page) {
    if (!ROUTES[page]) page = "inicio";
    STATE.page = page;
    if (location.hash !== `#${page}`) {
      history.replaceState(null, "", `#${page}`);
    }

    runCleanups();
    document.querySelectorAll(".nav-link").forEach((a) => {
      const isActive = a.dataset.nav === page;
      a.classList.toggle("active", isActive);
      if (isActive) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
    closeMobileMenu();

    const main = document.getElementById("app-main");
    main.classList.remove("view-enter");
    ROUTES[page](main, KF.DATA);
    void main.offsetWidth;
    main.classList.add("view-enter");
    main.scrollTop = 0;
    window.scrollTo(0, 0);
  }

  function closeMobileMenu() {
    const sb = document.getElementById("sidebar");
    const bd = document.getElementById("sidebar-backdrop");
    const btn = document.getElementById("mobile-menu-btn");
    if (sb) sb.classList.remove("open");
    if (bd) bd.hidden = true;
    if (btn) btn.setAttribute("aria-expanded", "false");
  }

  async function init() {
    const mobileBtn = document.getElementById("mobile-menu-btn");
    const collapseBtn = document.getElementById("sidebar-collapse-btn");
    const sb = document.getElementById("sidebar");
    const bd = document.getElementById("sidebar-backdrop");

    if (collapseBtn && sb) {
      const labelEl = collapseBtn.querySelector(".collapse-label");
      const applyCollapsed = (collapsed) => {
        sb.classList.toggle("collapsed", collapsed);
        collapseBtn.setAttribute("aria-expanded", String(!collapsed));
        collapseBtn.setAttribute("aria-label", collapsed ? "Expandir barra lateral" : "Retraer barra lateral");
        collapseBtn.title = collapsed ? "Expandir menú" : "Retraer menú";
        if (labelEl) labelEl.textContent = collapsed ? "Expandir menú" : "Retraer menú";
      };
      try {
        if (localStorage.getItem("kf_sidebar_collapsed") === "1") applyCollapsed(true);
      } catch (_) { }
      collapseBtn.addEventListener("click", () => {
        const next = !sb.classList.contains("collapsed");
        applyCollapsed(next);
        try {
          localStorage.setItem("kf_sidebar_collapsed", next ? "1" : "0");
        } catch (_) { }
      });
    }

    if (mobileBtn) {
      mobileBtn.addEventListener("click", () => {
        const open = !sb.classList.contains("open");
        sb.classList.toggle("open", open);
        bd.hidden = !open;
        mobileBtn.setAttribute("aria-expanded", String(open));
      });
    }
    if (bd) bd.addEventListener("click", closeMobileMenu);

    document.addEventListener("click", (ev) => {
      const link = ev.target.closest("[data-nav]");
      if (link) {
        ev.preventDefault();
        navigate(link.dataset.nav);
      }
    });

    window.addEventListener("hashchange", () => {
      const target = (location.hash || "#inicio").replace("#", "");
      if (ROUTES[target] && target !== STATE.page) navigate(target);
    });

    try {
      await KF.loadDataset();
      const initial = (location.hash || "#inicio").replace("#", "");
      navigate(ROUTES[initial] ? initial : "inicio");
    } catch (err) {
      document.getElementById("app-main").innerHTML = `
        <div class="card">
          <h2>Error al cargar el dataset</h2>
          <p class="card-note">${err.message}</p>
        </div>
      `;
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})(window);
