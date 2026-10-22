# Navby Website

> Sitio público de marketing (estático). Explica el producto y lleva al usuario a la webapp. Los mensajes comerciales salen de [product-marketing.md](../product-marketing.md) y los datos (créditos, paquetes y perfiles), de [navby-documentation.md](../navby-documentation.md). No llama al backend.

## 1. Páginas y secciones

| Ruta | Contenido |
| :--- | :--- |
| `/es/`, `/en/` | **Hero** con el eslogan «El mejor vuelo. Al mejor precio.» y CTA `[Planificar vuelo]` hacia la webapp. **Cómo funciona** en 3 pasos: buscas por ciudad → Navby evalúa precio, duración y escalas a la vez → recibes un podio de 3 recomendaciones con compra directa. **Perfiles** Equilibrado, Ahorro y Rapidez. **Precios**: 10 créditos diarios gratis y paquetes Escapada, Viajero Frecuente y Nómada, en soles (con el equivalente en USD como referencia). **Preguntas frecuentes** y CTA final. |
| `/es/privacidad`, `/es/terminos` (y en `/en/`) | Política de Privacidad y Términos de Servicio en Markdown. Muestran su versión (igual a `TERMS_VERSION`, RL-01), declaran que los precios son referenciales (RL-03) y explican cómo eliminar la cuenta (RL-02). |

Regla de contenido: el sitio **nunca** promete «el vuelo más barato» o «el más rápido» como categorías. El mensaje es siempre el balance de los tres criterios.

## 2. Stack

| Área | Herramienta | Uso |
| :--- | :--- | :--- |
| Framework | Astro 5 (`output: "static"`) | HTML estático con arquitectura de islas. |
| Islas interactivas | `@astrojs/react` + React 19 | Solo para el menú móvil y el selector de idioma (`client:idle`). |
| Estilos | Tailwind CSS v4 (`@tailwindcss/vite`) | Tokens de [design-system.md](design-system.md). |
| Animación | GSAP 3 + ScrollTrigger, Lenis | Animaciones de entrada y desplazamiento suave. |
| Contenido | Content Collections + Zod, `@astrojs/mdx` | FAQ y páginas legales tipadas. |
| Iconos | `lucide-astro`, `lucide-react` | SVG. |
| Lenguaje | TypeScript estricto | |
| Paquetes | `pnpm` | |

## 3. Internacionalización

- Enrutamiento nativo `astro:i18n` con prefijos `/es/` (predeterminado) y `/en/`.
- Textos en catálogos JSON tipados por clave.
- Etiquetas `hreflang` y OpenGraph (`og:locale`) por idioma.

## 4. Accesibilidad (WCAG 2.1 AA)

- HTML semántico (`header`, `nav`, `main`, `footer`) y *skip link* hacia `#main-content`.
- `prefers-reduced-motion` desactiva GSAP, ScrollTrigger y Lenis.
- Foco visible con `:focus-visible` y foco atrapado en el menú móvil abierto.
- `eslint-plugin-jsx-a11y` en desarrollo y `@axe-core/playwright` en las pruebas E2E.

## 5. Calidad y despliegue

- ESLint 9, Prettier con `prettier-plugin-astro` y `prettier-plugin-tailwindcss`.
- Playwright: navegación, cambio de idioma, CTAs y auditoría de accesibilidad.
- Despliegue estático en Vercel (plan gratuito, $0 USD/mes). No requiere adaptador de servidor.

## 6. Dependencias

| Paquete | Versión | Tipo |
| :--- | :--- | :--- |
| `astro` | `^5.4.0` | dependency |
| `@astrojs/react`, `@astrojs/mdx` | `^4.2.0`, `^4.1.0` | dependency |
| `react`, `react-dom` | `^19.0.0` | dependency |
| `tailwindcss` | `^4.0.0` | dependency |
| `gsap`, `lenis` | `^3.12.5`, `^1.1.20` | dependency |
| `zod` | `^3.24.2` | dependency |
| `lucide-astro`, `lucide-react` | `^0.475.0` | dependency |
| `@tailwindcss/vite`, `typescript` | `^4.0.0`, `^5.7.3` | devDependency |
| `eslint`, `eslint-plugin-jsx-a11y` | `^9.20.0`, `^6.10.2` | devDependency |
| `prettier`, `prettier-plugin-astro`, `prettier-plugin-tailwindcss` | `^3.5.1`, `^0.14.1`, `^0.6.11` | devDependency |
| `@playwright/test`, `@axe-core/playwright` | `^1.50.1`, `^4.10.1` | devDependency |
