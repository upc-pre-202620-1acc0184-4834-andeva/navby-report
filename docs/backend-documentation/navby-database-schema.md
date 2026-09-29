# Modelo de Base de Datos y Persistencia por Bounded Contexts (Navby Platform)

Este documento define la arquitectura integral de almacenamiento y persistencia física de **Navby Platform** (PostgreSQL 16 para agregados duraderos y Redis 7 para aceleración en memoria, caché volátil y control de concurrencia atómica, ambos desplegados en contenedores Docker oficiales sobre Azure VM `Standard_B2s`), mapeada de forma estricta a los Bounded Contexts establecidos en la arquitectura táctica Domain-Driven Design (DDD) y Clean Architecture del sistema.

<!-- prettier-ignore -->
> [!NOTE]
> **Convención Arquitectónica Transversal y Persistencia Políglota:**
> 1. **Identificadores Universales Inmutables (`UUID`):** Para garantizar el desacoplamiento modular y prevenir la fuga de secuencias correlativas entre módulos, todas las claves primarias técnicas en PostgreSQL emplean el tipo `UUID` generado nativamente en PostgreSQL 16 mediante `gen_random_uuid()`.
> 2. **Aislamiento Físico de Datos (Regla Zero Cross-Module FKs):** Queda terminantemente prohibido declarar claves foráneas físicas (`FOREIGN KEY`) entre tablas de distintos Bounded Contexts. La vinculación entre agregados de módulos diferentes se realiza exclusivamente mediante identificadores lógicos inmutables (`user_id`, `origin_iata`), preservando la autonomía transaccional de cada módulo.
> 3. **Separación de Responsabilidades de Almacenamiento:** PostgreSQL 16 custodia el estado duradero, la consistencia ACID contable y la auditoría histórica. Redis 7 opera como capa de aceleración en memoria (*Hot Data*), resolviendo caché volátil de cotizaciones externas, control de cuotas (*Rate Limiting*) y mutaciones atómicas de saldo en microsegundos.
> 4. **Control de Concurrencia Optimista (`version`):** Todas las entidades mutables en PostgreSQL y los registros de saldo en Redis incorporan un contador `version` que se incrementa en cada actualización para prevenir colisiones y actualizaciones perdidas (*lost updates*).
> 5. **Trazabilidad y Marcas Temporales:** Las marcas de auditoría utilizan el tipo `TIMESTAMPTZ` con zona horaria UTC (`NOW()`). Las entidades mutables gestionan `updated_at` a nivel de aplicación (SQLAlchemy 2.0 / Unit of Work).
> 6. **Borrado Físico:** En consonancia con la regla anti-sobreingeniería, no se implementa borrado lógico (*Soft Delete*). Los itinerarios o tokens eliminados se borran físicamente mediante `DELETE` relacional con cascada interna controlada (`ON DELETE CASCADE`).

---

## Mapeo Estratégico: Bounded Contexts ↔ Persistencia Políglota

Navby adopta una persistencia políglota pragmática dividida entre almacenamiento relacional duradero y estructuras optimizadas en memoria:

### Persistencia Relacional Duradera (PostgreSQL 16)

La siguiente matriz clasifica la persistencia relacional duradera de cada Bounded Context dentro de la plataforma:

| Bounded Context | Tipo de Subdominio | Persistencia en PostgreSQL 16 | Tablas Físicas Asignadas | Justificación y Estrategia de Almacenamiento |
| :--- | :---: | :---: | :--- | :--- |
| **Routing** | **Core** | ❌ **Ninguna (0 tablas)** | *(Ninguna)* | Topología de OpenFlights (3,354 nodos y 37,326 aristas) y algoritmos A*/BFS operan 100% en memoria RAM (~10 MB) precargados en `lifespan`. |
| **Quotes** | **Core** | ❌ **Ninguna (0 tablas)** | *(Ninguna)* | Motor de cotizaciones en tiempo real respaldado en Redis 7 (TTL 30 min) a costo $0. Los precios capturados se congelan en Itineraries cuando el usuario decide guardar. |
| **Itineraries** | **Supporting** | ✅ **Sí (2 tablas)** | `itineraries`, `itinerary_quotes` | Custodia de planes de viaje guardados con congelamiento de ruta y podio de ofertas en documentos inmutables JSONB. |
| **Billing** | **Supporting** | ✅ **Sí (3 tablas)** | `credit_wallets`, `credit_transactions`, `credit_orders` | Libro mayor inmutable de créditos prepagos, órdenes de recarga vía Mercado Pago y balance autoritativo de cuentas. |
| **IAM** | **Generic** | ✅ **Sí (3 tablas)** | `users`, `refresh_tokens`, `verification_tokens` | Directorio de identidades, credenciales protegidas con BCrypt (12 rondas), sesiones JWT con rotación y códigos OTP. |
| **Shared Kernel** | **Transversal** | ✅ **Sí (1 tabla)** | `outbox_events` | Infraestructura del patrón Transactional Outbox para publicación confiable y atómica de eventos de integración. |

De los cinco Bounded Contexts y el Shared Kernel, cuatro componentes gestionan persistencia física en PostgreSQL 16, totalizando **9 tablas relacionales**.

### Almacenamiento Acelerado en Memoria (Redis 7)

La siguiente matriz detalla las estructuras activas en Redis 7 bajo las directrices de diseño de `redis-core` y `redis-best-practices`:

| Bounded Context | Rol Operativo en Redis 7 | Estructura de Datos | Patrón de Clave Canónica | TTL / Política | Propósito y Garantía de Rendimiento |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **Quotes** | Cache-Aside de Cotizaciones | String (JSON) | `navby:quotes:cache:{cache_key}` | 1,800 s (30 min) | Latencia < 5 ms en búsquedas idénticas; evita sobrecostos de API y cargos duplicados de créditos. |
| **Quotes** | Quota Guard Diario | String (Integer) | `navby:quotes:quota:flightapi:{date}` | 172,800 s (48 h) | Contador atómico diario (`INCR`) para garantizar el límite mensual de peticiones externas gratuitas. |
| **Billing** | Hot Wallet Balance Mirror | Hash | `navby:billing:wallets:{user_id}` | 86,400 s + Jitter | Réplica en memoria de saldo de créditos con débito atómico submilisegundo mediante script Lua. |
| **Billing** | Mutex Idempotencia Webhook | String | `navby:billing:lock:webhook:{payment_id}` | 120 s | Cerrojo distribuido (`SETNX`) para procesar exactamente una vez cada notificación de Mercado Pago. |
| **IAM** | Limitador de Tasa (Rate Limit) | String (Integer) | `navby:iam:ratelimit:{client}:{endpoint}:{window}` | 60 s | Contador por ventana fija contra abusos de tráfico y ataques de denegación de servicio (DoS). |
| **IAM** | Mitigación de Fuerza Bruta | String (Integer) | `navby:iam:login_attempts:{email_hash}` | 900 s (15 min) | Bloqueo temporal progresivo de autenticación tras intentos fallidos repetidos de acceso. |

---

## 1. Identity and Access Management Context (IAM)
**Módulo Backend:** `src/modules/iam`

Gobierna la seguridad perimetral, el registro de cuentas locales, la autenticación federada con Google Identity Services (OAuth 2.0 / OIDC), la gestión de credenciales criptográficas y el ciclo de vida de las sesiones de usuario mediante rotación de tokens JWT.

### 1.1 `users` (Cuentas de Usuario e Identidad Central)
Entidad raíz del contexto IAM. Representa a una persona registrada en la plataforma Navby, custodiando sus datos de contacto, método de acceso y rol operativo.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `UUID` | PK | Sí | `gen_random_uuid()` | Identificador universal inmutable de la cuenta de usuario |
| `email` | `VARCHAR(150)` | UK | Sí | - | Correo electrónico unívoco normalizado en minúsculas (login principal) |
| `password_hash` | `VARCHAR(255)` | - | No | `null` | Hash criptográfico generado mediante BCrypt (costo 12). Obligatorio para cuentas locales |
| `username` | `VARCHAR(50)` | UK | Sí | - | Nombre de usuario único e identificador público de la cuenta en la plataforma |
| `auth_provider` | `VARCHAR(20)` | - | Sí | `'local'` | Proveedor de identidad (`local`, `google`) |
| `google_id` | `VARCHAR(255)` | UK | No | `null` | Identificador inmutable federado de Google (`sub` del token OIDC) |
| `role` | `VARCHAR(20)` | - | Sí | `'passenger'` | Rol de autorización (`passenger`, `admin`) |
| `status` | `VARCHAR(20)` | - | Sí | `'pending_verification'` | Estado operativo (`pending_verification`, `active`, `suspended`) |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal inmutable de registro en UTC |
| `updated_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de última modificación en UTC |
| `version` | `BIGINT` | - | Sí | `0` | Contador para control de concurrencia optimista |

* **Relaciones Internas (Integridad Referencial en IAM):**
  * `1:N` hacia `refresh_tokens` (Un usuario mantiene sesiones en múltiples dispositivos).
  * `1:N` hacia `verification_tokens` (Un usuario recibe códigos OTP de activación o reset).
* **Relaciones Lógicas Cross-Context (Sin Foreign Key Física):**
  * `1:1` hacia `credit_wallets` en Billing Context mediante el identificador `users.id`.
  * `1:N` hacia `itineraries` en Itineraries Context mediante el identificador `users.id`.
  * `1:N` hacia `credit_orders` en Billing Context mediante el identificador `users.id`.
* **Restricciones (Constraints):**
  * `pk_users`: `PRIMARY KEY (id)`
  * `uk_users_email`: `UNIQUE (email)`
  * `uk_users_username`: `UNIQUE (username)`
  * `uk_users_google_id`: `UNIQUE (google_id)`
  * `chk_users_auth_provider`: `CHECK (auth_provider IN ('local', 'google'))`
  * `chk_users_role`: `CHECK (role IN ('passenger', 'admin'))`
  * `chk_users_status`: `CHECK (status IN ('pending_verification', 'active', 'suspended'))`
  * `chk_users_local_password`: `CHECK (auth_provider <> 'local' OR password_hash IS NOT NULL)`
* **Índices Físicos (B-Tree):**
  * `idx_users_email`: B-Tree implícito por la restricción `UNIQUE (email)` para autenticación rápida.
  * `idx_users_username`: B-Tree implícito por la restricción `UNIQUE (username)` para resolución de perfiles y menciones.
  * `idx_users_google_id`: B-Tree parcial sobre `(google_id) WHERE google_id IS NOT NULL` para inicios de sesión OIDC.
  * `idx_users_status`: B-Tree sobre `(status)` para tareas administrativas de activación.

---

### 1.2 `refresh_tokens` (Tokens de Refresco y Rotación de Sesiones)
Custodia los tokens de refresco de sesión activa en formato hash (SHA-256). Implementa el patrón *Token Family* para invalidar cadenas de tokens en caso de sospecha de robo o reutilización fraudulenta.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `UUID` | PK | Sí | `gen_random_uuid()` | Identificador técnico del token de refresco |
| `user_id` | `UUID` | FK | Sí | - | Identificador de la cuenta propietaria (`FK -> users(id) ON DELETE CASCADE`) |
| `token_hash` | `VARCHAR(255)` | UK | Sí | - | Resumen criptográfico SHA-256 del token emitido (el token en texto claro nunca se almacena) |
| `family_id` | `UUID` | - | Sí | - | Identificador de la familia criptográfica de tokens para detección de rotación indebida |
| `is_revoked` | `BOOLEAN` | - | Sí | `false` | Bandera de revocación explícita (por logout o rotación) |
| `expires_at` | `TIMESTAMPTZ` | - | Sí | - | Fecha y hora límite de vigencia de la sesión (máximo 7 días) |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de emisión del token |

* **Relaciones Internas (Integridad Referencial):**
  * `N:1` hacia `users` (`user_id` referencia a `users.id` con eliminación en cascada).
* **Restricciones (Constraints):**
  * `pk_refresh_tokens`: `PRIMARY KEY (id)`
  * `fk_refresh_tokens_user`: `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`
  * `uk_refresh_tokens_hash`: `UNIQUE (token_hash)`
* **Índices Físicos (B-Tree):**
  * `idx_refresh_tokens_user_id`: B-Tree sobre `(user_id)` para revocación de sesiones por usuario.
  * `idx_refresh_tokens_family_id`: B-Tree sobre `(family_id)` para revocación masiva ante reutilización ilícita.
  * `idx_refresh_tokens_expires_at`: B-Tree sobre `(expires_at)` para jobs de purga de sesiones vencidas.

---

### 1.3 `verification_tokens` (Códigos OTP y Tokens de Un Solo Uso)
Almacena códigos de verificación temporal (códigos OTP de 6 dígitos numéricos para activación de cuenta por correo electrónico y tokens para restablecimiento de contraseña).

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `UUID` | PK | Sí | `gen_random_uuid()` | Identificador técnico del código de verificación |
| `user_id` | `UUID` | FK | Sí | - | Cuenta destinataria del código (`FK -> users(id) ON DELETE CASCADE`) |
| `token_hash` | `VARCHAR(255)` | - | Sí | - | Resumen SHA-256 del código OTP o token enviado por correo |
| `type` | `VARCHAR(30)` | - | Sí | - | Finalidad (`email_verification`, `password_reset`) |
| `expires_at` | `TIMESTAMPTZ` | - | Sí | - | Marca temporal límite de validez (OTP: 10 minutos; Reset: 1 hora) |
| `used_at` | `TIMESTAMPTZ` | - | No | `null` | Momento exacto de consumo (`null` = token disponible; no null = consumido) |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de generación del código |

* **Relaciones Internas (Integridad Referencial):**
  * `N:1` hacia `users` (`user_id` referencia a `users.id` con eliminación en cascada).
* **Restricciones (Constraints):**
  * `pk_verification_tokens`: `PRIMARY KEY (id)`
  * `fk_verification_tokens_user`: `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`
  * `chk_verification_tokens_type`: `CHECK (type IN ('email_verification', 'password_reset'))`
* **Índices Físicos (B-Tree):**
  * `idx_verification_tokens_lookup`: B-Tree compuesto sobre `(user_id, type, used_at)` para consulta instantánea de tokens activos.
  * `idx_verification_tokens_expires_at`: B-Tree sobre `(expires_at)` para limpieza programada de registros caducados.

---

## 2. Itineraries Context (Planes de Vuelo Guardados)
**Módulo Backend:** `src/modules/itineraries`

Gobierna la custodia duradera de las planificaciones de vuelo guardadas por los usuarios. Congela la trayectoria física del viaje y el podio de ofertas capturadas en documentos inmutables JSONB, garantizando que el viaje permanezca accesible e inalterado aun si las cotizaciones en Redis expiran o la topología de OpenFlights se actualiza.

### 2.1 `itineraries` (Planes de Viaje Guardados)
Entidad raíz del contexto Itineraries. Representa una planificación guardada por un usuario registrado, indexada por origen, destino y fecha.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `UUID` | PK | Sí | `gen_random_uuid()` | Identificador único del itinerario guardado |
| `user_id` | `UUID` | - | Sí | - | Propietario del plan (referencia lógica a `users.id` en IAM; sin FK física) |
| `name` | `VARCHAR(100)` | - | Sí | - | Denominación asignada por el usuario (ej. «Viaje a Madrid 2026») |
| `origin_iata` | `CHAR(3)` | - | Sí | - | Código IATA del aeropuerto de origen (ej. `'LIM'`) |
| `destination_iata` | `CHAR(3)` | - | Sí | - | Código IATA del aeropuerto de destino (ej. `'MAD'`) |
| `origin_city` | `VARCHAR(100)` | - | Sí | - | Nombre de la ciudad de partida para visualización en interfaz |
| `destination_city` | `VARCHAR(100)` | - | Sí | - | Nombre de la ciudad de llegada para visualización en interfaz |
| `departure_date` | `DATE` | - | Sí | - | Fecha de salida programada para el viaje |
| `return_date` | `DATE` | - | No | `null` | Fecha de retorno (`null` para viajes de solo ida) |
| `adults` | `SMALLINT` | - | Sí | `1` | Cantidad de pasajeros adultos ($\ge 1$) |
| `children` | `SMALLINT` | - | Sí | `0` | Cantidad de pasajeros niños |
| `infants` | `SMALLINT` | - | Sí | `0` | Cantidad de infantes |
| `cabin_class` | `VARCHAR(20)` | - | Sí | `'Economy'` | Clase de cabina (`Economy`, `Premium_Economy`, `Business`, `First`) |
| `currency` | `CHAR(3)` | - | Sí | `'USD'` | Código de divisa ISO 4217 de los precios de referencia |
| `route_snapshot` | `JSONB` | - | Sí | - | Snapshot inmutable de la trayectoria física calculada (secuencia de escalas, distancias, tiempo y waypoints) |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de guardado del itinerario |
| `updated_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de última modificación del nombre o detalles |
| `version` | `BIGINT` | - | Sí | `0` | Contador para control de concurrencia optimista |

* **Relaciones Internas (Integridad Referencial en Itineraries):**
  * `1:N` hacia `itinerary_quotes` (El itinerario retiene su podio histórico de cotizaciones).
* **Relaciones Lógicas Cross-Context (Sin Foreign Key Física):**
  * `N:1` hacia `users` en IAM Context mediante `itineraries.user_id`.
* **Restricciones (Constraints):**
  * `pk_itineraries`: `PRIMARY KEY (id)`
  * `chk_itineraries_distinct_airports`: `CHECK (origin_iata <> destination_iata)`
  * `chk_itineraries_dates`: `CHECK (return_date IS NULL OR return_date >= departure_date)`
  * `chk_itineraries_adults`: `CHECK (adults >= 1)`
  * `chk_itineraries_children`: `CHECK (children >= 0)`
  * `chk_itineraries_infants`: `CHECK (infants >= 0 AND infants <= adults)`
  * `chk_itineraries_total_passengers`: `CHECK (adults + children + infants <= 9)`
  * `chk_itineraries_cabin_class`: `CHECK (cabin_class IN ('Economy', 'Premium_Economy', 'Business', 'First'))`
* **Índices Físicos (B-Tree):**
  * `idx_itineraries_user_id`: B-Tree sobre `(user_id)` para listar los planes de un usuario.
  * `idx_itineraries_user_created`: B-Tree compuesto sobre `(user_id, created_at DESC)` para ordenamiento cronológico.

---

### 2.2 `itinerary_quotes` (Snapshot de Ofertas Comerciales Capturadas)
Almacena el podio de las tres mejores ofertas de mercado capturadas en el instante del guardado (`rank` 1 a 3), preservando las tarifas, aerolíneas y enlaces oficiales de compra (*deep links*).

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `UUID` | PK | Sí | `gen_random_uuid()` | Identificador técnico del snapshot de oferta |
| `itinerary_id` | `UUID` | FK | Sí | - | Itinerario asociado (`FK -> itineraries(id) ON DELETE CASCADE`) |
| `rank` | `SMALLINT` | - | Sí | - | Posición en el podio de optimalidad de Pareto (1 = mejor balance/precio) |
| `price` | `DECIMAL(12,2)` | - | Sí | - | Tarifa monetaria total capturada para todos los pasajeros |
| `currency` | `CHAR(3)` | - | Sí | `'USD'` | Código de divisa ISO 4217 de la tarifa |
| `total_duration_minutes` | `INTEGER` | - | Sí | - | Duración total acumulada del itinerario en minutos |
| `stops` | `SMALLINT` | - | Sí | `0` | Cantidad de escalas intermedias del vuelo |
| `airline_codes` | `VARCHAR(100)` | - | Sí | - | Códigos IATA de las aerolíneas operadoras (ej. `'LA, AV'`) |
| `airline_names` | `VARCHAR(255)` | - | Sí | - | Denominaciones comerciales de las aerolíneas |
| `deep_link` | `TEXT` | - | Sí | - | Enlace verificado y firmado hacia el portal oficial de la aerolínea |
| `quoted_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal exacta de captura de la cotización externa |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de inserción del registro físico |

* **Relaciones Internas (Integridad Referencial):**
  * `N:1` hacia `itineraries` (`itinerary_id` referencia a `itineraries.id` con eliminación en cascada).
* **Restricciones (Constraints):**
  * `pk_itinerary_quotes`: `PRIMARY KEY (id)`
  * `fk_itinerary_quotes_itinerary`: `FOREIGN KEY (itinerary_id) REFERENCES itineraries(id) ON DELETE CASCADE`
  * `uk_itinerary_quotes_rank`: `UNIQUE (itinerary_id, rank)`
  * `chk_itinerary_quotes_rank`: `CHECK (rank BETWEEN 1 AND 3)`
  * `chk_itinerary_quotes_price`: `CHECK (price >= 0.0)`
  * `chk_itinerary_quotes_stops`: `CHECK (stops >= 0)`
* **Índices Físicos (B-Tree):**
  * `idx_itinerary_quotes_itinerary_id`: B-Tree sobre `(itinerary_id)` para carga eagerly del podio asociado.

---

## 3. Billing Context (Monetización Prepaga y Créditos)
**Módulo Backend:** `src/modules/billing`

Gestiona la economía interna de la plataforma basada en créditos de uso, la venta de paquetes comerciales mediante Mercado Pago Checkout Pro, la verificación criptográfica HMAC de webhooks de pago y el asentamiento inmutable de cada transacción en un libro mayor (*ledger*).

### 3.1 `credit_wallets` (Billetera Virtual de Créditos de Usuario)
Entidad autoritativa de saldo por usuario (relación 1:1 lógica con IAM). Redis mantiene el espejo caliente de alta velocidad para deducciones atómicas vía scripts Lua, pero `credit_wallets` es la fuente de verdad persistente y duradera.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `UUID` | PK | Sí | `gen_random_uuid()` | Identificador técnico único de la billetera virtual |
| `user_id` | `UUID` | UK | Sí | - | Titular de la cuenta (referencia lógica a `users.id` en IAM; sin FK física) |
| `balance` | `INTEGER` | - | Sí | `10` | Saldo consolidado total de créditos disponibles ($\ge 0$) |
| `free_credits` | `SMALLINT` | - | Sí | `10` | Créditos de bienvenida o cortesía otorgados por la plataforma |
| `paid_credits` | `INTEGER` | - | Sí | `0` | Créditos adquiridos mediante compra comercial (no vencen) |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de alta de la billetera |
| `updated_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de última mutación del saldo |
| `version` | `BIGINT` | - | Sí | `0` | Contador para control de concurrencia optimista |

* **Relaciones Internas (Integridad Referencial en Billing):**
  * `1:N` hacia `credit_transactions` (Una billetera audita su historial de movimientos).
* **Relaciones Lógicas Cross-Context (Sin Foreign Key Física):**
  * `1:1` hacia `users` en IAM Context mediante `credit_wallets.user_id`.
* **Restricciones (Constraints):**
  * `pk_credit_wallets`: `PRIMARY KEY (id)`
  * `uk_credit_wallets_user_id`: `UNIQUE (user_id)`
  * `chk_credit_wallets_balance`: `CHECK (balance >= 0)`
  * `chk_credit_wallets_free`: `CHECK (free_credits >= 0)`
  * `chk_credit_wallets_paid`: `CHECK (paid_credits >= 0)`
  * `chk_credit_wallets_total`: `CHECK (balance = free_credits + paid_credits)`
* **Índices Físicos (B-Tree):**
  * `idx_credit_wallets_user_id`: B-Tree implícito por la restricción `UNIQUE (user_id)` para lecturas de saldo en < 1 ms.

---

### 3.2 `credit_transactions` (Libro Mayor Inmutable de Créditos)
Registro append-only (estrictamente de solo inserción) que audita cada movimiento que incrementa o debita créditos de la billetera. Garantiza trazabilidad contable absoluta.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `UUID` | PK | Sí | `gen_random_uuid()` | Identificador único de la transacción contable |
| `wallet_id` | `UUID` | FK | Sí | - | Billetera afectada (`FK -> credit_wallets(id) ON DELETE RESTRICT`) |
| `user_id` | `UUID` | - | Sí | - | Titular del movimiento (referencia lógica a `users.id`) |
| `transaction_type` | `VARCHAR(30)` | - | Sí | - | Naturaleza (`SIGNUP_BONUS`, `PURCHASE_CREDIT`, `ROUTE_QUOTE_DEBIT`, `REFUND`, `MANUAL_ADJUSTMENT`) |
| `amount` | `INTEGER` | - | Sí | - | Cantidad transferida (positivo para abono, negativo para consumo; $\ne 0$) |
| `balance_after` | `INTEGER` | - | Sí | - | Saldo resultante en la billetera inmediatamente posterior al movimiento ($\ge 0$) |
| `reason` | `VARCHAR(255)` | - | Sí | - | Motivo descriptivo (ej. «Búsqueda de cotización LIM-MIA», «Recarga Paquete 50») |
| `reference_id` | `VARCHAR(100)` | - | No | `null` | Identificador de correlación (ID de orden de compra o hash de cotización) |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de registro inmutable en el libro mayor |

* **Relaciones Internas (Integridad Referencial):**
  * `N:1` hacia `credit_wallets` (`wallet_id` referencia a `credit_wallets.id` con `ON DELETE RESTRICT` para evitar pérdida de registros contables).
* **Restricciones (Constraints):**
  * `pk_credit_transactions`: `PRIMARY KEY (id)`
  * `fk_credit_transactions_wallet`: `FOREIGN KEY (wallet_id) REFERENCES credit_wallets(id) ON DELETE RESTRICT`
  * `chk_credit_transactions_type`: `CHECK (transaction_type IN ('SIGNUP_BONUS', 'PURCHASE_CREDIT', 'ROUTE_QUOTE_DEBIT', 'REFUND', 'MANUAL_ADJUSTMENT'))`
  * `chk_credit_transactions_amount`: `CHECK (amount <> 0)`
  * `chk_credit_transactions_balance`: `CHECK (balance_after >= 0)`
* **Índices Físicos (B-Tree):**
  * `idx_credit_transactions_wallet_id`: B-Tree sobre `(wallet_id)` para auditorías internas.
  * `idx_credit_transactions_user_created`: B-Tree compuesto sobre `(user_id, created_at DESC)` para el listado cronológico de movimientos del usuario.

---

### 3.3 `credit_orders` (Órdenes de Compra de Créditos vía Mercado Pago)
Registra las intenciones y confirmaciones de compra de paquetes comerciales de créditos. Gestiona la preferencia de pago en Mercado Pago Checkout Pro y aplica idempotencia criptográfica ante reintentos de webhooks de notificación.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `UUID` | PK | Sí | `gen_random_uuid()` | Identificador único de la orden de compra |
| `user_id` | `UUID` | - | Sí | - | Comprador (referencia lógica a `users.id` en IAM; sin FK física) |
| `package_code` | `VARCHAR(30)` | - | Sí | - | Código del paquete adquirido (`pack_50`, `pack_100`, `pack_250`) |
| `credits_amount` | `INTEGER` | - | Sí | - | Cantidad de créditos comerciales a transferir (50, 100, 250) |
| `unit_price` | `DECIMAL(10,2)` | - | Sí | - | Precio formal cobrado en la pasarela |
| `currency` | `CHAR(3)` | - | Sí | `'PEN'` | Moneda del cobro comercial (PEN o USD) |
| `status` | `VARCHAR(20)` | - | Sí | `'PENDING'` | Estado de la orden (`PENDING`, `APPROVED`, `REJECTED`, `CANCELLED`) |
| `payment_provider` | `VARCHAR(30)` | - | Sí | `'MERCADO_PAGO'` | Pasarela de procesamiento |
| `mp_preference_id` | `VARCHAR(100)` | - | No | `null` | Identificador de preferencia generado en Mercado Pago Checkout Pro |
| `external_payment_id` | `VARCHAR(100)` | UK | No | `null` | Identificador de pago devuelto por Mercado Pago (garantía de idempotencia) |
| `paid_at` | `TIMESTAMPTZ` | - | No | `null` | Momento exacto de confirmación del cobro |
| `created_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de emisión de la orden |
| `updated_at` | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de última actualización de estado |
| `version` | `BIGINT` | - | Sí | `0` | Contador para control de concurrencia optimista |

* **Relaciones Lógicas Cross-Context (Sin Foreign Key Física):**
  * `N:1` hacia `users` en IAM Context mediante `credit_orders.user_id`.
* **Restricciones (Constraints):**
  * `pk_credit_orders`: `PRIMARY KEY (id)`
  * `uk_credit_orders_external_payment_id`: `UNIQUE (external_payment_id)`
  * `chk_credit_orders_status`: `CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED'))`
  * `chk_credit_orders_credits`: `CHECK (credits_amount > 0)`
  * `chk_credit_orders_price`: `CHECK (unit_price >= 0.0)`
* **Índices Físicos (B-Tree):**
  * `idx_credit_orders_user_id`: B-Tree sobre `(user_id)` para el historial de compras del usuario.
  * `idx_credit_orders_status`: B-Tree sobre `(status)` para conciliación y reintentos.
  * `idx_credit_orders_external_payment`: B-Tree implícito por la restricción `UNIQUE (external_payment_id)` que evita acreditar pagos duplicados ante reintentos de red.

---

## 4. Shared Kernel (Infraestructura Transversal y Transactional Outbox)
**Módulo Backend:** `src/shared/infrastructure`

Gobierna la persistencia de infraestructura común y aloja la tabla `outbox_events` que materializa el patrón de diseño arquitectónico **Transactional Outbox**. Este patrón elimina el problema de doble escritura (*dual-write problem*) al persistir eventos de integración en la misma transacción ACID de PostgreSQL en la que se muta cualquier agregado, garantizando entrega confiable *at-least-once*.

![Diagrama Entidad-Relación de Base de Datos para el Bounded Context Shared (PostgreSQL 16 y Redis 7)](../../report/assets/database-diagrams/database-diagram-shared.png){#fig:database-diagram-shared}

*Nota.* Elaboración propia en base al diseño físico de persistencia en PostgreSQL 16 y Redis 7 bajo el estándar PlantUML ERD.

### 4.1 Arquetipo Base de Persistencia y Mixin de Auditoría (BaseSqlAlchemyModel & AuditMixin)
Provee la superclase declarativa de persistencia en SQLAlchemy 2.0+ (`DeclarativeBase`, `AsyncAttrs`) y el mixin de auditoría temporal compartida por todas las entidades relacionales de la plataforma Navby. Este arquetipo centraliza la definición de claves primarias universales, el registro cronológico inmutable de mutaciones y la gobernanza determinista de metadatos.

#### Convenciones de Nomenclatura (`POSTGRES_NAMING_CONVENTION`)
Para garantizar migraciones reproducibles y deterministas mediante Alembic, evitando los identificadores anónimos o generados pseudoaleatoriamente por PostgreSQL, el arquetipo configura formalmente la plantilla `POSTGRES_NAMING_CONVENTION` en la colección de metadatos (`MetaData`):

* **Índices (`ix`):** `ix_%(column_0_label)s`
* **Restricciones de unicidad (`uq`):** `uq_%(table_name)s_%(column_0_name)s`
* **Restricciones check (`ck`):** `chk_%(table_name)s_%(constraint_name)s`
* **Claves foráneas intramodulares (`fk`):** `fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s`
* **Claves primarias (`pk`):** `pk_%(table_name)s`

#### Regla de Aislamiento Físico de Datos (*Zero Cross-Module FKs*)
En estricta observancia del desacoplamiento modular en arquitecturas Domain-Driven Design, las tablas de distintos Bounded Contexts tienen terminantemente prohibido declarar restricciones físicas de clave foránea (`FOREIGN KEY`) entre sí. Toda correlación o enlace intermodular se efectúa exclusivamente mediante identificadores lógicos inmutables de tipo `UUID`, como ocurre con el campo `user_id` en las tablas `itineraries`, `credit_wallets` y `credit_orders`. Esta regla técnica preserva la autonomía transaccional de cada módulo, previene contenciones o bloqueos en cascada y viabiliza la extracción futura a microservicios independientes sin migraciones destructivas de esquemas de base de datos.

#### Atributos Transversales de Auditoría (`AuditMixin`)
Todas las tablas de negocio heredan físicamente las columnas gestionadas por `AuditMixin`, consolidando un esquema homogéneo de identificación técnica y trazabilidad temporal:

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
| :----------------- | :------------- | :---: | :---: | :------------------ | :------------------------------------------------------------------------------------------------- |
| id | `UUID` | PK | Sí | `gen_random_uuid()` | Identificador técnico único global generado en base de datos (UUID v4) |
| created_at | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal inmutable en UTC del momento de inserción del registro |
| updated_at | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal en UTC actualizada automáticamente ante mutaciones |

### 4.2 outbox_events (Eventos de Integración para Despacho Confiable)
Almacena de forma atómica y duradera los eventos emitidos por cualquier Bounded Context, tales como `UserRegisteredIntegrationEvent` o `PaymentApprovedIntegrationEvent`. Un trabajador en segundo plano (*Outbox Relay Worker*) desacola los registros pendientes mediante consultas concurrentes no bloqueantes (`FOR UPDATE SKIP LOCKED`) y los publica de forma desacoplada.

| Atributo | Tipo de Dato | Llave | Req. | Default | Descripción |
| :----------------- | :------------- | :---: | :---: | :------------------ | :------------------------------------------------------------------------------------------------- |
| id | `UUID` | PK | Sí | `gen_random_uuid()` | Identificador técnico único del evento en la cola outbox |
| aggregate_type | `VARCHAR(50)` | - | Sí | - | Nombre formal del agregado emisor (`User`, `CreditOrder`, `SavedItinerary`) |
| aggregate_id | `VARCHAR(100)` | - | Sí | - | Identificador del agregado emisor representado como cadena |
| event_type | `VARCHAR(100)` | - | Sí | - | Nombre calificado del evento (`UserRegisteredIntegrationEvent`, etc.) |
| payload | `JSONB` | - | Sí | - | Cuerpo estructurado del evento serializado en JSONB inmutable |
| status | `VARCHAR(20)` | - | Sí | `'PENDING'` | Estado de despacho (`PENDING`, `PUBLISHED`, `FAILED`) |
| retry_count | `INTEGER` | - | Sí | `0` | Cantidad de reintentos de publicación ejecutados |
| last_error | `TEXT` | - | No | `null` | Traza del último error capturado durante el intento de despacho |
| occurred_on | `TIMESTAMPTZ` | - | Sí | `NOW()` | Momento en el que ocurrió el suceso dentro del agregado de dominio |
| processed_at | `TIMESTAMPTZ` | - | No | `null` | Marca temporal en UTC en la que el evento fue despachado exitosamente |
| created_at | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal de inserción del registro físico en PostgreSQL |
| updated_at | `TIMESTAMPTZ` | - | Sí | `NOW()` | Marca temporal en UTC de última actualización de estado o reintento |

* **Relaciones Lógicas (Desacoplamiento Polimórfico DDD):**
  * `N:1` hacia los agregados emisores mediante la tupla polimórfica `(aggregate_type, aggregate_id)`. Sin llaves foráneas duras para mantener la independencia modular.
* **Restricciones (Constraints):**
  * `pk_outbox_events`: `PRIMARY KEY (id)`
  * `chk_outbox_events_status`: `CHECK (status IN ('PENDING', 'PUBLISHED', 'FAILED'))`
  * `chk_outbox_events_retry_count`: `CHECK (retry_count >= 0)`
* **Índices Físicos (B-Tree):**
  * `idx_outbox_events_pending_relay`: B-Tree compuesto sobre `(status, occurred_on) WHERE status = 'PENDING'`. **Índice parcial de máxima selectividad:** permite al *Outbox Relay Worker* ejecutar `SELECT ... WHERE status = 'PENDING' ORDER BY occurred_on ASC LIMIT N FOR UPDATE SKIP LOCKED` en tiempo submilisegundo sin lecturas secuenciales de disco.
  * `idx_outbox_events_aggregate`: B-Tree compuesto sobre `(aggregate_type, aggregate_id)` para auditoría y trazabilidad histórica de eventos por entidad.
  * `idx_outbox_events_event_type`: B-Tree sobre `(event_type)` para tareas de reenvío selectivo de eventos.

---

## 5. Modelo de Datos en Memoria — Redis 7 (Caché, Atomicidad y Rate Limiting)
**Instancia:** Contenedor Docker oficial `redis:7-alpine` desplegado en la red interna Docker Compose (`ports: 6379`, aislado perimetralmente con autenticación obligatoria `requirepass`).

Redis 7 desempeña una función cardinal en la arquitectura de Navby Platform como capa de alto rendimiento para datos calientes (*Hot Data*), coordinación de concurrencia y amortiguación de peticiones externas. En cumplimiento estricto de las directrices de `redis-core` y `redis-best-practices`, no se utiliza Redis como motor de persistencia duradera ni como bus de eventos permanente, sino como un acelerador en memoria para evitar el sobrecosto de I/O en PostgreSQL 16 y blindar la cuota de la API externa de vuelos.

### 5.1 Principios de Modelado y Nomenclatura Canónica

1. **Selección de Estructuras por Patrón de Acceso (*Access Pattern Matching*):**
   - **`String`:** Empleado para valores atómicos indivisibles, contadores escalares (`INCR`), bloqueos distribuidos de exclusión mutua (`SETNX`) y documentos JSON completos que se leen y escriben en su totalidad (cotizaciones de vuelos agregadas). No se desglosan en subestructuras cuando el caso de uso siempre requiere el objeto íntegro.
   - **`Hash`:** Empleado para objetos con atributos numéricos o textuales que se leen, inspeccionan o incrementan de manera independiente (como el saldo de billeteras prepagas en Billing). El tipo `Hash` evita el antipatrón de serializar y deserializar cadenas JSON completas ante cada microtransacción de débito o recarga, optimizando la memoria RAM y reduciendo la contención de CPU.

2. **Convención de Nombres de Claves (*Keyspace Namespacing*):**
   - Estructura jerárquica estricta segmentada por dos puntos:
     `navby:<bounded_context>:<entity>:<identifier>[:<attribute>]`
   - Nombres normalizados en minúsculas, sin espacios ni caracteres especiales.
   - Las cargas útiles con identificadores largos o cadenas complejas (consultas de rutas con múltiples filtros, direcciones IP o correos electrónicos) se abrevian mediante funciones de resumen criptográfico SHA-256 (`sha256(cadena)`), garantizando claves compactas de longitud predecible para minimizar el consumo de memoria en la tabla de claves de Redis.

---

### 5.2 Catálogo Detallado de Estructuras por Bounded Context

#### 5.2.1 Quotes Context: `navby:quotes:cache:{cache_key}` (Caché de Cotizaciones de Vuelo)
Implementa el patrón **Cache-Aside** para absorber búsquedas de tarifas idénticas dentro de una ventana temporal de 30 minutos, garantizando respuestas en submilisegundos (< 5 ms) a costo financiero cero ($0 USD) y sin debitar créditos al usuario.

| Parámetro | Especificación Técnica |
| :--- | :--- |
| **Clave Canónica** | `navby:quotes:cache:{cache_key}` |
| **Tipo de Estructura** | `String` (JSON serializado y minificado) |
| **Generación del Identificador** | `cache_key = sha256(origin_iata:destination_iata:departure_date:return_date:adults:cabin:currency)` |
| **Tiempo de Vida (TTL)** | 1,800 segundos (30 minutos) con política de evicción `volatile-lru` |
| **Patrón de Acceso** | Lectura preliminar con `GET`. En *Cache Hit*, retorno directo al cliente sin cobro de créditos. En *Cache Miss*, débito de 1 crédito, consulta externa a FlightAPI y persistencia con `SET key value EX 1800` |
| **Tamaño Típico** | ~2.5 KB a ~6.0 KB por entrada (podio con las 3 mejores opciones) |

* **Estructura del Payload JSON Serializado:**
  ```json
  {
    "cached_at": "2026-09-21T10:30:00Z",
    "expires_at": "2026-09-21T11:00:00Z",
    "query": {
      "origin_iata": "LIM",
      "destination_iata": "MAD",
      "departure_date": "2026-11-15",
      "return_date": null,
      "adults": 1,
      "cabin_class": "Economy",
      "currency": "USD"
    },
    "quotes": [
      {
        "rank": 1,
        "price": 645.20,
        "currency": "USD",
        "total_duration_minutes": 710,
        "stops": 0,
        "airline_codes": "IB",
        "airline_names": "Iberia",
        "deep_link": "https://provider.flightapi.io/checkout/..."
      },
      {
        "rank": 2,
        "price": 680.00,
        "currency": "USD",
        "total_duration_minutes": 890,
        "stops": 1,
        "airline_codes": "UX,AF",
        "airline_names": "Air Europa, Air France",
        "deep_link": "https://provider.flightapi.io/checkout/..."
      },
      {
        "rank": 3,
        "price": 715.50,
        "currency": "USD",
        "total_duration_minutes": 940,
        "stops": 1,
        "airline_codes": "LA,IB",
        "airline_names": "LATAM Airlines, Iberia",
        "deep_link": "https://provider.flightapi.io/checkout/..."
      }
    ]
  }
  ```

#### 5.2.2 Quotes Context: `navby:quotes:quota:flightapi:{date}` (Quota Guard de API Externa)
Contador atómico que salvaguarda los límites contractuales y financieros con el proveedor externo de vuelos FlightAPI (plan mensual de 500 solicitudes gratuitas), evitando cobros imprevistos por sobreconsumo o bucles no intencionados de peticiones.

| Parámetro | Especificación Técnica |
| :--- | :--- |
| **Clave Canónica** | `navby:quotes:quota:flightapi:{YYYY-MM-DD}` |
| **Tipo de Estructura** | `String` (Integer escalar de 64 bits) |
| **Tiempo de Vida (TTL)** | 172,800 segundos (48 horas para auditoría y cambio de husos horarios) |
| **Operaciones Atómicas** | `INCR` atómico y validación de umbral diario (`current_calls <= DAILY_CEILING`). Si el contador supera el límite, el backend conmuta a modo degradado (*graceful degradation*), respondiendo con itinerarios topológicos estimados sin cotización de mercado en vivo |

#### 5.2.3 Billing Context: `navby:billing:wallets:{user_id}` (Hot Wallet Balance Mirror)
Réplica optimizada en memoria del saldo de créditos prepagos de cada usuario. Permite verificar y deducir créditos en microsegundos ante solicitudes concurrentes de cotización de vuelos, mitigando la contención de bloqueos transaccionales (`SELECT FOR UPDATE`) en PostgreSQL 16.

| Parámetro | Especificación Técnica |
| :--- | :--- |
| **Clave Canónica** | `navby:billing:wallets:{user_id}` (donde `user_id` es el UUID del usuario) |
| **Tipo de Estructura** | `Hash` (Campos numéricos segmentados) |
| **Tiempo de Vida (TTL)** | 86,400 segundos (24 horas) con variación pseudoaleatoria (*jitter*) de ±3,600 s para prevenir la expiración masiva concurrente (*thundering herd*) |
| **Política de Desalojo** | `volatile-lru`. Si la clave expira o es desalojada, el backend la reconstruye transparentemente desde PostgreSQL mediante *Lazy-Load* |

* **Campos Internos del Hash:**

| Campo | Tipo de Dato | Req. | Descripción | Mutación Atómica |
| :--- | :---: | :---: | :--- | :--- |
| `balance` | Integer | Sí | Saldo total de créditos disponibles | Calculado atómicamente: `free_credits + paid_credits` |
| `free_credits` | Integer | Sí | Créditos de cortesía (consumo prioritario) | Reducido mediante `HINCRBY` negativo vía Lua |
| `paid_credits` | Integer | Sí | Créditos comerciales adquiridos vía pasarela | Reducido cuando `free_credits == 0` vía Lua |
| `version` | BigInt | Sí | Versión de sincronización con PostgreSQL | Incrementado en 1 con cada débito o recarga |

#### 5.2.4 Billing Context: `navby:billing:lock:webhook:{payment_id}` (Mutex de Idempotencia de Pagos)
Mecanismo de exclusión mutua distribuida que blinda al módulo de facturación contra la recepción duplicada o simultánea de notificaciones webhook emitidas por Mercado Pago ante un pago aprobado.

| Parámetro | Especificación Técnica |
| :--- | :--- |
| **Clave Canónica** | `navby:billing:lock:webhook:{external_payment_id}` |
| **Tipo de Estructura** | `String` (Cerrojo booleano o timestamp de procesamiento) |
| **Tiempo de Vida (TTL)** | 120 segundos (ventana suficiente para culminar la transacción ACID en PostgreSQL) |
| **Comando Atómico** | `SET navby:billing:lock:webhook:{id} "locked" NX EX 120`. Si retorna `nil`, el evento ya está siendo procesado por otro hilo de trabajo; el sistema descarta el procesamiento duplicado y responde inmediatamente HTTP 200 |

#### 5.2.5 IAM Context: `navby:iam:ratelimit:{client}:{endpoint}:{window}` (Limitador de Tasa Perimetral)
Controlador volumétrico de tráfico basado en ventanas temporales fijas para proteger los endpoints públicos de Navby contra ataques de fuerza bruta, scraping agresivo de rutas y saturación de ancho de banda.

| Parámetro | Especificación Técnica |
| :--- | :--- |
| **Clave Canónica** | `navby:iam:ratelimit:{client_identifier}:{endpoint_hash}:{window_minute}` |
| **Tipo de Estructura** | `String` (Integer Counter) |
| **Composición** | `client_identifier`: IP pública o `user_id` autenticado; `endpoint_hash`: identificador del recurso (`search`, `login`, `register`); `window_minute`: marca temporal normalizada en minutos (`epoch // 60`) |
| **Tiempo de Vida (TTL)** | 60 segundos (auto-expiración al cerrar la ventana) |
| **Umbrales Operativos** | Rutas públicas anónimas: 60 peticiones/minuto; Búsqueda de cotizaciones autenticadas: 300 peticiones/minuto. Superado el límite, retorna HTTP 429 con cabecera `Retry-After: 60` |

#### 5.2.6 IAM Context: `navby:iam:login_attempts:{email_hash}` (Mitigación de Fuerza Bruta)
Contador de seguridad que bloquea temporalmente el intento de acceso por contraseña tras sucesivos fallos de autenticación.

| Parámetro | Especificación Técnica |
| :--- | :--- |
| **Clave Canónica** | `navby:iam:login_attempts:{sha256(email)}` |
| **Tipo de Estructura** | `String` (Integer Counter) |
| **Tiempo de Vida (TTL)** | 900 segundos (15 minutos) renovable |
| **Lógica Operativa** | Cada autenticación fallida ejecuta `INCR` + `EXPIRE 900`. Al alcanzar 5 intentos erróneos, la cuenta queda temporalmente bloqueada para inicios de sesión locales durante 15 minutos, mitigando ataques de diccionario |

---

### 5.3 Script Canónico Lua de Débito Atómico (`atomic_debit.lua`)

Para garantizar que el descuento de créditos en la billetera virtual sea estrictamente atómico, inmune a condiciones de carrera y ejecutable en tiempo constante sin bloqueos pesados en disco, la deducción de saldo se implementa mediante el siguiente script Lua canónico ejecutado en el motor monohilo de Redis 7:

```lua
-- =============================================================================
-- SCRIPT LUA CANÓNICO: DÉBITO ATÓMICO DE CRÉDITOS PREPAGOS (NAVBY BILLING)
-- Archivo: src/modules/billing/infrastructure/scripts/atomic_debit.lua
-- =============================================================================
-- KEYS[1] : Clave de la billetera en Redis (ej. 'navby:billing:wallets:usr_123')
-- ARGV[1] : Cantidad de créditos a debitar (entero positivo, ej. 1)
-- ARGV[2] : TTL de renovación en segundos (ej. 86400)
--
-- CÓDIGOS DE RETORNO (Array de 5 elementos):
--   [1, balance, free_credits, paid_credits, version] -> Éxito, débito efectuado
--   [-1, balance, free_credits, paid_credits, version] -> Error: Saldo insuficiente
--   [-2, 0, 0, 0, 0]                                  -> Error: Cache Miss (requiere Lazy-Load)
-- =============================================================================

local wallet_key = KEYS[1]
local debit_amount = tonumber(ARGV[1])
local ttl_seconds = tonumber(ARGV[2]) or 86400

-- 1. Validar existencia de la billetera en Redis (Detección de Cache Miss)
if redis.call('EXISTS', wallet_key) == 0 then
    return {-2, 0, 0, 0, 0}
end

-- 2. Obtener los saldos y versión actuales del Hash
local wallet_data = redis.call('HMGET', wallet_key, 'free_credits', 'paid_credits', 'version')
local free_credits = tonumber(wallet_data[1]) or 0
local paid_credits = tonumber(wallet_data[2]) or 0
local version = tonumber(wallet_data[3]) or 0

local total_available = free_credits + paid_credits

-- 3. Validar disponibilidad de fondos
if total_available < debit_amount then
    return {-1, total_available, free_credits, paid_credits, version}
end

-- 4. Aplicar regla de prelación: Consumir primero créditos de cortesía (free_credits)
local new_free = free_credits
local new_paid = paid_credits

if free_credits >= debit_amount then
    new_free = free_credits - debit_amount
else
    local remainder = debit_amount - free_credits
    new_free = 0
    new_paid = paid_credits - remainder
end

local new_balance = new_free + new_paid
local new_version = version + 1

-- 5. Actualizar el Hash atómicamente en memoria y renovar el TTL
redis.call('HMSET', wallet_key,
    'balance', new_balance,
    'free_credits', new_free,
    'paid_credits', new_paid,
    'version', new_version
)
redis.call('EXPIRE', wallet_key, ttl_seconds)

-- 6. Retornar confirmación de éxito con los nuevos estados consolidados
return {1, new_balance, new_free, new_paid, new_version}
```

#### Protocolo de Ejecución y Resiliencia en Python (FastAPI / `redis.asyncio`)
El flujo de consumo del script sigue una estrategia tolerante a fallos:
1. **Intento en Caché (*Hot Path*):** El microservicio ejecuta `evalsha` sobre el script precompilado en Redis.
2. **Manejo de Cache Miss (`-2`):** Si Redis retorna `-2`, la billetera no reside en memoria (por desalojo o reinicio). La aplicación consulta la tabla `credit_wallets` en PostgreSQL 16, ejecuta un `HSET` con los valores oficiales de la base de datos aplicando un TTL de 24 horas con jitter, y reintenta la invocación del script Lua.
3. **Manejo de Fondos Insuficientes (`-1`):** Se cancela la operación de cotización externa de forma inmediata y se retorna HTTP 402 (*Payment Required*) al cliente sin tocar la red externa ni la base de datos relacional.
4. **Sincronización Transaccional (*Cold Path*):** Cuando el script retorna éxito (`1`), el proceso encola un evento transaccional en el Outbox o actualiza asíncronamente el libro contable (`credit_transactions` y `credit_wallets`) en PostgreSQL para asegurar durabilidad ACID.

---

### 5.4 Políticas de Memoria, Persistencia y Resiliencia en Redis 7

En correspondencia con las directrices de `redis-best-practices` y los límites de la máquina virtual Azure `Standard_B2s` (2 vCPUs, 4 GB RAM compartida con PostgreSQL, API y Caddy):

1. **Gestión de Memoria y Política de Desalojo:**
   - `maxmemory 256mb`: Techo estricto de memoria asignado a la instancia de Redis, garantizando estabilidad y previniendo el sacrificio del proceso por el OOM Killer del kernel Linux.
   - `maxmemory-policy volatile-lru`: **Política crítica de protección.** Redis desaloja exclusivamente las claves que posean un tiempo de expiración (`TTL`) activo mediante el algoritmo de menor uso reciente (*Least Recently Used*). Dado que las cotizaciones de vuelo (`navby:quotes:cache:*`) y los limitadores de tasa tienen TTLs cortos (30 minutos y 1 minuto), son los primeros candidatos a desalojo ante picos de tráfico. Las billeteras (`navby:billing:wallets:*`) también poseen TTL pero son rehidratadas bajo demanda si fuesen desalojadas.

2. **Estrategia de Persistencia Híbrida:**
   - **Append-Only File (AOF):** Habilitado mediante `appendonly yes` y `appendfsync everysec`. Registra cada mutación en disco cada segundo en segundo plano. En caso de caída abrupta del contenedor, la pérdida máxima se restringe a un segundo de operaciones de billetera en memoria (las cuales quedan respaldadas permanentemente en PostgreSQL).
   - **Snapshots RDB:** Configuración periódica `save 900 1 300 10 60 10000` como mecanismo de respaldo compacto para restauraciones rápidas en frío.

3. **Pool de Conexiones Asíncrono en Python:**
   - Implementado mediante `redis.asyncio.ConnectionPool` con:
     - `max_connections = 50`: Límite acorde a la capacidad de concurrencia de la API.
     - `socket_timeout = 5.0`: Prevención de bloqueos indefinidos por latencia de red interna.
     - `socket_connect_timeout = 5.0`: Detección temprana de indisponibilidad.
     - `decode_responses = True`: Decodificación automática UTF-8 en el cliente.

---

### 5.5 Arquitectura del Grafo en Memoria RAM (Subdominio Routing)

Un principio de diseño central en Navby Platform es que **la topología aeroportuaria mundial no reside ni en PostgreSQL ni en Redis**.

* **Justificación Cuantitativa:** El dataset comercial consolidado de Navby comprende 3,354 nodos aeroportuarios y 37,326 aristas de vuelo. En formato binario de grafo en memoria (mediante listas de adyacencia e índices directos de arrays en Python), esta estructura ocupa **~10.4 MB de memoria RAM**.
* **Rendimiento Algorítmico:** Mantener el grafo en memoria de proceso del backend permite que los algoritmos de búsqueda heurística (A* con distancia ortodrómica Haversine, BFS y Backtracking con poda) recorran el grafo con cero sobrecarga de red o deserialización, logrando tiempos de cómputo inferiores a **1.8 milisegundos por ruta**.
* **Ciclo de Vida:** La carga del grafo se realiza de forma determinista durante el evento `lifespan` del arranque de FastAPI, leyendo directamente los archivos inmutables `airports.csv` y `routes_unique.csv` de `docs/navby-datasets/`.

---

## 6. Script DDL Completo y Determinista (PostgreSQL 16)

A continuación se proporciona el script SQL completo para la inicialización y migración determinista del esquema de Navby Platform:

```sql
-- =============================================================================
-- NAVBY PLATFORM: SCHEMA RELACIONAL CANÓNICO (POSTGRESQL 16)
-- Monolito Modular Desacoplado con Aislamiento Estricto por Bounded Contexts
-- =============================================================================

-- 0. EXTENSIONES CRIPTOGRÁFICAS
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =============================================================================
-- 1. IAM BOUNDED CONTEXT (Identidad, Autenticación y Sesiones)
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(150) NOT NULL,
    password_hash VARCHAR(255) NULL,
    username VARCHAR(50) NOT NULL,
    auth_provider VARCHAR(20) NOT NULL DEFAULT 'local',
    google_id VARCHAR(255) NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'passenger',
    status VARCHAR(20) NOT NULL DEFAULT 'pending_verification',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 0,
    CONSTRAINT uk_users_email UNIQUE (email),
    CONSTRAINT uk_users_username UNIQUE (username),
    CONSTRAINT uk_users_google_id UNIQUE (google_id),
    CONSTRAINT chk_users_auth_provider CHECK (auth_provider IN ('local', 'google')),
    CONSTRAINT chk_users_role CHECK (role IN ('passenger', 'admin')),
    CONSTRAINT chk_users_status CHECK (status IN ('pending_verification', 'active', 'suspended')),
    CONSTRAINT chk_users_local_password CHECK (auth_provider <> 'local' OR password_hash IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_users_google_id ON users (google_id) WHERE google_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_status ON users (status);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    family_id UUID NOT NULL,
    is_revoked BOOLEAN NOT NULL DEFAULT false,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_refresh_tokens_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT uk_refresh_tokens_hash UNIQUE (token_hash)
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_family_id ON refresh_tokens (family_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens (expires_at);

CREATE TABLE IF NOT EXISTS verification_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    type VARCHAR(30) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_verification_tokens_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT chk_verification_tokens_type CHECK (type IN ('email_verification', 'password_reset'))
);

CREATE INDEX IF NOT EXISTS idx_verification_tokens_lookup ON verification_tokens (user_id, type, used_at);
CREATE INDEX IF NOT EXISTS idx_verification_tokens_expires_at ON verification_tokens (expires_at);

-- =============================================================================
-- 2. ITINERARIES BOUNDED CONTEXT (Planes de Vuelo Guardados)
-- =============================================================================

CREATE TABLE IF NOT EXISTS itineraries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- Enlace lógico a users(id) en IAM (Sin FK física)
    name VARCHAR(100) NOT NULL,
    origin_iata CHAR(3) NOT NULL,
    destination_iata CHAR(3) NOT NULL,
    origin_city VARCHAR(100) NOT NULL,
    destination_city VARCHAR(100) NOT NULL,
    departure_date DATE NOT NULL,
    return_date DATE NULL,
    adults SMALLINT NOT NULL DEFAULT 1,
    children SMALLINT NOT NULL DEFAULT 0,
    infants SMALLINT NOT NULL DEFAULT 0,
    cabin_class VARCHAR(20) NOT NULL DEFAULT 'Economy',
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    route_snapshot JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 0,
    CONSTRAINT chk_itineraries_distinct_airports CHECK (origin_iata <> destination_iata),
    CONSTRAINT chk_itineraries_dates CHECK (return_date IS NULL OR return_date >= departure_date),
    CONSTRAINT chk_itineraries_adults CHECK (adults >= 1),
    CONSTRAINT chk_itineraries_children CHECK (children >= 0),
    CONSTRAINT chk_itineraries_infants CHECK (infants >= 0 AND infants <= adults),
    CONSTRAINT chk_itineraries_total_passengers CHECK (adults + children + infants <= 9),
    CONSTRAINT chk_itineraries_cabin_class CHECK (cabin_class IN ('Economy', 'Premium_Economy', 'Business', 'First'))
);

CREATE INDEX IF NOT EXISTS idx_itineraries_user_id ON itineraries (user_id);
CREATE INDEX IF NOT EXISTS idx_itineraries_user_created ON itineraries (user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS itinerary_quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    itinerary_id UUID NOT NULL,
    rank SMALLINT NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    total_duration_minutes INTEGER NOT NULL,
    stops SMALLINT NOT NULL DEFAULT 0,
    airline_codes VARCHAR(100) NOT NULL,
    airline_names VARCHAR(255) NOT NULL,
    deep_link TEXT NOT NULL,
    quoted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_itinerary_quotes_itinerary FOREIGN KEY (itinerary_id) REFERENCES itineraries (id) ON DELETE CASCADE,
    CONSTRAINT uk_itinerary_quotes_rank UNIQUE (itinerary_id, rank),
    CONSTRAINT chk_itinerary_quotes_rank CHECK (rank BETWEEN 1 AND 3),
    CONSTRAINT chk_itinerary_quotes_price CHECK (price >= 0.0),
    CONSTRAINT chk_itinerary_quotes_stops CHECK (stops >= 0)
);

CREATE INDEX IF NOT EXISTS idx_itinerary_quotes_itinerary_id ON itinerary_quotes (itinerary_id);

-- =============================================================================
-- 3. BILLING BOUNDED CONTEXT (Monetización Prepaga y Créditos)
-- =============================================================================

CREATE TABLE IF NOT EXISTS credit_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- Enlace lógico a users(id) en IAM (Sin FK física)
    balance INTEGER NOT NULL DEFAULT 10,
    free_credits SMALLINT NOT NULL DEFAULT 10,
    paid_credits INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 0,
    CONSTRAINT uk_credit_wallets_user_id UNIQUE (user_id),
    CONSTRAINT chk_credit_wallets_balance CHECK (balance >= 0),
    CONSTRAINT chk_credit_wallets_free CHECK (free_credits >= 0),
    CONSTRAINT chk_credit_wallets_paid CHECK (paid_credits >= 0),
    CONSTRAINT chk_credit_wallets_total CHECK (balance = free_credits + paid_credits)
);

CREATE TABLE IF NOT EXISTS credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id UUID NOT NULL,
    user_id UUID NOT NULL, -- Enlace lógico para trazabilidad directa
    transaction_type VARCHAR(30) NOT NULL,
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    reason VARCHAR(255) NOT NULL,
    reference_id VARCHAR(100) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_credit_transactions_wallet FOREIGN KEY (wallet_id) REFERENCES credit_wallets (id) ON DELETE RESTRICT,
    CONSTRAINT chk_credit_transactions_type CHECK (transaction_type IN ('SIGNUP_BONUS', 'PURCHASE_CREDIT', 'ROUTE_QUOTE_DEBIT', 'REFUND', 'MANUAL_ADJUSTMENT')),
    CONSTRAINT chk_credit_transactions_amount CHECK (amount <> 0),
    CONSTRAINT chk_credit_transactions_balance CHECK (balance_after >= 0)
);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_wallet_id ON credit_transactions (wallet_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_created ON credit_transactions (user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS credit_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- Enlace lógico a users(id) en IAM (Sin FK física)
    package_code VARCHAR(30) NOT NULL,
    credits_amount INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'PEN',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    payment_provider VARCHAR(30) NOT NULL DEFAULT 'MERCADO_PAGO',
    mp_preference_id VARCHAR(100) NULL,
    external_payment_id VARCHAR(100) NULL,
    paid_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version BIGINT NOT NULL DEFAULT 0,
    CONSTRAINT uk_credit_orders_external_payment_id UNIQUE (external_payment_id),
    CONSTRAINT chk_credit_orders_status CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')),
    CONSTRAINT chk_credit_orders_credits CHECK (credits_amount > 0),
    CONSTRAINT chk_credit_orders_price CHECK (unit_price >= 0.0)
);

CREATE INDEX IF NOT EXISTS idx_credit_orders_user_id ON credit_orders (user_id);
CREATE INDEX IF NOT EXISTS idx_credit_orders_status ON credit_orders (status);

-- =============================================================================
-- 4. SHARED KERNEL (Transactional Outbox Pattern)
-- =============================================================================

CREATE TABLE IF NOT EXISTS outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(64) NOT NULL,
    aggregate_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(128) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    retry_count INTEGER NOT NULL DEFAULT 0,
    last_error TEXT NULL,
    occurred_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_outbox_events_status CHECK (status IN ('PENDING', 'PUBLISHED', 'FAILED')),
    CONSTRAINT chk_outbox_events_retry_count CHECK (retry_count >= 0)
);

-- Índice parcial de alto rendimiento para el Outbox Relay Worker
CREATE INDEX IF NOT EXISTS idx_outbox_events_pending_relay 
    ON outbox_events (status, occurred_on ASC) 
    WHERE status = 'PENDING';

CREATE INDEX IF NOT EXISTS idx_outbox_events_aggregate 
    ON outbox_events (aggregate_type, aggregate_id);

CREATE INDEX IF NOT EXISTS idx_outbox_events_event_type 
    ON outbox_events (event_type);
```

---

## 7. Verificación, Comandos CLI y Pruebas Operativas

Para validar la correcta inicialización y comportamiento de los motores de persistencia en los entornos de desarrollo e integración continua, se proporcionan los siguientes comandos canónicos de verificación:

### 7.1 Pruebas Operativas en Redis 7 (`redis-cli`)

Las operaciones clave de Redis 7 se pueden validar directamente mediante la consola interactiva `redis-cli`:

```bash
# Conectar a la instancia local de Redis en contenedor Docker
docker exec -it navby-redis redis-cli -a "${REDIS_PASSWORD}"
```

```redis
# 1. Validación de Cache-Aside (Quotes Context)
SET navby:quotes:cache:a1b2c3d4e5f6 '{"quotes":[{"rank":1,"price":645.20}]}' EX 1800
TTL navby:quotes:cache:a1b2c3d4e5f6
GET navby:quotes:cache:a1b2c3d4e5f6

# 2. Inicialización de Hot Wallet Mirror (Billing Context)
HSET navby:billing:wallets:a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11 balance 10 free_credits 10 paid_credits 0 version 0
EXPIRE navby:billing:wallets:a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11 86400
HGETALL navby:billing:wallets:a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11

# 3. Carga y Ejecución del Script Lua de Débito Atómico (atomic_debit.lua)
# Cargar el script canónico en el caché SHA-1 de Redis
SCRIPT LOAD "local k=KEYS[1] local d=tonumber(ARGV[1]) if redis.call('EXISTS',k)==0 then return {-2,0,0,0,0} end local w=redis.call('HMGET',k,'free_credits','paid_credits','version') local f=tonumber(w[1]) or 0 local p=tonumber(w[2]) or 0 local v=tonumber(w[3]) or 0 if (f+p)<d then return {-1,f+p,f,p,v} end local nf,np=f,p if f>=d then nf=f-d else np=p-(d-f) nf=0 end redis.call('HMSET',k,'balance',nf+np,'free_credits',nf,'paid_credits',np,'version',v+1) redis.call('EXPIRE',k,tonumber(ARGV[2]) or 86400) return {1,nf+np,nf,np,v+1}"

# Ejecutar débito atómico de 1 crédito sobre la billetera (retorna array: [1, 9, 9, 0, 1])
EVALSHA <sha_retornado> 1 navby:billing:wallets:a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11 1 86400

# 4. Verificación del Mutex de Idempotencia para Webhooks de Mercado Pago
SET navby:billing:lock:webhook:mp_pay_987654321 "locked" NX EX 120
# Reintento concurrente inmediato (debe retornar nil al estar bloqueado)
SET navby:billing:lock:webhook:mp_pay_987654321 "locked" NX EX 120

# 5. Limitador de Tasa Perimetral (IAM Context)
INCR navby:iam:ratelimit:192.168.1.1:search:29829340
EXPIRE navby:iam:ratelimit:192.168.1.1:search:29829340 60
TTL navby:iam:ratelimit:192.168.1.1:search:29829340

# 6. Diagnóstico de Memoria y Políticas de Desalojo
INFO memory
MEMORY USAGE navby:billing:wallets:a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11
```

### 7.2 Pruebas de Integridad Estructural en PostgreSQL 16 (`psql`)

```sql
-- 1. Verificar la creación unificada de las 9 tablas del esquema relacional
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 2. Validar que no existan Foreign Keys cross-module no autorizadas
SELECT
    tc.table_name AS local_table,
    kcu.column_name AS local_column,
    ccu.table_name AS foreign_table,
    ccu.column_name AS foreign_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;

-- 3. Confirmar la efectividad del índice parcial del Outbox Relay Worker
EXPLAIN ANALYZE
SELECT id, aggregate_type, aggregate_id, event_type, payload
FROM outbox_events
WHERE status = 'PENDING'
ORDER BY occurred_on ASC
LIMIT 50
FOR UPDATE SKIP LOCKED;
```

