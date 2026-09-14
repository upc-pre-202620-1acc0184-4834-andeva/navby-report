# Navby Webapp — Arquitectura Detallada del Frontend

> Alcance: este documento define **stack, framework, arquitectura, estructura y convenciones** de la aplicación principal de Navby (la webapp con mapa interactivo). Es la fuente de verdad para cualquier agente de IA o desarrollador que trabaje en este frontend.
>
> - Producto: ver [navby-documentation.md](navby-documentation.md)
> - Website (landing): ver [navby-website-architecture.md](navby-website-architecture.md)

---

## 1. Ecosistema y Stack Tecnológico General (Anti-sobreingeniería)

Dentro del ecosistema desacoplado de Navby, la **Webapp (`navby-webapp`)** opera como el cliente interactivo principal del viajero:

* **Stack tecnológico:** **React 19** + **TypeScript** + **Vite 6** + **Tailwind CSS v4** + **MapLibre GL JS (4.x)** + **deck.gl (9.x)** + **TanStack Query v5** + **Zustand 5** + **boneyard** + **Sileo** + **shadcn/ui**.
* **Propósito, layout y experiencia de usuario:** SPA (*Single Page Application*) interactiva centrada en la planificación de vuelo y visualización cartográfica:
  * **Sidebar a la izquierda:** Panel lateral persistente y colapsable que alberga el planificador completo (origen, destino, calendario de fechas, desglose de pasajeros, cabina y despliegue del Top 3 de cotizaciones).
  * **Interactividad bidireccional mapa $\leftrightarrow$ sidebar:** La interacción es completamente reactiva. Si el usuario hace clic sobre un nodo o ciudad en el mapa (ej. Lima), la sidebar se actualiza automáticamente asignándolo como origen (o destino si el origen ya fue fijado) y centrando la cámara.
  * **Buscador flotante en el mapa:** Barra de búsqueda flotante (*floating search bar*) ubicada sobre el mapa para localizar y enfocar **ciudades** rápidamente mediante autocompletado y geocodificación.
  * **Mapa plano 2D con arcos WebGL:** MapLibre GL JS provee el lienzo cartográfico en proyección Mercator web (open-source, sin cuotas ni vendor lock-in de Mapbox); deck.gl (`GreatCircleLayer` y `ArcLayer`) renderiza los arcos ortodrómicos de vuelo con aceleración GPU fluida.
  * **Animaciones de carga con boneyard:** Estados de carga elegantes mediante *skeletons* durante el cómputo de rutas y la consulta de tarifas externas.
  * **Notificaciones con Sileo:** Sistema de notificaciones toast reactivas para confirmar acciones (itinerario guardado, enlaces copiados, débitos de créditos o alertas de conectividad).
  * **Gestión de estado:** TanStack Query para caché cliente de cotizaciones y Zustand para estado UI local sin *boilerplate*.
* **Criterio anti-sobreingeniería:** Se descartan globos terráqueos esféricos en 3D (CesiumJS / Globe.gl) por consumo innecesario de GPU/batería y distorsión visual; se descarta SSR (la app es una herramienta de productividad tras autenticación o de uso interactivo libre); se descarta Redux Toolkit por exceso de ceremonia; y se descarta Axios en favor de un cliente `fetch` nativo tipado y conciso.
* **Despliegue:** **Vercel** como SPA estática con reescritura de rutas (*rewrites* hacia `index.html`) y coste operativo de $0.

---

## 2. Naturaleza de la Aplicación

Navby Webapp es una **SPA (Single Page Application)** de alta interactividad centrada en un mapa:

- El usuario navega un **mapa plano** interactivo (experiencia inspirada en Google Earth/Google Maps: sidebar a la izquierda, tarjetas flotantes, buscador de ciudades flotante sobre el mapa, zoom fluido). **No** se usa globo terráqueo 3D: la visualización es un mapa 2D (proyección web Mercator).
- **Sidebar a la izquierda:** Panel principal persistente y colapsable con el formulario de búsqueda (origen, destino, fechas, pasajeros, cabina) y el despliegue ordenado de las 3 mejores opciones cotizadas.
- **Interactividad bidireccional mapa $\leftrightarrow$ sidebar:** Si el usuario hace clic en el mapa sobre un nodo/ciudad (ej. Lima), la sidebar actualiza automáticamente el campo de origen (o destino si el origen ya está establecido) y ajusta la cámara del mapa.
- **Buscador flotante de ciudades:** Barra de búsqueda tipo command-palette flotante sobre el mapa para buscar rápidamente cualquier ciudad global con autocompletado y geocodificación instantánea.
- **Animaciones de carga con boneyard:** Skeletons de carga elegantes y fluidos mientras el motor calcula las rutas o consulta FlightAPI.
- **Notificaciones con Sileo:** Sistema de notificaciones toast para confirmar acciones críticas (itinerario guardado, enlaces de reserva copiados, alertas de créditos o fallos de red).
- La app consulta al backend (Navby Platform) las rutas óptimas (tiempo, escalas) y los 3 mejores precios (datos de Flight API, servidos por el backend).
- El usuario guarda itinerarios planificados (requiere autenticación).

**No hay SSR/SEO como requisito** (es una aplicación tras login o de uso libre, no contenido indexable) → se descarta Next.js y se usa un build SPA puro con Vite desplegado en **Vercel**.

---

## 3. Experiencia de Usuario e Interacción Visual (Frontend UX)

### 3.1 Planificación Inmersiva sobre Mapa Plano 2D
* **Descarte de Globo 3D:** Se adopta estrictamente una proyección plana 2D (Web Mercator) mediante MapLibre GL JS, eliminando distorsiones polares y cargas pesadas de librerías tridimensionales.
* **Renderizado WebGL de Arcos:** Empleo de deck.gl (`ArcLayer`) superpuesto a MapLibre para renderizar rutas de vuelo con gradientes de color que diferencian escalas y conexiones en tiempo real sin degradar los 60 FPS.
* **Sidebar Izquierda Principal:** Panel lateral colapsable donde el usuario define origen, destino, fechas de vuelo y pasajeros, y visualiza las 3 mejores opciones de itinerario cotizadas con precios reales y enlaces de reserva.
* **Interactividad Bidireccional Mapa $\leftrightarrow$ Sidebar:** Si el usuario hace clic sobre un nodo aeroportuario o ciudad en el mapa (por ejemplo, Lima), la sidebar abierta asigna automáticamente dicha ubicación como origen (o como destino si el origen ya está fijado) y centra la cámara sobre el punto.
* **Buscador Flotante de Ciudades:** Barra de búsqueda flotante tipo paleta de comandos posicionada en la parte superior del mapa, permitiendo buscar cualquier ciudad global por nombre o código IATA con autocompletado instantáneo y vuelo de cámara automático.
* **Skeletons de Carga con Boneyard:** Mientras el motor algorítmico resuelve los caminos o se consulta la cotización externa en FlightAPI, la interfaz despliega skeletons adaptativos y fluidos construidos con boneyard, evitando saltos bruscos de diseño (CLS).
* **Notificaciones Toast con Sileo:** Sistema de alertas reactivas y no bloqueantes para informar sobre itinerarios guardados, enlaces de compra copiados al portapapeles o recordatorios de saldo de créditos.

---

## 4. Stack Tecnológico (Decisiones Finales)

| Capa | Tecnología | Versión objetivo | Justificación |
| :--- | :--- | :--- | :--- |
| Lenguaje | **TypeScript** | 5.x (strict) | Seguridad de tipos de extremo a extremo (DTOs del backend, estado, props). |
| Build tool | **Vite** | 6.x | Dev server instantáneo (HMR), build con Rollup, code splitting nativo. |
| Framework UI | **React** | 19.x | Ecosistema de mapas y componentes más maduro; hiring/curva mínima. |
| Routing | **React Router** | v7 | Estándar del ecosistema; búsquedas representadas en URL (search params compartibles). |
| Estado servidor | **TanStack Query** | v5 | Caché, revalidación y estados async de búsquedas de rutas/precios e itinerarios. Evita re-implementar fetch/loading/error. |
| Estado UI (cliente) | **Zustand** | 5.x | Estado de sesión de mapa y UI (origen/destino seleccionados, panel activo). Ligero, sin boilerplate. |
| Mapa | **MapLibre GL JS** + **react-map-gl** | MapLibre 4.x | Motor de mapas open-source, sin vendor lock-in ni costos por tile; render de **mapa plano** (Mercator web) con zoom/pan fluido. `react-map-gl` lo envuelve con API declarativa React. |
| Capas de rutas | **deck.gl** | 9.x | Renderizado WebGL de alto rendimiento: `ArcLayer`/`GreatCircleLayer` para dibujar arcos de vuelo sobre el mapa, miles de vértices sin lag. Integración nativa con react-map-gl (`MapboxOverlay`). |
| Estilos | **Tailwind CSS** | v4 | Utility-first; diseño de tarjetas flotantes/sidebar sin CSS a medida verboso. |
| Componentes | **shadcn/ui** (sobre Radix UI) | latest | Primitivas accesibles (Dialog, Popover, Calendar, Command) base para tarjetas flotantes, sidebar y picker de fechas/pasajeros. Se copian al repo (no son dependencia opaca). |
| Animaciones de carga | **boneyard** | latest | Skeletons de carga elegantes y fluidos durante la resolución de rutas y cotizaciones. |
| Notificaciones | **Sileo** | latest | Sistema de notificaciones toast reactivo y accesible para alertas de usuario. |
| Calendario | **react-day-picker** (vía shadcn Calendar) | 9.x | Rangos ida/vuelta accesibles y personalizables. |
| Formularios/validación | **react-hook-form** + **zod** | latest | Validación del formulario de búsqueda (fechas coherentes, pasajeros ≥ 1, origen ≠ destino). |
| HTTP client | **fetch** nativo envuelto en un `ApiClient` | — | Sin Axios: un wrapper propio con tipos, manejo de errores e inyección de auth token. |
| Despliegue | **Vercel** | SPA | Hosting estático automatizado con rewrites (`vercel.json`) hacia `index.html`. |
| Tests unitarios | **Vitest** + **Testing Library** | latest | Runner nativo de Vite; tests de componentes y hooks. |
| Tests E2E | **Playwright** | latest | Flujos críticos: búsqueda de ruta, visualización de resultados, guardar itinerario. |
| Calidad | **ESLint** (flat config) + **Prettier** | latest | Lint + formato consistente; `typescript-eslint` en modo strict. |

### Decisiones descartadas (y por qué)

| Opción descartada | Motivo del descarte |
| :--- | :--- |
| Gráficos de benchmarks en UI (Recharts) | Las curvas de complejidad algorítmica se ejecutan mediante scripts de backend (`benchmarks/`) para alimentar el informe académico; la webapp de usuario final se mantiene como producto limpio para viajeros sin herramientas de benchmarking invasivas. |
| Next.js / Remix | La webapp no necesita SSR ni SEO; añade complejidad de servidor sin beneficio. (El SEO vive en el Website con Astro.) |
| Mapbox GL | Licencia propietaria y costos por uso; MapLibre es el fork open-source compatible. |
| CesiumJS / Globe.gl (globo 3D) | El producto usa **mapa plano** (decisión de diseño), no globo terráqueo; el 3D añade peso sin aportar valor a rutas aéreas. |
| Redux Toolkit | Excesivo para este dominio: el estado servidor lo gestiona TanStack Query y la UI local con Zustand basta. |
| Axios | `fetch` nativo + wrapper propio es suficiente y reduce dependencias. |

---

## 5. Arquitectura por Capas

La webapp sigue una arquitectura por capas con **dependencias hacia adentro** (la UI nunca habla directo con `fetch`; el dominio nunca importa de React):

```
┌────────────────────────────────────────────────────┐
│ Presentation    (componentes React, mapa, layouts) │
├────────────────────────────────────────────────────┤
│ Application     (hooks, stores Zustand, queries)   │
├────────────────────────────────────────────────────┤
│ Domain          (tipos/entidades, lógica de neg.)  │
├────────────────────────────────────────────────────┤
│ Infrastructure  (ApiClient, DTOs, adaptadores)     │
└────────────────────────────────────────────────────┘
```

### Responsabilidades por capa

- **Presentation:** componentes puros de UI (presentational) y contenedores de features. Renderizan mapa, sidebar, tarjetas flotantes. **No contienen lógica de fetch ni reglas de negocio.**
- **Application:** hooks de features (ej. `useFlightSearch`), stores Zustand (estado del mapa y UI), queries/mutations TanStack Query. Orquesta.
- **Domain:** entidades TypeScript (`Airport`, `FlightRoute`, `Itinerary`, `Passengers`), value objects y reglas puras (ej. normalización de criterios de orden: por tiempo, escalas o precio). Cero imports de React/librerías de UI.
- **Infrastructure:** `ApiClient` (fetch tipado), DTOs del contrato con Navby Platform y **mappers DTO → entidad de dominio** (capa anticorrupción ligera para que cambios del backend no rompan la UI).

### Regla de oro de estado

| Tipo de estado | Dónde vive | Ejemplos |
| :--- | :--- | :--- |
| Datos del servidor | **TanStack Query cache** | Aeropuertos, rutas calculadas, precios (top 3), itinerarios guardados |
| Estado de UI/mapa | **Zustand** | Origen/destino seleccionado, ruta activa en el mapa, panel abierto, modo de vista |
| Estado de formulario | **react-hook-form** (local) | Fechas, contadores de pasajeros |
| Estado compartible por URL | **URL search params** (React Router) | `?from=LIM&to=CUZ&date=...` para búsquedas compartibles |

**Relación estado ↔ costo de la API externa:** cada cotización de precios le cuesta créditos al backend (2 por request a Flight API). Por eso:

* Query keys compuestas por criterio exacto (`['prices', from, to, date, pax]`) con **`staleTime` agresivo** en cotizaciones → buscar lo mismo dos veces no re-consulta al backend.
* Datos casi estáticos (catálogo de aeropuertos/nodos del grafo) con `staleTime` muy alto (días).

---

## 6. Estructura de Carpetas (Feature-based)

```
navby-webapp/
├── index.html
├── vite.config.ts
├── package.json
├── tsconfig.json                 # strict: true
├── src/
│   ├── main.tsx                  # bootstrap: QueryClient, Router, auth provider
│   ├── App.tsx
│   ├── core/                     # transversal a la app
│   │   ├── api/
│   │   │   ├── api-client.ts     # fetch tipado + errores + auth header
│   │   │   └── dto/              # contratos del backend (DTOs)
│   │   ├── config/               # env, constantes (VITE_API_URL, etc.)
│   │   ├── router/               # definición de rutas (React Router v7)
│   │   └── providers/            # QueryClientProvider, AuthProvider, Theme
│   ├── shared/                   # reutilizable entre features
│   │   ├── components/ui/        # shadcn/ui (button, calendar, dialog...)
│   │   ├── hooks/
│   │   ├── lib/                  # utils puros (date, format, geo)
│   │   └── types/
│   ├── domain/                   # entidades y lógica pura de negocio
│   │   ├── airport.ts
│   │   ├── flight-route.ts
│   │   ├── itinerary.ts
│   │   └── passengers.ts
│   ├── features/                 # un módulo por capacidad del producto
│   │   ├── map/                  # mapa interactivo (corazón visual)
│   │   │   ├── components/       #   MapCanvas, RouteArcsLayer, AirportMarkers
│   │   │   ├── hooks/            #   useMapCamera, useMapSelection
│   │   │   └── store/            #   map-store.ts (Zustand)
│   │   ├── flight-search/        # búsqueda y planificación
│   │   │   ├── components/       #   SearchSidebar, DateRangeCard, PassengersCard,
│   │   │   │                     #   RouteResults (comparación tiempo/escalas/precio)
│   │   │   ├── hooks/            #   useFlightSearch, useBestPrices
│   │   │   └── api/              #   queries del feature (TanStack Query)
│   │   ├── itineraries/          # vuelos planificados guardados
│   │   │   ├── components/       #   ItineraryList, ItineraryCard
│   │   │   ├── hooks/            #   useItineraries (queries + mutations)
│   │   │   └── api/
│   │   └── explore/              # feature secundario: "¿a dónde puedo volar?"
│   │       ├── components/
│   │       └── hooks/
│   ├── auth/                     # (si aplica aquí) guards, sesión
│   ├── layouts/                  # AppLayout (sidebar + mapa full-bleed + floating cards)
│   ├── pages/                    # componentes página por ruta
│   └── assets/
└── tests/
    ├── setup.ts
    └── e2e/                      # Playwright
```

### Convenciones

- Componentes: `PascalCase.tsx`. Hooks: `useXxx.ts`. Stores: `xxx-store.ts`.
- Un componente por archivo; componentes de más de ~150 líneas se dividen (presentational vs container).
- Imports con alias: `@/core`, `@/shared`, `@/domain`, `@/features/*` (configurar en `tsconfig` + Vite `resolve.alias`).
- Todo DTO cruza a entidad de dominio en la frontera de `api/` (nada de filtrar DTOs crudos a componentes).

---

## 7. Arquitectura del Mapa (Módulo Crítico)

### 6.1 Stack de renderizado

```
┌──────────────────────────────────────────────────────────┐
│  deck.gl overlays (ArcLayer / ScatterplotLayer / Icon)   │  ← arcos de rutas, marcadores
├──────────────────────────────────────────────────────────┤
│  react-map-gl  <Map>  (wrapper React declarativo)        │
├──────────────────────────────────────────────────────────┤
│  MapLibre GL JS  (motor: tiles vectoriales, mapa plano)  │
└──────────────────────────────────────────────────────────┘
```

- **Mapa plano (proyección web Mercator)** fijo: no se usa proyección globo. El look "Google Earth" se logra con el glassmorphism de tarjetas flotantes, sidebar y animaciones de cámara (flyTo) al seleccionar ciudades, no con 3D.
- **Arcos de vuelo:** cada ruta calculada se dibuja con `ArcLayer` (origen→destino por tramo/escala). La ruta activa (hover/seleccionada) se resalta (color/grosor) y el resto se atenúa.
- **Tiles:** proveedor de tiles vectoriales de estilo libre (definir en `core/config`; evitar dependencia pagada en desarrollo).

### 6.2 Patrones de interacción

- **Selección origen/destino:** dos fuentes sincronizadas: (a) click sobre marcador/aeropuerto en el mapa; (b) buscador en sidebar (`Command` de shadcn con autocompletado). Ambas escriben en el mismo store Zustand → una sola fuente de verdad.
- **Tarjetas flotantes (floating cards):** paneles posicionados (no modales bloqueantes) implementados con Tailwind + shadcn `Card`/`Popover`: resultados de ruta, detalle de precios, resumen de pasajeros.
- **Sidebar:** columnas colapsables (búsqueda, resultados, itinerarios), patrón Google Earth.

### 6.3 Rendimiento del mapa

- Aeropuertos en dos niveles de detalle: clúster/liga a nivel zoom bajo (ScatterplotLayer agregado), marcadores individuales al acercar.
- Datos estáticos del grafo (aeropuertos) cacheados con TanStack Query + `staleTime` alto.
- Capas deck.gl memoizadas (`useMemo` en `layers`); nunca recrear arrays de datos por render.

---

## 8. Flujo de Datos Principal (Happy Path)

```
Usuario selecciona origen/destino/fechas/pasajeros (sidebar o mapa)
  → react-hook-form valida (zod): origen≠destino, fechas coherentes, pasajeros≥1
  → useFlightSearch dispara query a Platform: GET /routes (motor de grafos)
      → respuesta: candidatas con tiempo total y nº de escalas
  → useBestPrices dispara query a Platform: GET /prices (top 3, datos Flight API)
  → TanStack Query cachea ambos; UI compone RouteResults
  → Zustand publica ruta activa → mapa dibuja arcos y resalta la elegida
  → Usuario guarda itinerario → mutation POST /itineraries → invalidate de la lista
```

Reglas:

- Las llamadas a precios **solo** se disparan cuando hay ruta válida seleccionada (reduce consultas y costo de la API; el rate limit real lo impone Platform).
- La webapp **nunca** habla con Flight API directamente ni conoce su clave: todo pasa por Platform.
- El autocompletado de ciudades/aeropuertos usa **debounce** (~250–300 ms) y, si el listado es largo, **virtualización** de la lista desplegable.
- Nota de honestidad de datos: los tiempos/escalas que muestra el motor de rutas son **estimados** (Haversine sobre OpenFlights); los tiempos **reales** llegan con la cotización (Flight API). La UI debe distinguir ambos (ver "Decisiones de Diseño Clave" en [navby-documentation.md](../navby-documentation.md)).

---

## 9. Seguridad (Frontend)

- Comunicación exclusiva con Navby Platform vía HTTPS; base URL por `VITE_API_URL` (env por entorno).
- Token de sesión (si hay login) en memoria/`httpOnly cookie` según defina Platform; **nunca** en código ni en `localStorage` si se usa cookie-based auth.
- Ninguna clave de terceros (Flight API) en el bundle. `import.meta.env` solo con variables públicas `VITE_*` no sensibles.
- Sanitizado de cualquier HTML renderizado (React escapa por defecto; prohibido `dangerouslySetInnerHTML` salvo justificación).

---

## 10. Testing

| Nivel | Herramienta | Qué cubre |
| :--- | :--- | :--- |
| Unitario | Vitest + Testing Library | Lógica de dominio (ordenamiento de candidatos), hooks, stores, componentes puros |
| Integración | Testing Library + MSW (opcional) | Features completos con API mockeada |
| E2E | Playwright | Flujo crítico: buscar ruta → ver 3 precios → guardar itinerario |

Estructura espejo: `Component.test.tsx` junto al componente; E2E en `tests/e2e/`.

---

## 11. Build, Calidad y Despliegue en Vercel

- **Scripts npm:** `dev`, `build`, `preview`, `test`, `test:e2e`, `lint`, `format`.
- **Code splitting:** carga diferida (`React.lazy`) del feature `explore` y de rutas secundarias; el chunk del mapa se carga en la página principal.
- **Despliegue:** compilación estática SPA (`vite build` → `dist/`) en **Vercel** con reglas de reescritura (`vercel.json`) hacia `index.html` ($0 USD/mes). CI con lint + tests antes de publicar.
- **Variables de entorno:** `VITE_API_URL` (URL de la API en Azure VM). Un `.env.example` documentado en el repo.

---

## 12. Referencias Rápidas para IAs/Devs

- Producto y features: [navby-documentation.md](../navby-documentation.md)
- Landing pública: [navby-website-architecture.md](navby-website-architecture.md)
- Backend Core / Platform: [navby-platform-architecture.md](../backend-documentation/navby-platform-architecture.md)
