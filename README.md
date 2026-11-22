# KivaFlow · Laboratorio de Rutas de Picking

Aplicación web interactiva para la optimización de rutas de *picking* y detección de cuellos de botella en un almacén inteligente tipo Amazon modelado como un grafo ponderado de **1 800 nodos y 3 515 aristas**.

Proyecto del curso **1ACC0184 - Complejidad Algorítmica** (Sección 4834), Universidad Peruana de Ciencias Aplicadas (UPC).

## Cómo abrir la página

No requiere instalar Python, Node ni servidores:

1. **En local:** abre directamente `index.html` con doble clic en cualquier navegador moderno (Chrome, Edge, Firefox).
2. **En la web (GitHub Pages):** sube este repositorio a GitHub y activa *Settings → Pages → Deploy from a branch (`main` / root)*.

## Vistas incluidas

| Vista | Qué permite hacer |
|---|---|
| **Inicio** | Animación «El operario que recalcula» (avería en ruta + recálculo en vivo con Bellman-Ford) y métricas del almacén. |
| **Explorar** | Ejecución paso a paso de **BFS**, **Bellman-Ford** y **Edmonds-Karp** con pseudocódigo iluminado, narración y reproductor (0.5×–4×). |
| **Comparar** | Mapa clicable para elegir inicio y hasta 10 destinos, comparando BFS y Bellman-Ford sincronizados por aristas revisadas. |
| **Simulación** | Simulación de turno con múltiples operarios, mapa de calor de congestión dinámica y cálculo del corte mínimo con Edmonds-Karp. |
| **Resultados** | Experimento comparativo en hora valle y hora punta (1, 5 y 10 productos por pedido) más mapa de cuellos de botella. |
| **Verificación** | Suite de pruebas en vivo: integridad del grafo, BFS, Bellman-Ford contra Dijkstra y teorema flujo máximo–corte mínimo en los 6 pares de zonas. |
| **Acerca** | Contexto académico del informe TB1, integrantes, reglas del modelo y referencias. |

## Dataset (`data/`)

- `data/nodos.csv`: 1 800 ubicaciones (`45 × 40`), 3 zonas (`Recepción y Almacenamiento` 585, `Picking` 630, `Empaque y Despacho` 585), 100 estaciones de trabajo y 1 700 racks con 571 SKUs.
- `data/aristas.csv`: 3 515 pasillos (`1.5 m` horizontales `PHxx`, `2.5 m` verticales `PVxx`), frecuencia de pedidos (`Baja`, `Media`, `Alta`), distancia ajustada y tiempo estimado a `1.1 m/s`.
- `data/dataset.js`: empaquetado offline automático de ambos CSV para permitir abrir `index.html` directamente vía `file://`.

## Equipo

- **Avila De La Cruz, Dario Fabian** (`u202412270`)
- **Cobades Zamora, Yhoshua Hebert** (`u20231h117`)
- **Morocho Pinedo, Mariana** (`u202411521`)
- **Profesor:** Johann Cristian Berny Perez Rojas
