# Navby Webapp — Documentación de Herramientas y Frameworks

Este documento define de forma exhaustiva el catálogo de tecnologías, frameworks, bibliotecas y herramientas que componen el ecosistema técnico de la aplicación web principal de Navby (`navby-webapp`), correspondiente al planificador interactivo de rutas aéreas con mapa plano 2D. Cada componente se describe con su versión semántica exacta objetivo, su función en el flujo de datos, su integración con la plataforma backend, y las estrategias técnicas de internacionalización, accesibilidad y despliegue.

---

## 1. Núcleo, Lenguaje y Herramientas de Construcción

La base operativa de la aplicación está construida sobre un entorno reactivo tipado y optimizado para compilación ultrarrápida en el cliente.

* **React (v19.0.x / `^19.0.0`):** Biblioteca declarativa de interfaces de usuario fundamentada en componentes funcionales, hooks avanzados (`useActionState`, `useOptimistic`, `useId`, `useTransition`) y renderizado concurrente. Su propósito es estructurar la aplicación en módulos desacoplados y gestionar de manera eficiente la sincronización de la interfaz reactiva ante eventos de búsqueda, navegación e interacción sobre el mapa.
* **React DOM (v19.0.x / `^19.0.0`):** Adaptador oficial para el renderizado eficiente de componentes en el árbol DOM del navegador.
* **TypeScript (v5.7.x / `^5.7.3` en modo estricto):** Lenguaje tipado que extiende JavaScript para garantizar la seguridad de tipos estática en toda la base de código. Se utiliza para modelar los contratos de datos provenientes de la API REST del backend (aeropuertos, segmentos de vuelo, métricas de itinerarios y cotizaciones de tarifas de mercado), así como los estados de la interfaz y las firmas de componentes, previniendo errores de acceso nulo o tipos incompatibles en tiempo de ejecución.
* **Vite (v6.2.x / `^6.2.0`):** Herramienta de construcción y servidor de desarrollo local de alta velocidad. Emplea ES Modules nativos en el navegador para brindar reemplazo de módulos en caliente (*Hot Module Replacement* - HMR) instantáneo durante el desarrollo, y orquesta el empaquetado optimizado para producción mediante Rollup, aplicando división de código por rutas (*code-splitting*), compresión y generación de chunks dinámicos.
* **`@vitejs/plugin-react` (v4.3.x / `^4.3.4`):** Plugin oficial de Vite para la compilación rápida de React mediante Babel o SWC con soporte completo para Fast Refresh.
* **Node.js (v22.x LTS):** Entorno de ejecución en el servidor utilizado como base para la ejecución de herramientas de desarrollo, compilación, transpilación y orquestación de scripts de prueba.
* **pnpm (v10.x / `^10.5.0`):** Gestor de paquetes unificado y estricto. Implementa un almacén global direccionable por contenido que previene dependencias fantasma, acelera las instalaciones y garantiza reproducibilidad absoluta en las compilaciones locales y de integración continua.

---

## 2. Enrutamiento y Gestión del Estado de la URL

La navegación interna del cliente ligero de una sola página (*Single Page Application* - SPA) se sincroniza con los parámetros de la dirección web para permitir enlaces compartibles y persistencia del estado de navegación.

* **React Router (v7.2.x / `^7.2.0`):** Enrutador declarativo estándar para aplicaciones React. Su propósito principal es desacoplar las vistas de la aplicación (búsqueda interactiva, detalle de itinerario, gestión de perfil, historial de cotizaciones) y gestionar los parámetros de consulta de la URL mediante `useSearchParams`. Esto permite que una consulta de vuelos (origen, destino, fecha de salida, fecha de retorno, número de pasajeros) funcione como la fuente única de la verdad en la barra de direcciones del navegador, facilitando que el usuario guarde o comparta enlaces con los parámetros de búsqueda ya configurados.

---

## 3. Gestión de Estado Asíncrono y Caché de Servidor

La comunicación con los servicios del backend genera estados asíncronos complejos que se administran mediante un gestor de caché dedicado.

* **TanStack Query (v5.66.x / `^5.66.0` - `@tanstack/react-query`):** Capa de sincronización de estado de servidor para React. Gestiona las peticiones HTTP asíncronas hacia el backend, ofreciendo almacenamiento en caché en memoria, deduplicación de solicitudes idénticas, revalidación en segundo plano cuando la ventana recupera el foco (*stale-while-revalidate*), políticas de reintento ante fallos de red y manejo reactivo de los estados de carga (`isLoading`, `isPending`), error (`isError`) y datos listos (`data`). Reduce drásticamente la necesidad de escribir efectos manuales (`useEffect`) y almacenes locales para peticiones remotas.
* **`@tanstack/react-query-devtools` (v5.66.x / `^5.66.0`):** Herramienta visual de depuración que se integra en el entorno de desarrollo local para inspeccionar el estado de la caché, verificar claves de consulta (*query keys*), observar el tiempo de vida de los datos (*staleTime* y *gcTime*) y simular respuestas lentas o fallidas.

---

## 4. Gestión de Estado de UI del Cliente

El estado local e interactivo que no proviene del servidor ni reside en la URL se maneja de forma centralizada sin sobrecarga de dependencias pesadas.

* **Zustand (v5.0.x / `^5.0.3`):** Almacén de estado global minimalista y desacoplado del ciclo de renderizado de React. Su propósito es coordinar el estado de la sesión interactiva del usuario sobre el mapa: aeropuerto de origen o destino seleccionado mediante clics en el lienzo, visibilidad de capas geoespaciales, panel lateral activo (expandido o colapsado), filtros de aerolíneas o escalas aplicados en memoria y preferencias temporales del usuario. Opera sin boilerplate, con consumo de memoria mínimo y selectores precisos que evitan re-renderizados innecesarios en la interfaz.

---

## 5. Motor Cartográfico y Renderizado de Grafos Geoespaciales

El núcleo visual interactivo de Navby se compone de un motor cartográfico vectorial en dos dimensiones y una capa de computación gráfica de alto rendimiento.

* **MapLibre GL JS (`maplibre-gl` v4.7.x / `^4.7.1`):** Motor de mapas de código abierto basado en WebGL y WebGPU, derivado de Mapbox GL JS bajo licencia BSD. Su propósito es renderizar mapas base vectoriales interactivos en proyección plana Web Mercator (2D). Proporciona navegación fluida (paneo, zoom continuo, rotación) a 60 cuadros por segundo sin dependencias de servicios de pago cerrados ni cobros por cuota de uso de teselas (*tiles*), integrando fuentes abiertas como Protomaps u OpenStreetMap.
* **`react-map-gl` (v7.1.x / `^7.1.8` - versión compatible con MapLibre):** Envoltorio reactivo oficial que conecta el ciclo de vida y los eventos nativos de MapLibre GL con los componentes declarativos de React (`<Map>`, `<Marker>`, `<Popup>`, `<Source>`, `<Layer>`), gestionando el estado de la cámara (*viewport*) mediante props controladas.
* **deck.gl (v9.1.x / `^9.1.0` - `@deck.gl/core`, `@deck.gl/layers`, `@deck.gl/mapbox`):** Suite de capas de visualización de datos geoespaciales acelerada por hardware (WebGL2). Su propósito en Navby es renderizar simultáneamente miles de arcos de vuelo sobre el mapa plano mediante la capa `ArcLayer` (arcos de círculo máximo ortodrómicos que representan trayectorias geodésicas en 2D). Permite pintar el grafo global de vuelos (más de 37,000 conexiones dirigidas) con interactividad en tiempo real (detección de clics (*picking*), resaltado de aristas y cambio dinámico de grosor) sin saturar el hilo principal de JavaScript gracias al procesamiento directo en los shaders de la GPU.

---

## 6. Primitivas de Componentes Accesibles y Formularios

La interfaz de usuario se construye utilizando primitivas sin estilos que delegan la accesibilidad y el control de teclado a especificaciones formales.

* **Radix UI Primitives (v1.1.x / v2.1.x):** Conjunto de primitivas de componentes *headless* (sin estilos predeterminados) diseñadas conforme a la especificación WAI-ARIA (`@radix-ui/react-dialog`, `@radix-ui/react-popover`, `@radix-ui/react-dropdown-menu`, `@radix-ui/react-tabs`, `@radix-ui/react-tooltip`, `@radix-ui/react-select`, `@radix-ui/react-scroll-area`). Garantizan de manera nativa la gestión de foco por teclado, descarte mediante la tecla Escape, anclaje de posición y atributos ARIA pertinentes.
* **shadcn/ui (CLI v2.x):** Patrón de arquitectura de componentes donde las primitivas de Radix UI se configuran con Tailwind CSS e integran directamente dentro de la carpeta de código fuente del proyecto (`src/components/ui/`). Esto asegura control absoluto sobre el código, personalización sin abstracciones opacas y eliminación de dependencias binarias externas en `node_modules`.
* **Recharts (`recharts` v2.15.x / `^2.15.0`):** Biblioteca declarativa de gráficos construida sobre primitivas SVG y componentes de React. Se emplea dentro del diálogo modal accesible de telemetría («Ver detalles») para renderizar gráficos de barras comparativos (`<BarChart>`, `<ResponsiveContainer>`, `<Bar>`, `<XAxis>`, `<YAxis>`, `<Tooltip>`) que contrastan empíricamente el tiempo de cómputo (milisegundos) y los nodos explorados entre $A^*$ (con heurística de Haversine), Dijkstra y BFS a partir del payload `AlgorithmTelemetryResponseSchema` retornado por el backend. Para preservar el rendimiento del hilo principal, se carga de forma diferida mediante importación dinámica (`React.lazy`).
* **React Hook Form (v7.54.x / `^7.54.2`):** Biblioteca de alto rendimiento para el manejo de formularios. Se fundamenta en referencias no controladas (*uncontrolled components*), registrando entradas de texto y controles interactivos sin desencadenar re-renderizados de todo el formulario con cada pulsación de tecla. Se utiliza en el panel de búsqueda de vuelos (selección de aeropuertos, fechas de salida y retorno, clase de cabina y cantidad de pasajeros).
* **Zod (v3.24.x / `^3.24.2`):** Biblioteca de validación y análisis de esquemas tipados en tiempo de ejecución. Valida que los datos ingresados en el formulario de búsqueda cumplan con las restricciones del dominio (código IATA válido de 3 letras, fecha de retorno posterior a la fecha de salida, mínimo 1 pasajero, origen diferente a destino). Además, se utiliza para validar las respuestas de la API del backend antes de que ingresen a la capa de dominio.
* **`@hookform/resolvers` (v3.10.x / `^3.10.0`):** Adaptador oficial que conecta los esquemas de validación de Zod con el ciclo de validación de React Hook Form, transmitiendo automáticamente los mensajes de error tipados hacia la interfaz.
* **`react-day-picker` (v9.5.x / `^9.5.1`):** Componente interactivo y accesible para la selección de fechas individuales y rangos de fechas (ida y vuelta). Proporciona navegación accesible por teclado mediante las teclas de dirección, soporte de internacionalización de nombres de meses/días y marcado ARIA semántico.

---

## 7. Animaciones de Carga y Sistema de Notificaciones

La retroalimentación visual durante operaciones asíncronas y eventos del sistema se gestiona mediante herramientas ligeras orientadas a la experiencia del usuario.

* **boneyard (v0.1.x / `^0.1.4`):** Biblioteca especializada en la composición de estructuras esqueléticas de carga (*skeleton loaders*) reactivas y adaptativas. Su propósito es proyectar estructuras previas de contenido visual durante los periodos de latencia de red (cálculo algorítmico de rutas en el backend o consulta externa de cotizaciones de tarifas), evitando saltos de diseño acumulativos (CLS) y transmitiendo sensación de dinamismo al usuario.
* **Sileo (`sileo` v0.1.x / `^0.1.5`):** Sistema reactivo de notificaciones flotantes (*toast notifications*). Proporciona alertas visuales y auditivas accesibles para comunicar el éxito o fracaso de operaciones clave (por ejemplo, «Itinerario guardado en su cuenta», «Cuota de búsquedas diarias agotada» o «Error al conectar con el servidor de precios»). Incluye soporte para temporizadores automáticos de cierre, pausas al interactuar con el cursor y atributos de accesibilidad para lectores de pantalla.

---

## 8. Cliente HTTP y Comunicación con la Plataforma

* **API Client Nativo (Envoltorio sobre `fetch`):** Cliente de red modular construido sobre la API estándar `window.fetch` del navegador, sin la sobrecarga de paquetes externos pesados como Axios. Incorpora interceptores tipados para:
  - Inyectar encabezados de autorización con tokens de sesión JWT (`Bearer <token>`).
  - Gestionar el refresco transparente de credenciales expiradas.
  - Normalizar las estructuras de error devueltas por la API de FastAPI a tipos tipados de dominio (`Result.failure` o instancias de error tipadas).
  - Configurar políticas de tiempo de espera (*timeout*) mediante `AbortController`.

---

## 9. Internacionalización (i18n)

Para permitir el uso de la aplicación por usuarios internacionales en múltiples regiones, se despliega una infraestructura completa de internacionalización y localización dinámica.

* **`i18next` (v24.2.x / `^24.2.2`):** Motor central de internacionalización para aplicaciones JavaScript. Ofrece un sistema integral de traducción que soporta interpolación de variables dinámicas, reglas de pluralización complejas dependientes de la lengua, gestión de contextos semánticos y división del catálogo de mensajes en múltiples espacios de nombres (*namespaces*, por ejemplo: `common`, `search`, `itinerary`, `errors`).
* **`react-i18next` (v15.4.x / `^15.4.1`):** Integración oficial de `i18next` para React. Proporciona el hook `useTranslation()` y el componente `<Trans />` para renderizar cadenas traducidas de forma reactiva, actualizando instantáneamente la interfaz ante cambios de idioma sin requerir recargas completas de la página.
* **`i18next-browser-languagedetector` (v8.0.x / `^8.0.2`):** Módulo para la detección automática y no intrusiva de la preferencia lingüística del usuario. Evalúa en orden de precedencia:
  1. Parámetros de consulta en la URL (`?lang=es` o `?lang=en`).
  2. Preferencia explícita previamente guardada en el almacenamiento local del navegador (`localStorage`).
  3. Cabecera o preferencia de idioma del sistema operativo y navegador (`navigator.languages`).
* **APIs Nativas `Intl` de JavaScript (Estándar ECMAScript):** Uso directo de los estándares de internacionalización del navegador para formateo localizado:
  - **`Intl.NumberFormat`:** Formateo localizado de importes monetarios y tarifas aéreas en múltiples divisas (USD, EUR, PEN), respetando los separadores de millares y decimales propios de cada configuración regional.
  - **`Intl.DateTimeFormat`:** Formateo de fechas, horarios de salida y tiempos de escala, considerando automáticamente los husos horarios IANA de cada aeropuerto de origen, tránsito y destino.

---

## 10. Accesibilidad (a11y)

Navby Webapp está diseñada bajo los lineamientos de las Pautas de Accesibilidad para el Contenido Web (WCAG 2.1 nivel AA), garantizando que las funcionalidades de búsqueda, lectura de rutas y selección de itinerarios sean plenamente operables mediante tecnologías de asistencia y navegación sin ratón.

* **Primitivas Radix UI con Conformidad WAI-ARIA:** Cada componente interactivo (menús, cuadros de diálogo, selectores, acordeones de escalas) integra por diseño el conjunto completo de atributos ARIA y comportamientos de teclado exigidos por el estándar:
  - Atributos `role="combobox"`, `role="listbox"`, `role="dialog"`, `aria-expanded`, `aria-activedescendant`.
  - Captura y contención de foco (*focus trapping*) en modales para que el tabulador no escape al fondo de la pantalla.
  - Cierre automático al pulsar la tecla Escape y restauración del foco en el elemento activador.
* **Vista Alternativa Accesible del Mapa (Lectores de Pantalla):** Dado que los lienzos WebGL (`<canvas>`) de MapLibre GL y deck.gl no son accesibles de forma nativa para lectores de pantalla, la aplicación provee una vista paralela en modo tabla/lista semántica accesible. Esta estructura textual detalla de forma secuencial cada segmento de vuelo, aeropuerto de conexión, tiempo de escala, duración estimada y aerolínea operadora, permitiendo que un usuario con lector de pantalla (como NVDA, JAWS o VoiceOver) explore y seleccione itinerarios sin depender de la visualización cartográfica gráfica.
* **Zonas Vivas ARIA (`aria-live`):** Implementación de regiones dinámicas con atributos `aria-live="polite"` y `aria-atomic="true"` en los paneles de resultados de búsqueda. Permiten que los lectores de pantalla anuncien automáticamente las actualizaciones de estado de la operación (por ejemplo: «Iniciando búsqueda de vuelos», «Calculando itinerarios con menor escala», «Se encontraron 5 opciones de vuelo disponibles») sin interrumpir la lectura del usuario.
* **Navegación por Teclado y Foco Visible:** Gestión estricta de tabulación en toda la aplicación, incluyendo atajos de teclado para controles del mapa (zoom mediante teclas `+` y `-`, paneo mediante flechas direccionales) e indicadores de foco visuales de alto contraste mediante la pseudo-clase `:focus-visible`.
* **Soporte de Movimiento Reducido (`prefers-reduced-motion`):** Detección de la preferencia del sistema operativo para deshabilitar las animaciones de interpolación de la cámara del mapa (saltando directamente a las coordenadas del vuelo sin efectos de vuelo cinemático) y suprimir las animaciones continuas de pulsos en los arcos de deck.gl.
* **`@axe-core/react` (v4.10.x / `^4.10.1`):** Herramienta de auditoría de accesibilidad en tiempo de desarrollo. Inspecciona el DOM de la aplicación en el navegador y emite advertencias detalladas en la consola de herramientas de desarrollo cuando se detectan problemas de contraste, etiquetas faltantes o jerarquías de encabezados incorrectas.
* **`eslint-plugin-jsx-a11y` (v6.10.x / `^6.10.2`):** Linter estático que audita el código fuente TSX durante la escritura y en los procesos de integración continua, previniendo la introducción de patrones no accesibles.
* **`@axe-core/playwright` (v4.10.x / `^4.10.1`):** Módulo de validación automatizada de accesibilidad integrado en las pruebas E2E para certificar de forma continua la conformidad WCAG 2.1 AA.

---

## 11. Iconografía y Recursos Gráficos

* **Lucide React (`lucide-react` v0.475.x / `^0.475.0`):** Biblioteca oficial de iconos SVG para React. Sus componentes son ligeros, totalmente configurables en tamaño y grosor de trazo, optimizados para *tree-shaking* y configurados con atributos `aria-hidden="true"` para prevenir lecturas erróneas en sintetizadores de voz, complementados con texto alternativo accesible mediante componentes descriptivos visualmente ocultos (`sr-only`).

---

## 12. Pruebas Automatizadas y Calidad de Código

* **Vitest (v3.0.x / `^3.0.5`):** Marco de pruebas unitarias y de integración de alto rendimiento. Opera nativamente sobre la configuración de transformación de Vite, ejecutando pruebas con soporte completo de TypeScript, JSX y simulación de módulos (*mocking*).
* **Testing Library (`@testing-library/react` v16.2.x / `^16.2.0`, `@testing-library/user-event` v14.6.x, `@testing-library/dom` v10.4.x, `@testing-library/jest-dom` v6.6.x):** Conjunto de utilidades de prueba orientadas al comportamiento del usuario. Evalúa los componentes interactuando con ellos tal como lo haría un usuario real (buscando elementos por rol, texto accesible o etiqueta de formulario) en lugar de depender de detalles internos de implementación.
* **Playwright (`@playwright/test` v1.50.x / `^1.50.1`):** Suite de pruebas de extremo a extremo (*E2E*). Ejecuta flujos de usuario reales de forma desatendida en navegadores Chromium, WebKit y Firefox:
  - Formulación de búsquedas de rutas aéreas.
  - Selección de aeropuertos desde el buscador de autocompletado.
  - Interacción y clics sobre los arcos de vuelo en el mapa.
  - Verificación del cambio de idioma en toda la interfaz.
  - Ejecución de pruebas automatizadas de regresión de accesibilidad con `axe-core`.
* **ESLint (v9.20.x / `^9.20.0` con Flat Config):** Reglas estrictas de calidad de código gobernadas por `typescript-eslint` (v8.24.x), `eslint-plugin-react-hooks` y `eslint-plugin-jsx-a11y`.
* **Prettier (v3.5.x / `^3.5.1`) + `prettier-plugin-tailwindcss` (v0.6.x / `^0.6.11`):** Formateo automático uniforme de archivos de código y ordenamiento determinista de clases de estilo.

---

## 13. Construcción, Empaquetado y Despliegue

* **Empaquetado SPA con Vite:** Genera artefactos estáticos HTML, CSS y JavaScript minificados con *hashes* en el nombre de archivo para permitir invalidación determinista de caché en navegadores.
* **Vercel (Hosting Estático para SPA):** Despliegue sobre la infraestructura de Edge CDN de Vercel configurado mediante un archivo de enrutamiento `vercel.json` con la directiva:
  ```json
  {
    "rewrites": [
      {
        "source": "/(.*)",
        "destination": "/index.html"
      }
    ]
  }
  ```
  Esta directiva asegura que cualquier ruta solicitada por el usuario (como `/search?origin=LIM&dest=MIA` o `/itineraries/123`) sea redirigida internamente hacia `index.html` para que el enrutador del cliente de React Router resuelva la vista correspondiente sin devolver errores HTTP 404.

---

## 14. Tabla Consolidada de Dependencias y Versiones Objetivo

La siguiente tabla resume todas las dependencias del proyecto con sus versiones semánticas exactas objetivo para la configuración del archivo `package.json` de `navby-webapp`:

| Paquete / Herramienta | Tipo | Versión SemVer Objetivo | Propósito Técnico |
| :--- | :--- | :--- | :--- |
| `react` | `dependency` | `^19.0.0` | Núcleo de interfaz reactiva concurrente |
| `react-dom` | `dependency` | `^19.0.0` | Adaptador de reconciliación DOM |
| `react-router` | `dependency` | `^7.2.0` | Enrutamiento SPA y gestión de URLs (`useSearchParams`) |
| `@tanstack/react-query` | `dependency` | `^5.66.0` | Caché, sincronización y revalidación de estado de servidor |
| `zustand` | `dependency` | `^5.0.3` | Estado global ligero de sesión interactiva del mapa |
| `maplibre-gl` | `dependency` | `^4.7.1` | Motor cartográfico vectorial plano 2D (WebGL/WebGPU) |
| `react-map-gl` | `dependency` | `^7.1.8` | Envoltorio reactivo declarativo para MapLibre |
| `@deck.gl/core` | `dependency` | `^9.1.0` | Núcleo de visualización geoespacial WebGL2 |
| `@deck.gl/layers` | `dependency` | `^9.1.0` | Capas gráficas (`ArcLayer` para arcos de vuelo) |
| `@deck.gl/mapbox` | `dependency` | `^9.1.0` | Integración de deck.gl sobre lienzo de MapLibre |
| `react-hook-form` | `dependency` | `^7.54.2` | Manejo de formularios de alto rendimiento no controlado |
| `zod` | `dependency` | `^3.24.2` | Validación estricta de esquemas de datos y APIs |
| `@hookform/resolvers` | `dependency` | `^3.10.0` | Integrador entre Zod y React Hook Form |
| `react-day-picker` | `dependency` | `^9.5.1` | Selector accesible de fechas y rangos de viaje |
| `boneyard` | `dependency` | `^0.1.4` | Generador de skeletons de carga adaptativos |
| `sileo` | `dependency` | `^0.1.5` | Sistema reactivo y accesible de notificaciones toast |
| `i18next` | `dependency` | `^24.2.2` | Motor nuclear de internacionalización multilingüe |
| `react-i18next` | `dependency` | `^15.4.1` | Enlaces y hooks reactivos de traducción para React |
| `i18next-browser-languagedetector` | `dependency` | `^8.0.2` | Detección automática de idioma del navegador |
| `lucide-react` | `dependency` | `^0.475.0` | Iconografía vectorial SVG accesible |
| `@radix-ui/react-dialog` | `dependency` | `^1.1.6` | Primitiva modal accesible WAI-ARIA |
| `recharts` | `dependency` | `^2.15.0` | Visualización declarativa de telemetría algorítmica y benchmarking |
| `@radix-ui/react-popover` | `dependency` | `^1.1.6` | Primitiva flotante accesible WAI-ARIA |
| `@radix-ui/react-dropdown-menu` | `dependency` | `^2.1.6` | Primitiva de menú desplegable accesible |
| `@radix-ui/react-tabs` | `dependency` | `^1.1.3` | Primitiva de pestañas accesibles |
| `@radix-ui/react-tooltip` | `dependency` | `^1.1.8` | Primitiva de tooltip accesible |
| `tailwindcss` | `dependency` | `^4.0.0` | Motor de estilos utilitarios CSS v4 |
| `@tailwindcss/vite` | `devDependency` | `^4.0.0` | Compilador de Tailwind CSS integrado en Vite |
| `typescript` | `devDependency` | `^5.7.3` | Tipado estático estricto para toda la app |
| `vite` | `devDependency` | `^6.2.0` | Servidor de desarrollo HMR y empaquetador Rollup |
| `@vitejs/plugin-react` | `devDependency` | `^4.3.4` | Plugin de compilación Fast Refresh para React |
| `@tanstack/react-query-devtools` | `devDependency` | `^5.66.0` | Panel de depuración de caché en desarrollo |
| `vitest` | `devDependency` | `^3.0.5` | Entorno de pruebas unitarias ultrarrápido |
| `@testing-library/react` | `devDependency` | `^16.2.0` | Utilidades de prueba centradas en el usuario |
| `@testing-library/user-event` | `devDependency` | `^14.6.1` | Simulación accesible de eventos de usuario |
| `@testing-library/jest-dom` | `devDependency` | `^6.6.3` | Aserciones semánticas para el DOM |
| `@playwright/test` | `devDependency` | `^1.50.1` | Automatización de pruebas E2E multi-navegador |
| `eslint` | `devDependency` | `^9.20.0` | Linter estático de código JavaScript/TypeScript |
| `eslint-plugin-jsx-a11y` | `devDependency` | `^6.10.2` | Auditor de reglas de accesibilidad WAI-ARIA |
| `@axe-core/react` | `devDependency` | `^4.10.1` | Diagnósticos de accesibilidad en consola de desarrollo |
| `@axe-core/playwright` | `devDependency` | `^4.10.1` | Auditoría automatizada de accesibilidad en E2E |
| `prettier` | `devDependency` | `^3.5.1` | Formateo consistente de código |
| `prettier-plugin-tailwindcss` | `devDependency` | `^0.6.11` | Ordenamiento automático de clases utilitarias |
