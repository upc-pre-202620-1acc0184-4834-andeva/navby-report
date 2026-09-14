# ANDEVA: STARTUP PROFILE

<!-- prettier-ignore -->
> [!NOTE]
> ### Mapa de Documentación y Guía de Rutas
>
> Este documento centraliza la visión de producto, features de negocio y perfil de startup de **Navby**. Para evitar duplicaciones y dispersión de diseño, actúa como el nodo enrutador central hacia las fuentes de verdad especializadas:
>
> 1. **Consultas de Base de Datos y Persistencia:**
>    * Contexto funcional del producto: [navby-documentation.md](navby-documentation.md)
>    * Esquema relacional DDL (PostgreSQL, tablas, constraints, índices): [backend-documentation/navby-database-schema.md](backend-documentation/navby-database-schema.md)
>    * Aislamiento físico inter-contexto (sin FKs físicas cruzadas) y Transactional Outbox: [backend-documentation/navby-tactical-ddd-guide.md](backend-documentation/navby-tactical-ddd-guide.md)
>    * Diagramas relacionales PlantUML: [`report/assets/diagram-sources/database-diagrams/`](../report/assets/diagram-sources/database-diagrams/)
>
> 2. **Consultas de Bounded Contexts y Diseño Táctico DDD:**
>    * Rúbrica y especificación de capas (Domain, Interface, Application, Infrastructure): [project-statement.md](project-statement.md) (Sección Móviles)
>    * Arquitectura maestra, bounded contexts e infraestructura cloud: [backend-documentation/navby-platform-architecture.md](backend-documentation/navby-platform-architecture.md)
>    * Esquema de persistencia del contexto: [backend-documentation/navby-database-schema.md](backend-documentation/navby-database-schema.md)
>    * Directrices tácticas canónicas (10 Mandamientos, `Result[T]`, Inmutabilidad, Assemblers): [backend-documentation/navby-tactical-ddd-guide.md](backend-documentation/navby-tactical-ddd-guide.md)
>    * Especificación del Shared Kernel y contratos base: [backend-documentation/navby-backend-tactical-specification.md](backend-documentation/navby-backend-tactical-specification.md)
>    * Especificación del Bounded Context solicitado (y contextos hermanos para integración OHS/ACL):
>      * Catálogo de contextos base: [`backend-documentation/bounded-contexts-description/`](backend-documentation/bounded-contexts-description/)
>      * Modelado táctico extendido: [`backend-documentation/extended-bounded-contexts-description/`](backend-documentation/extended-bounded-contexts-description/)
>      * Planes de implementación: [`backend-documentation/plans/`](backend-documentation/plans/)
>
> 3. **Consultas de Datasets y Malla Aeroportuaria (OpenFlights):**
>    * Datasets definitivos limpios y listos para producción (3,354 nodos comerciales / 37,326 aristas únicas): [`navby-datasets/`](navby-datasets/)
>    * Documentación técnica del pipeline de limpieza y esquemas de datos: [navby-datasets/README.md](navby-datasets/README.md)
>    * Análisis de preprocesamiento, métricas del grafo y conectividad: [`report/chapters/20-dataset-description/22-preprocessing-and-metrics.md`](../report/chapters/20-dataset-description/22-preprocessing-and-metrics.md)
>    * Datasets crudos de origen: [`backend-documentation/datasets/`](backend-documentation/datasets/)
>
> 4. **Consultas de Integraciones y APIs Externas:**
>    * Catálogo integral de servicios externos (OpenFlights, FlightAPI, Mercado Pago, Resend, Google Identity): [backend-documentation/navby-platform-architecture.md](backend-documentation/navby-platform-architecture.md) §7
>    * Especificación técnica de FlightAPI (One Way, Round Trip, ACL, Redis, Circuit Breaker): [backend-documentation/flight-api-documentation.md](backend-documentation/flight-api-documentation.md)
>    * Integración de pasarela de pagos (Mercado Pago) y correo (Resend): [backend-documentation/navby-platform-architecture.md](backend-documentation/navby-platform-architecture.md)
>
> 5. **Consultas de Frontend y Experiencia de Usuario:**
>    * Landing pública institucional (Website Astro 5 + Tailwind v4 + GSAP 3 + Lenis): [frontend-architecture/navby-website-architecture.md](frontend-architecture/navby-website-architecture.md)
>    * Aplicación web interactiva (Webapp React 19 + MapLibre GL 2D + deck.gl + TanStack Query + Zustand + boneyard + Sileo): [frontend-architecture/navby-webapp-architecture.md](frontend-architecture/navby-webapp-architecture.md)
>
> 6. **Consultas de Infraestructura Cloud, Despliegue y Presupuesto Azure:**
>    * Frontend en Vercel (Edge CDN para Website y hosting SPA estático para Webapp con coste $0).
>    * Backend Platform en Azure VM (`Standard_B2s`, Docker Compose: Caddy 2, FastAPI, PostgreSQL 16, Redis 7, viabilidad de crédito $100 USD): [backend-documentation/navby-platform-architecture.md](backend-documentation/navby-platform-architecture.md) §4
>
> 7. **Consultas del Reporte Académico Oficial (Complejidad Algorítmica 1ACC0184):**
>    * Reglas editoriales y moderación visual: [../GEMINI.md](../GEMINI.md)
>    * Rúbrica académica, hitos TB1/TB2 y dataset (≥ 1500 nodos): [project-statement.md](project-statement.md)
>    * Capítulos modulares del reporte: [`report/chapters/`](../report/chapters/)
>    * Estándar de tablas y figuras APA 7: [guidelines_tables_figures_apa7.md](guidelines_tables_figures_apa7.md)
>    * Manual de compilación y comandos Makefile: [how-to-use.md](how-to-use.md)
>
> 8. **Resumen Consolidado del Ecosistema Navby:**
>    * Visión ejecutiva, stack tecnológico y enrutador maestro a los subsistemas: [Resumen Consolidado](#resumen-consolidado-del-ecosistema-navby)

## Descripción de la Startup

Andeva es un equipo especializado de ingeniería de software dedicado al diseño y desarrollo de soluciones tecnológicas de vanguardia. Nuestro propósito fundamental es resolver desafíos complejos a través de la innovación, construyendo herramientas digitales eficientes, escalables y centradas en el usuario que impulsen la transformación y el progreso en un entorno tecnológico exigente.

## Significado del nombre

El nombre **Andeva** encapsula la esencia de nuestra identidad y nuestra vocación creadora. Nace de la fusión armónica de dos conceptos poderosos:

* **Andes:** Representa nuestro lugar de origen y el profundo arraigo a la riqueza de la cultura peruana. Simboliza la majestuosidad, la solidez y la visión de altura con la que abordamos cada desafío tecnológico.
* **Eva:** Cuyo significado universal es "la que da vida". Este concepto refleja directamente nuestro ADN tecnológico y carácter innovador: la capacidad de concebir ideas disruptivas y darles vida mediante la creación de productos de software de la más alta calidad.

Juntos, Andeva expresa nuestro compromiso de crear tecnología viva, útil y trascendente desde el Perú hacia el futuro.

## Objetivo

Diseñar y desarrollar soluciones de software innovadoras que empoderen a las organizaciones y a las personas. Buscamos brindar herramientas tecnológicas de primera categoría que optimicen procesos, fomenten la creatividad y resuelvan problemas complejos, garantizando siempre la máxima calidad técnica y una experiencia de usuario excepcional.

## Visión

Ser el equipo de ingeniería de software líder y referente tecnológico a nivel internacional, reconocido por nuestra capacidad de innovar y dar vida a productos digitales excepcionales. Aspiramos a construir ecosistemas tecnológicos que definan los estándares del mañana, manteniendo siempre nuestro compromiso inquebrantable con la excelencia y el orgullo por nuestra identidad cultural.

## Producto: Navby

**Navby** es una plataforma web inteligente de **planificación y optimización de rutas aéreas** diseñada para encontrar las mejores alternativas de vuelo entre cualquier par de ciudades del mundo. Inspirada en la experiencia de reserva de **LATAM Airlines** y desarrollada a partir del Caso de Estudio N.° 9 de Complejidad Algorítmica, Navby resuelve el problema de la conectividad aérea combinando tres dimensiones críticas: **tiempo/distancia de vuelo, menor número de escalas posibles y el mejor precio de boletos en el mercado**.

A diferencia de los buscadores tradicionales que operan como cajas negras o los visualizadores académicos con grafos teóricos sin precios de mercado, Navby integra una arquitectura de dos etapas:
1. **Modelado Topológico y Poda Algorítmica:** Construye una red aeroportuaria global sobre el dataset de **OpenFlights** (miles de aeropuertos como nodos y rutas comerciales como aristas) para encontrar y filtrar las rutas geodésicas más eficientes.
2. **Cotización y Validación en Tiempo Real:** Confronta únicamente las mejores rutas candidatas con **FlightAPI** (mediante sus variantes *One Way Trip API* y *Round Trip API*), entregando al usuario las **3 mejores opciones con precios reales de boletos**.

Para garantizar la viabilidad económica y la protección de la infraestructura ante consultas masivas a APIs externas, Navby opera bajo un **modelo de créditos por uso**: cada usuario dispone de **5 créditos gratuitos diarios no acumulables** (que se renuevan cada 24 horas) y la posibilidad de adquirir **paquetes de créditos acumulables** para búsquedas extendidas.

### Problema que Busca Solucionar Navby

El transporte aéreo comercial global moviliza anualmente a más de 4,700 millones de pasajeros bajo una red altamente tensionada y jerárquica gobernada por centros de conexión (*hubs*). En este escenario, la búsqueda y planificación de vuelos presenta tres problemas estructurales críticos que perjudican tanto la experiencia del usuario como la viabilidad técnica del software:

1. **La Disyuntiva Multiobjetivo Ineficiente (Costo vs. Duración vs. Escalas):**
   El viajero se enfrenta cotidianamente a un conflicto de optimización: los vuelos directos brindan máxima comodidad temporal pero con tarifas con frecuencia astronómicas; en contraste, los itinerarios con múltiples escalas ofrecen reducciones tarifarias a costa de multiplicar la fatiga, la duración total y el riesgo operativo. De acuerdo con estadísticas de la industria (SITA), más del 41% de las incidencias globales por pérdida o deterioro de equipaje ocurren durante transbordos aeroportuarios, sumado a la probabilidad latente de perder conexiones ante demoras en cascada en hubs congestionados. Los usuarios carecen de herramientas transparentes que equilibren formalmente estas tres dimensiones en recomendaciones claras.

2. **Opacidad y Sesgo Comercial de las Plataformas Tradicionales (OTAs y GDS):**
   Los motores de búsqueda convencionales y agregadores comerciales (Google Flights, Skyscanner, Kayak) funcionan como cajas negras condicionadas por alianzas comerciales cerradas (Star Alliance, SkyTeam, oneworld) y convenios corporativos privados. Estas plataformas descartan combinaciones interlineales lógicamente viables si no pertenecen a sus convenios de distribución, aplican podas no informadas y saturan la interfaz con cientos de alternativas redundantes o con desvíos absurdos, provocando sobrecarga cognitiva y parálisis de decisión en el comprador.

3. **Explosión Combinatoria y Coste Prohibitivo de Consultas en Tiempo Real:**
   Desde la perspectiva computacional, la red aeroportuaria global representa un grafo masivo libre de escala con miles de terminales y decenas de miles de conexiones comerciales. Si un motor intenta resolver itinerarios alternativos realizando consultas directas y exhaustivas contra APIs comerciales de vuelos en vivo (como FlightAPI o Amadeus), el sistema detona una **explosión combinatoria inmanejable** ($O(b^d)$) debido al elevado factor de ramificación en los hubs. Cada llamada a una API comercial conlleva una latencia de red sensible (1 a 3 segundos) y un costo financiero por transacción; consultar a ciegas combinaciones inviables agotaría las cuotas de API en minutos y haría financieramente insostenible el servicio.

4. **La Solución Integral de Navby: Arquitectura en Dos Etapas («Escudo OpenFlights»):**
   Navby resuelve esta problemática desacoplando la exploración topológica de la cotización comercial mediante un enfoque innovador:
   * **Etapa 1 (Exploración y Poda Algorítmica a Costo Cero):** El backend carga la red global de OpenFlights (3,354 aeropuertos y 37,326 rutas) en memoria RAM y ejecuta algoritmos exactos de grafos (BFS, Dijkstra, A*, Programación Dinámica y Backtracking acotado a $\le 2$ escalas con poda geométrica) para encontrar y filtrar en milisegundos las rutas geodésicas y temporalmente óptimas, con costo de API externa igual a $0.00.
   * **Etapa 2 (Validación de Mercado Selectiva y Recomendación Accionable):** Únicamente las mejores rutas candidatas resultantes del filtro algorítmico se envían a cotizar contra FlightAPI (*One Way* o *Round Trip*). El sistema protege su infraestructura mediante una billetera de créditos por uso y entrega al usuario las **3 mejores opciones definitivas** con precios en vivo y enlaces directos de reserva, erradicando la sobrecarga cognitiva y garantizando la viabilidad económica del producto.

### Propuesta de valor

Navby no es un simple buscador comercial ni una simulación teórica de aula. Su propuesta de valor se sustenta en:

1. **Optimización Topológica Transparente (OpenFlights):** Descubre rutas y conexiones viables entre miles de aeropuertos del mundo (más de 1,500 nodos conectados), incluso cuando no hay vuelo directo comercial obvio, calculando la ruta geodésica mínima (Haversine) y minimizando escalas.
2. **Confrontación con Tarifas Reales (FlightAPI):** Solo las mejores rutas candidatas se cotizan con FlightAPI (*One Way* y *Round Trip*), obteniendo precios vivos del mercado y enlaces de reserva directos.
3. **Recomendación Multicriterio Accionable (El «Top 3»):** Presenta las 3 alternativas óptimas balanceando distancia/tiempo, escalas y costo final, evitando la sobrecarga cognitiva de cientos de opciones irrelevantes.
4. **Sostenibilidad y Protección de Infraestructura:** El sistema de créditos por uso financia las llamadas a la API de terceros y blinda el backend contra abuso o scraping.

## Features Principales (Business Core)

### 1. Motor de Optimización Topológica de Rutas (Grafo OpenFlights)
El corazón algorítmico del sistema. Modela los aeropuertos como nodos (con coordenadas de latitud/longitud) y las rutas comerciales como aristas ponderadas por distancia geodésica (fórmula de Haversine). Aplica algoritmos de recorrido y caminos mínimos (BFS para minimizar escalas, Dijkstra / A* con heurística admisible para distancia mínima) junto con poda por Backtracking para descartar rutas inviables o con desvíos excesivos, pre-filtrando el espacio de búsqueda antes de consumir cuota de API.

### 2. Cotización en Tiempo Real y Selección Multicriterio del «Top 3»
Transforma las rutas topológicas en decisiones reales de compra. Una vez filtradas las mejores conexiones por el grafo, consulta la **FlightAPI** (*One Way Trip API* y *Round Trip API*) y ejecuta un ordenamiento multicriterio sobre las opciones retornadas, entregando al usuario los **3 vuelos con mejores precios** junto a sus aerolíneas operadoras, duración exacta y enlaces de reserva directos.

### 3. Planificador Integral de Vuelos (Experiencia LATAM Airlines)
Interfaz de configuración de viaje con la fidelidad y semántica de una aerolínea de primer nivel:
* **Modalidad de viaje:** Solo ida (*One-way*) o ida y vuelta (*Round-trip*).
* **Calendario de viaje:** Selección de fecha de salida y fecha de retorno opcional.
* **Desglose de pasajeros:** Conteo diferenciado de adultos (titular y acompañantes), niños (2 a 11 años) e infantes (<2 años).
* **Categoría de cabina:** Selección entre *Economy*, *Premium Economy*, *Business* y *First Class*.

### 4. Gestión y Persistencia de Itinerarios Guardados
Permite a los usuarios autenticados guardar los vuelos e itinerarios planificados (ruta, escalas, fechas, desglose de pasajeros y precios capturados) en su perfil personal para consultarlos, compararlos en el tiempo o eliminarlos, dotando al producto de persistencia relacional y uso recurrente.

### 5. Billetera de Créditos de Uso y Modelo de Sostenibilidad
Control de cuotas y financiamiento transparente del servicio:
* **5 créditos diarios gratuitos:** Asignados a cada cuenta registrada, no acumulables y renovados automáticamente cada 24 horas.
* **Créditos prepagados acumulables:** Paquetes adquiridos mediante pasarela de pago para viajeros frecuentes, sin vencimiento diario.
* **Descuento transaccional:** Cada búsqueda con cotización descuenta créditos del usuario protegiendo la viabilidad financiera del backend.

## Features Secundarios y de Apoyo

* **Visualización en Mapa Plano 2D:** Representación cartográfica interactiva con arcos geodésicos entre ciudades y aeropuertos de conexión sobre un mapa 2D (sin globo terráqueo).
* **Comparador Lado a Lado del Top 3:** Vista comparativa que resalta cuál de las tres alternativas es la más rápida, la más económica o la de menor cantidad de escalas.
* **Historial de Consultas Rápidas:** Registro de búsquedas recientes para re-ejecutar trayectos frecuentes con un solo clic.

## Alcance del Proyecto

El alcance de Navby está delimitado para resolver integralmente el problema de la planificación inteligente de vuelos bajo el Caso de Estudio N.° 9 de Complejidad Algorítmica y los estándares de ingeniería de software para plataformas comerciales de alta fidelidad, manteniendo fronteras operativas claras y justificadas.

### 1. Dentro del Alcance (In-Scope)

#### A. Ámbito Algorítmico y Teoría de Grafos
* **Modelado formal de la red aérea:** Representación de la malla aeroportuaria global mediante un grafo dirigido y ponderado $G = (V, E, W)$ construido sobre el dataset depurado de OpenFlights. El sistema integra exactamente **3,354 aeropuertos comerciales activos ($|V|$)** como vértices (superando en 2.2× el requisito mínimo de 1,500 nodos de la cátedra) y **37,326 rutas comerciales dirigidas únicas ($|E|$)** como aristas.
* **Ponderación geodésica y temporal:** Cálculo de distancias ortodrómicas en kilómetros mediante la **fórmula de Haversine** con $R \approx 6,371\text{ km}$, modelando los pesos de las aristas como el tiempo de vuelo estimado $w_t(u, v) = \frac{d_H(u, v)}{v_{\text{crucero}}} + t_{\text{maniobra}}$ ($v_{\text{crucero}} = 800\text{ km/h}$, $t_{\text{maniobra}} = 30\text{ min}$) y penalización por escala de $t_{\text{conexión}} = 60\text{ min}$.
* **Motor de rutas en tiempo real (Python Runtime):**
  * **BFS (Breadth-First Search):** Búsqueda por niveles para identificar rutas con el mínimo número de escalas posibles ($k - 1$ conexiones).
  * **Dijkstra y A\*:** Cálculo de caminos de menor tiempo de vuelo estimado acumulado sobre aristas ponderadas con pesos no negativos ($w_t \ge 0$), utilizando la distancia Haversine admisible y consistente en A* para acelerar la convergencia hacia el destino.
  * **Backtracking con poda heurística:** Enumeración controlada de rutas alternativas viables, aplicando podas por límite de escalas ($\le 2$), cota de duración acumulada ($T \le 1.5 \times T_{\text{Dijkstra}}$) y desvío ortodrómico.
  * **Programación Dinámica en Grafos:** Optimización multi-criterio que equilibra tiempo acumulado y número de conexiones mediante memoización sobre estados $(u, \text{escalas\_restantes})$ para derivar la frontera de Pareto del viaje.
  * **Divide y Vencerás:** Descomposición geográfica de trayectos intercontinentales complejos a través de macro-regiones IATA y aeropuertos *gateway*.
  * **DFS:** Validación de caminos simples y prevención estricta de ciclos en itinerarios multiconexión ($u \neq v$).
* **Preprocesamiento, conectividad y benchmarking (Data Pipeline & Reporte):**
  * **UFDS (Union-Find):** Poda de terminales aisladas ($k = 0$) y validación casi instantánea $O(\alpha(V))$ de conexidad previa entre aeropuertos.
  * **SCC (Tarjan / Kosaraju):** Verificación de la componente conexa dominante y análisis de centralidad de hubs globales.
  * **MST (Kruskal / Prim):** Determinación del esqueleto de conectividad de distancia mínima y análisis de resiliencia de la red.
  * **Ordenamiento Topológico:** Secuenciación temporal estricta de las etapas de vuelo en el DAG del itinerario.
  * **Validación experimental:** Comparación asintótica y empírica frente a **Fuerza Bruta**, **Bellman-Ford**, **Floyd-Warshall** y **Flujo Máximo**.

#### B. Ámbito Funcional y Producto
* **Planificador integral estilo LATAM Airlines:** Interfaz de configuración completa de viaje con soporte para trayectos de **Solo Ida (One-way)** e **Ida y Vuelta (Round-trip)**, selección de fechas de salida y retorno, selección de categoría de cabina (*Economy*, *Premium Economy*, *Business*, *First Class*) y desglose diferenciado de pasajeros (adultos, niños de 2 a 11 años e infantes menores de 2 años).
* **Búsqueda y resolución de aeropuertos:** Búsqueda por ciudad o terminal aeroportuaria con autocompletado; resolución inteligente de aeropuertos principales por conectividad ($k$) en metrópolis multiaeropuerto con opción de selección manual, operando estrictamente sobre códigos canónicos IATA de 3 letras.
* **Cotización en tiempo real y Top 3:** Consulta selectiva a **FlightAPI** (*One Way Trip API* y *Round Trip API*, consumiendo 2 créditos/request) aplicada exclusivamente sobre las mejores rutas candidatas del grafo, entregando las **3 opciones óptimas con tarifas reales de mercado**, aerolínea operadora, duración exacta y enlaces directos de compra (*deepLinks*).
* **Gestión y persistencia de itinerarios:** Almacenamiento seguro en la cuenta del usuario para guardar, consultar, comparar y eliminar planes de vuelo e itinerarios cotizados.
* **Modelo de sostenibilidad (Créditos por uso):** Asignación automática de **5 créditos gratuitos diarios no acumulables** (renovados cada 24 horas) y adquisición de paquetes de créditos prepagados acumulables mediante pasarela de pago para solventar las cotizaciones en vivo y proteger la infraestructura contra abusos o scraping.
* **Identidad y autenticación:** Registro y acceso mediante credenciales locales con verificación de correo por código OTP (Resend) y autenticación federada Single Sign-On mediante Google Identity Services (OAuth 2.0 / OIDC).
* **Visualización cartográfica 2D:** Renderizado interactivo de arcos geodésicos de vuelo y aeropuertos de conexión sobre un mapa plano interactivo 2D.

#### C. Ámbito de Ingeniería y Arquitectura (Visión General)
* **Demarcación de tres aplicaciones desacopladas:**
  * **Website (Marketing y Presencia Pública):** Sitio estático con **Astro 5** y **Tailwind CSS v4**, optimizado para Core Web Vitals, indexabilidad SEO y presentación institucional del producto.
  * **Webapp (Aplicación Interactiva del Viajero):** SPA interactiva con **React 19**, **Vite**, **TypeScript**, **MapLibre GL JS** y **deck.gl**, enfocada en la planificación fluida y renderizado de arcos de vuelo sobre un mapa plano 2D.
  * **Platform (Backend Core y Motor de Grafos):** API RESTful en **Python 3.12+** (mandatorio por cátedra) con **FastAPI**, **PostgreSQL 16** y **Redis 7**, que alberga el grafo mundial en memoria RAM (~10 MB), ejecuta los algoritmos de ruteo y orquesta las integraciones externas.
* **Arquitectura pragmática sin sobreingeniería:** Se implementa un monolito modular con Clean Architecture y DDD táctico-lite; se prescinde de microservicios y de brokers de mensajería externos complejos (Kafka/RabbitMQ), resolviendo la consistencia inter-contexto mediante el patrón Transactional Outbox sobre PostgreSQL.
* **Fuentes de verdad detalladas:** La especificación exhaustiva de capas, esquemas DDL, contratos OpenAPI, diagramas C4 y código canónico se delega a sus documentos maestros: [navby-platform-architecture.md](backend-documentation/navby-platform-architecture.md), [navby-webapp-architecture.md](frontend-architecture/navby-webapp-architecture.md) y [navby-website-architecture.md](frontend-architecture/navby-website-architecture.md).

---

### 2. Fuera del Alcance (Out-of-Scope / Exclusiones Justificadas)

1. **Consultas de vuelos multiciudad / multidestino (Multi Trip API):**
   * *Justificación:* El soporte de vuelos multidestino (`GET /multitrip`) queda formalmente excluido. La API externa impone una restricción rígida de 3 a 5 tramos obligatorios, exige una tarifa de 5 créditos por consulta y no permite la optimización de caminos mínimos por grafos de Navby. El alcance se concentra estrictamente en trayectos de **Solo Ida (One-way)** e **Ida y Vuelta (Round-trip)**.
2. **Módulo abierto de exploración de conectividad aeroportuaria:**
   * *Justificación:* Esta funcionalidad fue descartada del producto por considerarse innecesaria para la propuesta de valor comercial. El algoritmo DFS y las comprobaciones de conectividad se preservan exclusivamente como mecanismos internos de validación topológica (prevención de ciclos $u \neq v$ y aciclicidad de itinerarios), sin exponer un visor libre de conectividad independiente.
3. **Renderizado de mapas en globo terráqueo esférico 3D:**
   * *Justificación:* La visualización geográfica se restringe intencionalmente a un mapa plano 2D interactivo. El globo 3D introduce sobrecoste de cómputo GPU/WebGL innecesario en el navegador del usuario y dificulta la lectura visual simultánea de trayectos y escalas en comparación con una proyección plana clara.
4. **Cobros periódicos recurrentes y suscripciones automáticas:**
   * *Justificación:* El modelo financiero se basa exclusivamente en compras puntuales prepagadas de paquetes de créditos de uso (*pay-per-use*) a través de Mercado Pago Checkout Pro. No se contemplan cargos automáticos mensuales recurrentes ni almacenamiento de datos sensibles de tarjetas bancarias.
5. **Gestión de capacidad física de asientos y despacho operativo de aerolíneas:**
   * *Justificación:* Aunque la rúbrica del curso menciona la «gestión de capacidad de vuelos / flujo máximo», Navby se sitúa desde la perspectiva del **usuario/viajero** (descubrimiento de rutas y optimización de tarifas de mercado). Navby no es un sistema interno de despacho operativo de aerolíneas ni un GDS/CRS encargado del inventario físico de asientos en cabina.
6. **Procesamiento de pagos de pasajes y emisión de boletos (PNR):**
   * *Justificación:* Navby no opera como agencia de viajes intermediaria ni emite billetes aéreos (*Passenger Name Record*). La transacción final de compra del boleto se delega a las aerolíneas u OTAs oficiales mediante los enlaces de reserva directa (*deepLinks*) provistos por FlightAPI.
7. **Radar y telemetría de vuelos en tiempo real (ADS-B):**
   * *Justificación:* El producto no realiza rastreo satelital ni geolocalización de aeronaves en vuelo; opera sobre mallas de rutas comerciales programadas y tarifas de mercado.
8. **Cálculo de tarifas y horarios dinámicos dentro del grafo estático:**
   * *Justificación:* El dataset de OpenFlights es estático y no contiene horarios ni precios en vivo. La separación arquitectónica es explícita: el grafo resuelve la topología óptima y FlightAPI resuelve el precio y la duración real en minutos.
9. **Transporte y logística de carga aérea:**
   * *Justificación:* La plataforma está orientada exclusivamente a la aviación comercial de pasajeros y equipaje personal estándar.

## Fuentes de Datos e Integraciones Externas

Navby interactúa con un conjunto acotado y desacoplado de servicios externos para nutrir la topología de red, obtener tarifas de mercado, procesar cobros y gestionar la identidad:

| Fuente / Servicio | Uso y Alcance en Navby | Naturaleza Técnica | Protocolo / Integración |
| :--- | :--- | :--- | :--- |
| **OpenFlights** | Catálogo mundial de aeropuertos (nodos) y rutas comerciales (aristas) para construir el grafo aéreo. | Dataset estático offline (depurado y versionado). | Ingesta local desde `docs/navby-datasets/`. |
| **FlightAPI** | Consulta de tarifas reales, duraciones de vuelo y enlaces de reserva (*deepLinks*) para el Top 3. | API externa SaaS de pago (2 créditos/request). | HTTPS REST JSON hacia `api.flightapi.io` vía Adaptador ACL. |
| **Mercado Pago** | Pasarela de pago para la compra de paquetes de créditos de uso (modelo prepago, sin suscripciones). | API externa SaaS de pagos y cobros electrónicos. | Checkout Pro / Webhooks HTTPS con firma criptográfica. |
| **Resend** | Envíos de correos transaccionales: verificación OTP, restablecimiento de contraseña y recibos de compra. | API externa SaaS de mensajería transaccional. | HTTPS REST (puerto 443) con SDK oficial. |
| **Google Identity Services** | Autenticación y registro federado mediante cuentas de Google (OAuth 2.0 / OIDC). | Servicio de identidad federada (IdP). | SDK de frontend + validación de `id_token` JWT en backend. |

---

### OpenFlights: Datasets del Grafo Aéreo y Limpieza de Datos

La topología de rutas de Navby se sustenta en el repositorio abierto de **OpenFlights** ([openflights.org](https://openflights.org/data)). Los archivos originales residen en `docs/backend-documentation/datasets/` y los conjuntos limpios definitivos están centralizados en [`docs/navby-datasets/`](navby-datasets/).

#### 1. Fases del Proceso de Depuración y Validación Matemática
Conforme a la memoria de ingeniería y el análisis de consistencia topológica (`report/chapters/20-dataset-description/22-preprocessing-and-metrics.md`), los datos crudos fueron sometidos a un proceso de sanitización de 4 fases:

1. **Fase 1 (Tipo de instalación aérea):** De las 12,668 instalaciones iniciales en `airports-extended.dat`, se retuvieron exclusivamente terminales aéreas comerciales (`type = "airport"`), descartando estaciones de tren (`station`), puertos marítimos (`port`) e infraestructuras militares o helipuertos.
2. **Fase 2 (Integridad de código IATA):** Se filtraron los registros para conservar únicamente aquellos con identificador IATA de 3 letras mayúsculas válido (descartando nulos `\N`), consolidando exactamente **6,472 aeropuertos comerciales**.
3. **Fase 3 (Validación de aristas activas):** Sobre las 67,663 rutas de `routes.dat`, se verificó la integridad referencial exigiendo que tanto el aeropuerto de origen como el de destino existan en el conjunto de aeropuertos comerciales válidos, reteniendo **67,305 rutas operativas**.
4. **Fase 4 (Poda de vértices aislados):** Se purgaron 3,118 aeródromos sin vuelos comerciales ($k = 0$), resultando en un grafo conexo de **3,354 aeropuertos activos ($|V|$)** y **37,326 aristas dirigidas únicas ($|E|$)**, superando en 2.2× el requisito de 1,500 nodos del curso.

#### 2. Catálogo de Datasets Utilizados (Verificados y Limpios)

| Dataset en `docs/navby-datasets/` | Registros | Campos Clave | Rol en Navby |
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

* **Documentación técnica detallada:** Consulta la especificación exhaustiva de endpoints, esquemas JSON, adaptador ACL y resiliencia en [backend-documentation/flight-api-documentation.md](backend-documentation/flight-api-documentation.md).
* **Endpoints consumidos:**
  * `GET /onewaytrip`: Cotización para viajes de solo ida (**2 créditos/request**).
  * `GET /roundtrip`: Cotización para viajes de ida y vuelta (**2 créditos/request**).
* **Parámetros clave:** Código IATA origen/destino, fechas ISO `YYYY-MM-DD`, pasajeros (`adults`, `children`, `infants`), cabina (`Economy`, `Premium_Economy`, `Business`, `First`) y moneda (`USD`, `PEN`).
* **Datos extraídos:** Precio consolidado, duración en minutos, aerolínea operadora, logotipo y enlace de reserva directo (*deepLink*).

### Seguridad, Caché y Uso Responsable de APIs Externas

Las llamadas a Flight API **nunca se ejecutan desde el navegador**: son orquestadas exclusivamente por el backend mediante la Capa Anticorrupción (ACL):

* **Custodia de secretos:** La clave de API reside únicamente en variables de entorno del servidor (`FLIGHT_API_KEY`).
* **Caché en memoria (Redis):** Toda cotización se almacena con un TTL de 30 minutos. Búsquedas concurrentes o idénticas se resuelven a costo de $0$ créditos y latencia mínima.
* **Pre-filtro algorítmico obligatorio:** El motor de grafos poda el universo de rutas posibles y **solo invoca la API para las 3 a 5 mejores opciones topológicas**, eliminando llamadas innecesarias.
* **Presupuesto transaccional de créditos:** El backend descuenta créditos antes de emitir la llamada externa; si el saldo es insuficiente, la petición se rechaza de forma preventiva.
* **Degradación controlada (Circuit Breaker):** Ante fallos del proveedor o cuota general agotada (HTTP 402/429), el sistema entrega la última tarifa en caché indicando su antigüedad al usuario.

## Decisiones de Diseño Clave

### 1. Los pesos del grafo son estimados (Haversine), no horarios reales

El dataset base de OpenFlights (`routes.dat`) **no incluye duraciones exactas ni horarios en tiempo real** de los vuelos — registra exclusivamente la existencia de la conexión comercial directa y sus escalas intermedias. En consecuencia:

* El motor de rutas calcula el peso temporal de cada arista dirigida $(u, v)$ a partir de la **distancia ortodrómica Haversine** $d_H(u, v)$ derivada de las coordenadas geográficas $(\phi, \lambda)$ de los aeropuertos, modelando el tiempo de vuelo estimado como:
  $$w_t(u, v) = \frac{d_H(u, v)}{v_{\text{crucero}}} + t_{\text{maniobra}}$$
  donde $v_{\text{crucero}} = 800\text{ km/h}$ representa la velocidad crucero promedio comercial y $t_{\text{maniobra}} = 30\text{ min}$ modela las maniobras de ascenso, aproximación y rodaje. Para itinerarios con conexiones, cada transbordo añade una penalización fija $t_{\text{conexión}} = 60\text{ min}$.
* Los **tiempos reales de viaje** (duración exacta por tramo en minutos) y las **tarifas de mercado en vivo** solo se determinan al cotizar mediante **FlightAPI** (extraídos de los campos `legs.duration` y `segments`).
* Esta delimitación arquitectónica es transparente y fundamental para el reporte: el grafo en memoria resuelve la **topología óptima y poda el espacio de búsqueda**; FlightAPI **valida la disponibilidad y concreta el precio real** de las mejores alternativas.

### 2. Búsqueda por ciudades o aeropuertos; resolución interna por códigos IATA

El usuario interactúa en la interfaz buscando por nombre de ciudad o terminal aeroportuaria con soporte de autocompletado inteligente. Sin embargo, dado que múltiples metrópolis cuentan con más de un aeropuerto comercial (ej. Buenos Aires: EZE y AEP; Nueva York: JFK, LGA y EWR; Londres: LHR, LGW y STN), Navby resuelve la ambigüedad en el backend:

* Por defecto, el sistema asigna el **aeropuerto principal** de la ciudad utilizando una heurística basada en el mayor grado de conectividad ($k$) en el grafo aéreo.
* Si el usuario lo prefiere, la interfaz web permite seleccionar explícitamente cualquiera de los aeropuertos secundarios disponibles en la metrópoli.
* Toda la ejecución algorítmica interna en el motor de grafos y las peticiones externas a FlightAPI se ejecutan de manera estricta y canónica sobre los **códigos IATA de 3 letras**.

### 3. Algoritmos y técnicas del curso: selección técnica, propósito y clasificación

Para satisfacer con rigor las competencias de la asignatura de **Complejidad Algorítmica (1ACC0184)** y resolver eficientemente el **Caso de Estudio N.° 9 (Planificación de vuelos - LATAM Airlines)**, las técnicas algorítmicas se estructuran en tres ámbitos operativos claramente diferenciados:

#### A. Algoritmos del Motor de Rutas en Tiempo Real (Runtime / Platform Engine - Core Domain)

Operan en memoria RAM sobre el grafo $G = (V, E)$ de OpenFlights (3,354 nodos y 37,326 aristas) para calcular las mejores rutas candidatas en milisegundos antes de invocar FlightAPI:

1. **BFS (Breadth-First Search - Búsqueda en Anchura):**
   * *Propósito:* Encontrar la ruta con el **mínimo número de escalas** ($k - 1$ conexiones, equivalente al menor número de aristas en el grafo no ponderado).
   * *Justificación de negocio:* Satisface al segmento de viajeros que prioriza vuelos directos o con una sola escala para minimizar el cansancio de transbordos, independientemente de la distancia kilométrica total.
   * *Complejidad:* $O(V + E)$ en tiempo, $O(V)$ en memoria.
2. **Dijkstra (Algoritmo Voraz de Caminos Mínimos):**
   * *Propósito:* Calcular la ruta con el **menor tiempo total estimado de vuelo** sobre aristas ponderadas con pesos no negativos ($w_t(u, v) \ge 0$).
   * *Justificación de negocio:* Ofrece la opción geodésicamente más veloz acumulando tiempos de vuelo Haversine y penalizaciones de escala, explorando el grafo mediante una cola de prioridad indexada (*min-heap*).
   * *Complejidad:* $O((V + E) \log V)$ en tiempo, $O(V)$ en memoria.
3. **A\* (Búsqueda Voraz con Heurística Admisible):**
   * *Propósito:* Acelerar la obtención de la ruta de menor tiempo orientando la exploración espacial hacia el aeropuerto de destino.
   * *Justificación de negocio:* Emplea la función de evaluación $f(u) = g(u) + h(u)$, donde $h(u) = d_H(u, \text{destino}) / v_{\text{crucero}}$ es la distancia Haversine en línea recta al destino dividida por la velocidad crucero. Al cumplir las propiedades de admisibilidad ($h(u) \le d^*(u)$) y consistencia triangular, garantiza optimalidad matemática expandiendo una fracción mínima de vértices en comparación con Dijkstra, reduciendo la latencia de respuesta en la webapp.
   * *Complejidad:* $O(E \log V)$ en el peor caso, con tiempo empírico significativamente inferior.
4. **Backtracking con Poda Heurística:**
   * *Propósito:* Enumerar un conjunto diverso de **rutas alternativas viables** (directas, con 1 escala o con 2 escalas) para enriquecer las opciones del usuario.
   * *Justificación de negocio:* Realiza una búsqueda exhaustiva controlada podando ramas inviables: descarta trayectos que excedan 2 escalas ($k - 1 > 2$), rutas cuyo tiempo supere una cota ($T > 1.5 \times T_{\text{Dijkstra}}$) o caminos que impliquen alejamiento geométrico o retrocesos respecto al destino.
   * *Complejidad:* Acotada por poda a $O(b_{\text{efectivo}}^d)$ con factor de ramificación efectivo $b_{\text{efectivo}} \ll \bar{b} \approx 22.26$ y profundidad $d \le 3$.
5. **Programación Dinámica en Grafos (Optimización Multi-criterio):**
   * *Propósito:* Computar itinerarios óptimos balanceando simultáneamente tiempo de vuelo y número de escalas mediante subestructura óptima y memoización sobre estados $(u, \text{escalas\_restantes})$.
   * *Justificación de negocio:* Construye la frontera de Pareto del viaje, permitiendo asignar un puntaje compuesto de conveniencia antes de someter las 3 mejores rutas candidatas a cotización de mercado.
   * *Complejidad:* $O(K \cdot (V + E))$ donde $K \le 2$ representa el número máximo de escalas admitidas.
6. **Divide y Vencerás (Divide & Conquer):**
   * *Propósito:* Descomponer la búsqueda de rutas intercontinentales complejas particionando el grafo mundial en macro-regiones aéreas IATA (Américas, Europa/África, Asia/Pacífico).
   * *Justificación de negocio:* Resuelve el trayecto en subproblemas regionales independientes conectando a través de aeropuertos *gateway* (hubs de transferencia intercontinental), reduciendo el espacio de búsqueda.
   * *Complejidad:* $O(V_{\text{regional}} + E_{\text{regional}})$.
7. **DFS (Búsqueda en Profundidad):**
   * *Propósito:* Detección de ciclos y validación de aciclicidad en itinerarios multiconexión para asegurar caminos simples sin aeropuertos repetidos ($u \neq v$), además de comprobaciones locales de conectividad. *(Nota: el feature de explorador libre de conectividad aeroportuaria fue descartado del producto para mantener el foco en la planificación y compra de vuelos).*
   * *Complejidad:* $O(V + E)$ en tiempo, $O(V)$ en memoria.

#### B. Algoritmos de Preprocesamiento, Conectividad y Estructura del Grafo (Offline / Data Pipeline)

Garantizan la integridad matemática y topológica de la red aérea durante la ingesta y preparación de los datasets:

1. **UFDS (Union-Find Disjoint Sets):**
   * *Propósito:* Agrupación y particionamiento disjunto de aeropuertos por conectividad.
   * *Uso en Navby:* En la Fase 4 de limpieza, permitió aislar la componente conexa comercial gigante (3,354 nodos con $k > 0$) de los 3,118 aeródromos aislados; en tiempo de ejecución, permite verificar en tiempo casi constante $O(\alpha(V))$ si dos aeropuertos están conectados antes de iniciar una búsqueda de ruta; además, actúa como estructura de soporte para el algoritmo de Kruskal.
   * *Complejidad:* $O(\alpha(V))$ por operación de búsqueda/unión.
2. **SCC (Componentes Fuertemente Conexas - Tarjan / Kosaraju):**
   * *Propósito:* Detección de componentes fuertemente conexas en el grafo dirigido.
   * *Uso en Navby:* Demuestra que la red comercial global forma una única componente dominante con reciprocidad casi simétrica de rutas y permite clasificar y jerarquizar los aeropuertos *hubs* globales en el capítulo de análisis del dataset.
   * *Complejidad:* $O(V + E)$ en tiempo y memoria.
3. **MST (Árbol de Expansión Mínima - Kruskal / Prim):**
   * *Propósito:* Construcción de la red base de interconexión con el costo acumulado de distancia mínima global y regional.
   * *Uso en Navby:* Permite contrastar la topología comercial real frente al árbol generador mínimo, cuantificando en el reporte académico la densidad, redundancia de rutas y tolerancia a fallos del sistema aéreo.
   * *Complejidad:* $O(E \log V)$ para Kruskal (ordenamiento de aristas + UFDS) o Prim.
4. **Ordenamiento Topológico (Kahn / DFS post-order):**
   * *Propósito:* Planificación y secuenciación cronológica de las etapas de vuelo en el DAG de itinerarios con escalas múltiples, asegurando que se cumplan las dependencias temporales estrictas entre salidas y llegadas ($t_{\text{salida}}^{i+1} > t_{\text{llegada}}^i + t_{\text{conexión}}$).
   * *Complejidad:* $O(V_{\text{itinerario}} + E_{\text{itinerario}})$.

#### C. Algoritmos de Benchmarking y Validación Asintótica (Reporte Académico / Experimentación)

Implementados en Python para la sección experimental de validación de resultados y contraste de complejidad:

1. **Fuerza Bruta:**
   * *Propósito:* Búsqueda exhaustiva sin poda de todas las rutas posibles entre dos terminales en subgrafos pequeños ($N \le 10$).
   * *Uso en Navby:* Actúa como línea base teórica de optimalidad absoluta y evidencia empíricamente la explosión combinatoria $O(b^d)$ al comparar sus tiempos de cómputo frente a Dijkstra, A* y Backtracking con poda.
   * *Complejidad:* $O(V!)$ o $O(b^d)$.
2. **Bellman-Ford:**
   * *Propósito:* Algoritmo de caminos mínimos basado en relajación exhaustiva de todas las aristas durante $|V|-1$ iteraciones.
   * *Uso en Navby:* Se incluye en el reporte para contrastar experimentalmente su elevado costo computacional frente a Dijkstra y demostrar analíticamente por qué no es eficiente en grafos de transporte con pesos estrictamente positivos ($w_t \ge 0$).
   * *Complejidad:* $O(V \cdot E)$.
3. **Floyd-Warshall:**
   * *Propósito:* Algoritmo de programación dinámica para caminos mínimos de todos contra todos.
   * *Uso en Navby:* Se evalúa sobre subgrafos densos de aeropuertos de alta conectividad (ej. los 50 principales *hubs* globales) para precalcular matrices de distancias inter-hub y verificar empíricamente la cota asintótica cúbica.
   * *Complejidad:* $O(V^3)$ en tiempo, $O(V^2)$ en memoria.
4. **Flujo Máximo (Edmonds-Karp / Dinic):**
   * *Propósito:* Modelado de capacidad de transporte y saturación de tráfico.
   * *Uso en Navby:* Utilizado en el análisis experimental del reporte para modelar la capacidad máxima de vuelos en corredores troncales y detectar cuellos de botella de conectividad.
   * *Complejidad:* $O(V \cdot E^2)$ para Edmonds-Karp o $O(V^2 \cdot E)$ para Dinic.

#### Resumen y Mapeo Comparativo de Técnicas

| Técnica Algorítmica | Propósito y Caso de Uso en Navby | Complejidad Temporal | Ámbito de Ejecución |
| :--- | :--- | :---: | :--- |
| BFS | Ruta con mínimo número de escalas (menos aristas). | $O(V + E)$ | Runtime (Motor de Rutas) |
| Dijkstra | Ruta con menor tiempo estimado de vuelo (pesos Haversine). | $O((V + E) \log V)$ | Runtime (Motor de Rutas) |
| A* | Búsqueda voraz guiada por distancia Haversine admisible. | $O(E \log V)$ | Runtime (Motor de Rutas) |
| Backtracking con poda | Enumeración acotada de rutas alternativas viables ($\le 2$ escalas). | $O(b_{\text{efectivo}}^d)$ | Runtime (Motor de Rutas) |
| Programación Dinámica (DP) | Optimización multi-criterio balanceando tiempo y escalas. | $O(K \cdot (V + E))$ | Runtime (Motor de Rutas) |
| Divide y Vencerás | Descomposición por macro-regiones IATA y hubs gateway. | $O(V_{\text{regional}} + E_{\text{regional}})$ | Runtime (Motor de Rutas) |
| DFS | Detección de ciclos y validación de caminos simples en itinerarios. | $O(V + E)$ | Runtime (Validación) |
| UFDS | Poda de nodos aislados y validación instantánea de conexidad. | $O(\alpha(V))$ | Data Pipeline / Engine |
| SCC (Tarjan / Kosaraju) | Detección de la componente conexa dominante y análisis de hubs. | $O(V + E)$ | Data Pipeline / Reporte |
| MST (Kruskal / Prim) | Esqueleto de conectividad de distancia mínima y resiliencia. | $O(E \log V)$ | Data Pipeline / Reporte |
| Ordenamiento Topológico | Secuenciación temporal de tramos y escalas en el DAG de viaje. | $O(V + E)$ | Data Pipeline / Itinerarios |
| Fuerza Bruta | Línea base de optimalidad y demostración de explosión combinatoria. | $O(b^d)$ | Benchmarks / Reporte |
| Bellman-Ford | Contraste comparativo frente a Dijkstra en grafos con pesos no negativos. | $O(V \cdot E)$ | Benchmarks / Reporte |
| Floyd-Warshall | Caminos mínimos todos-contra-todos en subgrafos densos de hubs. | $O(V^3)$ | Benchmarks / Reporte |
| Flujo Máximo | Análisis de saturación y capacidad teórica en corredores troncales. | $O(V \cdot E^2)$ | Benchmarks / Reporte |

#### Ciclo de Vida y Flujo Operativo de los Algoritmos (Diagrama ASCII)

El siguiente diagrama ilustra la arquitectura de ejecución y el encadenamiento integral de las 14 técnicas algorítmicas a través de las fases del sistema, desde la ingesta de datos hasta la respuesta al usuario y el banco experimental:

```text
====================================================================================================
                        FASE 0: PREPROCESAMIENTO Y TOPOLOGÍA (OFFLINE / STARTUP)
====================================================================================================
 [OpenFlights Datasets] ────────┐
 (airports.dat, routes.dat)    │
                               ▼
            ┌─────────────────────────────────────────┐
            │   UFDS (Union-Find Disjoint Sets)       │ ──> Poda de 3,118 aeródromos aislados (k=0).
            │               [O(α(V))]                 │ ──> Aísla la componente comercial gigante (3,354 nodos).
            └─────────────────────────────────────────┘
                               │
                               ▼
            ┌─────────────────────────────────────────┐
            │       SCC (Tarjan / Kosaraju)           │ ──> Valida componente fuertemente conexa dominante.
            │              [O(V + E)]                 │ ──> Clasifica hubs globales y simetría de rutas.
            └─────────────────────────────────────────┘
                               │
                               ▼
            ┌─────────────────────────────────────────┐
            │      MST (Kruskal con UFDS / Prim)      │ ──> Genera el árbol de expansión mínima de distancia.
            │             [O(E log V)]                │ ──> Cuantifica redundancia y resiliencia de la red.
            └─────────────────────────────────────────┘
                               │
                               ▼
            ┌─────────────────────────────────────────┐
            │   Carga del Grafo en Memoria RAM        │ ──> Singleton en FastAPI lifespan (~10 MB).
            │  (3,354 nodos / 37,326 aristas únicas)  │ ──> Listas de adyacencia con pesos Haversine wt(u,v).
            └─────────────────────────────────────────┘

====================================================================================================
                  FASE 1: PETICIÓN DE RUTA Y VALIDACIÓN INSTANTÁNEA (RUNTIME)
====================================================================================================
 [Usuario en Webapp] ──> Introduce: Origen (u), Destino (v), Fechas, Pasajeros, Cabina
                               │
                               ▼
            ┌─────────────────────────────────────────┐
            │   Verificación Rápida de Conexidad      │
            │          UFDS: find(u) == find(v)       │
            └─────────────────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               │ ¿Conectados en el Grafo?     │
               └───────────────┬───────────────┘
                      NO       │       SÍ
         ┌─────────────────────┘       └─────────────────────────────┐
         ▼                                                           ▼
┌────────────────────────────────┐                 ┌──────────────────────────────────┐
│ Rechazo Inmediato en O(1)      │                 │  ¿Ruta Intercontinental Lejana?  │
│ Mensaje: Ruta Inviable en Red  │                 └─────────────────┬────────────────┘
│ (0 ms de cómputo desperdiciado)│                                   │
└────────────────────────────────┘                       SÍ          │          NO
                                     ┌───────────────────────────────┘          │
                                     ▼                                          ▼
                      ┌─────────────────────────────┐           ┌────────────────────────────┐
                      │    DIVIDE Y VENCERÁS        │           │  Ruta Intra-regional       │
                      │ Descomposición por macro-   │           │  (Búsqueda directa sobre   │
                      │ regiones IATA y gateways    │           │   el grafo continental)    │
                      └──────────────┬──────────────┘           └──────────────┬─────────────┘
                                     │                                         │
                                     └────────────────────┬────────────────────┘
                                                          │
                                                          ▼
====================================================================================================
             FASE 2: MOTOR POLIMÓRFICO DE RUTAS (RoutePlanningStrategy EN MEMORIA RAM)
====================================================================================================
                     ┌─────────────────────────────────────────────────────────┐
                     │            ORQUESTADOR DE ESTRATEGIAS EN RAM            │
                     │  (Cómputo en paralelo / selección de criterio de viaje) │
                     └────────────────────────────┬────────────────────────────┘
                                                  │
         ┌──────────────────┬─────────────────────┼─────────────────────┬──────────────────┐
         ▼                  ▼                     ▼                     ▼                  ▼
┌─────────────────┐┌─────────────────┐  ┌─────────────────┐  ┌────────────────────┐┌───────────────┐
│     B F S       ││   DIJKSTRA      │  │      A *        │  │ BACKTRACKING CON   ││ PROGRAMACIÓN │
│ (Menor Escalas) ││ (Menor Tiempo)  │  │ (Búsqueda Guíada│  │ PODA HEURÍSTICA    ││ DINÁMICA (DP)│
│                 ││                 │  │    Admisible)   │  │ (Rutas Alternativas││ (Frontera de │
│   [O(V + E)]    ││ [O((V+E) log V)]│  │  [O(E log V)]   │  │    Viables)        ││   Pareto)    │
└────────┬────────┘└────────┬────────┘  └────────┬────────┘  └─────────┬──────────┘└───────┬───────┘
         │                  │                    │                     │                   │
         │  Minimiza        │  Minimiza peso     │  f(n) = g(n) + h(n) │ • Poda escalas ≤ 2│ Recurrencia:
         │  aristas (k-1    │  Haversine wt(u,v) │  h(n): Haversine al │ • Duración ≤ 1.5x │ f(u, k) =
         │  conexiones)     │  vía Min-Heap      │  destino admisible  │ • Sin desvíos 180°│ min[w+f(v,k-1)]
         │                  │                    │  Podas espaciales   │ • Aciclicidad DFS │ Estados
         │                  │                    │  ultra-rápidas      │                   │ acotados
         └──────────────────┼────────────────────┴─────────────────────┼───────────────────┘
                            │                                          │
                            ▼                                          ▼
            ┌──────────────────────────────────────────────────────────────────┐
            │          CONSOLIDACIÓN DE RUTAS TOPOLÓGICAS CANDIDATAS           │
            │           (3 a 5 itinerarios óptimos pre-seleccionados)          │
            └─────────────────────────────────┬────────────────────────────────┘
                                              │
                                              ▼
====================================================================================================
                 FASE 3: VALIDACIÓN Y ORDENAMIENTO DE ITINERARIO (DAG)
====================================================================================================
                                              │
                                              ▼
            ┌──────────────────────────────────────────────────────────────────┐
            │              DFS (Búsqueda en Profundidad): Aciclicidad          │
            │   Valida camino simple: aeropuertos no repetidos (u ≠ v).        │
            └─────────────────────────────────┬────────────────────────────────┘
                                              │
                                              ▼
            ┌──────────────────────────────────────────────────────────────────┐
            │         ORDENAMIENTO TOPOLÓGICO (Grafo Acíclico Dirigido)        │
            │   Secuenciación temporal estricta de escalas:                    │
            │   t_salida(vuelo_i+1) > t_llegada(vuelo_i) + t_conexion_min     │
            └─────────────────────────────────┬────────────────────────────────┘
                                              │
                                              ▼
====================================================================================================
           FASE 4: ESCUDO OPENFLIGHTS Y COTIZACIÓN DE MERCADO (QUOTES CONTEXT)
====================================================================================================
                                              │
                                              ▼
            ┌──────────────────────────────────────────────────────────────────┐
            │               CONSULTA A FAST-PATH REDIS 7 (Cache-Aside)         │
            └─────────────────────────────────┬────────────────────────────────┘
                                              │
                              ┌───────────────┴───────────────┐
                              │    ¿Existe en Caché Local?    │
                              └───────────────┬───────────────┘
                                     SÍ       │       NO
                        ┌─────────────────────┘       └──────────────────────┐
                        ▼                                                    ▼
            ┌───────────────────────┐                        ┌───────────────────────────────┐
            │ Retorna cotización    │                        │ Débito Atómico en Redis (Lua) │
            │ desde memoria         │                        │ (1 o 2 créditos según viaje)  │
            │ (0 llamadas a API)    │                        └───────────────┬───────────────┘
            └───────────┬───────────┘                                        │
                        │                                                    ▼
                        │                                    ┌───────────────────────────────┐
                        │                                    │  Llamada HTTPS a FlightAPI    │
                        │                                    │  (One Way o Round Trip API)   │
                        │                                    │  Solo para el Top de Rutas    │
                        │                                    └───────────────┬───────────────┘
                        │                                                    │
                        └─────────────────────┬──────────────────────────────┘
                                              │
                                              ▼
            ┌──────────────────────────────────────────────────────────────────┐
            │          PRESENTACIÓN ACCIONABLE AL VIAJERO («TOP 3»)            │
            │   • 3 mejores opciones reales (precio USD/PEN, escalas, duración)│
            │   • Enlaces directos de reserva (deepLinks de aerolíneas)        │
            │   • Renderizado de arcos ortodrómicos WebGL con deck.gl en mapa  │
            └──────────────────────────────────────────────────────────────────┘

====================================================================================================
             FASE 5: BANCO EXPERIMENTAL Y VALIDACIÓN ASINTÓTICA (REPORTE ACADÉMICO)
====================================================================================================
  (Scripts de experimentación en Python para validar formalmente las complejidades teóricas)

   [Subgrafos Pequeños N ≤ 10]          [Grafos con Pesos wt ≥ 0]         [Top 50 Hubs Mundiales]
               │                                   │                                 │
               ▼                                   ▼                                 ▼
   ┌───────────────────────┐           ┌───────────────────────┐         ┌───────────────────────┐
   │    FUERZA BRUTA       │           │     BELLMAN-FORD      │         │    FLOYD-WARSHALL     │
   │      [O(b^d)]         │           │      [O(V · E)]       │         │        [O(V³)]        │
   │ Demuestra explosión   │           │ Demuestra lentitud    │         │ Matriz todos-a-todos  │
   │ combinatoria vs A*    │           │ innecesaria vs        │         │ en subgrafo denso de  │
   │ y Dijkstra.           │           │ Dijkstra.             │         │ aeropuertos troncales.│
   └───────────────────────┘           └───────────────────────┘         └───────────────────────┘
                                                   │
                                                   ▼
                                       ┌───────────────────────┐
                                       │     FLUJO MÁXIMO      │
                                       │ (Edmonds-Karp/Dinic)  │
                                       │      [O(V · E²)]      │
                                       │ Modela capacidad y    │
                                       │ cuellos de botella en │
                                       │ corredores troncales. │
                                       └───────────────────────┘
```

### 4. Resumen Consolidado del Stack Tecnológico

Navby se concibe como un ecosistema desacoplado en tres aplicaciones complementarias e independientes (Website, Webapp y Platform). Cada subsistema adopta la tecnología estrictamente adecuada para su naturaleza operativa bajo un riguroso criterio anti-sobreingeniería, delegando sus especificaciones profundas a sus respectivos documentos de arquitectura:

| Componente | Tipo de Aplicación | Stack Principal | Despliegue / Hosting | Criterio Anti-sobreingeniería | Fuente de Verdad |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Website** | Sitio Público / Landing | Astro 5, TypeScript, Tailwind CSS v4, GSAP 3, Lenis, MDX | Vercel (Edge CDN) | SSG puro e Islands Architecture; cero JS innecesario, smooth scroll y animaciones fluidas sin servidor dinámico. | [navby-website-architecture.md](frontend-architecture/navby-website-architecture.md) |
| **Webapp** | Cliente Interactivo (SPA) | React 19, TypeScript, Vite 6, MapLibre GL, deck.gl, TanStack Query, Zustand, boneyard, Sileo | Vercel (SPA Estática) | Sidebar interactiva y buscador flotante de ciudades sobre mapa plano 2D WebGL; sin SSR pesado ni globo 3D. | [navby-webapp-architecture.md](frontend-architecture/navby-webapp-architecture.md) |
| **Platform** | Backend Core & Grafos | Python 3.12+, FastAPI, uv, PostgreSQL 16, Redis 7, SQLAlchemy 2.0 (async), Caddy 2 | Azure VM (Standard_B2s, 2 vCPU / 4 GB) | Mandatorio Python por cátedra; monolito modular con grafo en RAM (~10 MB), Outbox en Postgres sin Kafka. $100 cubren >3 meses. | [navby-platform-architecture.md](backend-documentation/navby-platform-architecture.md) |

## Resumen Consolidado del Ecosistema Navby

Este apartado centraliza y consolida la visión ejecutiva y los componentes del ecosistema de **Navby**, sirviendo como síntesis de alto nivel y enrutador hacia las especificaciones técnicas detalladas de cada subsistema:

### 1. Visión Ejecutiva y Componentes del Sistema

El ecosistema de Navby está compuesto por tres piezas desacopladas diseñadas bajo principios de modularidad, alta eficiencia y moderación de sobreingeniería:

1. **Navby Website (Landing pública de conversión):** Sitio web estático enfocado en presentación institucional, comunicación de propuesta de valor, optimización SEO y conversión hacia el aplicativo principal. Especificación completa en [navby-website-architecture.md](frontend-architecture/navby-website-architecture.md).
2. **Navby Webapp (Cliente interactivo de usuario):** Aplicación de una sola página (SPA) centrada en un mapa interactivo plano 2D, donde el usuario explora rutas globales, resuelve itinerarios multiconexión y visualiza cotizaciones de mercado en tiempo real. Especificación completa en [navby-webapp-architecture.md](frontend-architecture/navby-webapp-architecture.md).
3. **Navby Platform (Backend Core y Motor Algorítmico):** Monolito modular en Python 3.12+ que encapsula el motor de grafos en memoria RAM (OpenFlights con 3,354 nodos comerciales y 37,326 aristas únicas), la orquestación de casos de uso bajo DDD-lite, la persistencia transaccional y la integración protegida con proveedores externos. Especificación completa en [navby-platform-architecture.md](backend-documentation/navby-platform-architecture.md).

### 2. Mapa de Navegación Documental de Arquitectura

Para profundizar en la ingeniería de cada subsistema, consultar sus documentos rectores dedicados:

* **Arquitectura de Frontend (Website):** [docs/frontend-architecture/navby-website-architecture.md](frontend-architecture/navby-website-architecture.md)
  * Stack (Astro 5, Tailwind v4, GSAP 3, Lenis), UX de marketing, arquitectura de islas, estructura de carpetas y despliegue en Vercel Edge CDN.
* **Arquitectura de Frontend (Webapp):** [docs/frontend-architecture/navby-webapp-architecture.md](frontend-architecture/navby-webapp-architecture.md)
  * Stack (React 19, Vite 6, MapLibre GL 2D, deck.gl, TanStack Query, Zustand, boneyard, Sileo), UX del mapa interactivo, arquitectura por capas, estructura feature-based, flujo de datos y despliegue en Vercel SPA.
* **Arquitectura Maestra de Backend (Platform):** [docs/backend-documentation/navby-platform-architecture.md](backend-documentation/navby-platform-architecture.md)
  * Stack (Python 3.12+, FastAPI, uv, PostgreSQL 16, Redis 7, Caddy 2), Clean Architecture, Tactical DDD-lite, CQRS-lite, Transactional Outbox, Bounded Contexts, modelo de grafos en memoria RAM, catálogo de servicios externos y despliegue contenerizado en Azure VM ($100 USD de crédito).
* **Especificaciones Tácticas Detalladas de Backend:**
  * Guía y Código Canónico DDD: [docs/backend-documentation/navby-tactical-ddd-guide.md](backend-documentation/navby-tactical-ddd-guide.md)
  * Especificación Táctica por Capas: [docs/backend-documentation/navby-backend-tactical-specification.md](backend-documentation/navby-backend-tactical-specification.md)
  * Esquema Relacional Físico: [docs/backend-documentation/navby-database-schema.md](backend-documentation/navby-database-schema.md)
