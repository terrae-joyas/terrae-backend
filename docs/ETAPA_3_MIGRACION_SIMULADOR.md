# Etapa 3 — Migración del simulador a componentes reales

## Objetivo

Convertir el simulador monolítico (`frontend/simulator/index.html`, 2.868
líneas) en componentes reales de Next.js/React, organizados por dominio,
sin alterar el diseño ni la identidad visual, y sin romper el simulador
original (que permanece intacto como referencia).

## Alcance y decisiones

El simulador original contiene, en un solo archivo:

| Elemento | Tamaño |
|---|---|
| CSS (`<style>`) | 952 líneas |
| HTML de las 4 vistas + shell global + modales | ~1.340 líneas, 712 atributos `class`, 93 `style` inline |
| JS (`<script>`) | 530 líneas, 32 funciones, 114 atributos `onclick` inline |

Dado ese tamaño y densidad de interacciones, se tomó una decisión de
ingeniería explícita para esta etapa, con dos objetivos en tensión:

1. **Fidelidad absoluta** — cero riesgo de bugs de transcripción al
   convertir manualmente cientos de atributos y cientos de líneas de
   lógica interdependiente.
2. **Componentización real** — dejar de tener un único archivo HTML y
   pasar a una arquitectura de componentes Next.js mantenible, por vista.

### Estrategia adoptada: extracción verbatim + componentización estructural

- **CSS**: extraído carácter por carácter a `frontend/src/styles/simulador-terrae.css`
  y cargado como hoja de estilos real de Next.js. Cero cambios de diseño.
- **HTML de cada vista**: extraído verbatim (incluyendo los `onclick="..."`
  originales) a archivos TypeScript que exportan el fragmento como
  constante de string (`frontend/src/lib/simulator/fragments/*.ts`), uno
  por vista + uno para el "shell" global (SVG defs, loader, skip-link,
  barra de navegación del simulador) + uno para los modales globales.
- **JS**: extraído verbatim a `frontend/src/lib/simulator/engine-source.ts`
  y **ejecutado como script real inyectado en tiempo de ejecución**
  (`document.createElement('script')`), exactamente como lo haría el
  navegador con el archivo original. Esto es una decisión técnica
  deliberada: si el motor se importara como módulo ES (`import`), sus 32
  funciones (`mostrarBC`, `irAVista`, `irAPasaporte`, etc.) quedarían con
  *scope de módulo* y dejarían de estar accesibles desde los atributos
  `onclick="..."` conservados en el HTML — que dependen de que esas
  funciones existan como propiedades de `window`, igual que en un
  `<script>` clásico no-módulo.
- **Componentes React reales**: `EcosistemaShell.tsx` es el componente
  raíz que ensambla los fragmentos, importa el CSS, e inyecta el motor
  JS en un `useEffect` (post-montaje, con guarda anti-doble-inyección
  para React StrictMode). Se monta en la ruta real de Next.js
  `/ecosistema` vía `app/ecosistema/page.tsx`.
- **Las 4 vistas se montan simultáneamente** en el DOM (igual que en el
  archivo original), y es el propio motor JS —ya verificado en el código
  fuente— el que controla cuál es visible mediante la clase CSS
  `.vista.activa`, tal como en el simulador original. No fue necesario
  reimplementar el enrutamiento de vistas en React porque el mecanismo
  original ya es puramente declarativo (clases CSS), no un framework
  competidor.

### Lo que esta etapa entrega

- Arquitectura de componentes real: 1 componente raíz + 6 módulos de
  contenido (5 fragmentos de vista/shell + 1 de modales) + 1 módulo de
  motor, en vez de 1 archivo de 2.868 líneas.
- Ruta real de Next.js (`/ecosistema`) sirviendo el ecosistema completo,
  con routing, metadata y CSS gestionados por el framework.
- Fidelidad visual 100% verificable: el CSS y HTML son literalmente los
  mismos bytes que el simulador original (ver checklist de validación).
- Corrección de dos conflictos reales de integración detectados durante
  la migración (ver siguiente sección) que, sin corregirse, habrían roto
  la identidad visual del simulador dentro de la app Next.js.

### Lo que esta etapa NO entrega (y por qué, y cuándo)

- **Conversión de `onclick`/`getElementById` a estado de React
  (`useState`/`useReducer`) idiomático.** Reimplementar 32 funciones y
  114 manejadores de forma manual, sin una API real detrás todavía
  (llega en la Etapa 6+), tiene alto riesgo de introducir comportamientos
  sutilmente distintos a los del simulador validado, y bajo valor
  inmediato: hoy esas funciones simulan datos, no consumen la API real.
  La conversión a React idiomático se hace **módulo por módulo**, en las
  etapas de dominio donde cada pantalla se conecta a datos reales:
  Etapa 7 (Gestión de joyas), Etapa 8 (Esmeraldas), Etapa 10
  (Certificados digitales), Etapa 12 (Blockchain), Etapa 13 (SIEGEM Lab
  / IA), Etapa 15 (Dashboard ejecutivo), Etapa 16 (Centro de
  operaciones). En cada una de esas etapas, el fragmento correspondiente
  se reescribe como JSX real con estado de React, a medida que se
  conecta a la API — evitando reescribir dos veces la misma lógica.
- **Reemplazo de `dangerouslySetInnerHTML` por JSX manual.** Es la
  consecuencia directa de la decisión anterior: mientras la interacción
  siga siendo la del motor original, el HTML que la sostiene se mantiene
  verbatim para no desincronizar markup y lógica.

## Conflictos detectados y corregidos durante la migración

Integrar el simulador dentro de la app Next.js (que ya traía Tailwind
desde la Etapa 2) reveló dos conflictos reales de CSS que se corrigieron
en esta etapa:

1. **Tailwind `preflight` vs. reset propio del simulador.** El simulador
   define su propio reset (`*{box-sizing:border-box}`,
   `body{margin:0;...}`, `h1,h2,h3,h4{margin:0 0 8px;...}`, `a{color:
   inherit;text-decoration:none}`). El preflight de Tailwind, cargado
   globalmente desde `app/globals.css`, competía con esas reglas.
   **Corrección**: `corePlugins.preflight: false` en
   `frontend/tailwind.config.js`.
2. **Especificidad CSS en `<body>`.** El layout raíz (Etapa 2) aplicaba
   clases Tailwind (`bg-marfil-50 text-verde-950 font-ui`) directamente
   sobre `<body>`. Por especificidad CSS, un selector de clase siempre
   gana sobre un selector de elemento, así que esas clases habrían
   pisado la regla `body{background:...;color:...;font-family:...}` del
   simulador. **Corrección**: se removieron las clases de `<body>` en
   `app/layout.tsx`; la página placeholder de la Etapa 2
   (`app/page.tsx`) ahora aplica sus propios estilos en un contenedor
   `<main>` interno, sin afectar a `/ecosistema`.

Ambas correcciones están comentadas en el propio código fuente
(`tailwind.config.js`, `app/layout.tsx`).

## Árbol de archivos nuevos de esta etapa

```
frontend/
├── tailwind.config.js                          (modificado: preflight desactivado)
├── src/
│   ├── app/
│   │   ├── layout.tsx                            (modificado: <body> sin clases)
│   │   ├── page.tsx                               (modificado: estilos movidos a <main>, enlace a /ecosistema)
│   │   └── ecosistema/
│   │       ├── page.tsx                            (nuevo — ruta real de Next.js)
│   │       └── EcosistemaClient.tsx                 (nuevo — wrapper dynamic import, ssr:false)
│   ├── components/simulator/
│   │   └── EcosistemaShell.tsx                       (nuevo — componente raíz de la migración)
│   ├── lib/simulator/
│   │   ├── engine-source.ts                            (nuevo — motor JS verbatim, 530 líneas)
│   │   └── fragments/
│   │       ├── global-shell.ts                           (nuevo — SVG defs, loader, skip-link, barra)
│   │       ├── sitio-publico.ts                           (nuevo — vista pública + colecciones)
│   │       ├── pasaporte-digital.ts                        (nuevo — pasaporte + certificado + blockchain)
│   │       ├── siegem-lab.ts                                (nuevo — panel de IA)
│   │       ├── centro-operaciones.ts                         (nuevo — dashboard + backoffice)
│   │       └── modales-globales.ts                            (nuevo — preview PDF + toast)
│   └── styles/
│       └── simulador-terrae.css                                (nuevo — CSS verbatim, 952 líneas)
```

## Validación realizada

- Verificación byte a byte de los rangos de línea extraídos contra el
  archivo original (`sed -n` con límites confirmados por búsqueda de
  aperturas/cierres de `<section>`).
- Conteo de balance de `<div>`/`</div>` y `<section>`/`</section>` en
  cada fragmento extraído: 100% balanceado en los 6 fragmentos.
- Escapado correcto de backtick, backslash y `${` en las plantillas de
  string (necesario porque el CSS del simulador usa `var(--x)`, que no
  colisiona, pero un comentario HTML contenía un backtick literal que sí
  requería escape — detectado y corregido).
- Validación de sintaxis de los 6 fragmentos `.ts` y de `engine-source.ts`
  con `node --check`.
- Verificación de balance de llaves y paréntesis en los 5 archivos
  `.tsx` nuevos/modificados.
- Búsqueda de selectores CSS que dependieran de relación directa
  padre-hijo o hermanos (`body > .vista`, `.vista ~ .vista`, etc.) antes
  de introducir contenedores `<div>` adicionales alrededor de cada
  fragmento: no se encontraron, por lo que la envoltura es segura.
- Confirmación de que el simulador no referencia imágenes externas
  (`<img>`, `background-image: url(...)`) — es 100% autocontenido
  (SVG inline + gradientes CSS), por lo que no había rutas de assets que
  romper.
- `diff` confirma que `frontend/simulator/index.html` (el original) no
  fue tocado en ningún momento de esta etapa.

### Pendiente de validar en un entorno con Docker/red (fuera del sandbox de esta conversación)

- `npm install && npm run dev` dentro del contenedor `frontend` y
  comparación visual pixel a pixel entre `/ecosistema` y
  `/simulator/index.html`.
- `npm run type-check` (validación completa de TypeScript con el
  compilador real, no solo el chequeo heurístico de balance de símbolos
  hecho en este sandbox sin `node_modules`).
- `npm run lint`.

## Checklist de validación (a ejecutar por el desarrollador)

- [ ] `make up` (o `npm install && npm run dev` dentro de `frontend/`).
- [ ] http://localhost:3000/ecosistema carga sin errores en consola.
- [ ] Las 4 vistas (público, pasaporte, SIEGEM Lab, backoffice) se ven
      pixel a pixel iguales a http://localhost:3000/simulator/index.html.
- [ ] La barra de navegación del simulador (`.simulador-barra`) cambia
      de vista correctamente.
- [ ] Los flujos interactivos ya presentes en el simulador (tabs del
      pasaporte, pipeline SIEGEM, paneles del backoffice) funcionan
      igual que en el original.
- [ ] `frontend/simulator/index.html` sigue siendo idéntico al archivo
      original (sin modificaciones).
- [ ] `npm run type-check` y `npm run lint` pasan sin errores.

## Commits recomendados

```
feat(frontend): extraer CSS del simulador a hoja de estilos real
feat(frontend): extraer HTML de las 4 vistas a fragmentos componentizados
feat(frontend): inyectar motor JS del simulador preservando scope global
feat(frontend): crear EcosistemaShell y ruta /ecosistema
fix(frontend): desactivar preflight de Tailwind para no romper el diseño del simulador
fix(frontend): remover clases de <body> en layout raíz por conflicto de especificidad CSS
docs: documentar estrategia y decisiones de la Etapa 3
```

## Próxima etapa

**Etapa 4 — Sistema de autenticación y roles (JWT).** Se implementará el
módulo de autenticación real en el backend (registro, login, refresh
token, roles: administrador, joyero, auditor, cliente) y su integración
en el frontend, incluyendo la primera conversión real de un fragmento
del simulador (probablemente el login/acceso del backoffice) a
componentes React con estado idiomático, como caso piloto del patrón que
se repetirá en las etapas de dominio siguientes.
