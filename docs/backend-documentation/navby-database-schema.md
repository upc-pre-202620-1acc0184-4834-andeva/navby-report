# Modelo de Base de Datos (Navby Platform)

Este documento define la estructura relacional de la base de datos de Navby (PostgreSQL 16, contenedor Docker en VM de Azure), mapeada a los bounded contexts del monolito backend definidos en [navby-platform-architecture.md](navby-platform-architecture.md) y clasificados en [../navby-documentation.md](../navby-documentation.md) §Bounded Contexts.

## Mapeo Bounded Context ↔ Tablas

| Bounded Context | Subdominio | ¿Tablas en PostgreSQL? | Tabla(s) |
| :--- | :--- | :--- | :--- |
| **Route Planning** (motor de rutas) | Core | ❌ Ninguna | El grafo vive en memoria (OpenFlights), no en la BD |
| **Flight Network** (catálogo + análisis de red) | Supporting | ❌ Ninguna | Igual: proviene de los `.dat` en memoria |
| **Itineraries** | Supporting | ✅ Sí | `itineraries`, `itinerary_quotes` |
| **Quotes** (cotización Flight API) | Supporting | ✅ Sí | `quote_caches`, `api_credit_usages` |
| **IAM** (usuarios, OTP, OAuth) | Generic | ✅ Sí | `user_accounts`, `refresh_tokens`, `verification_tokens` |
| **Credits & Payments** | Supporting | ✅ Sí | `credit_wallets`, `credit_ledger_entries`, `credit_purchase_orders` |
| **Shared Kernel** | Infraestructura Transversal | ✅ Sí | `outbox_events` (Patrón Transactional Outbox para entrega at-least-once) |

De los bounded contexts de Navby, 4 de negocio (`IAM`, `Itineraries`, `Quotes`, `Credits & Payments`) y el **Shared Kernel** (mediante su infraestructura transversal de persistencia y mensajería) persisten tablas físicas en PostgreSQL 16 (11 tablas en total). Los dos contextos centrales algorítmicos (`Route Planning` y `Flight Network`) operan **en memoria** por diseño (ver §Nota de exclusión al final).

> **Alcance y diferencias frente a un SaaS (ej. Atelier):** Navby **no es multi-tenant** (sin tabla `tenants` ni columna `tenant_id`), **no tiene RBAC** (autorización por propiedad del recurso vía `user_id`), **no procesa pagos** (la cotización es consulta de precios con deepLink, no transacción), y **no tiene sincronización offline-first** (la webapp es online; los itinerarios viven solo en el servidor). El esquema es deliberadamente pequeño y focalizado.

> **Nota de Convenciones Transversales:**
> * **Claves primarias:** `BIGINT GENERATED ALWAYS AS IDENTITY` (enteros monótonos: mejor localidad de índice B-Tree y menos bytes que UUID v4). No se usan UUID aleatorios como PK.
> * **Nomenclatura:** tablas en singular `snake_case`; índices como `{tabla}_{columna}_idx`; restricciones como `pk_`, `fk_`, `uk_`, `chk_`.
> * **Nulos:** el dataset origen (OpenFlights) usa `\N`, pero ese formato nunca llega a la base de datos (el grafo no se persiste; ver §Nota de exclusión al final).
> * **Enums:** se evita el tipo `ENUM` de PostgreSQL; se usan `VARCHAR` + restricciones `CHECK` (más fáciles de migrar).
> * **Auditoría ligera:** todas las tablas de negocio llevan `created_at TIMESTAMPTZ DEFAULT NOW()`. `updated_at` solo se incluye en tablas mutables (`user_accounts`, `itineraries`) y se actualiza vía `onupdate` de SQLAlchemy (no trigger).
> * **Borrado:** se usa **borrado físico** (`DELETE` real, con `ON DELETE CASCADE` donde aplica). No hay *soft delete*: los itinerarios eliminados no tienen valor histórico para el negocio y simplifica el modelo.

---

## 1. Identity and Access Management Context (IAM)
**Módulo Backend:** `app.modules.iam`

Gobierna el registro, la autenticación por email/contraseña y el ciclo de vida de los tokens de sesión JWT.

### 1.1 `user_accounts` (Cuenta de Usuario)

Entidad raíz del contexto. Representa a una persona registrada en Navby.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
|---|---|---|---|---|---|
| `id` | `BIGINT GENERATED ALWAYS AS IDENTITY` | PK | Sí | - | Identificador técnico del usuario |
| `email` | `VARCHAR(150)` | UK | Sí | - | Correo electrónico unívoco (login principal) |
| `password_hash` | `VARCHAR(255)` | - | No* | `null` | Hash bcrypt (costo 12). **Nullable**: obligatorio solo si `auth_provider='local'` (ver `chk_user_accounts_local_pwd`) |
| `display_name` | `VARCHAR(100)` | - | No | `null` | Nombre visible en la interfaz |
| `status` | `VARCHAR(20)` | - | Sí | `'pending_verification'` | Estado (`pending_verification`, `active`, `suspended`) |
| `auth_provider` | `VARCHAR(20)` | - | Sí | `'local'` | Proveedor (`local` = email+contraseña, `google` = federado Google OAuth) |
| `google_id` | `VARCHAR(255)` | - | No | `null` | Identificador único de Google (`sub` del id_token); `null` en cuentas locales |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de registro |
| `updated_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de última modificación |

* **Relaciones (Integridad Referencial):**
  * `1:N` hacia `refresh_tokens` (Un usuario posee múltiples sesiones activas).
  * `1:N` hacia `verification_tokens` (Un usuario recibe tokens OTP / de reset).
  * `1:N` hacia `itineraries` (Un usuario guarda múltiples itinerarios planificados).
  * `1:N` hacia `credit_ledger_entries` (Un usuario tiene un historial de movimientos de créditos).
  * `1:N` hacia `credit_purchase_orders` (Un usuario realiza compras de paquetes).
  * `1:1` hacia `credit_wallets` (billetera única por usuario).
  * `1:N` hacia `api_credit_usages` (Un usuario origina consumos de la API de precios).
* **Restricciones (Constraints):**
  * `pk_user_accounts`: `PRIMARY KEY (id)`
  * `uk_user_accounts_email`: `UNIQUE (email)`
  * `chk_user_accounts_status`: `CHECK (status IN ('pending_verification', 'active', 'suspended'))`
  * `chk_user_accounts_auth_provider`: `CHECK (auth_provider IN ('local', 'google'))`
  * `chk_user_accounts_local_pwd`: `CHECK (auth_provider <> 'local' OR password_hash IS NOT NULL)` *(las cuentas locales exigen contraseña)*
  * `uk_user_accounts_google_id`: `UNIQUE (google_id)` *(índice parcial: implicito por ser nullable único)*
* **Índices Físicos (B-Tree):**
  * El `UNIQUE` de `email` ya crea su índice implícito; no se duplica.
  * `user_accounts_status_idx`: B-Tree sobre `(status)` *(baja cardinalidad — opcional; mantener solo si existen usuarios suspendidos en volúmenes relevantes, de lo contrario omitir)*.

### 1.2 `refresh_tokens` (Tokens de Refresco de Sesión)

Almacena de forma revocable los refresh tokens JWT (se guarda el **hash**, nunca el token en claro), permitiendo logout real e invalidación de sesiones.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
|---|---|---|---|---|---|
| `id` | `BIGINT GENERATED ALWAYS AS IDENTITY` | PK | Sí | - | Identificador técnico del token |
| `user_id` | `BIGINT` | FK | Sí | - | Cuenta propietaria (`FK -> user_accounts(id) ON DELETE CASCADE`) |
| `token_hash` | `VARCHAR(255)` | UK | Sí | - | SHA-256 del refresh token emitido (nunca el valor en claro) |
| `expires_at` | `TIMESTAMPTZ` | - | Sí | - | Caducidad del token (ej. 7–30 días según política) |
| `is_revoked` | `BOOLEAN` | - | Sí | `false` | Marca de revocación (logout / cambio de contraseña) |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de emisión |

* **Relaciones (Integridad Referencial):**
  * `N:1` hacia `user_accounts` (`user_id` referencia a `user_accounts.id`, borrado en cascada).
* **Restricciones (Constraints):**
  * `pk_refresh_tokens`: `PRIMARY KEY (id)`
  * `fk_refresh_tokens_user_id`: `FOREIGN KEY (user_id) REFERENCES user_accounts(id) ON DELETE CASCADE`
  * `uk_refresh_tokens_hash`: `UNIQUE (token_hash)`
* **Índices Físicos:**
  * `refresh_tokens_user_id_idx`: B-Tree sobre `(user_id)` (FK — Postgres no la auto-indexa).
  * `refresh_tokens_expires_at_idx`: B-Tree sobre `(expires_at)` — soporta el job de purga de tokens vencidos.

### 1.3 `verification_tokens` (Tokens de Un Solo Uso: OTP y Password Reset)

Almacena tokens de un solo uso para los flujos de verificación de email (OTP de 6 dígitos) y recuperación de contraseña (token en enlace). Se guarda el **hash** del valor, nunca el valor en claro.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
|---|---|---|---|---|---|
| `id` | `BIGINT GENERATED ALWAYS AS IDENTITY` | PK | Sí | - | Identificador técnico del token |
| `user_id` | `BIGINT` | FK | Sí | - | Cuenta destinataria (`FK -> user_accounts(id) ON DELETE CASCADE`) |
| `token_hash` | `VARCHAR(255)` | - | Sí | - | SHA-256 del código OTP o del token de reset (nunca el valor en claro) |
| `type` | `VARCHAR(20)` | - | Sí | - | Propósito (`email_verification`, `password_reset`) |
| `expires_at` | `TIMESTAMPTZ` | - | Sí | - | Caducidad (OTP: ~10–15 min; reset: ~1–2 h) |
| `used_at` | `TIMESTAMPTZ` | - | No | `null` | Cuándo se consumió (un solo uso; `null` = vigente) |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de emisión |

* **Relaciones (Integridad Referencial):**
  * `N:1` hacia `user_accounts` (`user_id` referencia a `user_accounts.id`, borrado en cascada).
* **Restricciones (Constraints):**
  * `pk_verification_tokens`: `PRIMARY KEY (id)`
  * `fk_verification_tokens_user_id`: `FOREIGN KEY (user_id) REFERENCES user_accounts(id) ON DELETE CASCADE`
  * `chk_verification_tokens_type`: `CHECK (type IN ('email_verification', 'password_reset'))`
* **Índices Físicos:**
  * `verification_tokens_user_id_idx`: B-Tree sobre `(user_id)` (FK).
  * `verification_tokens_lookup_idx`: B-Tree compuesto sobre `(user_id, type, used_at)` — lookup del token vigente del usuario.
  * `verification_tokens_expires_at_idx`: B-Tree sobre `(expires_at)` — job de limpieza de tokens expirados.
  * *Regla operativa:* al emitir un nuevo token de un `type` para un usuario, se invalidan (`used_at = NOW()`) los anteriores del mismo tipo — un solo token vigente por tipo.

---

## 2. Itineraries Context (Vuelos Planificados Guardados)
**Módulo Backend:** `app.modules.itineraries`

Persiste los itinerarios que el usuario planificó en la webapp: los criterios del viaje (origen, destino, fechas, pasajeros), la ruta elegida (snapshot) y sus cotizaciones asociadas.

### 2.1 `itineraries` (Itinerario Planificado)

Entidad raíz del contexto. Cada fila es un viaje planificado por un usuario. La ruta elegida se guarda como **snapshot inmutable en JSONB**, porque el grafo se calcula en memoria y no existe en la base de datos.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
|---|---|---|---|---|---|
| `id` | `BIGINT GENERATED ALWAYS AS IDENTITY` | PK | Sí | - | Identificador técnico del itinerario |
| `user_id` | `BIGINT` | FK | Sí | - | Usuario propietario (`FK -> user_accounts(id) ON DELETE CASCADE`) |
| `origin_city` | `VARCHAR(100)` | - | Sí | - | Ciudad de origen elegida en el mapa |
| `origin_iata` | `CHAR(3)` | - | Sí | - | Código IATA del aeropuerto de origen resuelto (ej. `LIM`) |
| `destination_city` | `VARCHAR(100)` | - | Sí | - | Ciudad de destino elegida |
| `destination_iata` | `CHAR(3)` | - | Sí | - | Código IATA del aeropuerto de destino resuelto (ej. `CUZ`) |
| `departure_date` | `DATE` | - | Sí | - | Fecha de salida del viaje |
| `return_date` | `DATE` | - | No | `null` | Fecha de retorno; `null` = viaje solo de ida |
| `adults` | `SMALLINT` | - | Sí | `1` | Número de pasajeros adultos |
| `children` | `SMALLINT` | - | Sí | `0` | Número de niños |
| `infants` | `SMALLINT` | - | Sí | `0` | Número de infantes |
| `cabin_class` | `VARCHAR(20)` | - | Sí | `'Economy'` | Cabina (`Economy`, `Premium_Economy`, `Business`, `First`) |
| `currency` | `CHAR(3)` | - | Sí | `'USD'` | Moneda ISO de las cotizaciones asociadas |
| `selected_route` | `JSONB` | - | Sí | - | Snapshot de la ruta elegida: secuencia de tramos `[{from_iata, to_iata}]`, `total_stops`, `estimated_minutes`, criterio (`min_time`/`min_stops`) |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de guardado |
| `updated_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de última modificación |

* **Relaciones (Integridad Referencial):**
  * `N:1` hacia `user_accounts` (`user_id` referencia a `user_accounts.id`, borrado en cascada).
  * `1:N` hacia `itinerary_quotes` (Un itinerario conserva sus top-3 cotizaciones).
* **Restricciones (Constraints):**
  * `pk_itineraries`: `PRIMARY KEY (id)`
  * `fk_itinerary_user_id`: `FOREIGN KEY (user_id) REFERENCES user_accounts(id) ON DELETE CASCADE`
  * `chk_itinerary_distinct_airports`: `CHECK (origin_iata <> destination_iata)`
  * `chk_itinerary_dates`: `CHECK (return_date IS NULL OR return_date >= departure_date)`
  * `chk_itinerary_adults`: `CHECK (adults >= 1)`
  * `chk_itinerary_children`: `CHECK (children >= 0)`
  * `chk_itinerary_infants`: `CHECK (infants >= 0 AND infants <= adults)` *(regla aérea estándar: un infante por adulto en falda)*
  * `chk_itinerary_total_pax`: `CHECK (adults + children + infants <= 9)` *(límite razonable de la API de precios)*
  * `chk_itinerary_cabin_class`: `CHECK (cabin_class IN ('Economy', 'Premium_Economy', 'Business', 'First'))`
* **Índices Físicos (B-Tree):**
  * `itineraries_user_id_idx`: B-Tree sobre `(user_id)` (FK + patrón de listado "mis itinerarios").
  * `itineraries_user_created_idx`: B-Tree compuesto sobre `(user_id, created_at DESC)` — cubre el listado cronológico de itinerarios de un usuario.

### 2.2 `itinerary_quotes` (Snapshot de Cotización Top-3)

Guarda los 3 mejores precios reales obtenidos para el itinerario en el momento de cotizarlo, uno por fila (`rank` 1–3). Es un snapshot: los precios reales fluctúan; cada cotización registra su `quoted_at`.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
|---|---|---|---|---|---|
| `id` | `BIGINT GENERATED ALWAYS AS IDENTITY` | PK | Sí | - | Identificador técnico de la cotización |
| `itinerary_id` | `BIGINT` | FK | Sí | - | Itinerario cotizado (`FK -> itineraries(id) ON DELETE CASCADE`) |
| `rank` | `SMALLINT` | - | Sí | - | Posición en el top-3 por precio (1 = más barata) |
| `price` | `DECIMAL(12,2)` | - | Sí | - | Precio total para todos los pasajeros |
| `currency` | `CHAR(3)` | - | Sí | - | Moneda ISO del precio |
| `total_duration_minutes` | `INTEGER` | - | No | `null` | Duración real total reportada por Flight API (`legs.duration`) |
| `stops` | `SMALLINT` | - | Sí | `0` | Número real de escalas de la opción |
| `carriers` | `VARCHAR(255)` | - | No | `null` | Aerolíneas principales de la opción (ej. `LATAM, Avianca`) |
| `agent_name` | `VARCHAR(100)` | - | No | `null` | Agencia/OTA que ofrece el precio |
| `deep_link` | `TEXT` | - | Sí | - | URL de reserva externa (deepLink del proveedor) |
| `quoted_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Momento exacto de la cotización (clave para mostrar antigüedad del precio) |
| `raw_payload` | `JSONB` | - | No | `null` | Respuesta normalizada completa (para depuración y features futuras) |

* **Relaciones (Integridad Referencial):**
  * `N:1` hacia `itineraries` (`itinerary_id` referencia a `itineraries.id`, borrado en cascada).
* **Restricciones (Constraints):**
  * `pk_itinerary_quotes`: `PRIMARY KEY (id)`
  * `fk_itinerary_quotes_itinerary_id`: `FOREIGN KEY (itinerary_id) REFERENCES itineraries(id) ON DELETE CASCADE`
  * `uk_itinerary_quotes_rank`: `UNIQUE (itinerary_id, rank)` *(un solo registro por posición del podio)*
  * `chk_itinerary_quotes_rank`: `CHECK (rank BETWEEN 1 AND 3)`
  * `chk_itinerary_quotes_price`: `CHECK (price >= 0)`
  * `chk_itinerary_quotes_stops`: `CHECK (stops >= 0)`
* **Índices Físicos (B-Tree):**
  * `itinerary_quotes_itinerary_id_idx`: B-Tree sobre `(itinerary_id)` (FK).
  * `itinerary_quotes_itinerary_rank_idx`: B-Tree compuesto sobre `(itinerary_id, rank)` — la consulta típica ("dame el top-3 ordenado") queda cubierta por el `UNIQUE (itinerary_id, rank)`, que ya genera este índice implícito; no duplicar.

---

## 3. Quotes Context (Cotización via Flight API)
**Módulo Backend:** `app.modules.quotes`

Soporta la integración con Flight API: respaldo persistente del caché caliente (Redis) y auditoría del consumo de créditos de la API (cada request cuesta créditos de pago).

### 3.1 `quote_caches` (Caché Persistente de Cotizaciones)

Respaldo duradero del caché de cotizaciones. Redis es la capa caliente (TTL corto); esta tabla permite (a) reconstruir el caché si Redis se reinicia y (b) servir datos con aviso de antigüedad ante degradación (402/429 del proveedor).

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
|---|---|---|---|---|---|
| `id` | `BIGINT GENERATED ALWAYS AS IDENTITY` | PK | Sí | - | Identificador técnico del registro |
| `cache_key` | `CHAR(64)` | UK | Sí | - | SHA-256 hex de la combinación exacta de parámetros de búsqueda (origen, destino, fechas, pax, cabina, moneda) |
| `origin_iata` | `CHAR(3)` | - | Sí | - | Origen de la búsqueda (para invalidación y diagnóstico) |
| `destination_iata` | `CHAR(3)` | - | Sí | - | Destino de la búsqueda |
| `departure_date` | `DATE` | - | Sí | - | Fecha de salida de la búsqueda |
| `return_date` | `DATE` | - | No | `null` | Fecha de retorno (`null` = one-way) |
| `trip_type` | `VARCHAR(12)` | - | Sí | - | Endpoint usado (`onewaytrip`, `roundtrip`) |
| `payload` | `JSONB` | - | Sí | - | Top-3 de cotizaciones normalizadas (mismo modelo que `itinerary_quotes`) |
| `credits_cost` | `SMALLINT` | - | Sí | `2` | Créditos consumidos al obtener este payload |
| `fetched_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Momento de la llamada real al proveedor |
| `expires_at` | `TIMESTAMPTZ` | - | Sí | - | Caducidad lógica de la entrada (coherente con el TTL de Redis, ~30–60 min) |

* **Restricciones (Constraints):**
  * `pk_quote_caches`: `PRIMARY KEY (id)`
  * `uk_quote_caches_key`: `UNIQUE (cache_key)`
  * `chk_quote_caches_trip_type`: `CHECK (trip_type IN ('onewaytrip', 'roundtrip'))`
  * `chk_quote_caches_expiry`: `CHECK (expires_at > fetched_at)`
* **Índices Físicos (B-Tree):**
  * El `UNIQUE (cache_key)` ya cubre las búsquedas puntuales.
  * `quote_caches_expires_at_idx`: B-Tree sobre `(expires_at)` — para el job de limpieza de entradas caducadas.
  * `quote_caches_route_date_idx`: B-Tree compuesto sobre `(origin_iata, destination_iata, departure_date)` — útil para diagnósticos y reportes de "trayectos más buscados".

### 3.2 `api_credit_usages` (Auditoría de Consumo de Créditos)

Registro **append-only** (solo inserciones, nunca `UPDATE`/`DELETE`) de cada llamada cobrada a Flight API. Alimenta el presupuesto de créditos y la observabilidad del gasto.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
|---|---|---|---|---|---|
| `id` | `BIGINT GENERATED ALWAYS AS IDENTITY` | PK | Sí | - | Identificador técnico del evento |
| `user_id` | `BIGINT` | - | Sí | - | Usuario que originó la consulta (referencia lógica a `user_accounts.id`; ver nota sobre desacoplamiento) |
| `endpoint` | `VARCHAR(12)` | - | Sí | - | Endpoint del proveedor invocado (`onewaytrip`, `roundtrip`) |
| `cache_key` | `CHAR(64)` | - | No | `null` | Clave de caché asociada (referencia lógica a `quote_caches.cache_key`) |
| `credits` | `SMALLINT` | - | Sí | `2` | Créditos cobrados por el proveedor en esa llamada |
| `cache_hit` | `BOOLEAN` | - | Sí | `false` | `false` = llamada real cobrada; `true` = servida desde caché (registrada para métricas de ahorro) |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal del evento (**inmutable**: nunca se actualiza) |

* **Relaciones (Integridad Lógica):**
  * `N:1` hacia `user_accounts` mediante ID lógico (`user_id`). Sin restricción de FK física inter-contexto para preservar la independencia de módulos.
* **Restricciones (Constraints):**
  * `pk_api_credit_usages`: `PRIMARY KEY (id)`
  * `chk_api_credit_usages_endpoint`: `CHECK (endpoint IN ('onewaytrip', 'roundtrip'))`
  * `chk_api_credit_usages_credits`: `CHECK (credits > 0)`
* **Índices Físicos:**
  * `api_credit_usages_user_id_idx`: B-Tree sobre `(user_id)`.
  * `api_credit_usages_created_at_idx`: B-Tree sobre `(created_at)` — consultas de gasto por rango temporal (presupuesto diario/mensual).

---

## 4. Credits Context (Monetización Pay-Per-Use)
**Módulo Backend:** `app.modules.credits`

Gestiona la billetera de créditos Navby (saldo gratis + saldo pagado), el ledger append-only de movimientos, y las órdenes de compra vía Mercado Pago. Los créditos se consumen al cotizar precios (ver [navby-platform-architecture.md](navby-platform-architecture.md) §5).

### 4.1 `credit_wallets` (Billetera de Créditos por Usuario)

Entidad única por usuario (relación 1:1). Replica local autoritativa del saldo; Redis guarda el espejo de lectura rápida, pero esta tabla es la fuente de verdad.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
|---|---|---|---|---|---|
| `user_id` | `BIGINT` | PK, FK | Sí | - | Dueño de la billetera (`PK, FK -> user_accounts(id) ON DELETE CASCADE`) |
| `free_credits` | `SMALLINT` | - | Sí | `5` | Créditos gratis restantes del día |
| `paid_credits` | `INTEGER` | - | Sí | `0` | Créditos comprados restantes (nunca expiran) |
| `free_credits_refreshed_on` | `DATE` | - | Sí | `CURRENT_DATE` | Última fecha en que se repusieron los gratuitos |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de creación |
| `updated_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de última modificación |

* **Relaciones (Integridad Referencial):**
  * `1:1` con `user_accounts` (`user_id` es PK y FK con borrado en cascada).
* **Restricciones (Constraints):**
  * `pk_credit_wallets`: `PRIMARY KEY (user_id)`
  * `fk_credit_wallets_user_id`: `FOREIGN KEY (user_id) REFERENCES user_accounts(id) ON DELETE CASCADE`
  * `chk_credit_wallets_free`: `CHECK (free_credits >= 0 AND free_credits <= 5)` *(el tope gratis diario es 5)*
  * `chk_credit_wallets_paid`: `CHECK (paid_credits >= 0)`
* **Índices Físicos:** solo la PK (toda lectura/escritura es por `user_id`).

> **Nota anti race-condition:** el refresh diario y todo débito se resuelven atómicamente: `UPDATE credit_wallets SET ... WHERE user_id = $1 AND free_credits_refreshed_on < CURRENT_DATE` (el refresco) y el débito con `UPDATE ... SET free_credits = free_credits - $n ... WHERE user_id = $1 AND free_credits + paid_credits >= $n` (falla con 0 filas si no hay saldo). Nunca read-modify-write en dos pasos. Redis `credits:{user_id}` es solo un espejo de consulta (invalidado al escribir Postgres).

### 4.2 `credit_ledger_entries` (Ledger Append-Only de Movimientos de Créditos)

Registro inmutable (solo `INSERT`) de todo movimiento de la billetera: consumos, reposiciones diarias, compras, reembolsos y ajustes. Fuente de auditoría y de debugging.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
|---|---|---|---|---|---|
| `id` | `BIGINT GENERATED ALWAYS AS IDENTITY` | PK | Sí | - | Identificador del movimiento |
| `user_id` | `BIGINT` | FK | Sí | - | Dueño del movimiento (`FK -> user_accounts(id) ON DELETE RESTRICT` — nunca perder auditoría) |
| `kind` | `VARCHAR(20)` | - | Sí | - | Tipo (`debit`, `daily_refresh`, `purchase_credit`, `refund`, `manual_adjustment`) |
| `amount` | `SMALLINT` | - | Sí | - | Cantidad firmada en créditos: negativa en `debit`, positiva en entradas |
| `bucket` | `VARCHAR(10)` | - | Sí | - | Sobre qué saldo aplicó (`free`, `paid`) |
| `balance_after` | `INTEGER` | - | Sí | - | Saldo total resultante tras el movimiento |
| `reason` | `VARCHAR(255)` | - | Sí | - | Motivo legible (ej. `quote:onewaytrip`, `daily_free_refresh`, `purchase order <id>`) |
| `reference_id` | `VARCHAR(100)` | - | No | `null` | Referencia externa (ej. `purchase_order.id`, cache_key de la cotización) |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal del movimiento (**inmutable**) |

* **Relaciones (Integridad Lógica):**
  * `N:1` hacia `user_accounts` mediante ID lógico (`user_id`).
* **Restricciones (Constraints):**
  * `pk_credit_ledger_entries`: `PRIMARY KEY (id)`
  * `chk_credit_ledger_entries_kind`: `CHECK (kind IN ('debit', 'daily_refresh', 'purchase_credit', 'refund', 'manual_adjustment'))`
  * `chk_credit_ledger_entries_bucket`: `CHECK (bucket IN ('free', 'paid'))`
  * `chk_credit_ledger_entries_amount`: `CHECK (amount <> 0)`
* **Índices Físicos:**
  * `credit_ledger_entries_user_id_idx`: B-Tree sobre `(user_id)`.
  * `credit_ledger_entries_user_created_idx`: B-Tree compuesto sobre `(user_id, created_at DESC)` — historial del usuario cronológico.

### 4.3 `credit_purchase_orders` (Órdenes de Compra vía Mercado Pago)

Cotiza el ciclo de vida de una compra de paquete de créditos: se crea `pending` al generar la preferencia en Mercado Pago, pasa a `approved`/`rejected` al confirmar el webhook (con idempotencia por `external_payment_id`).

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
|---|---|---|---|---|---|
| `id` | `BIGINT GENERATED ALWAYS AS IDENTITY` | PK | Sí | - | Identificador de la orden |
| `user_id` | `BIGINT` | - | Sí | - | Comprador (referencia lógica a `user_accounts.id`) |
| `package_code` | `VARCHAR(30)` | - | Sí | - | Paquete elegido (ej. `pack_5`, `pack_15`, `pack_35`) |
| `credits_to_grant` | `SMALLINT` | - | Sí | - | Créditos que acreditará al aprobarse |
| `unit_price` | `DECIMAL(10,2)` | - | Sí | - | Precio cobrado en la transacción |
| `currency` | `CHAR(3)` | - | Sí | `'PEN'` | Moneda del cobro (Perú → PEN) |
| `status` | `VARCHAR(20)` | - | Sí | `'pending'` | Estado (`pending`, `approved`, `rejected`, `cancelled`) |
| `mp_preference_id` | `VARCHAR(100)` | - | No | `null` | Preference ID creada en Mercado Pago |
| `external_payment_id` | `VARCHAR(100)` | UK | No | `null` | Payment ID del webhook de Mercado Pago — **único** (idempotencia) |
| `paid_at` | `TIMESTAMPTZ` | - | No | `null` | Momento de la confirmación del pago |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de emisión |
| `updated_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de última modificación |

* **Relaciones (Integridad Lógica):**
  * `N:1` hacia `user_accounts` (`user_id` referencia lógica).
* **Restricciones (Constraints):**
  * `pk_credit_purchase_orders`: `PRIMARY KEY (id)`
  * `uk_credit_purchase_orders_external_payment_id`: `UNIQUE (external_payment_id)` — **idempotencia: el mismo `payment_id` nunca acredita dos veces** (ante reintentos del webhook, `INSERT ... ON CONFLICT DO NOTHING`).
  * `chk_credit_purchase_orders_status`: `CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled'))`
  * `chk_credit_purchase_orders_credits`: `CHECK (credits_to_grant > 0)`
  * `chk_credit_purchase_orders_price`: `CHECK (unit_price >= 0)`
* **Índices Físicos (B-Tree):**
  * `credit_purchase_orders_user_id_idx`: B-Tree sobre `(user_id)`.
  * `credit_purchase_orders_status_idx`: B-Tree sobre `(status)` — para jobs administrativos.
  * La unicidad de `external_payment_id` ya genera su índice implícito.

---

## 5. Shared Kernel Context (Infraestructura Transversal & Transactional Outbox)
**Módulo Backend:** `app.shared.infrastructure`

Gobierna los componentes transversales de persistencia física: el mixin de auditoría temporal estándar (`AuditablePersistenceMixin`) compartido por todos los modelos relacionales de la plataforma, y la tabla física `outbox_events` que materializa el patrón de diseño arquitectónico **Transactional Outbox**.

### 5.1 `outbox_events` (Eventos de Dominio para Publicación Confiable)

Almacena de forma atómica y duradera los eventos de dominio producidos por las raíces de agregado de cualquier Bounded Context (`IAM`, `Itineraries`, `Credits & Payments`). Al persistir el evento en la misma transacción ACID de PostgreSQL en la que se actualiza el agregado, se elimina el problema de doble escritura (*dual-write problem*). Un proceso de fondo (*Outbox Relay Worker*) desacola los registros pendientes mediante consultas concurrentes no bloqueantes (`FOR UPDATE SKIP LOCKED`) y los despacha hacia el bus de eventos en memoria o brokers externos, garantizando entrega *at-least-once*.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
|---|---|---|---|---|---|
| `id` | `BIGINT GENERATED ALWAYS AS IDENTITY` | PK | Sí | - | Identificador técnico secuencial monótono de 64 bits para ordenamiento estricto |
| `event_id` | `UUID` | UK | Sí | - | Identificador universal del evento para deduplicación e idempotencia en consumidores |
| `aggregate_type` | `VARCHAR(64)` | - | Sí | - | Nombre formal del agregado emisor (ej. `UserAccount`, `Itinerary`, `CreditWallet`) |
| `aggregate_id` | `VARCHAR(64)` | - | Sí | - | Identificador del agregado emisor representado como cadena |
| `event_type` | `VARCHAR(128)` | - | Sí | - | Nombre calificado de la clase del evento de dominio (ej. `ItineraryCreatedEvent`) |
| `payload` | `JSONB` | - | Sí | - | Cuerpo serializado del evento en formato JSON estructurado |
| `occurred_on` | `TIMESTAMPTZ` | - | Sí | - | Marca temporal en UTC en la que ocurrió el suceso dentro del agregado |
| `status` | `VARCHAR(20)` | - | Sí | `'PENDING'` | Estado de despacho (`PENDING`, `PUBLISHED`, `FAILED`) |
| `retry_count` | `INTEGER` | - | Sí | `0` | Número de reintentos de publicación fallidos ejecutados por el worker |
| `last_error` | `TEXT` | - | No | `null` | Traza del último error capturado durante el intento de despacho |
| `processed_at` | `TIMESTAMPTZ` | - | No | `null` | Marca temporal en UTC en la que el evento fue despachado exitosamente |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de inserción del registro físico en PostgreSQL (heredado de `AuditablePersistenceMixin`) |
| `updated_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de última modificación del registro físico (heredado de `AuditablePersistenceMixin`) |

* **Relaciones (Integridad Lógica / Desacoplamiento DDD):**
  * `N:1` desacoplada hacia los agregados de los bounded contexts emisores mediante la tupla polimórfica `(aggregate_type, aggregate_id)`. No se declaran llaves foráneas duras para preservar la independencia y autonomía modular de cada Bounded Context.
* **Restricciones (Constraints):**
  * `pk_outbox_events`: `PRIMARY KEY (id)`
  * `uk_outbox_events_event_id`: `UNIQUE (event_id)`
  * `chk_outbox_events_status`: `CHECK (status IN ('PENDING', 'PUBLISHED', 'FAILED'))`
  * `chk_outbox_events_retry_count`: `CHECK (retry_count >= 0)`
* **Índices Físicos (B-Tree):**
  * `ix_outbox_events_status_occurred_on`: B-Tree compuesto sobre `(status, occurred_on)`. Índice vital de alta selectividad para el *Outbox Relay Worker*: permite ejecutar `SELECT ... WHERE status = 'PENDING' ORDER BY occurred_on ASC LIMIT N FOR UPDATE SKIP LOCKED` en tiempo submilisegundo sin realizar table scans.
  * `ix_outbox_events_aggregate`: B-Tree compuesto sobre `(aggregate_type, aggregate_id)` para auditoría y trazabilidad histórica de eventos por entidad.
  * `ix_outbox_events_event_id`: Generado implícitamente por la restricción `UNIQUE (event_id)`.
  * `ix_outbox_events_event_type`: B-Tree sobre `(event_type)` para filtrado por tipología de evento en tareas de reintento o reenvío selectivo.

---

## 6. Modelo de Datos en Memoria — Redis 7 (Caché, Atomicidad y Rate Limiting)

Conforme a las directrices de `redis-core` y `redis-best-practices`, Redis se emplea exclusivamente para estructuras de acceso de alta frecuencia, contadores atómicos y caché volátil. Todo dato en Redis posee una estrategia definida de respaldo o recarga autoritativa (*Lazy-Load*) desde PostgreSQL.

### 6.1 Convención Canónica de Nombres de Claves (Keyspace)

Se adopta la convención de segmentos en minúsculas delimitados por dos puntos (`:`):
```
navby:{entidad}:{identificador}:{atributo_o_subclave}
```

### 6.2 Catálogo de Claves y Estructuras de Datos

| Patrón de Clave | Estructura Redis | TTL / Expiración | Política de Evicción | Propósito Operativo |
| :--- | :--- | :--- | :--- | :--- |
| `navby:credits:{user_id}` | **Hash** (`free_credits`, `paid_credits`, `version`) | Sin expiración o 86400s (24 h) | Lazy-load desde `credit_wallets` ante MISS | Billetera de créditos para lectura y deducción atómica en microsegundos vía Lua. |
| `navby:cache:quote:{cache_key}` | **String** (JSON serializado de `QuoteOption[]`) | 1800s a 3600s (30–60 min) | Volátil (se recalcula o consulta fallback PG) | Fast-path del Cache-Aside canónico. Alivia el 100% del costo externo ante HIT. |
| `navby:quota:flightapi:used:{YYYY-MM-DD}` | **String** (Contador entero, `INCRBY`) | 172800s (48 h) | Volátil (reinicio diario automático) | Control de presupuesto global diario del proveedor Flight API (límite 1,000 req/día). |
| `navby:ratelimit:{ip_o_user}:{endpoint}:{YYYYMMDDHHMM}` | **String** (Contador entero, `INCR`) | 60s (1 minuto) | Expiración automática estricta | Rate limiting por ventana fija para mitigar abuso en endpoints públicos. |

### 6.3 Script Lua Canónico de Débito Atómico (`navby:credits:{user_id}`)

Para erradicar condiciones de carrera en ráfagas de consultas concurrentes, la deducción se ejecuta en un único paso atómico dentro del motor de Redis:

```lua
local key = KEYS[1]
local cost = tonumber(ARGV[1])

if redis.call('EXISTS', key) == 0 then
    return -2 -- Señal de MISS: Aplicar Lazy-Load desde PostgreSQL credit_wallets
end

local free = tonumber(redis.call('HGET', key, 'free_credits') or '0')
local paid = tonumber(redis.call('HGET', key, 'paid_credits') or '0')

if (free + paid) < cost then
    return -1 -- Saldo insuficiente: Disparar 402 Payment Required
end

local free_deducted = math.min(free, cost)
local paid_deducted = cost - free_deducted

redis.call('HINCRBY', key, 'free_credits', -free_deducted)
redis.call('HINCRBY', key, 'paid_credits', -paid_deducted)
redis.call('HINCRBY', key, 'version', 1)

return 1 -- Deducción exitosa
```

---

## 7. Nota de Exclusión: lo que NO vive en esta base de datos

* **El grafo de aeropuertos y rutas (OpenFlights):** no se persiste en tablas. Su fuente de verdad son los archivos `.dat` versionados ([`docs/datasets/`](../datasets/)) y se reconstruye en memoria en cada arranque del backend (ver [navby-platform-architecture.md](navby-platform-architecture.md) §4). Esto elimina duplicidad y *drift* de datos.
* **Caché caliente, rate limiting, contadores en tiempo real y espejos de saldo:** viven en **Redis** (`navby:cache:quote:{hash}`, `navby:credits:{user_id}`, `navby:ratelimit:{user_o_ip}`, etc.), no en PostgreSQL. `quote_caches` y `api_credit_usages` son su respaldo/auditoría duradera; `credit_wallets` es la fuente de verdad de saldos (Redis solo espejo).
* **Historial de búsquedas no guardadas:** las búsquedas efímeras no se persisten; solo se guarda cuando el usuario decide *guardar* el itinerario (decisión de producto).

## 8. Resumen de Tablas Relacionales (PostgreSQL 16)

| Módulo | Tabla | Naturaleza |
| :--- | :--- | :--- |
| IAM | `user_accounts` | Entidad raíz de usuario (local + Google OAuth) |
| IAM | `refresh_tokens` | Sesiones revocables (hash SHA-256) |
| IAM | `verification_tokens` | Tokens de un solo uso (OTP de email, reset de contraseña) |
| Itineraries | `itineraries` | Viaje planificado (ruta = snapshot JSONB) |
| Itineraries | `itinerary_quotes` | Top-3 precios por itinerario (snapshot con `quoted_at`) |
| Quotes | `quote_caches` | Respaldo persistente del caché de cotizaciones |
| Quotes | `api_credit_usages` | Auditoría append-only del consumo de créditos de Flight API |
| Credits | `credit_wallets` | Billetera por usuario (saldo gratis + pagado) |
| Credits | `credit_ledger_entries` | Ledger append-only de movimientos de créditos |
| Credits | `credit_purchase_orders` | Órdenes de compra vía Mercado Pago (idempotentes) |
| Shared Kernel | `outbox_events` | Publicación atómica de eventos de dominio (Transactional Outbox) |
