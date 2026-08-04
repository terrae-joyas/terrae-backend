# Identidad Visual Terrae — Design Tokens

> Fuente de verdad: `frontend/simulator/index.html` (bloque `<style>`,
> variables CSS `:root`). Este documento es un espejo legible de esos
> tokens para que cualquier desarrollador los use sin tener que leer el
> CSS completo del simulador.

## Marca

- **Nombre:** TERRAE
- **Tagline:** "Lo que la tierra esconde, Terrae lo revela"
- **Posicionamiento:** alta joyería colombiana certificada por ciencia y
  trazabilidad blockchain, en el segmento de lujo (referencia competitiva:
  Cartier, Hermès, Patek Philippe).
- **Monograma:** "RTR" enlazado con un diamante central que contiene una
  esmeralda tallada en escalón (emerald cut), enmarcado en un cuadrado —
  ver los 4 archivos en `frontend/simulator/assets/brand/`:
  - `terrae-logo-color-horizontal.jpg` — versión color, horizontal, fondo blanco (uso principal en fondos claros)
  - `terrae-logo-black-vertical.jpg` — versión negra, vertical, fondo blanco
  - `terrae-logo-gold-black-vertical.jpg` — versión dorada, vertical, fondo negro (uso principal en fondos oscuros / hero)
  - `terrae-monograma-gold-black.jpg` — monograma solo (sin wordmark), dorado sobre negro, para favicon/avatares/marcas de agua

## Paleta de color (tokens CSS reales del simulador)

| Token CSS | Valor HEX | Uso |
|---|---|---|
| `--verde-950` | `#3F3F2C` | Verde Terrae — color base oscuro (fondos, textos principales) |
| `--verde-800` | `#81754B` | Verde Terrae claro / variante secundaria |
| `--oro-500` | `#B4833D` | Oro Satinado — color de acento principal (líneas, bordes, CTA) |
| `--oro-300` | `#CBA35F` | Oro Satinado claro — hover, detalles secundarios |
| `--nogal-950` | `#3F3F2C` | Nogal (alias del verde base en la paleta actual) |
| `--nogal-900` | `#3F3F2C` | Nogal |
| `--nogal-800` | `#7A4A28` | Nogal cálido — acentos cálidos/madera |
| `--marfil-100` | `#E3D8C1` | Marfil — fondos cálidos claros |
| `--marfil-050` | `#F7F1E1` | Marfil claro — fondo base de secciones claras |
| `--esmeralda-500` | `#0F9D63` | Esmeralda — color gema, usado en acentos vivos y estados de éxito |
| `--esmeralda-300` | `#3DBE85` | Esmeralda claro — variante de acento |

## Tipografía

| Token CSS | Fuentes | Uso |
|---|---|---|
| `--font-display` | `'Mango', 'Cormorant Garamond', serif` | Titulares, wordmark, momentos editoriales/lujo |
| `--font-ui` | `'Jost', sans-serif` | Interfaz, navegación, cuerpos de texto UI |
| `--font-mono` | `'JetBrains Mono', monospace` | Datos técnicos: hashes, códigos de pieza, IDs blockchain |

Fuentes cargadas vía Google Fonts:
`Mango`, `Cormorant Garamond` (300/500/600, itálica 500), `Jost` (300/400/500),
`JetBrains Mono` (400/500).

## Estructura de vistas del simulador (mapa de navegación)

| Vista (`id`) | Nombre | Rol |
|---|---|---|
| `vista-publico` | Sitio Público | Landing premium + colecciones (`#colecciones`) |
| `vista-pasaporte` | Pasaporte Digital | Página de la joya + certificado oficial + tabs de blockchain |
| `vista-siegem` | SIEGEM Lab | Panel de IA — pipeline de certificación gemológica |
| `vista-backoffice` | Centro de Operaciones | Dashboard ejecutivo + backoffice operativo |

## Regla de uso para desarrollo

- Todo componente React/Next.js construido a partir de la Etapa 3 debe
  consumir estos tokens como variables de tema (ej. Tailwind config o
  CSS variables), **replicando exactamente** los valores de esta tabla.
- No se introducen nuevos colores, tipografías o logotipos sin que el
  equipo de diseño lo defina explícitamente fuera de este flujo de
  ingeniería.
- Los 4 archivos de logo son los activos oficiales; no se generan
  variantes adicionales por IA sin aprobación.
