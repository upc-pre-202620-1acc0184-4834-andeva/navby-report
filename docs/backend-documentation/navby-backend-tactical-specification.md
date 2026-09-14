# Especificación Táctica Canónica del Backend: Navby Platform

> **Rol del Documento:** Especificación Maestra de Diseño Táctico (Tactical-Level Domain-Driven Design) para el backend de **Navby Platform** (`navby-platform`). Sintetiza y alinea la biblia de producto ([../navby-documentation.md](../navby-documentation.md)), la arquitectura de plataforma ([navby-platform-architecture.md](navby-platform-architecture.md)), la guía de patrones ([navby-tactical-ddd-guide.md](navby-tactical-ddd-guide.md)) y el modelo físico de datos ([navby-database-schema.md](navby-database-schema.md)).
>
> Constituye la **fuente suprema de verdad técnica** de la que derivan las especificaciones técnicas exhaustivas por bounded context ([extended-bounded-contexts-description/](extended-bounded-contexts-description/)) y la documentación académica ([bounded-contexts-description/](bounded-contexts-description/)).

---

## 1. Identidad del Sistema, Filosofía y Stack Tecnológico

### 1.1 Filosofía de Diseño: Anti-Sobreingeniería y Foco B2C
A diferencia de sistemas SaaS multi-inquilino corporativos (como Atelier, concebido para talleres automotrices con inventario FIFO, facturación electrónica tributaria y telemetría IoT), **Navby Platform es un servicio B2C especializado y concreto** orientado a viajeros:
* **Cero Multi-Tenancy:** No existe particionamiento por organizaciones ni columnas `tenant_id`. La cuenta de usuario es global y directa.
* **Cero RBAC:** La autorización se fundamenta exclusivamente en la titularidad directa del recurso (`user_id == current_user.id`).
* **Cero Soft-Delete:** Los itinerarios eliminados se suprimen físicamente (`DELETE CASCADE`) sin sobrecostos de indexación ni columnas `deleted_at`.
* **Cero Colas/Brokers Pesados:** El sistema no introduce Kafka ni RabbitMQ. CQRS-lite se implementa mediante separación limpia de servicios en memoria.
* **Núcleo Algorítmico en Memoria RAM:** El motor de cálculo de rutas (Planning) y el catálogo de navegación (Network) **no tocan la base de datos relacional**. Operan sobre un grafo en memoria principal indexado con listas de adyacencia de Python, respondiendo en $<10$ milisegundos.
* **Persistencia Acotada:** Solo 4 contextos interactúan con PostgreSQL 16, totalizando exactamente 10 tablas relacionales optimizadas.

### 1.2 Stack Tecnológico Oficial

| Componente | Tecnología Seleccionada | Justificación y Rol en Navby |
| :--- | :--- | :--- |
| **Lenguaje** | **Python 3.12+** | Tipado estático moderno (`typing.Protocol`, `type`, `Self`), dataclasses inmutables y rendimiento. |
| **Framework HTTP** | **FastAPI** (ASGI / Uvicorn) | Asincronía nativa, validación Pydantic v2 y especificación OpenAPI 3.1 viva. |
| **Gestor de Paquetes** | **uv** (`pyproject.toml`, `uv.lock`) | Gestión determinista de dependencias y ejecución ultra-veloz (`uv run`). |
| **Persistencia / ORM** | **SQLAlchemy 2 (async)** + **Alembic** | Mapeo objeto-relacional desacoplado, driver `asyncpg` y migraciones versionadas. |
| **Base de Datos** | **PostgreSQL 16** (Docker en VM Azure) | Persistencia duradera, transacciones ACID y almacenamiento semiestructurado JSONB. |
| **Caché y Atomicidad** | **Redis 7** (Docker en VM Azure) | Caché caliente (String/Hash), rate limiting y deducción atómica mediante scripts Lua. |
| **Email Transaccional** | **Resend** (API HTTPS 443) | Entrega confiable de códigos OTP y confirmaciones de pago sin puertos SMTP. |
| **Pasarela de Pagos** | **Mercado Pago** (SDK / REST) | Checkout en moneda nacional (PEN) con webhooks idempotentes. |
| **Autenticación Social** | **Google Identity** (`id_token` OIDC) | Verificación de tokens criptográficos federados en el backend. |
| **Tarifas Reales** | **Flight API** | Cotización externa protegida bajo el escudo OpenFlights. |
| **Dataset de Rutas** | **OpenFlights** (`.dat` versionados) | 12,668 aeropuertos, 67,663 rutas aéreas, 1,255 aerolíneas activas. |

---

## 2. Los 10 Mandamientos Arquitectónicos de Navby Platform

1. **Inmutabilidad Absoluta en Capas de Transferencia y Dominio:** Todos los Commands, Queries, Value Objects y Domain Events son inmutables mediante `@dataclass(frozen=True)`. Precondiciones validadas en `__post_init__`.
2. **Hexagonal Persistence Decoupling:** Las entidades y raíces de agregado **nunca importan SQLAlchemy ni dependencias de infraestructura**. Heredan de `AbstractDomainAggregateRoot`. Los modelos ORM residen exclusivamente en `infrastructure/persistence/models/`.
3. **Control de Flujo Funcional (`Result[T]`):** Queda prohibido el uso de excepciones (`raise Exception`) para control de flujo de negocio esperado (recursos ausentes, saldo insuficiente, validaciones). Los casos de uso retornan `Result.success(value)` o `Result.failure(ApplicationError)`.
4. **Separación Estricta de Transporte (Assemblers):** Los routers de FastAPI nunca reciben ni devuelven entidades de dominio ni modelos ORM. Emplean `Assemblers` para transformar DTOs Pydantic en Commands y Aggregates en DTOs de salida.
5. **Aislamiento Físico entre Bounded Contexts (Sin Foreign Keys Cruzadas):** Queda prohibido definir restricciones de clave foránea física (`FOREIGN KEY`) entre tablas de distintos contextos en PostgreSQL. La vinculación inter-módulo se realiza exclusivamente mediante **IDs lógicos indexados** (`UserId`, `IATACode`).
6. **Open Host Service (OHS) para Integración Interna:** Todo módulo que provea servicios a otro dentro del monolito expone una fachada pública tipada en `interfaces/acl/` (`AirportCatalogFacade`, `CreditAuthorizerFacade`).
7. **Anti-Corruption Layer (ACL) para Integraciones Externas:** Las APIs de terceros (Flight API, Mercado Pago, Google Identity, Resend) se aíslan tras adaptadores en `infrastructure/acl/`. Ningún JSON crudo externo cruza hacia la capa de dominio o aplicación.
8. **Coreografía de Eventos de Dominio:** Las mutaciones de estado en agregados registran eventos con `self.register_domain_event(event)`. El repositorio los extrae atómicamente con `pull_domain_events()` al persistir.
9. **Auditoría Transversal Estandarizada:** Todas las tablas físicas mutables integran las marcas temporales `created_at` y `updated_at` en formato `TIMESTAMPTZ` mediante `AuditablePersistenceMixin`.
10. **Contratos Vivos OpenAPI:** Cada punto de entrada REST en FastAPI define esquemas Pydantic v2 tipados, garantizando contratos de interfaz vivos y validados para los clientes web.

---

## 3. Plan de Desarrollo Bounded Context por Bounded Context

El backend se organiza en 1 Shared Kernel transversal y 6 Bounded Contexts de negocio estructurados en 7 fases secuenciales:

| Fase | Bounded Context | Módulo Python | Tablas Físicas PostgreSQL | Tipo de Persistencia | Integraciones Externas |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **0** | **Shared Kernel** | `app/shared` | — (sin tablas de negocio) | Base SQLAlchemy, pool Redis | FastAPI, Pydantic, Redis |
| **1** | **Route Planning** | `app/modules/planning` | — (grafo en memoria) | Adjacency List RAM | OpenFlights (vía puerto) |
| **2** | **Flight Network** | `app/modules/network` | — (in-memory) | Catálogo RAM | OpenFlights (datasets `.dat`) |
| **3** | **Quotes** | `app/modules/quotes` | `quote_caches`, `api_credit_usages` | PostgreSQL 16 + Redis 7 | **Flight API** |
| **4** | **Identity & Access (IAM)** | `app/modules/iam` | `user_accounts`, `refresh_tokens`, `verification_tokens` | PostgreSQL 16 | **Resend**, **Google OAuth**, bcrypt, JWT |
| **5** | **Itineraries** | `app/modules/itineraries` | `itineraries`, `itinerary_quotes` | PostgreSQL 16 (JSONB) | — (autocontenido) |
| **6** | **Credits & Payments** | `app/modules/credits` | `credit_wallets`, `credit_ledger_entries`, `credit_purchase_orders` | PostgreSQL 16 + Redis 7 (Lua) | **Mercado Pago**, **Resend** |

### Nomenclatura Canónica de Archivos

* **Tier 1 (Especificación Técnica Extendida):** `docs/backend-documentation/extended-bounded-contexts-description/`
  1. [`00-shared.md`](extended-bounded-contexts-description/00-shared.md)
  2. [`01-planning.md`](extended-bounded-contexts-description/01-planning.md)
  3. [`02-network.md`](extended-bounded-contexts-description/02-network.md)
  4. [`03-quotes.md`](extended-bounded-contexts-description/03-quotes.md)
  5. [`04-iam.md`](extended-bounded-contexts-description/04-iam.md)
  6. [`05-itineraries.md`](extended-bounded-contexts-description/05-itineraries.md)
  7. [`06-credits.md`](extended-bounded-contexts-description/06-credits.md)

* **Tier 2 (Documentación Académica para el Reporte):** `docs/backend-documentation/bounded-contexts-description/`
  1. [`00-shared.md`](bounded-contexts-description/00-shared.md)
  2. [`01-planning.md`](bounded-contexts-description/01-planning.md)
  3. [`02-network.md`](bounded-contexts-description/02-network.md)
  4. [`03-quotes.md`](bounded-contexts-description/03-quotes.md)
  5. [`04-iam.md`](bounded-contexts-description/04-iam.md)
  6. [`05-itineraries.md`](bounded-contexts-description/05-itineraries.md)
  7. [`06-credits.md`](bounded-contexts-description/06-credits.md)

---

## 4. Plantilla Estricta de Documentación por Bounded Context (7 Secciones Canónicas)

Cada especificación por Bounded Context implementa rigurosamente las siguientes 7 secciones canónicas, idénticas al estándar de excelencia de Atelier:

1. **Diccionario de Lenguaje Ubicuo y Propósito del Contexto:**
   * Definición funcional, responsabilidades exactas, fronteras de aislamiento y decisiones de diseño clave.
   * Matriz formal del Lenguaje Ubicuo (término en inglés, concepto en el dominio, invariantes y reglas de negocio).
2. **Domain Layer (Capa de Dominio):**
   * Raíces de Agregado (`AbstractDomainAggregateRoot[ID]`), Entidades dependientes, Value Objects inmutables (`@dataclass(frozen=True)`), Typed IDs (`int > 0`) y Enumeraciones de dominio (`StrEnum`).
   * Domain Events inmutables (`DomainEvent`).
   * Puertos de Repositorio puros definidos con `typing.Protocol`.
   * Servicios de Dominio (`DomainService`) para lógica pura multi-agregado.
   * Jerarquía semántica de excepciones de dominio (`DomainException`).
3. **Interface Layer (Capa de Interfaces):**
   * Controladores REST orientados a objetos (`<<RestController>>`) con especificaciones OpenAPI 3.1.
   * Resources / DTOs Pydantic v2 inmutables (`*RequestResource`, `*ResponseResource`).
   * Fowler's DTO Assemblers bidireccionales (`*ResourceAssembler`).
   * Open Host Service (OHS) / Inbound ACL Facade para consumo inter-contexto.
   * Controladores de Webhooks externos (ej. Mercado Pago con validación HMAC-SHA256).
   * Integration Events (Published Language) para consumo asíncrono inter-módulos.
4. **Application Layer (Capa de Aplicación):**
   * Commands y Queries inmutables tipados.
   * Command Handlers y Query Handlers orquestados mediante el monad funcional `Result[T, ApplicationError]`.
   * Manejadores de eventos de dominio (`event_handlers`) para coordinación reactiva.
   * Outbound ACL Services / Ports (`application/acl/ports/`) definiendo los contratos hacia servicios externos.
5. **Infrastructure Layer (Capa de Infraestructura):**
   * Modelos de persistencia física relacional SQLAlchemy 2 (`Mapped[...]`).
   * Persistence Converters (`TypeDecorator` para GeoPoint, Money, etc.).
   * Adaptadores de repositorio concretos (`*RepositoryImpl`).
   * Persistence Assemblers bidireccionales ORM Model $\longleftrightarrow$ Agregado de Dominio.
   * Adaptadores Anticorrupción de salida hacia pasarelas externas (Resend, Flight API, Mercado Pago, Google OIDC).
   * Adaptadores de caché Redis 7 con scripts Lua atómicos.
   * Servicios de cifrado (BCrypt) y tokens (PyJWT).
6. **Diagramas UML y Modelado de Arquitectura (Code Level):**
   * Diagrama de clases de dominio (`Domain Layer Class Diagram` en PlantUML DSL y PNG compilado).
   * Diagrama de clases de interfaz (`Interface Layer Class Diagram` en PlantUML DSL y PNG compilado).
   * Catálogo taxonómico y tabla explicativa de miembros con el estándar Atelier de 5 columnas sin puntos y coma internos.
7. **Database Design Diagram (ERD Relacional):**
   * Diagrama de entidad-relación relacional en PlantUML DSL y Mermaid con tipos PostgreSQL 16, PKs, FKs y restricciones UNIQUE.

---

## 5. Fase 0: Bounded Context Shared Kernel (`app/shared`)

### 5.1 Propósito y Límites
Provee los cimientos transversales del sistema. Abarca las 4 capas de Clean Architecture sin constituir un subdominio de negocio independiente.

### 5.2 Resumen de Componentes Clave

```
app/shared/
├── domain/
│   ├── model/                      # AbstractDomainAggregateRoot, DomainEvent
│   ├── value_objects/              # IATACode, GeoPoint (Haversine puro), Money, UserId, EmailAddress
│   └── exceptions/                 # DomainException, EntityNotFoundException, InvalidCoordinatesException
├── application/
│   ├── result/                     # Result[T, E], ResultStatus, ApplicationError
│   ├── pagination/                 # PagedQuery, PagedResult[T], SortDirection
│   ├── handlers/                   # CommandHandler, QueryHandler, DomainEventHandler
│   ├── bus/                        # CommandBus, QueryBus, InMemoryEventBus, DomainEventPublisher
│   └── ports/                      # CachePort
├── interfaces/
│   ├── rest/
│   │   ├── resources/              # ErrorResource (RFC 7807), MessageResource, PaginationParams
│   │   └── transform/              # ErrorAssembler, ResponseAssembler (result_to_response)
│   ├── errors/                     # GlobalExceptionHandler (FastAPI interceptors)
│   └── middleware/                 # CorrelationIdMiddleware, SecurityHeadersMiddleware, RateLimitMiddleware
└── infrastructure/
    ├── db/                         # Base declarativa SQLAlchemy 2, AuditablePersistenceMixin, DatabaseSessionManager
    ├── outbox/                     # OutboxEventModel, SqlAlchemyOutboxRepository, OutboxDomainEventPublisherAdapter
    ├── redis/                      # RedisConnectionManager (aioredis pool)
    ├── cache/                      # RedisCacheAdapter (implementa CachePort)
    └── config/                     # AppSettings (pydantic-settings validando .env)
```

* **Fórmula de Haversine Canónica (Trigonometría Esférica):**
  Implementada de forma pura en [`GeoPoint.haversine_distance_km_to()`](extended-bounded-contexts-description/00-shared.md#L141):
  $$d = 2r \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \varphi}{2}\right) + \cos(\varphi_1)\cos(\varphi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)$$

---

## 6. Fase 1: Bounded Context Route Planning (`app/modules/planning`) — Core Domain

### 6.1 Propósito y Límites
Computa las rutas aéreas óptimas entre dos terminales sobre el grafo en memoria, minimizando el tiempo estimado de viaje o las escalas de conexión.

### 6.2 Decisiones Técnicas y Patrón Strategy
1. **Desacoplamiento de Persistencia:** Opera 100% en memoria; no posee tablas relacionales.
2. **Cálculo Cinematográfico Honesto:** Duración estimada = Distancia Haversine / 850 km/h + penalización fija de 120 minutos por escala de conexión.
3. **Estrategias Algorítmicas Intercambiables (`RouteSearchStrategy`):**
   * `BfsMinStopsStrategy`: Minimiza la cantidad de escalas ($O(V + E)$).
   * `DijkstraMinTimeStrategy`: Minimiza el tiempo estimado acumulado ($O(E \log V)$).
   * `BacktrackingAlternativesStrategy`: Explora rutas alternativas con poda por profundidad.
4. **Consumo por Puertos:** Consume `RouteGraphPort` para acceder al grafo y `AirportResolverPort` para resolver topónimos.

---

## 7. Fase 2: Bounded Context Flight Network (`app/modules/network`) — Supporting Subdomain

### 7.1 Propósito y Límites
Custodio soberano de los archivos OpenFlights (`.dat`). Responsable del saneamiento, deduplicación e indexación del catálogo aéreo en el arranque de la plataforma.

### 7.2 Decisiones Técnicas y Open Host Service
1. **Ingestión Determinista (`OpenFlightsLoader`):**
   * Filtra registros `\N` y aeropuertos no comerciales $\to$ 6,472 candidatos comerciales.
   * Deduplica 67,663 rutas a **37,595 aristas únicas** entre **3,354 aeropuertos activos**.
2. **Fachada Open Host Service (`AirportCatalogFacade`):**
   * Publica métodos tipados (`find_airports_by_city`, `get_airport_coordinates`, `is_valid_airport`) consumidos por Planning y Quotes.
3. **Servicios de Análisis Topológico (`NetworkAnalysisService`):**
   * Detección de hubs mediante Componentes Fuertemente Conexos (Tarjan SCC, $O(V + E)$).
   * Árbol de Expansión Mínimo (Kruskal MST con Conjuntos Disjuntos UFDS, $O(E \log E)$).
   * Análisis de alcanzabilidad acotada mediante DFS ($O(V + E)$).

---

## 8. Fase 3: Bounded Context Quotes (`app/modules/quotes`) — Supporting Subdomain

### 8.1 Propósito y Límites
Cotización de precios reales y generación de *deepLinks* de reserva mediante integración con Flight API, garantizando el ahorro de créditos y la auditoría del gasto.

### 8.2 Arquitectura del Cache-Aside Canónico
1. **Escudo OpenFlights:** Solo se cotiza un trayecto específico validado previamente en Planning.
2. **Flujo Canónico en 4 Pasos:**
   * **Paso 1 (Cache HIT en Redis):** Clave `navby:cache:quote:{cache_key}` (TTL 30-60 min). Retorna de inmediato el top 3. **Costo: 0 créditos Navby y 0 llamadas a Flight API**.
   * **Paso 2 (Cache MISS):** Invoca `CreditAuthorizerPort` para debitar atómicamente el saldo del usuario mediante script Lua en Redis. Si no hay saldo, retorna `402 Payment Required`.
   * **Paso 3 (Invocación Externa ACL):** `FlightApiAdapter` invoca Flight API vía `httpx` async con timeout y circuit breaker.
   * **Paso 4 (Persistencia Dual y Auditoría):** Guarda en Redis, respalda en PostgreSQL `quote_caches`, y registra el consumo en `api_credit_usages`.
3. **Degradación Controlada:** Ante contingencias (429/402 del proveedor), sirve la última cotización histórica de `quote_caches` con cabecera `X-Data-Stale: true`.

---

## 9. Fase 4: Bounded Context Identity & Access Management (`app/modules/iam`) — Generic Subdomain

### 9.1 Propósito y Límites
Administra el registro de usuarios, autenticación local con contraseña segura, autenticación federada con Google Identity (OIDC), rotación de tokens JWT y verificación asíncrona por correo.

### 9.2 Decisiones Técnicas de Seguridad
1. **Autorización por Propiedad:** Sin roles ni permisos complejos (no RBAC). La autorización se evalúa por `user_id`.
2. **Hashes Criptográficos para Sesiones:** Los tokens de refresco se guardan en `refresh_tokens` únicamente como hashes SHA-256 (`token_hash`), garantizando revocación instantánea en logout.
3. **Verificación Asíncrona (OTP):** Generación de códigos numéricos de 6 dígitos persistidos como hash en `verification_tokens` (expiración de 15 minutos) y enviados vía Resend (HTTPS 443).
4. **Contraseñas Seguras:** Hasheadas con bcrypt (costo 12 rondas). Nullables solo si el proveedor es Google OAuth.

---

## 10. Fase 5: Bounded Context Itineraries (`app/modules/itineraries`) — Supporting Subdomain

### 10.1 Propósito y Límites
Almacena y gestiona los planes de viaje guardados por los usuarios autenticados, congelando la ruta y el podio de ofertas capturado al momento de guardar.

### 10.2 Inmutabilidad por Snapshots JSONB
1. **Independencia del Grafo:** La ruta seleccionada se almacena como un documento JSONB inmutable en `itineraries.selected_route`. Si el grafo de OpenFlights cambia, el viaje guardado permanece intacto.
2. **Podio Relacional de Ofertas:** Las 3 mejores cotizaciones se persisten en `itinerary_quotes` vinculadas mediante clave foránea con eliminación en cascada (`ON DELETE CASCADE`).
3. **Borrado Físico:** Eliminación directa sin sobrecostos de soft-delete.

---

## 11. Fase 6: Bounded Context Credits & Payments (`app/modules/credits`) — Supporting Subdomain

### 11.1 Propósito y Límites
Monetización por uso mediante billetera virtual (5 créditos diarios gratuitos no acumulables + créditos comprados permanentes), compras vía Mercado Pago y control contable estricto.

### 11.2 Decisiones Técnicas y Fast-Path Atómico
1. **Prioridad de Consumo:** Todo débito consume en primer lugar `free_credits`. Agotada la bolsa gratuita, se descuenta de `paid_credits`.
2. **Script Lua Canónico en Redis (`navby:credits:{user_id}`):**
   * Resuelve validación y descuento en un único paso atómico sin condiciones de carrera.
   * Retorna `1` (éxito), `-1` (saldo insuficiente) o `-2` (MISS en caché $\to$ Lazy-load desde PostgreSQL).
3. **Fuente de Verdad Contable:** PostgreSQL `credit_wallets` asienta el saldo duradero y `credit_ledger_entries` registra cada movimiento en un libro mayor append-only.
4. **Idempotencia de Pagos:** La tabla `credit_purchase_orders` impone una restricción de unicidad sobre `external_payment_id`, previniendo abonos dobles ante reintentos de webhook de Mercado Pago.

---

## 12. Estrategia de Benchmarking, Pruebas y Validación

### 12.1 Separación Estricta: Benchmarking de Complejidad vs WebApp de Usuario
* **La WebApp de Usuario (`navby-webapp`):** Es un producto comercial limpio para viajeros. **No contiene gráficos ni herramientas de benchmarking**.
* **La Suite de Benchmarks (`benchmarks/`):** Consiste en scripts de Python independientes (`run_benchmarks.py`) ejecutados en el servidor que:
  1. Generan subgrafos inducidos de tamaño creciente ($N \in [500, 1000, 1500, 2000, 3354]$ nodos).
  2. Evalúan el tiempo de ejecución empírico de BFS, Dijkstra y Backtracking utilizando `time.perf_counter`.
  3. Exportan tablas de datos y gráficos analíticos estáticos para la sección de **Validación de resultados y pruebas** del reporte académico de la universidad (Word/LaTeX).

### 12.2 Pirámide de Pruebas Automatizadas
1. **Pruebas Unitarias de Dominio (Python Puro):** Pruebas deterministas sobre Value Objects, invariantes de agregados, monad `Result[T]` y algoritmos de grafos sin infraestructura (ejecución en $<1$ segundo).
2. **Pruebas de Casos de Uso con Fakes en Memoria:** Uso de implementaciones falsas (`InMemoryRouteGraphAdapter`, `FakeQuoteCacheAdapter`, `FakeCreditAuthorizer`) para validar la orquestación completa sin tocar bases de datos.
3. **Pruebas de Integración (FastAPI TestClient + TestContainers):** Verificación de serialización de endpoints REST, migraciones Alembic sobre PostgreSQL y operaciones de script Lua sobre Redis.

---

## 13. Resumen Unificado de Persistencia (PostgreSQL 16 y Redis 7)

### 13.1 Tablas Relacionales en PostgreSQL 16

| Módulo | Tabla | Clave Primaria | Relaciones Físicas (Intra-Contexto) | Naturaleza y Rol |
| :--- | :--- | :--- | :--- | :--- |
| **IAM** | `user_accounts` | `BIGINT IDENTITY` | — | Entidad raíz de usuarios (local + Google OAuth). |
| **IAM** | `refresh_tokens` | `BIGINT IDENTITY` | `FK -> user_accounts(id) CASCADE` | Hashes SHA-256 de sesiones revocables. |
| **IAM** | `verification_tokens` | `BIGINT IDENTITY` | `FK -> user_accounts(id) CASCADE` | Hashes SHA-256 de OTPs y tokens de reseteo. |
| **Itineraries** | `itineraries` | `BIGINT IDENTITY` | Referencia lógica a `user_accounts(id)` | Viajes guardados (ruta como snapshot JSONB). |
| **Itineraries** | `itinerary_quotes` | `BIGINT IDENTITY` | `FK -> itineraries(id) CASCADE` | Podio congelado de hasta 3 cotizaciones. |
| **Quotes** | `quote_caches` | `BIGINT IDENTITY` | — | Respaldo persistente del caché de cotizaciones. |
| **Quotes** | `api_credit_usages` | `BIGINT IDENTITY` | Referencia lógica a `user_accounts(id)` | Auditoría contable append-only de Flight API. |
| **Credits** | `credit_wallets` | `BIGINT (user_id)` | Referencia lógica a `user_accounts(id)` | Billetera autoritativa de créditos por usuario. |
| **Credits** | `credit_ledger_entries` | `BIGINT IDENTITY` | Referencia lógica a `user_accounts(id)` | Libro mayor inmutable append-only de movimientos. |
| **Credits** | `credit_purchase_orders`| `BIGINT IDENTITY` | Referencia lógica a `user_accounts(id)` | Órdenes de compra con unicidad de pago externo. |

### 13.2 Estructuras de Datos en Redis 7

| Patrón de Clave | Estructura Redis | TTL | Acceso y Operación |
| :--- | :--- | :--- | :--- |
| `navby:credits:{user_id}` | **Hash** | Sin TTL / 24 h | Script Lua atómico para consulta y deducción de saldo. |
| `navby:cache:quote:{sha256_key}` | **String** (JSON) | 1800s a 3600s | Fast-path del Cache-Aside canónico de cotizaciones. |
| `navby:quota:flightapi:used:{YYYY-MM-DD}` | **String** (Contador) | 48 h | Presupuesto diario global del proveedor Flight API. |
| `navby:ratelimit:{ip_o_user}:{endpoint}:{minuto}` | **String** (Contador) | 60 s | Protección contra abuso en endpoints públicos. |

---

## 14. Referencias Cruzadas del Pipeline

* **Biblia de Producto y Dominio:** [../navby-documentation.md](../navby-documentation.md)
* **Arquitectura de Plataforma:** [navby-platform-architecture.md](navby-platform-architecture.md)
* **Guía Maestra de Diseño Táctico DDD:** [navby-tactical-ddd-guide.md](navby-tactical-ddd-guide.md)
* **Diccionario Físico de Base de Datos:** [navby-database-schema.md](navby-database-schema.md)
* **Especificaciones Extendidas por Bounded Context (Tier 1):** [extended-bounded-contexts-description/](extended-bounded-contexts-description/)
* **Documentación Académica para el Reporte (Tier 2):** [bounded-contexts-description/](bounded-contexts-description/)
