# Navby Website — Arquitectura Detallada del Frontend

> Alcance: este documento define **stack, arquitectura, estructura y convenciones** del sitio web público de Navby (landing/marketing). Fuente de verdad para agentes de IA y desarrolladores.
>
> - Producto: ver [navby-documentation.md](navby-documentation.md)
> - Webapp (aplicación principal): ver [navby-webapp-architecture.md](navby-webapp-architecture.md)

---

## 1. Ecosistema y Stack Tecnológico General (Anti-sobreingeniería)

Dentro del ecosistema desacoplado de Navby, el subsistema **Website (`navby-website`)** cumple el rol de presencia institucional, captación y marketing:

* **Stack tecnológico:** **Astro 5.x** + **TypeScript** + **Tailwind CSS v4** + **GSAP 3** + **Lenis** + Markdown/MDX (*Content Collections*).
* **Propósito y justificación:** Portal público de captación, marketing y presentación institucional de Navby:
  * **SSG puro e Islands Architecture:** Astro genera HTML estático puro en tiempo de compilación con cero JavaScript innecesario en el cliente, logrando Core Web Vitals sobresalientes y máxima indexabilidad SEO.
  * **Animaciones y Smooth Scroll:** **GSAP** gestiona las animaciones de entrada, transiciones y microinteracciones de marca; **Lenis** provee un desplazamiento suave (*smooth scroll*) ultraligero y sincronizado con GSAP ScrollTrigger sin la sobrecarga ni restricciones comerciales de librerías propietarias.
* **Criterio anti-sobreingeniería:** Se descartan frameworks dinámicos pesados como Next.js o Remix (innecesarios para contenido estático) y se evita convertir la landing en una SPA de React que degrade la velocidad inicial.
* **Despliegue:** **Vercel** como plataforma de despliegue estático sobre Edge CDN global con coste operativo de $0.

---

## 2. Naturaleza del Sitio

El Website de Navby es el **sitio público de marketing/presentación**:

- Comunica qué es Navby, sus features y su propuesta de valor.
- SEO es prioridad (contenido indexable, Core Web Vitals altos).
- Es mayormente estático, con poca interactividad (animaciones leves, CTA "Abrir la app" que enlaza a la webapp, quizá una demo visual embebida).

**Conclusión:** es un sitio de contenido, no una aplicación → se construye con generación de sitio estático, no con un framework de app.

---

## 3. Experiencia de Usuario e Interacción Visual (Frontend UX)

* **Rendimiento y SEO:** Construido con Astro 5 bajo arquitectura de islas; el HTML se entrega pre-renderizado desde el Edge CDN de Vercel, alcanzando puntuaciones perfectas en Google Lighthouse.
* **Coreografía Visual:** Uso de **GSAP 3** para transiciones de entrada, revelación progresiva de tarjetas de valor y micro-interacciones sutiles.
* **Scroll Suave Continuo:** Integración con **Lenis** (`@darkroom.engineering/lenis`), garantizando un desplazamiento fluido y sincronizado con los gatillos de animación de GSAP ScrollTrigger sin penalización en la carga inicial ni dependencias de pago.

---

## 4. Stack Tecnológico (Decisiones Finales)

| Capa | Tecnología | Justificación |
| :--- | :--- | :--- |
| Framework | **Astro** (5.x) | Generación estática con "islands architecture": HTML puro por defecto, JS solo donde se necesita. SEO y performance óptimos para landing. |
| Lenguaje | **TypeScript** | Consistente con el resto del ecosistema Navby. |
| Estilos | **Tailwind CSS** (v4) | Mismo sistema de diseño que la webapp (identidad visual única). |
| Animaciones | **GSAP** (3.x) | Animaciones de entrada, coreografías visuales y microinteracciones de alto impacto estético. |
| Smooth Scroll | **Lenis** | Desplazamiento suave ultra-fluido y moderno, sincronizado con GSAP ScrollTrigger sin cuotas de licencia. |
| Islas interactivas | **React** (solo donde haga falta, vía integración oficial de Astro) | Componentes puntuales (ej. un mini-mapa demo o animación) sin convertir todo el sitio en SPA. |
| Contenido | Markdown/MDX (Content Collections de Astro) | Secciones como features, FAQ o blog se editan como contenido, no como código. |
| Despliegue | **Vercel** | Hosting estático automatizado en Edge CDN de baja latencia con coste operativo $0. |
| Calidad | ESLint + Prettier | Misma disciplina que la webapp. |
| Tests | Playwright (smoke E2E) | Verificar render de páginas clave y CTAs. |

### Decisiones descartadas

| Opción | Motivo del descarte |
| :--- | :--- |
| Next.js | Excelente para apps web; innecesario para una landing mayormente estática. |
| Vite + React SPA | Convertiría el sitio en SPA: peor SEO inicial y más JS del necesario. |
| 11ty / Hugo | Menos alineados con el ecosistema React/TS del equipo; Astro permite reutilizar componentes React. |

---

## 5. Arquitectura

- **SSG (Static Site Generation):** todas las páginas se compilan a HTML estático en build time. Despliegue en **Vercel** (Edge CDN) sin servidor dinámico propio.
- **Islands architecture:** el HTML es estático por defecto; los componentes interactivos (islas) se hidratan de forma aislada con directivas `client:*` solo donde se necesita.
- **Animaciones desacopladas:** GSAP y Lenis operan sobre el cliente enriqueciendo la experiencia visual sin degradar la puntuación de Lighthouse / Core Web Vitals.
- **Comunicación con la webapp:** ninguna lógica compartida en runtime. La webapp es una app separada en su propio subdominio (ej. `app.navby.*`); el website enlaza a ella con CTAs.

---

## 6. Estructura de Carpetas

```
navby-website/
├── astro.config.mjs
├── package.json
├── tsconfig.json
├── public/                       # estáticos tal cual (favicon, imágenes)
├── src/
│   ├── content/                  # colecciones (features, faq, ...) en MD/MDX
│   ├── layouts/                  # BaseLayout (head, meta SEO, header/footer)
│   ├── pages/                    # rutas de Astro (index.astro, about, ...)
│   ├── components/
│   │   ├── ui/                   # presentacionales puros (Astro o React)
│   │   └── islands/              # componentes React con client:* (interactivos)
│   ├── styles/                   # tailwind config / css global
│   └── lib/                      # utils (seo helpers, formateo)
└── tests/
    └── e2e/                      # Playwright smoke tests
```

### Convenciones

- Páginas en `src/pages` (file-based routing de Astro).
- Componentes visuales sin estado = Astro (`.astro`); con estado/interacción = React en `components/islands/` con directiva `client:visible` o `client:load`.
- Identidad visual compartida con la webapp: mismos tokens de Tailwind (colores, tipografía) para coherencia de marca.
- SEO por página: título, descripción y Open Graph centralizados en `BaseLayout`.

---

## 7. Despliegue en Vercel

- `astro build` → `dist/` estático.
- Hosting estático sobre Edge CDN de Vercel ($0 USD/mes).
- CI/CD: build + lint + smoke E2E automatizado antes de publicar a producción.

---

## 8. Referencias Rápidas para IAs/Devs

- Producto y features: [navby-documentation.md](../navby-documentation.md)
- App principal interactiva: [navby-webapp-architecture.md](navby-webapp-architecture.md)
- Backend Core / Platform: [navby-platform-architecture.md](../backend-documentation/navby-platform-architecture.md)
