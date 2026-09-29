# Navby Website — Documentación de Herramientas y Frameworks

Este documento define de forma exhaustiva el catálogo de tecnologías, frameworks, bibliotecas y herramientas que componen el ecosistema técnico del sitio web público y portal de marketing de Navby (`navby-website`). Cada componente se detalla junto con su versión semántica exacta objetivo, su propósito específico en el ciclo de vida del desarrollo, ejecución, internacionalización, accesibilidad y despliegue.

---

## 1. Arquitectura Base y Runtime

La infraestructura de ejecución y empaquetado del sitio web se fundamenta en herramientas modernas que garantizan un rendimiento óptimo de carga estática, tipado estricto y compilación determinista.

* **Astro (v5.4.x / `^5.4.0`):** Framework web orientado a contenido y generación estática (SSG) basado en la arquitectura de islas (*Islands Architecture*). Su propósito es entregar HTML puro y optimizado por defecto sin enviar JavaScript innecesario al navegador del cliente, logrando puntuaciones máximas en métricas de Core Web Vitals (LCP, FID/INP, CLS) y tiempos de respuesta inicial (TTFB) inmediatos.
* **Node.js (v22.x LTS):** Entorno de ejecución de JavaScript del lado del servidor utilizado para los procesos de build, generación de páginas estáticas y ejecución de scripts de integración en tiempo de compilación.
* **pnpm (v10.x / `^10.5.0`):** Gestor de paquetes oficial del proyecto. Proporciona una instalación de dependencias rápida mediante enlaces duros y simbólicos, asegurando un árbol de `node_modules` estricto que elimina dependencias fantasma y reduce el uso de disco.
* **TypeScript (v5.7.x / `^5.7.3`):** Lenguaje de programación con tipado estático estricto. Permite modelar con precisión las propiedades de los componentes, la configuración de integraciones, los esquemas de datos y las interfaces de contenido, previniendo errores en tiempo de compilación.
* **Vite (v6.2.x / `^6.2.0`):** Motor de construcción y empaquetado integrado internamente dentro de Astro. Proporciona un servidor de desarrollo con reemplazo de módulos en caliente (*Hot Module Replacement* - HMR) instantáneo y optimización de activos para producción mediante Rollup.

---

## 2. Islas Interactivas y Componentes de UI

Para aquellos elementos de la página que requieren interactividad dinámica en el cliente, se utiliza la integración oficial de componentes desacoplados.

* **`@astrojs/react` (v4.2.x / `^4.2.0`):** Integración oficial de Astro que permite incrustar y renderizar componentes de React de manera aislada dentro de las plantillas de Astro. Facilita la directiva de hidratación selectiva (`client:load`, `client:idle`, `client:visible`), cargando el bundle de JavaScript únicamente cuando el componente entra en el viewport del usuario.
* **React (v19.0.x / `^19.0.0`):** Biblioteca para la construcción de interfaces de usuario declarativas. Se emplea exclusivamente en componentes aislados que demandan estado reactivo en el navegador, como selectores interactivos de moneda/idioma, menús de navegación móvil colapsables o micro-widgets de demostración funcional.
* **React DOM (v19.0.x / `^19.0.0`):** Punto de entrada al DOM para el renderizado y reconciliación de los componentes de React hidratados en el cliente.

---

## 3. Procesamiento y Estilizado CSS

El sistema de estilos adopta herramientas utilitarias de última generación orientadas a compilación de alto rendimiento y cero sobrecarga de tiempo de ejecución.

* **Tailwind CSS (v4.0.x / `^4.0.0`):** Motor de estilos utilitarios de alto rendimiento integrado a través del plugin oficial `@tailwindcss/vite`. Su propósito es construir interfaces modulares mediante clases utilitarias predefinidas, eliminando archivos CSS monolíticos a medida y reduciendo drásticamente el tamaño del archivo final generado gracias a la purga automática de estilos no utilizados.
* **`@tailwindcss/vite` (v4.0.x / `^4.0.0`):** Plugin oficial de Vite para la integración y compilación nativa de Tailwind CSS v4 con rendimiento instantáneo en tiempo de desarrollo.
* **PostCSS (v8.5.x / `^8.5.0`):** Procesador de CSS integrado dentro del pipeline de Vite que permite aplicar transformaciones automatizadas sobre las hojas de estilo y optimizar la compatibilidad entre navegadores.

---

## 4. Animación, Microinteracciones y Desplazamiento

El sitio incorpora un conjunto de herramientas especializadas para coreografiar la entrada visual de contenidos y ofrecer una navegación cinemática y fluida.

* **GSAP - GreenSock Animation Platform (v3.12.x / `^3.12.5`):** Motor de animación estándar de la industria para JavaScript. Se utiliza para orquestar líneas de tiempo (*timelines*), transiciones de entrada escalonadas y transformaciones de elementos en la pantalla con alta precisión de cuadros por segundo (60-120 fps).
* **GSAP ScrollTrigger (v3.12.x):** Plugin oficial incluido en la suite de GSAP que vincula animaciones visuales con la posición de desplazamiento de la ventana. Permite revelar secciones, fijar elementos (*pinning*) y coordinar microinteracciones a medida que el usuario navega verticalmente por la landing page.
* **Lenis (`lenis` v1.1.x / `^1.1.20`):** Biblioteca de desplazamiento suave (*smooth scrolling*) moderna y ligera. Normaliza la inercia de la rueda del ratón y el desplazamiento táctil entre diferentes plataformas y navegadores, sincronizándose de forma nativa con GSAP ScrollTrigger sin bloquear el hilo principal ni interferir con la accesibilidad del teclado.

---

## 5. Gestión de Contenido Estructurado

El contenido informativo del sitio web se administra de forma desacoplada del código mediante colecciones fuertemente tipadas.

* **Astro Content Collections (`astro:content` nativo en Astro 5.4.x):** Módulo nativo de Astro para organizar, cargar y validar contenido estructurado en archivos Markdown y MDX (como listados de funcionalidades, preguntas frecuentes, especificaciones y artículos informativos).
* **Zod (v3.24.x / `^3.24.2`):** Biblioteca de declaración y validación de esquemas TypeScript. Define y valida en tiempo de compilación la estructura de los metadatos (*frontmatter*) de cada archivo de contenido, garantizando que campos requeridos como títulos, descripciones, fechas o enlaces existan y cumplan con los tipos definidos.
* **`@astrojs/mdx` (v4.1.x / `^4.1.0`):** Integración que permite utilizar componentes de React y Astro dentro de los documentos de contenido Markdown, facilitando la inclusión de llamadas interactivas, tablas comparativas y componentes dinámicos en páginas informativas.

---

## 6. Internacionalización (i18n)

El portal de marketing está diseñado para soportar audiencias globales mediante herramientas de enrutamiento localizado y gestión determinista de idiomas.

* **Enrutamiento Nativo de Astro (`astro:i18n` nativo en Astro 5.4.x):** Sistema integrado en Astro 5 para la gestión de rutas multilingües mediante prefijos de URL deterministas (por ejemplo, `/es/` para español y `/en/` para inglés). Proporciona detección automática de idioma a través de la cabecera HTTP `Accept-Language`, redirección configurada y funciones auxiliares como `getRelativeLocaleUrl()` para generar enlaces coherentes con el idioma activo.
* **Catálogos de Traducción en JSON con Tipado TypeScript (v5.7.x):** Archivos estructurados de mensajes organizados por módulos temáticos. Se combinan con interfaces de TypeScript para ofrecer autocompletado y validación estricta de claves de traducción, evitando errores de referencias nulas o textos faltantes durante la compilación.
* **Metadatos SEO Multilingües:** Utilidades automatizadas para la inyección de etiquetas canónicas `<link rel="alternate" hreflang="...">` y etiquetas OpenGraph localizadas (`og:locale` y `og:locale:alternate`), permitiendo a los motores de búsqueda indexar adecuadamente las versiones en cada idioma y prevenir penalizaciones por contenido duplicado.

---

## 7. Accesibilidad (a11y)

La plataforma aplica estándares rigurosos de accesibilidad para garantizar la inclusión y navegación efectiva de personas con discapacidades visuales, auditivas, motoras o cognitivas, conforme a las pautas WCAG 2.1 nivel AA.

* **Semántica HTML5 y Marcado WAI-ARIA:** Estructuración del documento mediante elementos semánticos estándar (`<header>`, `<main>`, `<nav>`, `<section>`, `<footer>`) combinados con atributos WAI-ARIA (`aria-label`, `aria-expanded`, `aria-controls`, `aria-hidden`) para comunicar el estado y función de los elementos a tecnologías de asistencia (como lectores de pantalla).
* **Enlaces de Salto de Contenido (*Skip Links*):** Enlace oculto al inicio del documento que se hace visible al recibir foco por teclado, permitiendo a los usuarios saltar directamente la barra de navegación hacia el contenido principal (`#main-content`).
* **Soporte de Movimiento Reducido (`prefers-reduced-motion`):** Integración nativa de la media query CSS `@media (prefers-reduced-motion: reduce)` con las configuraciones de GSAP y Lenis, desactivando o mitigando automáticamente las animaciones de desplazamiento, transiciones cinemáticas y efectos de paralaje para usuarios con trastornos vestibulares o fotosensibilidad.
* **Control de Foco y Navegación por Teclado:** Estilos explícitos de foco visible (`:focus-visible`) que proporcionan un indicador visual claro para usuarios que navegan mediante tabulación, junto con trampas de foco (*focus traps*) en paneles modales o menús desplegables para impedir que el cursor del teclado se desplace detrás del diálogo activo.
* **`eslint-plugin-jsx-a11y` (v6.10.x / `^6.10.2`):** Plugin de análisis estático para ESLint que evalúa las plantillas JSX/TSX en tiempo de desarrollo, alertando sobre elementos no accesibles (como imágenes sin atributo `alt`, botones sin texto accesible o roles ARIA inválidos).
* **`@axe-core/playwright` (v4.10.x / `^4.10.1`) / `axe-core` (v4.10.x / `^4.10.2`):** Motor de pruebas automatizado de accesibilidad integrado dentro de la suite de pruebas E2E. Analiza el árbol DOM renderizado en busca de infracciones contra las directrices WCAG 2.1 AA e interrumpe la tubería de integración continua ante cualquier regresión.

---

## 8. Iconografía y Recursos Vectoriales

* **Lucide Astro (`lucide-astro` v0.475.x / `^0.475.0`):** Componentes de iconos SVG nativos para Astro con rendimiento cero JavaScript en el cliente.
* **Lucide React (`lucide-react` v0.475.x / `^0.475.0`):** Conjunto modular de iconos vectoriales SVG para las islas de React. Proporciona gráficos ligeros y coherentes que admiten *tree-shaking* completo (solo se incluyen en el bundle los iconos explícitamente importados) y cuentan con atributos de accesibilidad preconfigurados (`aria-hidden="true"` y soporte para etiquetas descriptivas).

---

## 9. Pruebas, Calidad de Código y Formateo

La confiabilidad del código y la coherencia del repositorio se mantienen mediante un conjunto estricto de herramientas de auditoría y pruebas automatizadas.

* **ESLint (v9.20.x / `^9.20.0` con Flat Config):** Analizador estático de código JavaScript, TypeScript y Astro. Aplica reglas de calidad, prevención de antipatrones y consistencia sintáctica.
* **Prettier (v3.5.x / `^3.5.1`):** Formateador de código obstinado que unifica el estilo visual de indentación, espaciado y comillas en archivos Markdown, TypeScript, Astro y JSON.
* **`prettier-plugin-astro` (v0.14.x / `^0.14.1`):** Plugin oficial para permitir que Prettier formatee archivos con extensión `.astro`.
* **`prettier-plugin-tailwindcss` (v0.6.x / `^0.6.11`):** Plugin que ordena automáticamente las clases utilitarias de Tailwind CSS siguiendo la jerarquía recomendada por el framework, optimizando la legibilidad y el mantenimiento del código.
* **Playwright (`@playwright/test` v1.50.x / `^1.50.1`):** Marco de automatización de pruebas de extremo a extremo (*End-to-End* - E2E) sobre navegadores reales (Chromium, Firefox, WebKit). Su propósito es verificar flujos críticos del sitio web: navegación entre secciones, persistencia y cambio de idioma, enlaces de llamada a la acción (CTAs) y ejecución de suites automatizadas de accesibilidad con `axe-core`.

---

## 10. Construcción, Empaquetado y Despliegue

* **`@astrojs/vercel` (v8.0.x / `^8.0.0`):** Adaptador oficial de Astro que optimiza la generación de la salida estática específicamente para la infraestructura de Vercel.
* **Vercel Edge Network:** Plataforma de alojamiento y distribución en la nube que publica los artefactos estáticos precompilados en una red global de distribución de contenido (*Edge CDN*). Ofrece almacenamiento en caché en el borde (*edge caching*), compresión Brotli/Gzip automática, renovación desatendida de certificados SSL y coste operacional cero ($0 USD/mes) bajo cuotas de uso de nivel gratuito.

---

## 11. Tabla Consolidada de Dependencias y Versiones Objetivo

La siguiente tabla resume todas las dependencias del proyecto con sus versiones semánticas exactas objetivo para la configuración del archivo `package.json` de `navby-website`:

| Paquete / Herramienta | Tipo | Versión SemVer Objetivo | Propósito Técnico |
| :--- | :--- | :--- | :--- |
| `astro` | `dependency` | `^5.4.0` | Framework web SSG con arquitectura de islas |
| `@astrojs/react` | `dependency` | `^4.2.0` | Integración de islas interactivas React |
| `@astrojs/mdx` | `dependency` | `^4.1.0` | Integración de contenido MDX enriquecido |
| `@astrojs/vercel` | `dependency` | `^8.0.0` | Adaptador de despliegue en Vercel Edge |
| `react` | `dependency` | `^19.0.0` | Biblioteca de UI para componentes cliente |
| `react-dom` | `dependency` | `^19.0.0` | Adaptador DOM para React 19 |
| `tailwindcss` | `dependency` | `^4.0.0` | Motor de estilos utilitarios CSS v4 |
| `@tailwindcss/vite` | `devDependency` | `^4.0.0` | Plugin Vite para compilación de Tailwind v4 |
| `gsap` | `dependency` | `^3.12.5` | Motor de animaciones y ScrollTrigger |
| `lenis` | `dependency` | `^1.1.20` | Desplazamiento suave cinemático desacoplado |
| `zod` | `dependency` | `^3.24.2` | Validación de esquemas en Content Collections |
| `lucide-astro` | `dependency` | `^0.475.0` | Iconografía SVG sin JS para Astro |
| `lucide-react` | `dependency` | `^0.475.0` | Iconografía SVG para islas React |
| `typescript` | `devDependency` | `^5.7.3` | Lenguaje con tipado estático estricto |
| `vite` | `devDependency` | `^6.2.0` | Motor de bundling subyacente de Astro |
| `postcss` | `devDependency` | `^8.5.0` | Procesador de soporte CSS |
| `eslint` | `devDependency` | `^9.20.0` | Linter de código estático (Flat Config) |
| `eslint-plugin-jsx-a11y` | `devDependency` | `^6.10.2` | Linter de accesibilidad WAI-ARIA |
| `prettier` | `devDependency` | `^3.5.1` | Formateador de código universal |
| `prettier-plugin-astro` | `devDependency` | `^0.14.1` | Formateo para archivos `.astro` |
| `prettier-plugin-tailwindcss` | `devDependency` | `^0.6.11` | Ordenamiento de clases utilitarias |
| `@playwright/test` | `devDependency` | `^1.50.1` | Suite de pruebas E2E en navegadores reales |
| `@axe-core/playwright` | `devDependency` | `^4.10.1` | Auditoría automatizada de accesibilidad WCAG 2.1 AA |
| `axe-core` | `devDependency` | `^4.10.2` | Motor nuclear de reglas de accesibilidad |
