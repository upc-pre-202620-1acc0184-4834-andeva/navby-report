# Navby Platform — Catálogo y Especificación de Endpoints RESTful

Este documento constituye la especificación canónica, exhaustiva y unificada de la interfaz de programación de aplicaciones (API RESTful) de la plataforma **Navby**. Detalla cada uno de los endpoints expuestos a través de los cinco Bounded Contexts del monolito modular (**IAM**, **Routing**, **Quotes**, **Itineraries** y **Billing**), así como los servicios transversales de salud, diagnóstico y observabilidad métrica.

---

## 1. Convenciones Globales de la API

La arquitectura de interfaces de Navby sigue las mejores prácticas de la industria para APIs orientadas a recursos bajo la especificación **OpenAPI 3.1** y el marco de trabajo **FastAPI**.

### 1.1. URLs Base y Versionamiento
El acceso perimetral se organiza mediante prefijos semánticos versionados:
* **Entorno de Producción:** `https://api.navby.com/api/v1`
* **Entorno de Desarrollo Local:** `http://localhost:8000/api/v1`
* **Estrategia de Versionamiento:** Versionamiento en la ruta URI (`/api/v1/`). Cualquier cambio con ruptura de compatibilidad hacia atrás requerirá la publicación bajo `/api/v2/`.

### 1.2. Protocolo, Codificación y Tipos de Contenido
* **Transporte:** Exclusivamente HTTPS (TLS 1.3 recomendado, TLS 1.2 mínimo) gobernado por el proxy inverso Caddy 2.
* **Codificación:** UTF-8 estricto en cabeceras y cuerpos de mensaje.
* **Content-Type Solicitud:** `application/json; charset=utf-8` para mutaciones con cuerpo.
* **Accept Cabecera:** `application/json` requerida en todas las consultas.
* **Formato Temporal:** Fechas y marcas de tiempo en conformidad con **ISO 8601** (`YYYY-MM-DD` para fechas calendario de vuelos y `YYYY-MM-DDTHH:MM:SS.ffffffZ` en UTC para marcas temporales auditables).

### 1.3. Esquema de Autenticación y Seguridad
* **Esquema:** Portador de credenciales (*Bearer Token*) mediante **JSON Web Tokens (JWT)** firmados criptográficamente con algoritmo **Ed25519** o **RS256**.
* **Cabecera Requerida:**
  ```http
  Authorization: Bearer <access_token>
  ```
* **Tiempo de Vida:** Los tokens de acceso (`access_token`) poseen un TTL de **15 minutos**. La renovación se gestiona mediante tokens de actualización (`refresh_token`) persistidos en Redis con rotación atómica y detección de reutilización fraudulenta.
* **Endpoints Públicos vs. Protegidos:** Aquellos endpoints marcados como `[Público]` no exigen la cabecera `Authorization`. Los endpoints marcados como `[Autenticado]` rechazan la petición con código `401 Unauthorized` si el token es inexistente, inválido o expirado.

### 1.4. Formato Canónico de Errores (RFC 7807)
Todas las respuestas con código de error HTTP ($4xx$ y $5xx$) retornan una estructura uniforme basada en **RFC 7807 (Problem Details for HTTP APIs)**:

```json
{
  "type": "https://errors.navby.com/errors/RESOURCE_NOT_FOUND",
  "title": "Recurso no encontrado",
  "status": 404,
  "detail": "El aeropuerto con código IATA 'XYZ' no existe en la red comercial activa.",
  "instance": "/api/v1/routing/airports/XYZ",
  "code": "AIRPORT_NOT_FOUND",
  "invalid_params": [],
  "timestamp": "2026-09-29T18:30:00.000000Z"
}
```

En errores de validación de esquemas Pydantic (`422 Unprocessable Content`), la propiedad `invalid_params` desglosa el campo exacto, la ubicación en la petición y el motivo del rechazo:

```json
{
  "type": "https://errors.navby.com/errors/UNPROCESSABLE_ENTITY",
  "title": "Error de validación sintáctica o de esquema",
  "status": 422,
  "detail": "Uno o más campos no cumplen con las restricciones de formato requeridas.",
  "instance": "/api/v1/routing/routes/search",
  "code": "SCHEMA_VALIDATION_ERROR",
  "invalid_params": [
    {
      "field": "origin",
      "location": "body",
      "reason": "String should match pattern '^[A-Z]{3}$'"
    }
  ],
  "timestamp": "2026-09-29T18:30:00.000000Z"
}
```

---

## 2. Matriz Sinóptica de Endpoints

La siguiente tabla resume todos los endpoints expuestos por la plataforma Navby, clasificados por Bounded Context, método HTTP, ruta perimetral y nivel de acceso requerido:

| Bounded Context | Método | Ruta Relativa | Nivel de Acceso | Propósito Operacional |
| :--- | :---: | :--- | :---: | :--- |
| **IAM** | `POST` | `/api/v1/auth/register` | Público | Registro de nueva cuenta de usuario y emisión de OTP vía Resend. |
| **IAM** | `POST` | `/api/v1/auth/login` | Público | Autenticación local con credenciales (email y password) y entrega de JWT. |
| **IAM** | `POST` | `/api/v1/auth/google` | Público | Autenticación federada Single Sign-On con Google OAuth 2.0 / OIDC. |
| **IAM** | `POST` | `/api/v1/auth/refresh` | Público | Rotación atómica de access token mediante refresh token. |
| **IAM** | `POST` | `/api/v1/auth/logout` | Autenticado | Revocación e invalidación de sesión en lista negra de Redis 7. |
| **IAM** | `POST` | `/api/v1/auth/verify-email` | Público | Verificación de dirección de correo mediante código OTP de 6 dígitos. |
| **IAM** | `GET` | `/api/v1/auth/me` | Autenticado | Obtención del perfil y estado de cuenta del usuario activo. |
| **IAM** | `POST` | `/api/v1/auth/change-password` | Autenticado | Actualización segura de contraseña para usuario autenticado. |
| **IAM** | `POST` | `/api/v1/auth/forgot-password` | Público | Solicitud de código de restablecimiento de contraseña vía email. |
| **IAM** | `POST` | `/api/v1/auth/reset-password` | Público | Confirmación y aplicación de nueva contraseña mediante token. |
| **IAM** | `GET` | `/api/v1/users/{username}` | Público | Consulta pública de perfil de usuario por nombre de usuario. |
| **IAM** | `GET` | `/api/v1/users/check-availability` | Público | Validación reactiva de disponibilidad de username o email en UI. |
| **IAM** | `PATCH` | `/api/v1/users/profile` | Autenticado | Modificación de metadatos de perfil (nombre, país, avatar). |
| **IAM** | `POST` | `/api/v1/users/{user_id}/suspend` | Admin | Bloqueo o suspensión administrativa de una cuenta de usuario. |
| **Routing** | `POST` | `/api/v1/routing/routes/search` | Público | Búsqueda geodésica $A^*$/BFS sobre el grafo en RAM con telemetría de benchmarking. |
| **Routing** | `GET` | `/api/v1/routing/airports/nearest` | Público | Resolución por vecino más cercano de Haversine ($O(V)$) para localidades sin pista. |
| **Routing** | `GET` | `/api/v1/routing/airports` | Público | Catálogo paginado y autocompletado de los 3,354 aeropuertos comerciales. |
| **Routing** | `GET` | `/api/v1/routing/airports/{iata_code}` | Público | Consulta de metadatos canónicos de un aeropuerto por código IATA. |
| **Routing** | `GET` | `/api/v1/routing/topology/metrics` | Público | Telemetría estructural de la red de grafos (nodos, aristas, conexidad UFDS). |
| **Quotes** | `POST` | `/api/v1/quotes/search` | Autenticado | Cotización en vivo vía FlightAPI, optimización Pareto y débito de 5 créditos. |
| **Quotes** | `GET` | `/api/v1/quotes/{session_id}` | Autenticado | Recuperación de los resultados completos de una sesión de cotización previa. |
| **Quotes** | `GET` | `/api/v1/quotes/{session_id}/podium` | Autenticado | Extracción del Podio de Pareto (Más Barato, Más Rápido y Mejor Balance). |
| **Quotes** | `GET` | `/api/v1/quotes/quota/status` | Autenticado | Monitoreo del saldo externo consumido en FlightAPI y Circuit Breaker. |
| **Itineraries** | `POST` | `/api/v1/itineraries` | Autenticado | Creación y custodia persistente de un itinerario en PostgreSQL 16. |
| **Itineraries** | `GET` | `/api/v1/itineraries/{itinerary_id}` | Autenticado | Detalle completo de un itinerario guardado por su identificador UUID. |
| **Itineraries** | `GET` | `/api/v1/itineraries` | Autenticado | Listado paginado de itinerarios asociados a la cuenta del usuario. |
| **Itineraries** | `PATCH` | `/api/v1/itineraries/{itinerary_id}/name` | Autenticado | Modificación del nombre personalizado del itinerario. |
| **Itineraries** | `PATCH` | `/api/v1/itineraries/{itinerary_id}/notes` | Autenticado | Actualización de notas personales de viaje en el itinerario. |
| **Itineraries** | `POST` | `/api/v1/itineraries/{itinerary_id}/quotes` | Autenticado | Vinculación de nuevas alternativas cotizadas a un itinerario persistido. |
| **Itineraries** | `POST` | `/api/v1/itineraries/{itinerary_id}/archive` | Autenticado | Transición de estado a archivado para un itinerario completado. |
| **Itineraries** | `DELETE` | `/api/v1/itineraries/{itinerary_id}` | Autenticado | Eliminación lógica (*soft delete*) de un itinerario persistido. |
| **Billing** | `GET` | `/api/v1/billing/wallets/me` | Autenticado | Saldo de créditos de cortesía, créditos adquiridos y caducidad diaria. |
| **Billing** | `GET` | `/api/v1/billing/wallets/me/transactions`| Autenticado | Libro mayor contable paginado de ingresos, débitos y recargas de créditos. |
| **Billing** | `GET` | `/api/v1/billing/packages` | Público | Catálogo oficial de paquetes de créditos prepagados (`pack_50`, `pack_100`, etc.). |
| **Billing** | `POST` | `/api/v1/billing/orders` | Autenticado | Creación de orden de compra e inicialización de Checkout Pro de Mercado Pago. |
| **Billing** | `GET` | `/api/v1/billing/orders/{order_id}` | Autenticado | Consulta de estado de orden de pago individual por identificador UUID. |
| **Billing** | `GET` | `/api/v1/billing/orders` | Autenticado | Listado paginado de intenciones de recarga y pagos del usuario. |
| **Billing** | `POST` | `/api/v1/billing/webhooks/mercadopago` | Público (Firma HMAC) | Notificación idempotente de cobro exitoso vía Mercado Pago Webhook. |
| **Sistema** | `GET` | `/health` / `/api/v1/health` | Público | Liveness y readiness check de base de datos, Redis 7 y grafo en RAM. |
| **Sistema** | `GET` | `/metrics` | Admin / Interno | Exportador de telemetría de Prometheus para latencias y nodos explorados. |
| **Sistema** | `GET` | `/docs` / `/redoc` | Público | Documentación interactiva Swagger UI / ReDoc generada en OpenAPI 3.1. |

---

## 3. Bounded Context IAM: Identidad y Control de Acceso

El Bounded Context de IAM gestiona el ciclo de vida de los usuarios, la autenticación local y federada, la verificación de identidad y la emisión segura de credenciales temporales.

### 3.1. `POST /api/v1/auth/register`
* **Propósito:** Inicia el registro de una cuenta de usuario local mediante credenciales de correo y contraseña. Genera un código OTP de 6 dígitos con expiración de 10 minutos y lo despacha de forma asíncrona mediante el adaptador transaccional de Resend.
* **Nivel de Acceso:** Público (`Rate Limit: 5 req/min por IP`).
* **Request Body (`RegisterRequestSchema`):**
  ```json
  {
    "email": "viajero@andeva.io",
    "password": "PasswordSegura123!",
    "full_name": "Carlos Mendoza",
    "username": "cmendoza"
  }
  ```
* **Respuestas:**
  * `201 Created`: Usuario creado exitosamente en estado pendiente de verificación.
    ```json
    {
      "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "email": "viajero@andeva.io",
      "username": "cmendoza",
      "status": "PENDING_VERIFICATION",
      "message": "Se ha remitido un código de verificación de 6 dígitos a su dirección de correo electrónico.",
      "created_at": "2026-09-29T18:30:00Z"
    }
    ```
  * `409 Conflict`: Si el correo o el nombre de usuario ya se encuentran registrados en el sistema.
  * `422 Unprocessable Content`: Si la contraseña no satisface la complejidad requerida (mínimo 8 caracteres, 1 mayúscula, 1 número y 1 carácter especial).

### 3.2. `POST /api/v1/auth/login`
* **Propósito:** Autentica a un usuario existente mediante verificación criptográfica Argon2id de la contraseña. Ante éxito, emite un par de tokens JWT (Access Token y Refresh Token) e inicializa la sesión en Redis 7.
* **Nivel de Acceso:** Público (`Rate Limit: 10 req/min por IP`).
* **Request Body (`LoginRequestSchema`):**
  ```json
  {
    "email": "viajero@andeva.io",
    "password": "PasswordSegura123!"
  }
  ```
* **Respuestas:**
  * `200 OK`: Autenticación exitosa.
    ```json
    {
      "access_token": "eyJhbGciOiJFZERTQ...",
      "refresh_token": "eyJhbGciOiJFZERTQ...",
      "token_type": "Bearer",
      "expires_in": 900,
      "user": {
        "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "email": "viajero@andeva.io",
        "username": "cmendoza",
        "role": "USER",
        "status": "ACTIVE"
      }
    }
    ```
  * `401 Unauthorized`: Credenciales erróneas o cuenta inexistente.
  * `403 Forbidden`: Cuenta suspendida por un administrador o pendiente de verificación de correo.

### 3.3. `POST /api/v1/auth/google`
* **Propósito:** Procesa la autenticación federada Single Sign-On (SSO) mediante Google Identity Services. Valida el token de identidad JWT (`id_token`) contra los servidores de Google mediante `google-auth`, aprovisiona automáticamente la cuenta si es un usuario nuevo y emite el par de credenciales JWT de Navby.
* **Nivel de Acceso:** Público.
* **Request Body (`GoogleAuthRequestSchema`):**
  ```json
  {
    "id_token": "eyJhbGciOiJSUzI1NiIs..."
  }
  ```
* **Respuestas:**
  * `200 OK`: Sesión federada autorizada con entrega de tokens JWT.

### 3.4. `POST /api/v1/auth/refresh`
* **Propósito:** Permite renovar un `access_token` caducado utilizando un `refresh_token` válido. Aplica **rotación estricta de refresh token**: el token antiguo se invalida en Redis y se entrega uno nuevo, detectando intentos de reutilización de tokens robados.
* **Nivel de Acceso:** Público.
* **Request Body (`RefreshTokenRequestSchema`):**
  ```json
  {
    "refresh_token": "eyJhbGciOiJFZERTQ..."
  }
  ```
* **Respuestas:**
  * `200 OK`: Nuevo par de tokens emitido.
  * `401 Unauthorized`: Token de refresco expirado, revocado o inválido.

### 3.5. `POST /api/v1/auth/logout`
* **Propósito:** Cierra la sesión activa del usuario. Extrae el JTI (*JWT ID*) del token de acceso y lo persiste en la lista negra (*blocklist*) de Redis 7 con un TTL igual al tiempo remanente del token, revocando de inmediato su validez en el sistema.
* **Nivel de Acceso:** Autenticado (`Bearer Token`).
* **Respuestas:**
  * `204 No Content`: Sesión revocada con éxito.

### 3.6. `POST /api/v1/auth/verify-email`
* **Propósito:** Valida el código OTP de 6 dígitos ingresado por el usuario para activar su cuenta.
* **Nivel de Acceso:** Público.
* **Request Body (`VerifyEmailRequestSchema`):**
  ```json
  {
    "email": "viajero@andeva.io",
    "otp_code": "849201"
  }
  ```
* **Respuestas:**
  * `200 OK`: Correo verificado satisfactoriamente; cuenta transicionada a estado `ACTIVE`.
  * `400 Bad Request`: Código OTP incorrecto o expirado.

### 3.7. `GET /api/v1/auth/me`
* **Propósito:** Retorna la información completa del perfil, roles y estado de la cuenta del usuario portador del token JWT de la sesión activa.
* **Nivel de Acceso:** Autenticado.
* **Respuestas:**
  * `200 OK`:
    ```json
    {
      "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "email": "viajero@andeva.io",
      "username": "cmendoza",
      "full_name": "Carlos Mendoza",
      "role": "USER",
      "status": "ACTIVE",
      "email_verified": true,
      "created_at": "2026-09-29T18:30:00Z"
    }
    ```

---

## 4. Bounded Context Routing: Topología y Motor de Grafos

El Bounded Context de Routing gestiona la red aeroportuaria en memoria RAM (**3,354 nodos y 37,326 aristas**) compilada de OpenFlights, resuelve algoritmos geodésicos en $O(E \log V)$ y provee telemetría cuantitativa para el benchmarking académico.

### 4.1. `POST /api/v1/routing/routes/search`
* **Propósito:** Resuelve la trayectoria de vuelo física óptima entre dos aeropuertos mediante el motor algorítmico en memoria. Ejecuta la búsqueda informada $A^*$ guiada por la heurística admisible de Haversine ($h(u) = d_H(u, \text{dest}) / v_{\text{crucero}}$), calcula la cota inferior teórica de duración física ($T_{\min}$) para normalizar el motor multicriterio, interpola 26 waypoints ortodrómicos para la visualización en MapLibre GL 2D / deck.gl y genera la telemetría comparativa con Dijkstra y BFS.
* **Nivel de Acceso:** Público.
* **Request Body (`RouteSearchRequestSchema`):**
  ```json
  {
    "origin": "LIM",
    "destination": "MAD",
    "max_stops": 2,
    "max_duration_minutes": 1200,
    "strategy": "OPTIMAL_DURATION"
  }
  ```
* **Respuestas:**
  * `200 OK` (`RouteSearchResponseSchema`):
    ```json
    {
      "route_id": "route_LIM_MAD_1759178400",
      "origin": "LIM",
      "destination": "MAD",
      "total_distance_km": 9524.38,
      "estimated_flight_duration_minutes": 744,
      "total_stops": 0,
      "path_nodes": ["LIM", "MAD"],
      "legs": [
        {
          "origin": "LIM",
          "destination": "MAD",
          "distance_km": 9524.38,
          "estimated_duration_minutes": 744,
          "geodesic_waypoints": [
            [-77.1143, -12.0219],
            [-60.5012, -2.1092],
            [-30.1294, 15.4091],
            [-3.5673, 40.4839]
          ]
        }
      ],
      "telemetry": {
        "algorithm_name": "ASTAR",
        "execution_time_ms": 1.84,
        "execution_time_us": 1840,
        "nodes_expanded": 142,
        "edges_evaluated": 1240,
        "effective_branching_factor": 2.14,
        "cache_hit": false,
        "benchmark_comparison": {
          "dijkstra_nodes_expanded": 1890,
          "dijkstra_execution_time_ms": 19.20,
          "bfs_stops_count": 0,
          "efficiency_gain_pct": 92.48
        }
      }
    }
    ```
  * `400 Bad Request`: Si el origen y destino son idénticos (`origin == destination`).
  * `404 Not Found`: Si uno de los códigos IATA no existe en la red aeroportuaria comercial activa o no existe conexidad física en la componente comercial (evaluada en $O(\alpha(V))$ por UFDS).

### 4.2. `GET /api/v1/routing/airports/nearest`
* **Propósito:** Resuelve la terminal aeroportuaria comercial más cercana para localidades, municipios o destinos turísticos que carecen de aeropuerto propio (por ejemplo, Máncora, Machu Picchu o Andorra). Ejecuta un barrido lineal exhaustivo en memoria RAM ($O(V)$, $< 0.08\text{ ms}$) calculando la distancia ortodrómica de Haversine contra los 3,354 nodos comerciales del sistema.
* **Nivel de Acceso:** Público.
* **Parámetros de Consulta (Query Params):**
  * `latitude` (`float`, requerido): Latitud en grados decimales (entre $-90.0$ y $90.0$).
  * `longitude` (`float`, requerido): Longitud en grados decimales (entre $-180.0$ y $180.0$).
  * `limit` (`int`, opcional, por defecto `3`): Cantidad de terminales de proximidad alternativas a retornar.
* **Ejemplo de Solicitud:** `GET /api/v1/routing/airports/nearest?latitude=-4.1078&longitude=-81.0475&limit=2`
* **Respuestas:**
  * `200 OK` (`NearestAirportResponseSchema`):
    ```json
    {
      "query_location": {
        "latitude": -4.1078,
        "longitude": -81.0475
      },
      "nearest_airport": {
        "iata": "TYL",
        "icao": "SPYL",
        "name": "Capitán FAP Víctor Montes Arias Airport",
        "city": "Talara",
        "country": "Peru",
        "distance_km": 68.42,
        "latitude": -4.3764,
        "longitude": -81.2542
      },
      "alternative_airports": [
        {
          "iata": "PIU",
          "name": "Capitán FAP Guillermo Concha Iberico International Airport",
          "city": "Piura",
          "country": "Peru",
          "distance_km": 118.25
        }
      ]
    }
    ```

### 4.3. `GET /api/v1/routing/airports`
* **Propósito:** Provee el catálogo maestro de terminales aéreas comerciales para el buscador flotante con autocompletado en el frontend, permitiendo búsquedas rápidas por nombre, ciudad, país o código IATA.
* **Nivel de Acceso:** Público.
* **Parámetros de Consulta:**
  * `q` (`string`, opcional): Término de búsqueda de coincidencia parcial en nombre, ciudad o IATA.
  * `country` (`string`, opcional): Filtro estricto por nombre de país.
  * `page` (`int`, opcional, default `1`): Número de página.
  * `page_size` (`int`, opcional, default `20`, máximo `100`): Registros por página.
* **Respuestas:**
  * `200 OK`: Lista paginada con metadatos de los aeropuertos encontrados.

### 4.4. `GET /api/v1/routing/airports/{iata_code}`
* **Propósito:** Retorna la ficha técnica de un aeropuerto comercial específico indexado en la red a partir de su código IATA de 3 letras.
* **Nivel de Acceso:** Público.
* **Respuestas:**
  * `200 OK`: Metadatos del nodo (nombre, ciudad, coordenadas geodésicas, altitud, zona horaria y grado $k$).
  * `404 Not Found`: Si el código IATA no existe en la red.

### 4.5. `GET /api/v1/routing/topology/metrics`
* **Propósito:** Expone las métricas analíticas y cuantitativas del grafo residente en memoria RAM para fines de validación técnica y auditoría de la cátedra de Complejidad Algorítmica.
* **Nivel de Acceso:** Público.
* **Respuestas:**
  * `200 OK`:
    ```json
    {
      "total_airports": 3354,
      "total_routes_directed_unique": 37326,
      "multigraph_raw_routes": 67305,
      "average_degree": 22.25,
      "connected_components_count": 1,
      "graph_memory_footprint_bytes": 10485760,
      "spatial_indexing": "Haversine In-Memory KD-Tree / Adjacency Array",
      "status": "HEALTHY"
    }
    ```

---

## 5. Bounded Context Quotes: Inteligencia Tarifaria y Optimización Pareto

El Bounded Context de Quotes es el núcleo económico de Navby. Se integra con **FlightAPI** mediante la Capa Anticorrupción (ACL), aplica caché distribuida en Redis 7 (TTL 30 min) y computa la **frontera de Pareto** en microsegundos para entregar itinerarios de vuelo óptimos no dominados.

### 5.1. `POST /api/v1/quotes/search`
* **Propósito:** Ejecuta una cotización completa de tarifas reales de mercado para vuelos de solo ida (`ONE_WAY`) o ida y vuelta (`ROUND_TRIP`). El proceso es determinista:
  1. Valida la viabilidad topológica en memoria RAM mediante el escudo UFDS ($0.00 USD de costo).
  2. Comprueba si existe caché previa en Redis 7 (`quote:{origin}:{dest}:{date}:{cabin}:{pax}`). Ante *Cache Hit*, retorna de inmediato en $< 5\text{ ms}$ a 0 créditos de penalización.
  3. Ante *Cache Miss*, descuenta atómicamente **5 créditos Navby** de la billetera del usuario en Redis.
  4. Realiza **una sola petición HTTPS** hacia FlightAPI (`/onewaytrip` o `/roundtrip`), consumiendo 2 créditos del plan de la plataforma.
  5. Ejecuta la optimización multicriterio en memoria: normaliza precio monetario, duración en minutos y escalas con base en $T_{\min}$, descarta alternativas dominadas (frontera de Pareto) y clasifica las recomendaciones óptimas.
* **Nivel de Acceso:** Autenticado (`Bearer Token`).
* **Request Body (`QuoteSearchRequestSchema`):**
  ```json
  {
    "origin": "LIM",
    "destination": "MAD",
    "departure_date": "2026-10-15",
    "return_date": "2026-10-30",
    "cabin_class": "ECONOMY",
    "adults": 1,
    "children": 0,
    "infants": 0,
    "currency": "USD"
  }
  ```
* **Respuestas:**
  * `200 OK` (`QuoteSearchResponseSchema`):
    ```json
    {
      "session_id": "session_8f3d1b9a2c_1759178400",
      "search_type": "ROUND_TRIP",
      "currency": "USD",
      "cached": false,
      "credits_debited": 5,
      "remaining_user_credits": 45,
      "market_offers_count": 42,
      "pareto_optimal_count": 3,
      "podium": {
        "best_value": {
          "itinerary_id": "itn_opt_001",
          "airline_name": "Air Europa",
          "airline_code": "UX",
          "total_price": 845.50,
          "total_duration_minutes": 725,
          "total_stops": 0,
          "utility_score": 0.94,
          "deep_link": "https://book.flightapi.io/checkout?ref=navby&id=itn_opt_001",
          "legs": [...]
        },
        "cheapest": {
          "itinerary_id": "itn_opt_002",
          "airline_name": "Avianca",
          "airline_code": "AV",
          "total_price": 620.00,
          "total_duration_minutes": 980,
          "total_stops": 1,
          "utility_score": 0.88,
          "deep_link": "https://book.flightapi.io/checkout?ref=navby&id=itn_opt_002",
          "legs": [...]
        },
        "fastest": {
          "itinerary_id": "itn_opt_003",
          "airline_name": "Iberia",
          "airline_code": "IB",
          "total_price": 910.00,
          "total_duration_minutes": 710,
          "total_stops": 0,
          "utility_score": 0.91,
          "deep_link": "https://book.flightapi.io/checkout?ref=navby&id=itn_opt_003",
          "legs": [...]
        }
      },
      "all_candidates": [...]
    }
    ```
  * `402 Payment Required`: Saldo de créditos insuficiente en la billetera del usuario (requiere recargar mediante paquete prepagado de Mercado Pago o esperar la cuota diaria).
  * `404 Not Found`: Si la ruta entre origen y destino no tiene conectividad física o comercial.
  * `503 Service Unavailable`: Si el agregador externo FlightAPI se encuentra saturado y el Circuit Breaker conmuta a estado `OPEN`.

### 5.2. `GET /api/v1/quotes/{session_id}`
* **Propósito:** Recupera el desglose íntegro de ofertas de vuelo recopiladas durante una sesión de búsqueda previa sin volver a invocar a la API externa ni debitar créditos.
* **Nivel de Acceso:** Autenticado.
* **Respuestas:**
  * `200 OK`: Estructura completa de la sesión de búsqueda con todas las alternativas de aerolíneas evaluadas.
  * `404 Not Found`: Sesión expirada o inexistente en caché.

### 5.3. `GET /api/v1/quotes/{session_id}/podium`
* **Propósito:** Extrae de forma concisa exclusivamente las 3 alternativas ganadoras del podio de Pareto (Mejor Balance, Más Barato y Más Rápido) para la visualización de tarjetas destacadas en la interfaz de usuario.
* **Nivel de Acceso:** Autenticado.
* **Respuestas:**
  * `200 OK` (`ParetoPodiumResponseSchema`).

### 5.4. `GET /api/v1/quotes/quota/status`
* **Propósito:** Endpoint de monitoreo operacional que expone el porcentaje de cuota consumido sobre el plan corporativo de FlightAPI y el estado actual del Circuit Breaker (`CLOSED`, `OPEN`, `HALF_OPEN`).
* **Nivel de Acceso:** Autenticado (`Role: ADMIN` o desarrollador autorizado).
* **Respuestas:**
  * `200 OK`:
    ```json
    {
      "monthly_requests_limit": 10000,
      "monthly_requests_used": 1420,
      "circuit_breaker_state": "CLOSED",
      "failure_count": 0,
      "resilience_mode": "LIVE"
    }
    ```

---

## 6. Bounded Context Itineraries: Custodia y Gestión de Itinerarios

El Bounded Context de Itineraries administra la persistencia transaccional en PostgreSQL 16 de los itinerarios elegidos, guardados y planificados por los usuarios registrados.

### 6.1. `POST /api/v1/itineraries`
* **Propósito:** Almacena de forma persistente un itinerario de vuelo seleccionado a partir de una cotización de mercado exitosa, asociándolo a la cuenta del usuario.
* **Nivel de Acceso:** Autenticado.
* **Request Body (`CreateItineraryRequestSchema`):**
  ```json
  {
    "name": "Vacaciones Europa 2026",
    "session_id": "session_8f3d1b9a2c_1759178400",
    "quote_candidate_id": "itn_opt_001",
    "origin": "LIM",
    "destination": "MAD",
    "departure_date": "2026-10-15",
    "return_date": "2026-10-30",
    "total_price": 845.50,
    "currency": "USD",
    "notes": "Vuelo directo con Air Europa."
  }
  ```
* **Respuestas:**
  * `201 Created`:
    ```json
    {
      "itinerary_id": "d3b07384-d113-4a15-b778-4db8a313e9a1",
      "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "name": "Vacaciones Europa 2026",
      "status": "ACTIVE",
      "created_at": "2026-09-29T18:35:00Z"
    }
    ```

### 6.2. `GET /api/v1/itineraries/{itinerary_id}`
* **Propósito:** Recupera la información detallada de un itinerario persistido, incluyendo sus tramos, aerolíneas, precios guardados y enlaces de reserva oficiales.
* **Nivel de Acceso:** Autenticado (verificación de propiedad: solo el usuario dueño puede leerlo).
* **Respuestas:**
  * `200 OK`: Entidad completa de itinerario.
  * `403 Forbidden`: Si el itinerario pertenece a otro usuario.
  * `404 Not Found`: Si no existe el identificador en la base de datos.

### 6.3. `GET /api/v1/itineraries`
* **Propósito:** Retorna la lista paginada de todos los itinerarios creados por el usuario autenticado, ordenados cronológicamente por fecha de creación o de salida.
* **Nivel de Acceso:** Autenticado.
* **Parámetros de Consulta:**
  * `status` (`string`, opcional: `ACTIVE`, `ARCHIVED`, `CANCELLED`).
  * `page` (`int`, default `1`).
  * `page_size` (`int`, default `10`).
* **Respuestas:**
  * `200 OK`: Lista paginada de itinerarios.

### 6.4. `PATCH /api/v1/itineraries/{itinerary_id}/name`
* **Propósito:** Actualiza el nombre personalizado de un itinerario existente.
* **Nivel de Acceso:** Autenticado.
* **Request Body:**
  ```json
  {
    "name": "Luna de Miel en Madrid"
  }
  ```
* **Respuestas:**
  * `200 OK`: Itinerario renombrado exitosamente.

### 6.5. `PATCH /api/v1/itineraries/{itinerary_id}/notes`
* **Propósito:** Actualiza las anotaciones de viaje del usuario en el itinerario persistido.
* **Nivel de Acceso:** Autenticado.
* **Request Body:**
  ```json
  {
    "notes": "Equipaje de mano de 10 kg incluido; llevar pasaporte biométrico."
  }
  ```
* **Respuestas:**
  * `200 OK`: Notas actualizadas.

### 6.6. `POST /api/v1/itineraries/{itinerary_id}/archive`
* **Propósito:** Cambia el estado de un itinerario a `ARCHIVED` para ocultarlo de la vista principal sin eliminarlo del historial.
* **Nivel de Acceso:** Autenticado.
* **Respuestas:**
  * `200 OK`: Itinerario archivado.

### 6.7. `DELETE /api/v1/itineraries/{itinerary_id}`
* **Propósito:** Aplica eliminación lógica (*soft delete*) sobre el itinerario del usuario.
* **Nivel de Acceso:** Autenticado.
* **Respuestas:**
  * `204 No Content`: Itinerario eliminado.

---

## 7. Bounded Context Billing: Billetera y Pagos con Mercado Pago

El Bounded Context de Billing administra la economía de créditos del usuario, aplica el consumo de cuotas mediante scripts Lua atómicos en Redis 7 y procesa la compra de paquetes prepagados mediante **Mercado Pago Checkout Pro**.

### 7.1. `GET /api/v1/billing/wallets/me`
* **Propósito:** Consulta el estado actual de la billetera de créditos del usuario portador del token JWT. Detalla los créditos de cortesía diarios (`free_credits`), los créditos adquiridos perpetuos (`paid_credits`), el saldo total disponible y la fecha de expiración de la cuota diaria (00:00 UTC).
* **Nivel de Acceso:** Autenticado.
* **Respuestas:**
  * `200 OK`:
    ```json
    {
      "wallet_id": "wal_8f3d1b9a2c_001",
      "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "free_credits": 10,
      "paid_credits": 50,
      "total_credits": 60,
      "daily_grant_expires_at": "2026-09-30T00:00:00Z",
      "equivalent_searches": 12
    }
    ```

### 7.2. `GET /api/v1/billing/wallets/me/transactions`
* **Propósito:** Retorna el extracto de cuenta contable paginado con todos los movimientos de saldo del usuario (débitos por búsqueda, acreditación diaria de cortesía, recargas comerciales y expiraciones).
* **Nivel de Acceso:** Autenticado.
* **Parámetros de Consulta:**
  * `page` (`int`, default `1`).
  * `page_size` (`int`, default `20`).
* **Respuestas:**
  * `200 OK`: Lista paginada de transacciones asentadas en la tabla `credit_transactions`.

### 7.3. `GET /api/v1/billing/packages`
* **Propósito:** Retorna el catálogo oficial de paquetes prepagados de recarga de créditos disponibles para adquisición en moneda local (PEN) y divisa internacional (USD).
* **Nivel de Acceso:** Público.
* **Respuestas:**
  * `200 OK`:
    ```json
    {
      "packages": [
        {
          "package_code": "pack_50",
          "name": "Paquete Inicial / Escapada",
          "credits": 50,
          "equivalent_searches": 10,
          "price_pen": 9.90,
          "price_usd": 2.49,
          "currency_rates": { "PEN": 9.90, "USD": 2.49 },
          "popular": false
        },
        {
          "package_code": "pack_100",
          "name": "Paquete Frecuente / Viajero",
          "credits": 100,
          "equivalent_searches": 20,
          "price_pen": 16.90,
          "price_usd": 4.49,
          "currency_rates": { "PEN": 16.90, "USD": 4.49 },
          "popular": true
        },
        {
          "package_code": "pack_250",
          "name": "Paquete Corporativo / Nómada",
          "credits": 250,
          "equivalent_searches": 50,
          "price_pen": 34.90,
          "price_usd": 8.99,
          "currency_rates": { "PEN": 34.90, "USD": 8.99 },
          "popular": false
        }
      ]
    }
    ```

### 7.4. `POST /api/v1/billing/orders`
* **Propósito:** Registra una intención de compra para un paquete de créditos e interactúa con la pasarela de **Mercado Pago** para generar la preferencia de pago de Checkout Pro. Retorna los enlaces de redirección a la pasarela (`init_point` y `sandbox_init_point`).
* **Nivel de Acceso:** Autenticado.
* **Request Body (`CreateCreditOrderRequestSchema`):**
  ```json
  {
    "package_code": "pack_100",
    "currency": "PEN"
  }
  ```
* **Respuestas:**
  * `201 Created`:
    ```json
    {
      "order_id": "ord_8f3d1b9a2c_1759178400",
      "package_code": "pack_100",
      "credits_to_grant": 100,
      "amount": 16.90,
      "currency": "PEN",
      "status": "PENDING",
      "mercadopago_preference_id": "98127391-72a1-4321-b3b2-910283910293",
      "init_point": "https://www.mercadopago.com.pe/checkout/v1/redirect?pref_id=98127391-72a1-4321-b3b2-910283910293",
      "sandbox_init_point": "https://sandbox.mercadopago.com.pe/checkout/v1/redirect?pref_id=98127391-72a1-4321-b3b2-910283910293",
      "created_at": "2026-09-29T18:40:00Z"
    }
    ```
  * `400 Bad Request`: Si el código de paquete o divisa no es soportado.

### 7.5. `GET /api/v1/billing/orders/{order_id}`
* **Propósito:** Consulta el estado de procesamiento de una orden de compra específica.
* **Nivel de Acceso:** Autenticado.
* **Respuestas:**
  * `200 OK`: Estado de la orden (`PENDING`, `APPROVED`, `REJECTED`, `CANCELLED`).

### 7.6. `POST /api/v1/billing/webhooks/mercadopago`
* **Propósito:** Receptor perimetral de notificaciones HTTP (Webhooks) emitidas por Mercado Pago cuando se actualiza el estado de una transacción. El controlador aplica:
  1. Validación criptográfica de la cabecera `x-signature` con el secreto del webhook (`MERCADOPAGO_WEBHOOK_SECRET`).
  2. Verificación de **idempotencia** en Redis 7 (`idempotency:mp:{payment_id}`) para evitar dobles acreditaciones ante reintentos automáticos.
  3. Despacho del evento `CreditOrderPaidDomainEvent` y acreditación atómica de los créditos perpetuos en la billetera del usuario.
* **Nivel de Acceso:** Público con verificación de firma HMAC-SHA256.
* **Cabeceras Críticas:**
  * `x-signature`: Firma HMAC con timestamp (`ts=...,v1=...`).
  * `x-request-id`: Identificador de trazabilidad del webhook.
* **Request Body (Emitido por Mercado Pago):**
  ```json
  {
    "action": "payment.created",
    "api_version": "v1",
    "data": {
      "id": "12345678901"
    },
    "date_created": "2026-09-29T18:40:15Z",
    "id": 1029384756,
    "live_mode": false,
    "type": "payment"
  }
  ```
* **Respuestas:**
  * `200 OK`: Evento procesado o descartado por idempotencia de manera satisfactoria.
  * `401 Unauthorized`: Firma criptográfica ausente o no coincidente.

---

## 8. Servicios de Diagnóstico, Salud y Observabilidad

### 8.1. `GET /health` y `GET /api/v1/health`
* **Propósito:** Sondeo unificado de disponibilidad (*Liveness* y *Readiness*) para orquestadores perimetrales (Docker Compose, Kubernetes o Caddy). Verifica la conectividad asíncrona hacia PostgreSQL 16, la latencia de ping hacia Redis 7 y la presencia del grafo mundial cargado en memoria RAM.
* **Nivel de Acceso:** Público.
* **Respuestas:**
  * `200 OK`:
    ```json
    {
      "status": "HEALTHY",
      "timestamp": "2026-09-29T18:42:00Z",
      "services": {
        "database": { "status": "UP", "engine": "PostgreSQL 16", "latency_ms": 1.2 },
        "cache": { "status": "UP", "engine": "Redis 7", "latency_ms": 0.4 },
        "graph_in_memory": { "status": "UP", "nodes": 3354, "edges": 37326 }
      }
    }
    ```
  * `503 Service Unavailable`: Si alguno de los servicios esenciales está degradado.

### 8.2. `GET /metrics`
* **Propósito:** Expone el catálogo de métricas en formato estándar de **Prometheus** para la ingestión por paneles de telemetría y grafana de observabilidad.
* **Nivel de Acceso:** Red interna o autenticación básica perimetral.
* **Métricas Principales Expuestas:**
  * `navby_routing_algorithm_duration_seconds`: Histograma de duración de $A^*$, Dijkstra y BFS.
  * `navby_routing_nodes_evaluated_total`: Contador de nodos explorados por algoritmo.
  * `navby_routing_edges_explored_total`: Contador de aristas evaluadas.
  * `navby_routing_graph_nodes_total`: Métrica Gauge fija de 3,354 nodos activos.
  * `navby_routing_graph_edges_total`: Métrica Gauge fija de 37,326 aristas activas.
  * `navby_quotes_flightapi_requests_total`: Contador de llamadas a la API externa.
  * `navby_quotes_cache_hits_total`: Contador de aciertos en caché Redis fast-path.
