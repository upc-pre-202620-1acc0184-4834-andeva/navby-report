# NAVBY: ESPECIFICACIÓN TÉCNICA GENERAL Y FUENTE DE VERDAD

<!-- prettier-ignore -->
> [!NOTE]
> ### Mapa de Documentación y Guía de Rutas Técnicas
>
> Este documento centraliza la especificación técnica general, la visión operativa del producto y el modelado algorítmico de **Navby**, actuando como el nodo enrutador principal y fuente de verdad técnica del repositorio. El desarrollo documental se estructura bajo una hoja de ruta progresiva:
>
> 1. **Definición General y Fuente de Verdad del Producto (Este Documento):**
>    * Definición técnica de Navby, arquitectura desacoplada en dos etapas, flujo de ejecución, capacidades del sistema, modelo de créditos y teoría de grafos aplicada: [docs/navby-documentation.md](navby-documentation.md)
>
> 2. **Arquitectura de Plataforma Backend (`docs/backend-documentation/`):**
>    * *Estado:* Consolidada y formalizada como fuente de verdad técnica oficial del backend.
>    * *Especificación general de plataforma:* [docs/backend-documentation/navby-platform-documentation.md](backend-documentation/navby-platform-documentation.md)
>    * *Catálogo y especificación de endpoints REST:* [docs/backend-documentation/navby-endpoints.md](backend-documentation/navby-endpoints.md)
>    * *Especificación táctica canónica y DDD:* [docs/backend-documentation/navby-backend-tactical-specification.md](backend-documentation/navby-backend-tactical-specification.md)
>    * *Esquema relacional y persistencia políglota:* [docs/backend-documentation/navby-database-schema.md](backend-documentation/navby-database-schema.md)
>    * *Integración y Adaptador ACL de FlightAPI:* [docs/backend-documentation/flight-api-documentation.md](backend-documentation/flight-api-documentation.md)
>    * *Catálogo detallado de Bounded Contexts:* [`docs/backend-documentation/extended-bounded-contexts-description/`](backend-documentation/extended-bounded-contexts-description/) ([IAM](backend-documentation/extended-bounded-contexts-description/bounded-context-iam.md), [Routing](backend-documentation/extended-bounded-contexts-description/bounded-context-routing.md), [Quotes](backend-documentation/extended-bounded-contexts-description/bounded-context-quotes.md), [Itineraries](backend-documentation/extended-bounded-contexts-description/bounded-context-itineraries.md), [Billing](backend-documentation/extended-bounded-contexts-description/bounded-context-billing.md) y [Shared Kernel](backend-documentation/extended-bounded-contexts-description/bounded-context-shared.md))
>
> 3. **Ecosistema de Frontend (`docs/frontend-documentation/`):**
>    * *Website público (Marketing):* [docs/frontend-documentation/navby-website-documentation.md](frontend-documentation/navby-website-documentation.md) (Astro 5, Tailwind CSS v4, GSAP 3, Lenis, Zod, Axe-core, Playwright, i18n nativo y accesibilidad WCAG 2.1 AA).
>    * *Webapp interactiva (Planificador):* [docs/frontend-documentation/navby-webapp-documentation.md](frontend-documentation/navby-webapp-documentation.md) (React 19, TypeScript, Vite 6, MapLibre GL 2D, deck.gl, TanStack Query, Zustand, Recharts, Sileo, Boneyard, i18n y accesibilidad WAI-ARIA/WCAG 2.1 AA).
>
> 4. **Datasets Canónicos y Malla Aeroportuaria (OpenFlights):**
>    * Datasets definitivos curados para producción (3,354 nodos aeroportuarios comerciales y 37,326 rutas dirigidas únicas): [`docs/backend-documentation/navby-datasets/`](backend-documentation/navby-datasets/)
>    * Especificación técnica del pipeline de datos, esquemas CSV y fases de depuración topológica: [docs/backend-documentation/navby-datasets/README.md](backend-documentation/navby-datasets/README.md)
>    * Análisis de preprocesamiento, métricas del grafo y conectividad: [`report/chapters/20-dataset-description/22-preprocessing-and-metrics.md`](../report/chapters/20-dataset-description/22-preprocessing-and-metrics.md)
>
> 5. **Memoria Académica Oficial (Complejidad Algorítmica 1ACC0184):**
>    * Rúbricas oficiales, competencias de razonamiento y ética y Caso de Estudio 9: [docs/project-statement.md](project-statement.md)
>    * Capítulos modulares del reporte: [`report/chapters/`](../report/chapters/)
>    * Estándar de tablas y figuras APA 7: [docs/tables-figures-apa-7-guidelines.md](tables-figures-apa-7-guidelines.md)
>    * Plantilla de reporte académico APA 7 y entorno contenerizado Docker: [docs/report-guidelines.md](report-guidelines.md) y [`../Makefile`](../Makefile)
>
> 6. **Contexto Comercial y Marketing de Producto (Referencia Externa Desacoplada):**
>    * Startup Overview de Andeva, slogan oficial (*«El mejor vuelo. Al mejor precio.»*), buyer personas, modelo pay-per-use (10 créditos diarios y paquetes prepagados) y directrices de marca: [docs/product-marketing.md](product-marketing.md) y [.agents/product-marketing.md](../.agents/product-marketing.md)
>
> ---
>
> *Nota de Alcance:* Este documento centraliza exclusivamente especificaciones de ingeniería, fundamentos matemáticos y arquitectura de sistemas. Todo requerimiento comercial reside formalmente en [docs/product-marketing.md](product-marketing.md).

## Definición Técnica del Sistema: Navby

**Navby** es una plataforma de software e infraestructura algorítmica diseñada para resolver el problema de planificación y optimización de rutas aéreas multicriterio sobre una red de transporte global modelada como un grafo dirigido y ponderado $G = (V, E, W)$, combinando la topología de la red con tarifas de mercado en tiempo real mediante una arquitectura desacoplada en dos etapas.

A diferencia de los buscadores tradicionales que fuerzan al usuario a elegir entre extremos aislados (el vuelo más barato con escalas extenuantes o el vuelo más rápido a precios prohibitivos), Navby evalúa conjuntamente **costo monetario, número de escalas y duración total de viaje**. El sistema integra estas tres dimensiones en un motor de optimización multicriterio en memoria que calcula la **frontera de Pareto** y aplica una función de utilidad compuesta para determinar y presentar **las alternativas de vuelo óptimas no dominadas**.

### Arquitectura Desacoplada en Dos Etapas (Two-Stage Pipeline)

Para garantizar viabilidad económica, latencias de respuesta en milisegundos y protección rigurosa del presupuesto de APIs externas, el sistema opera bajo una estricta separación de responsabilidades:

1. **Etapa 1: Escudo de Conectividad, Resolución Topológica y Modelado en Grafo ($0.00 Costo de API):**
   El backend mantiene en memoria RAM el grafo aeroportuario global compilado desde OpenFlights (**3,354 aeropuertos activos** y **37,326 rutas dirigidas únicas**). Antes de invocar cualquier servicio externo con costo:
   * **Validación de conexidad y cota de escalas:** Mediante búsqueda en anchura (BFS) en memoria RAM, el sistema comprueba al instante la conectividad comercial y determina el número mínimo de escalas ($k - 1$) para acotar el espacio de búsqueda de Pareto. Si los aeropuertos no tienen conexión viable, la consulta se descarta de inmediato a costo cero de API ($0.00 USD / 0 créditos).
   * **Resolución de metrópolis multiaeropuerto:** En ciudades con múltiples terminales (Londres, Nueva York, Tokio), el grafo resuelve el hub primario por grado de conectividad ($k$) u ofrece las terminales secundarias con base en la adyacencia de rutas.
   * **Cota teórica geodésica y trazado en mapa:** Calcula el camino mínimo referencial mediante A* sobre distancias ortodrómicas de Haversine, derivando la cota inferior de duración ($T_{\min}$) y proveyendo las coordenadas espaciales para el trazado inmediato del arco geodésico en el mapa cliente durante la carga.

2. **Etapa 2: Cotización de Mercado Selectiva y Motor Multicriterio en Tiempo Real:**
   Una vez validada la viabilidad topológica de la consulta:
   * **Consulta única hacia FlightAPI (2 créditos):** El backend ejecuta **una sola petición HTTPS** hacia el agregador oficial (**FlightAPI**, respaldado por Skyscanner), ya sea mediante `/onewaytrip` o `/roundtrip`. Esta llamada única extrae el universo completo de ofertas reales del mercado (vuelos directos, conexiones con 1 escala y conexiones con 2 escalas de múltiples aerolíneas) consumiendo exactamente **2 créditos de FlightAPI**.
   * **Caché distribuida en Redis 7 (TTL 30 min):** Si la misma ruta, fecha y cabina ya fue cotizada recientemente, el resultado se entrega desde Redis en $< 5\text{ ms}$ a **0 créditos de costo externo**.
   * **Motor de Optimización Multicriterio en Memoria:** El sistema recibe el array desordenado de ofertas de FlightAPI y ejecuta el algoritmo de optimización conjunta en Python: normaliza precio, tiempo y escalas, descarta opciones dominadas (frontera de Pareto) y clasifica las mejores combinaciones globales.
   * **Entrega accionable:** Retorna al usuario las recomendaciones óptimas estructuradas, con desglose de segmentos, escalas, duraciones exactas, coordenadas geodésicas y enlaces directos de compra (*deepLinks*) oficiales.

---

## Flujo Técnico de Ejecución del Sistema

El procesamiento de una consulta de vuelo sigue una secuencia determinista a través de las capas del sistema:

1. **Ingesta y Validación de Parámetros:**
   El controlador REST (`GET /api/v1/routes/plan`) valida los parámetros canónicos: aeropuertos origen y destino (códigos IATA de 3 letras), fechas ISO-8601, pasajeros tipificados (`adults`, `children`, `infants`), clase de cabina (`Economy`, `Premium_Economy`, `Business`, `First`) y estrategia de ponderación requerida.
2. **Validación Previa de Conectividad y Escalas con BFS:**
   Antes de consumir recursos de red o API externa, el motor ejecuta BFS en memoria RAM para verificar si origen y destino están conectados y calcular la cota de escalas mínimas. Si no existe conexión comercial registrada, la consulta se descarta inmediatamente sin consumo de créditos.
3. **Resolución de Referencia Topológica en RAM:**
   El motor de grafos ejecuta el cálculo geodésico con A*:
   * Determina la cota teórica de menor tiempo acumulado por Haversine ($T_{\min}$).
   * Prepara los vectores de coordenadas geográficas de los arcos ortodrómicos para la visualización en el mapa 2D.
4. **Verificación de Caché Fast-Path en Redis 7 (Cache-Aside):**
   Se genera la clave canónica `quote:{origin}:{dest}:{date}:{cabin}:{pax}` en Redis 7. Si existe en caché (*cache hit*), se entrega de forma inmediata (< 5 ms) a costo de 0 créditos de FlightAPI.
5. **Débito Transaccional y Petición Única a FlightAPI:**
   En caso de *cache miss*, el servicio debita atómicamente la cuota correspondiente (**5 créditos Navby por búsqueda**) de la bolsa de créditos del usuario mediante un script Lua en Redis. Posteriormente, despacha **una sola petición HTTPS** hacia FlightAPI (`/onewaytrip` o `/roundtrip`), consumiendo exactamente 2 créditos del plan de la plataforma.
6. **Ejecución del Motor de Optimización Multicriterio en Memoria:**
   El backend procesa la respuesta cruda de FlightAPI (que contiene decenas de alternativas de vuelo) y ejecuta el algoritmo multicriterio:
   * Evalúa conjuntamente la tarifa monetaria real, la duración exacta por tramo y el número de escalas comerciales.
   * Filtra las opciones no dominadas de la frontera de Pareto y aplica el puntaje de conveniencia global.
   * Selecciona las mejores recomendaciones integrales que balancean rapidez, precio y comodidad.
7. **Entrega de Itinerarios Accionables:**
   Se serializa la respuesta hacia el cliente con las mejores recomendaciones de vuelo, el desglose de escalas y aerolíneas operadoras, las coordenadas para el renderizado WebGL de arcos de vuelo en el frontend y los enlaces directos de compra (*deepLinks*).

---

## Módulos y Capacidades Técnicas del Sistema

* **Escudo Topológico y Grafo en RAM:** Singleton en el ciclo de vida de FastAPI (`lifespan`) que mantiene la red global de OpenFlights en memoria (~10 MB), aislando la ejecución de algoritmos de conectividad y geodésicos en Python 3.12+.
* **Adaptador ACL y Cotización de Mercado:** Módulo desacoplado en la Capa Anticorrupción que aísla el modelo de datos foráneo de FlightAPI, gestiona reintentos con *backoff* exponencial, Circuit Breaker y almacenamiento temporal en Redis 7.
* **Motor de Optimización Multicriterio:** Componente de dominio puro que procesa las opciones de vuelo de mercado, normalizando costo, tiempo y escalas para calcular la frontera de Pareto y extraer las recomendaciones óptimas.
* **Control Transaccional de Cuotas y Créditos:** Mecanismo en Redis mediante scripts Lua que aplica debitación atómica de cuota (**10 créditos diarios gratuitos** por usuario equivalentes a 2 búsquedas completas a razón de 5 créditos por consulta, renovados cada 24 horas, o paquetes prepagados adquiridos vía webhook de Mercado Pago) previo a cualquier invocación a la API externa.
* **Persistencia Transaccional y Transactional Outbox:** Repositorios desacoplados sobre PostgreSQL 16 con SQLAlchemy 2.0 asíncrono. Los eventos de dominio se registran atómicamente en la tabla `outbox_events` dentro de la misma transacción de negocio, garantizando consistencia eventual sin requerir brokers de mensajería externos pesados.
* **Motor Cartográfico WebGL 2D:** Renderizado cliente de alto rendimiento basado en MapLibre GL JS y deck.gl (`ArcLayer`), proyectando arcos geodésicos ortodrómicos calculados con la formulación de Haversine sobre Web Mercator plano 2D.

---

## Modelo de Monetización, Economía de Créditos y Catálogo de Paquetes

Navby opera bajo un modelo de consumo por uso (*Pay-per-use*) transparente y desacoplado, diseñado para alinear la economía del usuario con los costos computacionales y de APIs externas de la infraestructura:

### 1. Dinámica de Créditos y Equivalencias Técnicas

* **Consumo por Consulta:** Cada búsqueda integral de itinerario (ya sea Solo Ida o Ida y Vuelta) consume exactamente **5 créditos Navby**.
* **Financiamiento de API Externa:** En caso de *Cache Miss* en Redis, los 5 créditos Navby del usuario financian la invocación única a FlightAPI (la cual debita 2 créditos comerciales al plan de la plataforma) y el cómputo de la frontera de Pareto. En caso de *Cache Hit*, la respuesta se entrega en $< 5\text{ ms}$ desde Redis sin penalizar al usuario ni incurrir en costos externos.
* **Bolsa Diaria de Cortesía (`free_credits`):** Cada cuenta registrada recibe automáticamente **10 créditos diarios gratuitos** (equivalentes a 2 búsquedas completas por día), renovados cada 24 horas. Estos créditos no son acumulables y caducan al expirar el ciclo diario.

### 2. Catálogo Canónico de Paquetes Prepagados (`credit_packages`)

Para usuarios que requieren planificar viajes extensos, comparar múltiples destinos o realizar búsquedas frecuentes, Navby ofrece paquetes de recarga prepagados acumulables a través de **Mercado Pago Checkout Pro** (con soporte en moneda local PEN y divisa internacional USD):

| Código Canónico (`package_code`) | Denominación Comercial | Créditos Navby | Búsquedas Equivalentes | Tarifa Oficial (PEN) | Tarifa Oficial (USD) | Política de Caducidad y Consumo |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `pack_50` | Paquete Inicial / Escapada | 50 | 10 búsquedas | S/ 9.90 | $2.49 USD | Créditos comerciales perpetuos (`paid_credits`). Consumo posterior al agotamiento de la cuota diaria. |
| `pack_100` | Paquete Frecuente / Viajero | 100 | 20 búsquedas | S/ 16.90 | $4.49 USD | Créditos comerciales perpetuos (`paid_credits`). Paquete recomendado para planificación exhaustiva de vacaciones. |
| `pack_250` | Paquete Corporativo / Nómada | 250 | 50 búsquedas | S/ 34.90 | $8.99 USD | Créditos comerciales perpetuos (`paid_credits`). Diseñado para nómadas digitales y planificadores intensivos. |

### 3. Reglas de Negocio y Prelación de Saldo (Billing Bounded Context)

1. **Orden de Prelación Estricta:** El motor de débito atómico (`atomic_debit.lua` en Redis) descuenta prioritariamente los créditos de cortesía (`free_credits`). Solo cuando el saldo de cortesía llega a cero, comienza a debitar de los créditos adquiridos (`paid_credits`).
2. **Inmutabilidad y No Caducidad:** Los créditos adquiridos mediante paquetes prepagados (`paid_credits`) son **perpetuos**: nunca caducan, son acumulables entre recargas sucesivas y se asientan de forma auditable en el libro contable de PostgreSQL 16 (`credit_transactions`).
3. **Cero Comisiones sobre Pasajes:** Navby no infla las tarifas ni actúa como comisionista de venta de boletos. Toda la monetización del producto se basa en el valor analítico y computacional del motor multicriterio, enlazando directamente al usuario con el proveedor oficial mediante *deepLinks*.

---

## El Desafío Computacional y Económico de la Red Aérea

Para comprender el diseño de ingeniería de Navby, es fundamental dimensionar el doble reto del transporte aéreo:

1. **El reto computacional (Explosión Combinatoria):**
   La red aeroportuaria global contiene miles de terminales comerciales y decenas de miles de conexiones directas. En los principales centros de conexión (*hubs*), el elevado factor de ramificación generaría una explosión combinatoria inmanejable ($O(b^d)$) si se intentara explorar todas las combinaciones posibles a ciegas.
2. **El reto económico y de latencia (Costo de APIs de Mercado):**
   Cada llamada a una API comercial de vuelos en vivo implica latencias de red (1 a 3 segundos) y un costo financiero estricto por consulta (2 créditos por petición en FlightAPI). Consultar combinaciones inviables o disparar llamadas fragmentadas por tramo agotaría el saldo de la startup en cuestión de minutos y degradaría la experiencia del usuario.

**La Solución Arquitectónica de Navby: Desacoplamiento Topológico y Optimización Multicriterio**
1. **El Grafo en RAM protege el presupuesto ($0.00 Costo):** Comprueba conectividad y cota de escalas mínimas mediante BFS en memoria RAM, estableciendo la referencia física de vuelo sin consumir créditos de API externa.
2. **Una sola llamada a FlightAPI por búsqueda (2 créditos):** Se consulta el par origen-destino en una única petición HTTP (ya sea One-Way o Round-Trip), obteniendo todas las alternativas reales de mercado.
3. **El Motor Multicriterio agrega el valor diferencial:** Procesa en microsegundos el universo de opciones devuelto por la API externa, combinando costo, rapidez y escalas para entregar al usuario las recomendaciones óptimas sin abrumarlo con datos caóticos.

## Alcance del Proyecto

El alcance de Navby está delimitado para resolver integralmente el problema de la planificación y optimización inteligente de rutas aéreas sobre grafos a gran escala y bajo los estándares de ingeniería de software para plataformas de alta fidelidad, manteniendo fronteras operativas claras y justificadas.

### 1. Dentro del Alcance (In-Scope)

#### A. Ámbito Algorítmico y Teoría de Grafos

El sistema modela la red aérea mundial como un grafo dirigido y ponderado $G = (V, E, W)$ construido sobre el dataset depurado de OpenFlights, integrando exactamente **3,354 aeropuertos comerciales activos ($|V|$)** y **37,326 rutas comerciales dirigidas únicas ($|E|$)**. Las distancias ortodrómicas se calculan mediante la **fórmula de Haversine** ($R \approx 6,371\text{ km}$), modelando el tiempo de vuelo estimado como $w_t(u, v) = \frac{d_H(u, v)}{v_{\text{crucero}}} + t_{\text{maniobra}}$ ($v_{\text{crucero}} = 800\text{ km/h}$, $t_{\text{maniobra}} = 30\text{ min}$) y penalización por conexión de $t_{\text{conexión}} = 60\text{ min}$.

Para evitar la sobreingeniería en el sistema operativo y mantener una estricta eficiencia computacional, el repertorio de algoritmos se divide formalmente en dos ámbitos de ejecución:

##### 1. Algoritmos del Producto (Runtime / Motor de Producción de Navby)
Conjunto pragmático y de alto rendimiento que se ejecuta en memoria RAM dentro del ciclo de vida de la aplicación para resolver las consultas del usuario:
* **A\* (Búsqueda Heurística Admisible con Haversine):** Algoritmo de camino geodésico óptimo sobre el grafo con pesos Haversine ($O(E \log V)$). Guiado por la distancia ortodrómica directa al destino ($h(u) = d_H(u, \text{dest}) / v_{\text{crucero}}$), converge velozmente hacia el destino, derivando la cota inferior teórica de duración física ($T_{\min}$) para la normalización del motor multicriterio y proveyendo la trayectoria ortodrómica inmediata para el trazado visual en el mapa 2D durante el estado de carga.
* **BFS (Búsqueda por Niveles / Mínimas Escalas):** Identifica la ruta con el mínimo número de escalas comerciales posibles ($k - 1$ saltos) en $O(V + E)$ sobre el grafo no ponderado, sirviendo como criterio de referencia para viajeros que priorizan minimizar transbordos y como cota máxima admisible para el diagrama de Pareto.
* **Motor Multicriterio (Frontera de Pareto y Podio Tridimensional):** Algoritmo de optimización en memoria ($O(N \log N)$) que procesa las alternativas reales de mercado devueltas por FlightAPI, descartando opciones dominadas y clasificando deterministamente las tres mejores recomendaciones globales (Top 1, Top 2, Top 3) mediante distancia euclidiana normalizada al punto ideal utópico $(0, 0, 0)$.

##### 2. Algoritmos de Benchmarking Asintótico y Calibración (Telemetría en Vivo en API)
Técnicas que operan como patrones de calibración analítica, validación de cotas teóricas y telemetría en tiempo real:
* **Dijkstra Clásico (Línea Base Omnidireccional en Telemetría):** Búsqueda de caminos mínimos sin heurística ($h(u) = 0$, $O((V + E) \log V)$) ejecutada en paralelo como patrón de calibración (*ground truth*) dentro de la telemetría en tiempo real (`dijkstra_nodes_expanded`, `dijkstra_execution_time_ms`, `efficiency_gain_pct`) para cuantificar empíricamente la ganancia de eficiencia de A*.
* **BFS de Benchmarking (Línea Base de Escalas Topológicas en Telemetría):** Ejecutado en tiempo real en la telemetría de enrutamiento (`bfs_stops_count`, `bfs_execution_time_ms`) para calcular la cota inferior teórica de escalas y contrastarla con el camino óptimo geodésico de A*.

#### B. Ámbito Funcional y Especificaciones de Producto

Define las capacidades operativas, requerimientos funcionales y reglas de negocio del sistema expuestos hacia los clientes consumidores (Website, Webapp y controladores API REST), delimitando los contratos de entrada, procesamiento y persistencia:

* **Planificación y parametrización de itinerarios:** Soporte para tipos de trayecto de solo ida (`ONE_WAY`) e ida y vuelta (`ROUND_TRIP`), validación de fechas de salida y retorno en formato estándar ISO-8601 (`YYYY-MM-DD`), selección de clase de cabina tipificada (`ECONOMY`, `PREMIUM_ECONOMY`, `BUSINESS`, `FIRST`) y desglose cuantitativo de pasajeros segmentado en adultos (`adults`), niños de 2 a 11 años (`children`) e infantes menores de 2 años (`infants`).
* **Búsqueda y resolución canónica de aeropuertos:** Servicio de autocompletado por nombre de ciudad o terminal aeroportuaria, con soporte integral para «Todos los aeropuertos» por defecto en metrópolis multiaeropuerto o selección opcional de una terminal específica, operando estrictamente sobre códigos canónicos IATA de 3 letras.
* **Cotización en tiempo real y optimización multicriterio:** Despacho de una única petición HTTPS hacia FlightAPI (`/onewaytrip` o `/roundtrip`, consumiendo 2 créditos de la API externa), extracción del universo de ofertas de mercado y procesamiento en memoria mediante la frontera de Pareto y la función de utilidad compuesta (normalización conjunta de precio monetario, tiempo de vuelo y escalas), retornando las alternativas óptimas no dominadas junto con sus enlaces de reserva oficial (`deepLinks`).
* **Persistencia y gestión de itinerarios:** Almacenamiento transaccional en PostgreSQL asociado al identificador de usuario (`user_id`), permitiendo operaciones CRUD (guardar, consultar, comparar métricas y eliminar itinerarios cotizados).
* **Control de cuotas y bolsa de créditos transaccional:** Mecanismo de control de consumo y protección contra abusos orquestado atómicamente en Redis 7:
  * *Cuota diaria gratuita:* Asignación de 10 créditos no acumulables restablecidos cada 24 horas (00:00 UTC), equivalentes a 2 cotizaciones completas (5 créditos Navby por búsqueda nueva con *cache miss*).
  * *Bolsa de créditos prepagados:* Saldo persistente sin fecha de caducidad, acreditado de forma atómica mediante webhooks criptográficos de pasarela de pago (Mercado Pago Checkout Pro) en paquetes de 50, 100 y 250 créditos.
* **Gestión de identidad y autenticación:** Control de acceso mediante credenciales locales con verificación de correo electrónico por código OTP de un solo uso (vía API de Resend) y autenticación federada Single Sign-On mediante Google Identity Services (OAuth 2.0 / OIDC) con emisión de tokens de sesión JWT.
* **Proyección cartográfica WebGL 2D:** Renderizado cliente de alto rendimiento sobre mapa plano en proyección Web Mercator (MapLibre GL JS y deck.gl `ArcLayer`), visualizando arcos geodésicos ortodrómicos calculados con la formulación de Haversine y marcadores interactivos para aeropuertos de origen, escalas intermedias y destino.

#### C. Ámbito de Ingeniería y Arquitectura (Visión General)

Sintetiza la demarcación de responsabilidades técnicas, desacoplamiento estructural y estándares de diseño aplicados entre los componentes de la plataforma:

* **Demarcación de responsabilidades:**
  * **Website (Portal Web Público y Marketing):** Sitio web estático de alto rendimiento construido con **Astro 5** bajo arquitectura de islas, estilizado con **Tailwind CSS v4**, coreografía de animaciones con **GSAP 3**, desplazamiento cinemático suave con **Lenis**, enrutamiento estático multilingüe (`/es`, `/en`) y cumplimiento estricto de accesibilidad **WCAG 2.1 AA**, desplegado en Edge CDN de Vercel ($0 USD/mes), formalizado en [docs/frontend-documentation/navby-website-documentation.md](frontend-documentation/navby-website-documentation.md).
  * **Webapp (Cliente Interactivo del Viajero):** SPA interactiva construida con **React 19**, **TypeScript**, **Vite 6**, motor cartográfico plano 2D **MapLibre GL JS** y arcos ortodrómicos WebGL con **deck.gl** (`ArcLayer`), sincronización de servidor con **TanStack Query**, estado global con **Zustand**, visualización de benchmarking con **Recharts**, notificaciones con **Sileo**, esqueletos adaptativos con **Boneyard**, accesibilidad conforme a **WAI-ARIA / WCAG 2.1 AA** e internalización reactiva con `i18next`, formalizada en [docs/frontend-documentation/navby-webapp-documentation.md](frontend-documentation/navby-webapp-documentation.md).
  * **Platform (Backend Core y Motor de Grafos):** Monolito modular en **Python 3.12+** con **FastAPI**, **uv**, **PostgreSQL 16**, **Redis 7** y **Caddy 2**, gobernado por Clean Architecture, Tactical DDD-lite, CQRS-lite y Transactional Outbox, que alberga el grafo mundial en memoria RAM (~10 MB), formalizado en [docs/backend-documentation/navby-platform-documentation.md](backend-documentation/navby-platform-documentation.md) y [`docs/backend-documentation/`](backend-documentation/).
* **Organización documental:** El detalle técnico de cada ámbito se especifica progresivamente siguiendo la [Hoja de Ruta y Mapa de Navegación Documental](#hoja-de-ruta-y-mapa-de-navegación-documental).

---

### 2. Fuera del Alcance (Out-of-Scope / Exclusiones Justificadas)

Establece los límites operativos y funcionales del sistema mediante la exclusión explícita de requerimientos y características que no forman parte de la arquitectura técnica del producto:

1. **Consultas de vuelos multiciudad / multidestino (Multi Trip API):**
   * *Justificación:* El soporte de vuelos multidestino (`GET /multitrip`) queda formalmente excluido. La API externa impone una restricción rígida de 3 a 5 tramos obligatorios, exige una tarifa de 5 créditos por consulta y no permite la optimización de caminos mínimos por grafos de Navby. El alcance se concentra estrictamente en trayectos de **Solo Ida (One-way)** e **Ida y Vuelta (Round-trip)**.
2. **Módulo abierto de exploración de conectividad aeroportuaria:**
   * *Justificación:* Esta funcionalidad fue descartada del sistema por no aportar a la optimización directa de rutas de vuelo. El algoritmo DFS y las comprobaciones de conectividad se preservan exclusivamente como mecanismos internos de validación topológica (prevención de ciclos $u \neq v$ y aciclicidad de itinerarios), sin exponer un visor libre de conectividad independiente.
3. **Renderizado de mapas en globo terráqueo esférico 3D:**
   * *Justificación:* La visualización geográfica se restringe intencionalmente a un mapa plano 2D interactivo. El globo 3D introduce sobrecoste de cómputo GPU/WebGL innecesario en el navegador del usuario y dificulta la lectura visual simultánea de trayectos y escalas en comparación con una proyección plana clara.
4. **Cobros periódicos recurrentes y suscripciones automáticas:**
   * *Justificación:* El modelo financiero se basa exclusivamente en compras puntuales prepagadas de paquetes de créditos de uso (*pay-per-use*) a través de Mercado Pago Checkout Pro. No se contemplan cargos automáticos mensuales recurrentes ni almacenamiento de datos sensibles de tarjetas bancarias.
5. **Gestión de capacidad física de asientos y despacho operativo de aerolíneas:**
   * *Justificación:* El modelo de dominio de Navby se sitúa estrictamente desde la perspectiva del **usuario/viajero** (descubrimiento de rutas y optimización de tarifas de mercado). Navby no opera como un sistema interno de despacho operativo de aerolíneas ni como un GDS/CRS encargado del inventario físico de asientos en cabina ni de la asignación de plazas por aeronave.
6. **Procesamiento de pagos de pasajes y emisión de boletos (PNR):**
   * *Justificación:* Navby no opera como agencia de viajes intermediaria ni emite billetes aéreos (*Passenger Name Record*). La transacción final de compra del boleto se delega a las aerolíneas u OTAs oficiales mediante los enlaces de reserva directa (*deepLinks*) provistos por FlightAPI.
7. **Radar y telemetría de vuelos en tiempo real (ADS-B):**
   * *Justificación:* El producto no realiza rastreo satelital ni geolocalización de aeronaves en vuelo, dado que opera sobre mallas de rutas comerciales programadas y tarifas de mercado.
8. **Cálculo de tarifas y horarios dinámicos dentro del grafo estático:**
   * *Justificación:* El dataset de OpenFlights es estático y no contiene horarios ni precios en vivo. La separación arquitectónica es explícita: el grafo resuelve la topología óptima y FlightAPI resuelve el precio y la duración real en minutos.
9. **Transporte y logística de carga aérea:**
   * *Justificación:* La plataforma está orientada exclusivamente a la aviación comercial de pasajeros y equipaje personal estándar.

## Fuentes de Datos e Integraciones Externas

Navby interactúa con un conjunto acotado y desacoplado de servicios externos para nutrir la topología de red, obtener tarifas de mercado, procesar cobros y gestionar la identidad:

| Fuente / Servicio | Uso y Alcance en Navby | Naturaleza Técnica | Protocolo / Integración |
| :--- | :--- | :--- | :--- |
| **OpenFlights** | Catálogo mundial de aeropuertos (nodos) y rutas comerciales (aristas) para construir el grafo aéreo. | Dataset estático offline (depurado y versionado). | Ingesta local desde `docs/backend-documentation/navby-datasets/`. |
| **FlightAPI** | Consulta de tarifas reales, duraciones de vuelo y enlaces de reserva (*deepLinks*) para los mejores vuelos recomendados. | API externa SaaS de pago (2 créditos/request). | HTTPS REST JSON hacia `api.flightapi.io` vía Adaptador ACL (con soporte de Mock en desarrollo). |
| **Mercado Pago** | Pasarela de pago para la compra de paquetes de créditos de uso (modelo prepago, sin suscripciones). | API externa SaaS de pagos y cobros electrónicos. | Checkout Pro / Webhooks HTTPS con firma criptográfica (Sandbox completo en desarrollo). |
| **Resend** | Envíos de correos transaccionales: verificación OTP, restablecimiento de contraseña y recibos de compra. | API externa SaaS de mensajería transaccional. | HTTPS REST (puerto 443) con SDK oficial `resend-py` (fallback a log de consola en local). |
| **Google Identity Services** | Autenticación y registro federado mediante cuentas de Google (OAuth 2.0 / OIDC). | Servicio de identidad federada (IdP). | SDK de frontend + validación de `id_token` JWT en backend con `google-auth`. |
| **CARTO Basemaps** | Teselas cartográficas vectoriales y capa base para el mapa plano 2D (Positron / Dark Matter). | Proveedor público de estilos cartográficos para WebGL. | HTTPS TileJSON consumido directamente por MapLibre GL JS en cliente (sin clave ni costo de API). |

---

### OpenFlights: Datasets del Grafo Aéreo y Limpieza de Datos

La topología de rutas de Navby se sustenta en el repositorio abierto de **OpenFlights** ([openflights.org](https://openflights.org/data)). Tras el proceso de depuración matemática y sanitización, los conjuntos de datos limpios y definitivos están centralizados en [`docs/backend-documentation/navby-datasets/`](backend-documentation/navby-datasets/).

#### 1. Fases del Proceso de Depuración y Validación Matemática
Conforme a la memoria de ingeniería y el análisis de consistencia topológica (`report/chapters/20-dataset-description/22-preprocessing-and-metrics.md`), los datos crudos fueron sometidos a un proceso de sanitización de 4 fases:

1. **Fase 1 (Tipo de instalación aérea):** De las 12,668 instalaciones iniciales en `airports-extended.dat`, se retuvieron exclusivamente terminales aéreas comerciales (`type = "airport"`), descartando estaciones de tren (`station`), puertos marítimos (`port`) e infraestructuras militares o helipuertos.
2. **Fase 2 (Integridad de código IATA):** Se filtraron los registros para conservar únicamente aquellos con identificador IATA de 3 letras mayúsculas válido (descartando nulos `\N`), consolidando exactamente **6,472 aeropuertos comerciales**.
3. **Fase 3 (Validación de aristas activas):** Sobre las 67,663 rutas de `routes.dat`, se verificó la integridad referencial exigiendo que tanto el aeropuerto de origen como el de destino existan en el conjunto de aeropuertos comerciales válidos, reteniendo **67,305 rutas operativas**.
4. **Fase 4 (Poda de vértices aislados):** Se purgaron 3,118 aeródromos sin vuelos comerciales ($k = 0$), resultando en un grafo conexo de **3,354 aeropuertos activos ($|V|$)** y **37,326 aristas dirigidas únicas ($|E|$)**, garantizando la representatividad y conectividad física de la red comercial global de pasajeros.

#### 2. Catálogo de Datasets Utilizados (Verificados y Limpios)

| Dataset en `docs/backend-documentation/navby-datasets/` | Registros | Campos Clave | Rol en Navby |
| :--- | :---: | :--- | :--- |
| **`airports.csv`** | **3,354** | `airport_id`, `name`, `city`, `country`, **`iata`**, `icao`, **`latitude`**, **`longitude`**, `altitude`, `timezone` | **Vértices del Grafo ($|V|$):** Nodos activos para ruteo algorítmico. |
| **`routes_unique.csv`** | **37,326** | **`source_airport`**, **`destination_airport`**, **`distance_km`**, `operating_airlines`, `min_stops` | **Aristas del Grafo ($|E|$):** Conexiones dirigidas únicas con distancia Haversine precalculada. |
| **`routes.csv`** | **67,305** | `airline`, `source_airport`, `destination_airport`, `stops`, `equipment` | **Multigrafo:** Malla de rutas considerando múltiples aerolíneas concurrentes. |
| **`airports_commercial_all.csv`** | **6,472** | Metadatos completos de aeropuertos comerciales con IATA. | Catálogo maestro de aeropuertos para búsqueda y autocompletado en UI. |
| **`airlines.csv`** | **6,162** | `airline_id`, `name`, `alias`, `iata`, `icao`, `callsign`, `country`, `active` | Enriquecimiento con nombres y códigos de aerolíneas operadoras. |
| **`countries.csv`** | **261** | `name`, `iso_code`, `dafif_code` | Enriquecimiento contextual de países. |
| **`planes.csv`** | **246** | `name`, `iata_code`, `icao_code` | Perfiles de aeronaves asociadas al equipamiento de vuelo. |

---

### FlightAPI: Cotización de Tarifas en Tiempo Real

Para transformar las mejores rutas candidatas del grafo en ofertas de compra accionables, Navby se integra con **FlightAPI** ([flightapi.io](https://www.flightapi.io)).

* **Especificación técnica del adaptador ACL:** La arquitectura detallada de integración, contratos de datos, resiliencia y gestión de cuotas de FlightAPI se encuentra formalizada en [docs/backend-documentation/flight-api-documentation.md](backend-documentation/flight-api-documentation.md).
* **Endpoints consumidos:**
  * `GET /onewaytrip`: Cotización para viajes de solo ida (**2 créditos/request**).
  * `GET /roundtrip`: Cotización para viajes de ida y vuelta (**2 créditos/request**).
* **Parámetros clave:** Código IATA origen/destino, fechas ISO `YYYY-MM-DD`, pasajeros (`adults`, `children`, `infants`), cabina (`Economy`, `Premium_Economy`, `Business`, `First`) y moneda (`USD`, `PEN`).
* **Datos extraídos:** Precio consolidado, duración en minutos, aerolínea operadora, logotipo y enlace de reserva directo (*deepLink*).

### Seguridad, Caché y Uso Responsable de APIs Externas

Las llamadas a Flight API **nunca se ejecutan desde el navegador**: son orquestadas exclusivamente por el backend mediante la Capa Anticorrupción (ACL):

* **Custodia de secretos:** La clave de API reside únicamente en variables de entorno del servidor (`FLIGHT_API_KEY`).
* **Caché en memoria (Redis):** Toda cotización se almacena con un TTL de 30 minutos. Búsquedas concurrentes o idénticas se resuelven a costo de $0$ créditos y latencia mínima.
* **Pre-filtro algorítmico a costo cero ($0.00):** El motor de grafos en RAM valida la conectividad y cota de escalas mediante BFS antes de cualquier llamada externa. Si no existe conectividad comercial factible, la consulta se rechaza de inmediato consumiendo 0 créditos de FlightAPI, protegiendo el presupuesto operativo de la plataforma.
* **Presupuesto transaccional de créditos:** El backend descuenta créditos antes de emitir la llamada externa, de modo que si el saldo es insuficiente, la petición se rechaza de forma preventiva.
* **Degradación controlada (Circuit Breaker):** Ante fallos del proveedor o cuota general agotada (HTTP 402/429), el sistema entrega la última tarifa en caché indicando su antigüedad al usuario.

### CARTO Basemaps: Teselas Cartográficas y Estilos WebGL

Para renderizar la proyección cartográfica Web Mercator 2D en el cliente sobre la cual **deck.gl** traza los arcos geodésicos ortodrómicos de vuelo, Navby consume las teselas públicas de **CARTO Basemaps**:

* **Estilo base:** `https://basemaps.cartocdn.com/gl/positron-gl-style/style.json` (variante clara de alto contraste) y `dark-matter-gl-style` (variante oscura opcional).
* **Integración:** Consumo directo desde el cliente en **MapLibre GL JS** mediante especificación TileJSON / Vector Tiles estándar.
* **Viabilidad operativa:** No requiere credenciales de API ni autenticación para entornos de código abierto o educativos, eliminando costos y cuotas de infraestructura cartográfica en el cliente.

### Aislamiento y Resiliencia en Entorno de Desarrollo Local (Modo Sandbox y Mocks)

Para permitir el desarrollo continuo y pruebas integrales del sistema sin incurrir en consumo prematuro de créditos de API ni bloqueos por dependencias de red externas, la arquitectura incorpora modos de aislamiento:

1. **FlightAPI Mock Adapter:** En entorno local (`ENVIRONMENT=development` o en ausencia de `FLIGHT_API_KEY`), el adaptador ACL conmuta a un generador determinista de ofertas de mercado basado en fixtures JSON, proveyendo precios, aerolíneas y segmentos simulados para ejercitar el motor multicriterio y la interfaz gráfica a costo cero ($0.00).
2. **Mercado Pago Sandbox:** Configuración de credenciales de prueba (`TEST-ACCESS-TOKEN`) que habilita el flujo completo de Checkout Pro y emisión de webhooks locales con tarjetas de prueba ficticias en moneda PEN y USD.
3. **Resend Console Fallback:** Ante la ausencia de un dominio corporativo validado en DNS durante etapas tempranas de desarrollo, el servicio transaccional registra el código OTP directamente en el flujo de salida estándar del backend (`logger.info`), permitiendo completar el flujo de registro y verificación localmente sin bloqueos de entrega.

## Decisiones de Diseño Clave

### 1. Los pesos del grafo son estimados (Haversine), no horarios reales

El dataset base de OpenFlights (`routes.dat`) **no incluye duraciones exactas ni horarios en tiempo real** de los vuelos — registra exclusivamente la existencia de la conexión comercial directa y sus escalas intermedias. En consecuencia:

* El motor de rutas calcula el peso temporal de cada arista dirigida $(u, v)$ a partir de la **distancia ortodrómica Haversine** $d_H(u, v)$ derivada de las coordenadas geográficas $(\phi, \lambda)$ de los aeropuertos, modelando el tiempo de vuelo estimado como:
  $$w_t(u, v) = \frac{d_H(u, v)}{v_{\text{crucero}}} + t_{\text{maniobra}}$$
  donde $v_{\text{crucero}} = 800\text{ km/h}$ representa la velocidad crucero promedio comercial y $t_{\text{maniobra}} = 30\text{ min}$ modela las maniobras de ascenso, aproximación y rodaje. Para itinerarios con conexiones, cada transbordo añade una penalización fija $t_{\text{conexión}} = 60\text{ min}$.
* Los **tiempos reales de viaje** (duración exacta por tramo en minutos) y las **tarifas de mercado en vivo** solo se determinan al cotizar mediante **FlightAPI** (extraídos de los campos `legs.duration` y `segments`).
* Esta delimitación arquitectónica es transparente y fundamental para el reporte: el grafo en memoria resuelve la **topología óptima y poda el espacio de búsqueda**, mientras que FlightAPI **valida la disponibilidad y concreta el precio real** de las mejores alternativas.

### 2. Búsqueda por ciudades o aeropuertos y resolución interna por códigos IATA

El usuario interactúa en la interfaz buscando por nombre de ciudad o terminal aeroportuaria con soporte de autocompletado inteligente. Para metrópolis que disponen de más de un aeropuerto comercial (por ejemplo, Tokio con `HND` y `NRT`, Londres con `LHR`, `LGW` y `STN`, Nueva York con `JFK`, `EWR` y `LGA`, o Buenos Aires con `EZE` y `AEP`), Navby implementa un esquema de resolución flexible y centrado en la conveniencia del pasajero:

* **Soporte nativo de «Todos los aeropuertos» en metrópolis multiaeropuerto (comportamiento por defecto):**
  Al seleccionar una ciudad con múltiples aeropuertos, el sistema activa por defecto la opción integral «Todos los aeropuertos» (`[x] Todos los aeropuertos`). De este modo, la exploración del grafo y la posterior cotización no quedan sesgadas artificialmente a una sola terminal, permitiendo evaluar el universo completo de combinaciones entre las terminales de la metrópoli para descubrir las mejores tarifas y duraciones de Pareto.
* **Selección opcional de un aeropuerto en concreto:**
  Si el viajero tiene una preferencia particular —por conveniencia geográfica, cercanía al centro urbano, facilidad de transporte terrestre o fidelidad a una aerolínea específica—, la interfaz le permite desmarcar la opción global y fijar una terminal individual concreta (por ejemplo, volar exclusivamente desde o hacia Tokio-Haneda `HND`).
* **Resolución directa 1:1 en ciudades mono-aeropuerto:**
  En ciudades con una única infraestructura aeroportuaria comercial (que abarca aproximadamente el 90% de los nodos de la red global, como Lima con `LIM` o Cusco con `CUZ`), la correspondencia con su código IATA es directa, automática e inmediata sin requerir que el usuario memorice siglas aeronáuticas.
* **Eliminación del concepto obsoleto de «aeropuerto principal»:**
  Se erradica por completo la heurística arbitraria de forzar un «aeropuerto principal» según el grado de conectividad nodal ($k$). Dicho criterio resultaba artificial y perjudicial, ya que excluía sistemáticamente terminales secundarias con gran volumen de rutas comerciales o mejores precios, limitando injustificadamente las opciones del usuario.
* **Canonicidad de códigos IATA en el motor de grafos y FlightAPI:**
  Toda la ejecución algorítmica interna en memoria RAM (A*, BFS, Dijkstra) y las peticiones a la API externa de vuelos (FlightAPI) se ejecutan de manera estricta y canónica sobre los **códigos IATA de 3 letras**, garantizando la consistencia relacional y matemática en todas las capas del sistema.

### 3. Buscador inteligente por ciudades y autosuficiencia del dataset aeroportuario

Para garantizar una experiencia de búsqueda rápida, familiar e intuitiva —alineada con los estándares de la aviación comercial global—, el sistema adopta una arquitectura de búsqueda centrada estrictamente en **ciudades de servicio**:

* **Autosuficiencia del Dataset Aeroportuario (Principio Anti-Sobreingeniería de Base de Datos):**
  Navby **no implementa una base de datos relacional de países y ciudades en PostgreSQL**. Almacenar un nomenclátor global masivo generaría un sobrecosto severo de almacenamiento, mantenimiento y tiempo de respuesta. En su lugar, el dataset canónico de OpenFlights consolidado en Navby (`docs/backend-documentation/navby-datasets/airports.csv`) contiene **3,354 nodos aeroportuarios comerciales**, donde cada registro incluye de forma intrínseca su ciudad de servicio (`city`), país (`country`), código IATA de 3 letras (`iata`), nombre oficial (`name`) y coordenadas geográficas ortodrómicas (`latitude`, `longitude`). Esta información se indexa en memoria en el backend y se exporta como un catálogo estático ligero en el cliente (~180 KB), permitiendo resolver búsquedas directas por ciudad o aeropuerto en $< 1\text{ ms}$ a costo cero de red y base de datos.

* **Flujo de Selección Centrado en Ciudades:**
  1. **Búsqueda Directa por Ciudad:** El usuario ingresa el nombre de la metrópoli de origen o destino (por ejemplo, "Lima", "Madrid", "Tokio" o "Nueva York"). El autocompletado en el frontend filtra instantáneamente sobre el catálogo en memoria.
  2. **Resolución Automática en Ciudades Mono-Aeropuerto:** Para ciudades que cuentan con una única terminal comercial (el 90% de los casos globales, como Lima con `LIM`), el sistema asocia de forma transparente el código IATA correspondiente sin requerir que el usuario memorice siglas aeronáuticas.
  3. **Gestión Inteligente en Ciudades Multiaeropuerto:** En metrópolis con múltiples terminales comerciales (por ejemplo, Tokio con `HND` y `NRT`, Nueva York con `JFK`, `EWR` y `LGA`, o Londres con `LHR`, `LGW` y `STN`), el sistema ofrece la opción integral por defecto:
     * `[x] Tokio (Todos los aeropuertos - HND, NRT)` *(por defecto)*
     * Si el pasajero desea forzar una terminal específica, dispone de un selector secundario opcional para marcar exclusivamente el aeropuerto de su preferencia (por ejemplo, solo `HND`).
  4. **Erradicación de Fricciones Innecesarias:** El flujo elimina por completo la geolocalización forzada por GPS, clics arbitrarios en coordenadas remotas del mapa y búsquedas artificiales de monumentos o poblados sin pista aérea comercial.

### 4. Algoritmos y técnicas: clasificación por ámbito de ejecución

Para garantizar un rendimiento óptimo en producción y responder con rigor al modelado formal del problema de rutas aéreas sin incurrir en sobreingeniería en la plataforma, las técnicas algorítmicas se dividen estrictamente en dos esferas de ejecución:

#### A. Algoritmos del Producto (Runtime / Motor de Producción)

Operan en memoria RAM durante el ciclo de vida de la aplicación para resolver las búsquedas del usuario de forma rápida, determinista y económica:

1. **A\* (Camino Geodésico Óptimo y Trazado Visual de Carga):**
   * *Propósito:* Calcular la ruta física más veloz sobre aristas ponderadas por tiempo estimado Haversine ($w_t \ge 0$).
   * *Rol de negocio y UX:* A* acelera la convergencia guiado por la heurística admisible $h(u) = d_H(u, \text{destino}) / v_{\text{crucero}}$. Cumple una doble función esencial: deriva la cota teórica inferior de duración física ($T_{\min}$) para la normalización del motor multicriterio y genera de inmediato los vectores ortodrómicos que el mapa proyecta durante el estado de carga (mientras FlightAPI cotiza en vivo).
   * *Complejidad:* $O(E \log V)$ en tiempo, $O(V)$ en memoria.
2. **BFS (Búsqueda por Niveles para Mínimas Escalas):**
   * *Propósito:* Identificar la ruta con el menor número de escalas posibles ($k - 1$ conexiones) sobre el grafo no ponderado.
   * *Rol de negocio:* Ofrece al usuario la referencia de la alternativa directa o con el mínimo de conexiones físicas posibles, priorizando la simplicidad del trayecto frente a la duración continua.
   * *Complejidad:* $O(V + E)$ en tiempo, $O(V)$ en memoria.
3. **Motor Multicriterio (Frontera de Pareto y Podio Tridimensional):**
   * *Propósito:* Optimización conjunta multi-objetivo sobre las tarifas y duraciones reales obtenidas de FlightAPI.
   * *Rol de negocio:* El núcleo de recomendación de Navby, que clasifica las alternativas de mercado en frentes de Pareto según precio, duración y escalas, descartando opciones dominadas y seleccionando el podio determinista de las 3 mejores recomendaciones globales (Top 1, Top 2, Top 3) mediante distancia euclidiana normalizada al punto ideal utópico $(0, 0, 0)$.
   * *Complejidad:* $O(N \log N)$ en tiempo, $O(N)$ en memoria (donde $N$ es el número de itinerarios cotizados por la API externa).

#### B. Algoritmos de Benchmarking Asintótico y Calibración (Telemetría en Vivo y Laboratorio Offline)

Técnicas que operan como patrones de calibración analítica, validación de cotas teóricas y telemetría en tiempo real:

1. **Dijkstra Clásico (Línea Base Omnidireccional en Telemetría):**
   * *Propósito:* Búsqueda de caminos mínimos sin heurística mediante cola de prioridad sobre aristas ponderadas Haversine ($w_t \ge 0$).
   * *Uso en Navby:* Ejecutado en paralelo dentro de la telemetría en tiempo real (`dijkstra_nodes_expanded`, `dijkstra_execution_time_ms`, `efficiency_gain_pct`) como patrón de calibración (*ground truth*) para cuantificar empíricamente el ahorro de nodos explorados por A* en redes espaciales y certificar la ganancia de eficiencia.
   * *Complejidad:* $O((V + E) \log V)$ en tiempo, $O(V)$ en memoria.
2. **BFS de Benchmarking (Línea Base de Escalas Topológicas):**
   * *Propósito:* Cómputo de la cota inferior teórica de escalas sobre el grafo no ponderado.
   * *Uso en Navby:* Ejecutado en la telemetría de enrutamiento (`bfs_stops_count`, `bfs_execution_time_ms`) para contrastar el número de transbordos de la ruta geodésica de A* con la alternativa puramente topológica.
#### Resumen y Mapeo Comparativo de Técnicas

| Técnica Algorítmica | Propósito y Caso de Uso en Navby | Complejidad Temporal | Complejidad Espacial | Ámbito de Ejecución |
| :--- | :--- | :---: | :---: | :--- |
| **A\*** | Búsqueda voraz con Haversine y trazado visual instantáneo de carga en mapa. | $O(E \log V)$ | $O(V)$ | **Producción (Runtime)** |
| **BFS** | Ruta de menor número de escalas comerciales ($k-1$) y cota para Pareto. | $O(V + E)$ | $O(V)$ | **Producción (Runtime)** |
| **Motor Multicriterio (Pareto)** | Optimización conjunta de precio, duración y escalas (Top 1, 2, 3). | $O(N \log N)$ | $O(N)$ | **Producción (Runtime)** |
| **Dijkstra Clásico** | Línea base omnidireccional en telemetría para medir ganancia de A*. | $O((V + E) \log V)$ | $O(V)$ | **Telemetría (Runtime)** |
| **BFS Benchmarking** | Cota inferior de escalas en telemetría de enrutamiento. | $O(V + E)$ | $O(V)$ | **Telemetría (Runtime)** |

#### Coreografía Visual e Interactiva en el Mapa

```text
  1. Usuario selecciona Ciudad Origen ("Lima") y Ciudad Destino ("Tokio")
                         │
                         ▼
  2. La cámara del mapa ejecuta fitBounds() instantáneamente
     (Encuadre suave y continuo entre Sudamérica y Asia)
                         │
                         ▼
  3. MIENTRAS CARGA (1 a 2 segundos de latencia de FlightAPI):
     ├──> A* calcula en < 2 ms la trayectoria física óptima en el globo terráqueo.
          Feedback visual instantáneo que elimina la percepción de espera vacía.
                         │
                         ▼
  4. LLEGAN LAS OFERTAS DE MERCADO (Pareto entrega el Podio Top 1, Top 2, Top 3):
     ├──> La línea temporal de A* se desvanece suavemente (fade-out).
     └──> El mapa dibuja las 3 RUTAS COMERCIALES REALES con sus respectivas escalas:
          * Top 1: LIM ──> MEX (escala 2h) ──> NRT
          * Top 2: LIM ──> LAX (escala 3h) ──> HND
          * Top 3: LIM ──> AMS (escala 1h 45m) ──> NRT
                         │
                         ▼
  5. INTERACCIÓN BIDIRECCIONAL CON EL PODIO:
     * Al pasar el cursor (hover) o pulsar sobre la tarjeta del Top 1 en el panel lateral,
     * Al seleccionar el Top 2, se ilumina la ruta alternativa por Los Ángeles.
```

### 5. Resumen Consolidado del Stack Tecnológico

Navby se estructura técnica y operativamente en componentes complementarios bajo un riguroso criterio anti-sobreingeniería, coordinando su evolución según la hoja de ruta documental:

| Component | Tipo de Aplicación | Stack Principal | Despliegue / Hosting | Enfoque de Ingeniería | Estado Documental |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Website** | Portal Web Público (SSG) | Astro 5, Tailwind CSS v4, GSAP 3, Lenis, Zod, Axe-core, Playwright | Vercel (Edge CDN Global) | Arquitectura de islas, cero JS innecesario, animaciones cinemáticas, i18n nativo y WCAG 2.1 AA. | Consolidado en [docs/frontend-documentation/navby-website-documentation.md](frontend-documentation/navby-website-documentation.md). |
| **Webapp** | Cliente Interactivo (SPA) | React 19, TypeScript, Vite 6, MapLibre GL 2D, deck.gl, CARTO Basemaps, TanStack Query, Zustand | Vercel (SPA Estática con reescritura) | Arquitectura por capas, consumo de APIs, renderizado WebGL 2D, Sileo, Boneyard e i18n reactivo. | Consolidado en [docs/frontend-documentation/navby-webapp-documentation.md](frontend-documentation/navby-webapp-documentation.md). |
| **Platform** | Backend Core & Grafos | Python 3.12+, FastAPI, uv, PostgreSQL 16, Redis 7, SQLAlchemy 2.0 (async), Caddy 2 | Azure VM (Standard_B2s, 2 vCPU / 4 GB) | Monolito modular con grafo en RAM (~10 MB), Clean Architecture, CQRS-lite, Outbox en Postgres sin Kafka. | Consolidado en [docs/backend-documentation/navby-platform-documentation.md](backend-documentation/navby-platform-documentation.md). |
| **Datasets** | Pipeline & Topología | OpenFlights (CSV depurado, Haversine) | Almacenamiento local versionado | Sanitización matemática en 5 fases, con 3,354 nodos comerciales activos y 37,326 rutas dirigidas únicas. | Canónico y consolidado en [docs/backend-documentation/navby-datasets/README.md](backend-documentation/navby-datasets/README.md). |

---

## Hoja de Ruta y Mapa de Navegación Documental

El repositorio organiza el desarrollo técnico y documental conforme a las responsabilidades de ingeniería acordadas:

1. **Definición General y Fuente de Verdad Técnica de Navby:**
   * Archivo: [docs/navby-documentation.md](navby-documentation.md)
   * Centraliza qué es el producto, cómo funciona la arquitectura de dos etapas, el flujo de procesamiento determinista, la economía de créditos y el catálogo algorítmico sobre grafos.

2. **Arquitectura y Plataforma Backend (`docs/backend-documentation/`):**
   * *Visión General y Plataforma:* [docs/backend-documentation/navby-platform-documentation.md](backend-documentation/navby-platform-documentation.md) (monolito modular, FastAPI, uv, PostgreSQL 16, Redis 7, Caddy 2 y catálogo de Bounded Contexts).
   * *Catálogo y Especificación de Endpoints RESTful:* [docs/backend-documentation/navby-endpoints.md](backend-documentation/navby-endpoints.md) (especificación exhaustiva de todos los endpoints perimetrales con contratos request/response, schemas, códigos de error y telemetría de benchmarking).
   * *Especificación Táctica Canónica:* [docs/backend-documentation/navby-backend-tactical-specification.md](backend-documentation/navby-backend-tactical-specification.md) (los 10 mandamientos arquitectónicos, Shared Kernel, Value Objects transversales y taxonomía de errores).
   * *Esquema Relacional y Persistencia:* [docs/backend-documentation/navby-database-schema.md](backend-documentation/navby-database-schema.md) (esquema DDL PostgreSQL 16, Redis 7, Transactional Outbox y aislamiento físico sin foreign keys cruzadas).
   * *Integración con FlightAPI:* [docs/backend-documentation/flight-api-documentation.md](backend-documentation/flight-api-documentation.md) (adaptador ACL, endpoints `/onewaytrip` y `/roundtrip`, Circuit Breaker y consumo de créditos).
   * *Especificaciones Detalladas por Bounded Context:* Directorio [`docs/backend-documentation/extended-bounded-contexts-description/`](backend-documentation/extended-bounded-contexts-description/) con diccionarios de clases, casos de uso CQRS-lite y contratos:
     * [Bounded Context IAM](backend-documentation/extended-bounded-contexts-description/bounded-context-iam.md): Identidad, autenticación local y federada Google OAuth, JWT y rotación de tokens.
     * [Bounded Context Routing](backend-documentation/extended-bounded-contexts-description/bounded-context-routing.md): Topología de red, grafo en memoria RAM, algoritmos A*, BFS, Dijkstra y distancias Haversine.
     * [Bounded Context Quotes](backend-documentation/extended-bounded-contexts-description/bounded-context-quotes.md): Inteligencia tarifaria, integración con FlightAPI y optimización multicriterio de Pareto.
     * [Bounded Context Itineraries](backend-documentation/extended-bounded-contexts-description/bounded-context-itineraries.md): Planificación, guardado, versionado y custodia de itinerarios por usuario.
     * [Bounded Context Billing](backend-documentation/extended-bounded-contexts-description/bounded-context-billing.md): Billetera de créditos, cuota diaria, paquetes prepagados y webhooks de Mercado Pago.
     * [Bounded Context Shared Kernel](backend-documentation/extended-bounded-contexts-description/bounded-context-shared.md): Primitivas de dominio, monad `Result[T, E]`, agregados base y tipos transversales.

3. **Ecosistema de Frontend (`docs/frontend-documentation/`):**
   * *Website público (Landing / Marketing):* [docs/frontend-documentation/navby-website-documentation.md](frontend-documentation/navby-website-documentation.md): Especificación técnica de herramientas y frameworks del portal web público en Astro 5 bajo arquitectura de islas, Tailwind CSS v4, coreografía de animaciones con GSAP 3, desplazamiento cinemático suave con Lenis, enrutamiento estático multilingüe (`/es`, `/en`) y auditoría automatizada de accesibilidad WCAG 2.1 AA con Playwright y `axe-core`.
   * *Webapp interactiva (Aplicación SPA):* [docs/frontend-documentation/navby-webapp-documentation.md](frontend-documentation/navby-webapp-documentation.md): Especificación técnica de herramientas y frameworks del cliente interactivo SPA en React 19, TypeScript y Vite 6, motor de mapa plano 2D MapLibre GL con teselas vectoriales de CARTO, arcos geodésicos acelerados por WebGL con deck.gl (`ArcLayer`), sincronización de servidor con TanStack Query, estado global con Zustand, telemetría y benchmarking con Recharts, notificaciones con Sileo, esqueletos de carga adaptativos con Boneyard, accesibilidad WAI-ARIA/WCAG 2.1 AA y motor reactivo de internacionalización `i18next`.

4. **Malla Aeroportuaria y Datasets Canónicos (`docs/backend-documentation/navby-datasets/`):**
   * Especificación de datos y pipeline: [docs/backend-documentation/navby-datasets/README.md](backend-documentation/navby-datasets/README.md)
   * Catálogo de datasets: `airports.csv` (3,354 nodos comerciales con grado $k \ge 1$), `routes_unique.csv` (37,326 aristas dirigidas únicas) y `airlines.csv` (catálogo complementario de 6,162 aerolíneas).
   * Análisis topológico y métricas: [`report/chapters/20-dataset-description/22-preprocessing-and-metrics.md`](../report/chapters/20-dataset-description/22-preprocessing-and-metrics.md)

5. **Memoria Académica Oficial y Guías de Redacción (Complejidad Algorítmica 1ACC0184):**
   * Caso de Estudio 9 y rúbricas: [docs/project-statement.md](project-statement.md)
   * Capítulos modulares del reporte: [`report/chapters/`](../report/chapters/)
   * Estándar de tablas y figuras APA 7: [docs/tables-figures-apa-7-guidelines.md](tables-figures-apa-7-guidelines.md)
   * Plantilla de reporte académico APA 7 y entorno contenerizado Docker: [docs/report-guidelines.md](report-guidelines.md) y automatización con [`../Makefile`](../Makefile).

6. **Marketing de Producto y Contexto Comercial:**
   * Visión de startup Andeva, slogan oficial (*«El mejor vuelo. Al mejor precio.»*), posicionamiento, buyer personas y modelo comercial pay-per-use: [docs/product-marketing.md](product-marketing.md) y [.agents/product-marketing.md](../.agents/product-marketing.md).
