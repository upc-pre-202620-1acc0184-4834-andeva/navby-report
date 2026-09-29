# Navby — Sistema de Diseño Canónico (Design System)

Este documento define la guía oficial y práctica de diseño visual para el ecosistema de Navby, aplicable tanto en el sitio web público ([`navby-website`](navby-website-documentation.md)) como en la aplicación interactiva ([`navby-webapp`](navby-webapp-documentation.md)). 

Está diseñado específicamente para integrarse de forma directa y sin fricciones con **Tailwind CSS v4**, aprovechando las clases nativas de Tailwind para tamaños (`text-sm`, `text-xl`), bordes (`rounded-md`, `rounded-xl`) y espaciados (`p-4`, `gap-3`), sin inventar escalas complejas e innecesarias.

Todos los activos vectoriales y fuentes tipográficas residen en [`docs/frontend-documentation/branding/`](branding/).

---

## 1. Identidad Visual de Marca y Logomarca

La marca de Navby se compone de dos elementos que se encuentran en la carpeta [`branding/`](branding/):

### 1.1 Anatomía del Isotipo (El Símbolo)
El isotipo de Navby representa formalmente una **«N» estilizada**:
* **Significado:** Su geometría continua sugiere las alas de una aeronave, una trayectoria ortodrómica de vuelo y el símbolo de avance constante.
* **Archivos vectoriales disponibles:**
  * [`branding/navby-isotipo-purple.svg`](branding/navby-isotipo-purple.svg): Isotipo oficial en púrpura de marca (`#604AFF`).
  * [`branding/navby-isotipo-white.svg`](branding/navby-isotipo-white.svg): Variante en blanco puro (`#FFFFFF`) para fondos oscuros.
  * [`branding/navby-isotipo-black.svg`](branding/navby-isotipo-black.svg): Variante en negro (`#262626`) para documentos monocromáticos.
  * [`branding/navby-icon.svg`](branding/navby-icon.svg) / [`.ico`](branding/navby-icon.ico): Isotipo blanco dentro de un contenedor redondeado púrpura, optimizado para el favicon del navegador e iconos de la app.

### 1.2 Anatomía del Isologo (Isotipo + Texto «avby»)
El isologo principal integra el isotipo y el texto en una sola marca:
* **Construcción:** El isotipo actúa visualmente como la primera letra **«N»** mayúscula estilizada. El resto del nombre («**avby**») se ubica a su derecha sobre la misma línea de base.
* **Tipografía del Isologo:** El texto «**avby**» utiliza la fuente **Raptor V3** ([`branding/raptor-v3/RaptorV3-Bold.woff2`](branding/raptor-v3/RaptorV3-Bold.woff2)). Su peso geométrico y proporciones encajan exactamente con el grosor del trazo del isotipo para formar la palabra completa «Navby».
* **Archivos vectoriales disponibles:**
  * [`branding/navby-isologo-purple.svg`](branding/navby-isologo-purple.svg): Isologo oficial completo en púrpura (`#604AFF`).
  * [`branding/navby-isologo-white.svg`](branding/navby-isologo-white.svg): Variante en blanco puro (`#FFFFFF`) para encabezados y fondos oscuros.
  * [`branding/navby-isologo-black.svg`](branding/navby-isologo-black.svg): Variante en negro (`#262626`) para contrastes sobre fondo blanco.

---

## 2. Paleta Cromática y Color de Acento

La paleta cromática oficial de Navby parte de los valores definidos en [`branding/pallette.txt`](branding/pallette.txt), incorporando el color de acento naranja seleccionado:

| Variable | Valor Hex | Muestra | ¿Para qué se usa en el producto? |
| :--- | :--- | :---: | :--- |
| `primary` | `#604AFF` | `■` | **Púrpura principal:** Botones primarios, isotipo principal, barras de navegación y selección activa. |
| `primary-dark` | `#4B37FB` | `■` | **Púrpura oscuro:** Estados hover de botones primarios (`hover:bg-primary-dark`). |
| `primary-soft` | `#DFDBFF` | `■` | **Púrpura suave:** Fondos tenues de insignias, etiquetas y selecciones secundarias. |
| `accent` | `#FF6B35` | `■` | **Color de acento (Aviation Sunset Orange):** Destacar la mejor tarifa encontrada, arcos de vuelo seleccionados, llamadas a la acción (CTAs) de oferta y microinteracciones de alta prioridad. |
| `accent-dark` | `#E8551E` | `■` | **Acento oscuro:** Hover de botones de acento (`hover:bg-accent-dark`). |
| `accent-soft` | `#FFE8DF` | `■` | **Acento suave:** Fondo de tarjetas de descuento, etiquetas de vuelos baratos y alertas suaves. |
| `surface-black` | `#262626` | `■` | **Fondo oscuro:** Fondo principal de la aplicación y de la landing en modo nocturno (`dark`). |
| `surface-white` | `#F8F8FA` | `■` | **Fondo claro:** Fondo principal en modo claro (`light`). Tono suave para evitar deslumbramiento. |
| `card-black` | `#272727` | `■` | **Tarjeta oscura:** Contenedores, tarjetas de vuelo y paneles flotantes en modo oscuro. |
| `card-white` | `#FFFFFF` | `■` | **Tarjeta clara:** Contenedores y tarjetas de vuelo en modo claro. |
| `text-black` | `#262626` | `■` | **Texto oscuro:** Texto principal en modo claro. |
| `text-white` | `#FFFFFF` | `■` | **Texto blanco:** Texto principal en modo oscuro y sobre botones primarios. |
| `text-subtitles` | `#C6C6C6` | `■` | **Subtítulos:** Textos secundarios y metadatos tenues (horas de vuelo, aerolíneas). |
| `border-card-dark` | `#EBEBEB` | `■` | **Bordes oscuros:** Líneas divisorias y bordes de tarjetas sobre fondo negro. |
| `border-card-light` | `#C6C6C6` | `■` | **Bordes claros:** Líneas divisorias y bordes de tarjetas sobre fondo blanco. |
| `success` | `#3AC530` | `■` | **Éxito:** Vuelos confirmados, validaciones de formulario y estado de conexión óptimo. |
| `error` | `#FB2C36` | `■` | **Error:** Vuelos sin disponibilidad, errores de red y alertas críticas. |
| `warning` | `#F0B100` | `■` | **Advertencia:** Conexiones con poco tiempo de escala o advertencias de equipaje. |

---

## 3. Tipografía Oficial: Albert Sans

La tipografía oficial del producto se organiza con estándares de rendimiento web de alto nivel:

1. **Raptor V3:** Uso exclusivo de marca para el texto del isologo («avby»).
2. **Albert Sans:** Tipografía oficial para el 100% de la web y de la webapp, ubicada en formato WOFF2 en [`branding/albert-sans/`](branding/albert-sans/).
   * **Carga optimizada en `global.css`:**
     * `font-display: swap`: Muestra el texto de inmediato con una fuente nativa mientras se descarga Albert Sans, evitando pantallas en blanco (*Flash of Invisible Text*).
     * `unicode-range` (subconjunto latino): Filtra la fuente para que el navegador descargue únicamente los caracteres que se usan en español, inglés y lenguas occidentales (abecedario, tildes `á, é, í, ó, ú`, `ñ`, símbolos y monedas `$`, `€`). Esto reduce el peso del archivo a solo 15-20 KB.
     * `font-weight: 100 900` (Variable Font): Un solo archivo soporta fluidamente todos los grosores de fuente sin tener que descargar múltiples archivos individuales.
   * **Integración con Tailwind v4:** Se utiliza directamente con la clase estándar `font-sans`.
   * **Escala de tamaños:** Utiliza directamente las clases nativas de Tailwind: `text-xs`, `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`, `text-4xl`, etc.

---

## 4. ¿Cómo Funciona Tailwind CSS v4 con Nuestros Colores?

### 4.1 ¿Qué es la directiva `@theme`?
En versiones anteriores de Tailwind (v3) tenías que configurar un archivo `tailwind.config.js`. 

En **Tailwind CSS v4**, ya **no** se usa `tailwind.config.js`. Ahora todo se configura dentro de tu CSS mediante el bloque `@theme`.

Cuando colocamos los colores dentro del bloque `@theme`:
```css
@theme {
  --color-primary: #604AFF;
  --color-primary-dark: #4B37FB;
  --color-accent: #FF6B35;
  --color-accent-soft: #FFE8DF;
  --color-surface-black: #262626;
  --color-surface-white: #F8F8FA;
  --color-card-black: #272727;
  --color-card-white: #FFFFFF;
  --color-text-black: #262626;
  --color-text-white: #FFFFFF;
  --color-text-subtitles: #C6C6C6;
  --color-border-card-dark: #EBEBEB;
  --color-border-card-light: #C6C6C6;
  --color-success: #3AC530;
  --color-error: #FB2C36;
  --color-warning: #F0B100;
}
```

Tailwind v4 lee esas variables y **crea automáticamente para ti** todas las clases utilitarias del framework con esos nombres (`bg-primary`, `text-accent`, `border-border-card-light`, etc.).

---

## 5. Guía Rápida de Clases en Tailwind (Cheat Sheet)

Aquí tienes exactamente qué clases escribir en tus componentes HTML, Astro o React:

### 5.1 Fondos (`bg-*`)
* `bg-primary` → Fondo púrpura corporativo (`#604AFF`)
* `hover:bg-primary-dark` → Hover del botón primario (`#4B37FB`)
* `bg-accent` → Fondo naranja de acento para la mejor oferta o llamada a la acción (`#FF6B35`)
* `bg-accent-soft` → Fondo naranja claro para etiquetas de descuento (`#FFE8DF`)
* `bg-surface-white` → Fondo claro de la página (`#F8F8FA`)
* `bg-surface-black` → Fondo oscuro de la página (`#262626`)
* `bg-card-white` → Fondo de tarjeta blanca (`#FFFFFF`)
* `bg-card-black` → Fondo de tarjeta negra (`#272727`)
* `bg-success`, `bg-error`, `bg-warning` → Fondos para estados del sistema

### 5.2 Textos (`text-*`)
* `text-primary` → Texto púrpura (`#604AFF`)
* `text-accent` → Texto naranja de acento (`#FF6B35`)
* `text-text-black` → Texto principal negro (`#262626`)
* `text-text-white` → Texto principal blanco (`#FFFFFF`)
* `text-text-subtitles` → Texto tenue de subtítulo (`#C6C6C6`)
* `text-success`, `text-error`, `text-warning` → Textos de alerta

### 5.3 Bordes (`border-*`)
* `border-primary` → Borde púrpura para campos seleccionados
* `border-accent` → Borde naranja para la mejor tarifa
* `border-border-card-light` → Borde sutil para tarjetas en fondo blanco
* `border-border-card-dark` → Borde para tarjetas en fondo negro

### 5.4 Modo Claro y Modo Oscuro Sencillo
Para hacer que un componente cambie automáticamente entre blanco y negro según el modo de la pantalla, simplemente usas el prefijo nativo `dark:` de Tailwind:

```html
<!-- La tarjeta es blanca por defecto, pero se vuelve negra en modo oscuro -->
<div class="bg-card-white dark:bg-card-black border border-border-card-light dark:border-border-card-dark text-text-black dark:text-text-white rounded-xl p-6 shadow-sm">
  <span class="text-accent text-sm font-semibold uppercase tracking-wider">Mejor Tarifa</span>
  <h3 class="text-2xl font-bold mt-1">Lima (LIM) → Miami (MIA)</h3>
  <p class="text-text-subtitles text-sm mt-1">Vuelo directo · 5h 45m</p>
  
  <div class="mt-4 flex items-center justify-between">
    <span class="text-3xl font-extrabold text-primary">$320 USD</span>
    <button class="bg-primary hover:bg-primary-dark text-text-white px-5 py-2.5 rounded-lg font-medium transition-colors">
      Seleccionar
    </button>
  </div>
</div>
```

---

## 6. Archivo Único Listo para Usar: `global.css`

Todo el sistema de diseño está empaquetado en un **único archivo maestro** listo para copiar directamente a tus aplicaciones:

👉 **[`styles/global.css`](styles/global.css)**

```css
/**
 * Navby — Archivo Maestro de Estilos Globales (Tailwind CSS v4)
 */

/* 1. Importación del Motor de Tailwind CSS v4 */
@import "tailwindcss";

/* 2. Carga Optimizada de la Tipografía Oficial (Albert Sans - WOFF2) */
@font-face {
  font-family: 'Albert Sans';
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
  src: url('/fonts/albert-sans/AlbertSans-VariableFont_wght.woff2') format('woff2-variations'),
       url('/fonts/albert-sans/AlbertSans-VariableFont_wght.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

@font-face {
  font-family: 'Albert Sans';
  font-style: italic;
  font-weight: 100 900;
  font-display: swap;
  src: url('/fonts/albert-sans/AlbertSans-Italic-VariableFont_wght.woff2') format('woff2-variations'),
       url('/fonts/albert-sans/AlbertSans-Italic-VariableFont_wght.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

/* 3. Configuración del Tema de Tailwind CSS v4 (@theme) */
@theme {
  --font-sans: 'Albert Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-isologo: 'Raptor V3', 'Albert Sans', sans-serif;

  /* Colores Corporativos Navby */
  --color-primary: #604AFF;
  --color-primary-dark: #4B37FB;
  --color-primary-soft: #DFDBFF;

  /* Color de Acento (Aviation Sunset Orange) */
  --color-accent: #FF6B35;
  --color-accent-dark: #E8551E;
  --color-accent-soft: #FFE8DF;

  /* Superficies (Fondos) */
  --color-surface-black: #262626;
  --color-surface-white: #F8F8FA;

  /* Tarjetas y Paneles (Cards) */
  --color-card-black: #272727;
  --color-card-white: #FFFFFF;

  /* Textos */
  --color-text-black: #262626;
  --color-text-white: #FFFFFF;
  --color-text-subtitles: #C6C6C6;

  /* Bordes de Tarjetas */
  --color-border-card-dark: #EBEBEB;
  --color-border-card-light: #C6C6C6;

  /* Estados Funcionales del Sistema */
  --color-success: #3AC530;
  --color-error: #FB2C36;
  --color-warning: #F0B100;
}

/* 4. Configuración Base Global */
body {
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

*(Nota: si en algún momento requieres tener los estilos separados en módulos, en la carpeta [`styles/`](styles/) también se conservan [`styles/typography.css`](styles/typography.css), [`styles/theme.css`](styles/theme.css) y [`styles/index.css`](styles/index.css)).*

---

## 7. ¿Dónde se Pega y Cómo se Usa en tus Proyectos?

### 7.1 En el Sitio Web (`navby-website` - Astro 5)
1. Copias la carpeta de fuentes [`branding/albert-sans/`](branding/albert-sans/) dentro de `public/fonts/albert-sans/`.
2. Copias el archivo [`styles/global.css`](styles/global.css) a `src/styles/global.css`.
3. En tu plantilla principal (`src/layouts/Layout.astro`), lo importas en el bloque frontmatter:
   ```astro
   ---
   import '../styles/global.css';
   ---
   <html lang="es">
     <head>
       <link rel="icon" type="image/svg+xml" href="/branding/navby-icon.svg" />
     </head>
     <body class="bg-surface-white dark:bg-surface-black text-text-black dark:text-text-white">
       <slot />
     </body>
   </html>
   ```

### 7.2 En la Aplicación Web (`navby-webapp` - React 19 + Vite 6)
1. Copias la carpeta de fuentes [`branding/albert-sans/`](branding/albert-sans/) dentro de `public/fonts/albert-sans/`.
2. Copias el archivo [`styles/global.css`](styles/global.css) a `src/styles/global.css`.
3. En el archivo de entrada (`src/main.tsx`), lo importas al inicio:
   ```tsx
   import React from 'react';
   import ReactDOM from 'react-dom/client';
   import App from './App';
   import './styles/global.css';

   ReactDOM.createRoot(document.getElementById('root')!).render(
     <React.StrictMode>
       <App />
     </React.StrictMode>
   );
   ```

¡Eso es todo! Con solo importar ese archivo, todas las clases de Tailwind (`bg-primary`, `bg-accent`, `text-accent`, `bg-surface-black`, `rounded-xl`, `text-2xl`, etc.) funcionarán de forma inmediata y automática en todo el proyecto.
