# Documentación Técnica de Integración: FlightAPI

> **Rol en la arquitectura:** Este documento constituye la especificación de referencia para la integración del proveedor externo **FlightAPI** ([flightapi.io](https://www.flightapi.io)) dentro del backend de Navby (`navby-platform`). Define los contratos HTTP, parámetros, esquemas de respuesta, gestión de cuotas de créditos y el diseño del adaptador de la Capa Anticorrupción (Anti-Corruption Layer - ACL).

---

## 1. Visión General del Servicio y Modelo de Costos

**FlightAPI** es un agregador de precios y disponibilidad de vuelos en tiempo real que consolida datos de más de 700 aerolíneas y agencias de viaje online (OTAs) a nivel global, respaldado por la infraestructura de Skyscanner.

### Información Base del Proveedor
* **URL Base:** `https://api.flightapi.io`
* **Protocolo:** HTTPS (TLS 1.3)
* **Formato de intercambio:** JSON
* **Autenticación:** Clave de API personal (`api_key`) inyectada en la ruta o como parámetro de consulta. Debe custodiarse exclusivamente en variables de entorno del servidor (`FLIGHT_API_KEY`), nunca expuesta al cliente.

### Catálogo de Endpoints y Consumo de Créditos
FlightAPI factura las consultas bajo un esquema de créditos por petición exitosa:

| Endpoint | Método | URL Canónica | Costo en Créditos | Rol en Navby |
| :--- | :---: | :--- | :---: | :--- |
| **Oneway Trip API** | `GET` | `/onewaytrip/<api_key>/<dep>/<arr>/<date>/<adults>/<children>/<infants>/<cabin>/<curr>` | **2 créditos** | Cotización de vuelos de solo ida para rutas candidatas del grafo. |
| **Round Trip API** | `GET` | `/roundtrip/<api_key>/<dep>/<arr>/<date_dep>/<date_arr>/<adults>/<children>/<infants>/<cabin>/<curr>` | **2 créditos** | Cotización de viajes de ida y vuelta para rutas candidatas del grafo. |

---

## 2. Especificación de Endpoints

### 2.1. Oneway Trip API (Solo Ida)
Diseñado para la cotización de trayectos de un solo sentido entre un aeropuerto de origen y uno de destino.

#### Esquema de Ruta y Parámetros
```http
GET https://api.flightapi.io/onewaytrip/{api_key}/{departure_airport_code}/{arrival_airport_code}/{departure_date}/{number_of_adults}/{number_of_childrens}/{number_of_infants}/{cabin_class}/{currency}
```

#### Diccionario de Parámetros
| Parámetro | Ubicación | Tipo | Obligatorio | Descripción y Restricciones |
| :--- | :---: | :---: | :---: | :--- |
| `api_key` | Path | String | Sí | Clave de API asignada en el panel de FlightAPI. |
| `departure_airport_code` | Path | String(3) | Sí | Código IATA de 3 letras del aeropuerto de salida (ej. `LIM`). |
| `arrival_airport_code` | Path | String(3) | Sí | Código IATA de 3 letras del aeropuerto de llegada (ej. `MIA`). |
| `departure_date` | Path | String | Sí | Fecha de salida en formato ISO `YYYY-MM-DD` (debe ser futura). |
| `number_of_adults` | Path | Integer | Sí | Cantidad de pasajeros adultos ($\ge 1$). |
| `number_of_childrens` | Path | Integer | Sí | Cantidad de pasajeros niños de 2 a 11 años ($\ge 0$). |
| `number_of_infants` | Path | Integer | Sí | Cantidad de infantes menores de 2 años en regazo ($\ge 0$). |
| `cabin_class` | Path | Enum | Sí | Valores permitidos: `Economy`, `Premium_Economy`, `Business`, `First`. |
| `currency` | Path | String(3) | Sí | Código de moneda ISO 4217 (ej. `USD`, `PEN`, `EUR`). |

#### Ejemplo de Petición cURL
```bash
curl -X GET "https://api.flightapi.io/onewaytrip/${FLIGHT_API_KEY}/LIM/CUZ/2026-10-15/1/0/0/Economy/USD"
```

---

### 2.2. Round Trip API (Ida y Vuelta)
Diseñado para cotizaciones que comprenden un tramo de ida y un tramo de retorno.

#### Esquema de Ruta y Parámetros
```http
GET https://api.flightapi.io/roundtrip/{api_key}/{departure_airport_code}/{arrival_airport_code}/{departure_date}/{arrival_date}/{number_of_adults}/{number_of_childrens}/{number_of_infants}/{cabin_class}/{currency}
```

#### Parámetros Adicionales frente a OneWay
* `arrival_date` (Path, String `YYYY-MM-DD`, Obligatorio): Fecha del vuelo de retorno. Debe satisfacer `arrival_date >= departure_date`.

#### Ejemplo de Petición cURL
```bash
curl -X GET "https://api.flightapi.io/roundtrip/${FLIGHT_API_KEY}/LIM/MIA/2026-11-01/2026-11-15/2/1/0/Economy/USD"
```

---

### 2.3. Exclusión Explícita de Multi Trip API (Fuera de Alcance)

El endpoint `GET /multitrip` de FlightAPI **no se contempla en el alcance de Navby** debido a tres restricciones fundamentales:

1. **Restricción rígida de tramos:** La API exige de forma mandatoria entre 3 y 5 tramos (`trips = 3..5`). No permite itinerarios simples de 2 tramos o trayectos flexibles.
2. **Costo operativo desproporcionado:** Consume **5 créditos por consulta** (2.5 veces el costo de OneWay o RoundTrip), lo que agotaría de inmediato los 5 créditos diarios gratuitos del usuario en una sola búsqueda.
3. **Desconexión con la optimización en grafos:** La planificación multi-ciudad (*multi-city*) requiere que el usuario imponga ciudades y fechas intermedias fijas de forma manual. Por tanto, no constituye un problema de camino mínimo sobre un grafo de escala global, apartándose del propósito del motor algorítmico de Navby.

---

## 3. Estructura y Esquema de Respuesta JSON

La respuesta de FlightAPI está normalizada en una estructura relacional desnormalizada compuesta por diccionarios indexados por ID:

```json
{
  "itineraries": [
    {
      "id": "itin_lim_mia_01",
      "leg_ids": ["leg_outbound_101", "leg_inbound_202"],
      "pricing_options": [
        {
          "agents": ["agent_latam", "agent_expedia"],
          "price": {
            "amount": 420.50,
            "update_status": "fresh"
          },
          "items": [
            {
              "agent_id": "agent_latam",
              "amount": 420.50,
              "deep_link": "https://www.latamairlines.com/booking/select?..."
            }
          ]
        }
      ]
    }
  ],
  "legs": [
    {
      "id": "leg_outbound_101",
      "departure": "2026-11-01T08:30:00",
      "arrival": "2026-11-01T14:45:00",
      "duration_in_minutes": 375,
      "stop_count": 0,
      "departure_airport_code": "LIM",
      "arrival_airport_code": "MIA",
      "carrier_ids": ["carrier_latam"],
      "segment_ids": ["seg_001"]
    }
  ],
  "segments": [
    {
      "id": "seg_001",
      "departure": "2026-11-01T08:30:00",
      "arrival": "2026-11-01T14:45:00",
      "duration": 375,
      "origin_station_code": "LIM",
      "destination_station_code": "MIA",
      "marketing_flight_number": "LA2510",
      "marketing_carrier_id": "carrier_latam",
      "operating_carrier_id": "carrier_latam"
    }
  ],
  "carriers": [
    {
      "id": "carrier_latam",
      "name": "LATAM Airlines",
      "iata": "LA",
      "logo": "https://logos.skyscnr.com/images/airlines/favicon/LA.png"
    }
  ],
  "places": [
    {
      "id": "LIM",
      "name": "Jorge Chávez International Airport",
      "city": "Lima",
      "country": "Peru"
    },
    {
      "id": "MIA",
      "name": "Miami International Airport",
      "city": "Miami",
      "country": "United States"
    }
  ]
}
```

### Campos Clave Extraídos por Navby
1. **`itineraries[].pricing_options[].items[0].deep_link`:** Enlace directo de reserva hacia la aerolínea o agencia oficial.
2. **`itineraries[].pricing_options[].price.amount`:** Tarifa monetaria consolidada para el total de pasajeros.
3. **`legs[].duration_in_minutes`:** Duración real del vuelo (sustituye la estimación por Haversine).
4. **`legs[].stop_count`:** Cantidad exacta de escalas comerciales.
5. **`carriers[].name` y `carriers[].logo`:** Identidad visual de la aerolínea operadora para la tarjeta de resultado.

---

## 4. Diseño del Adaptador ACL (Anti-Corruption Layer) en Navby

Para aislar el dominio de Navby de los cambios en los contratos de FlightAPI, la integración se encapsula estrictamente bajo la arquitectura hexagonal del backend:

```
app/modules/flight_planning/
├── application/
│   └── acl/
│       └── ports/
│           └── flight_api_port.py       # Interfaz abstracta (Protocol)
└── infrastructure/
    └── adapters/
        ├── flight_api_adapter.py        # Adaptador HTTP concreto (httpx)
        └── flight_api_assembler.py      # Mapeo de JSON externo a Domain DTOs
```

### Puerto Abstracto (`FlightApiPort`)
```python
from typing import Protocol
from app.modules.flight_planning.domain.model.dtos import (
    FlightSearchCriteria,
    FlightOfferResult,
)
from app.shared.domain.result import Result

class FlightApiPort(Protocol):
    async def search_oneway_flights(
        self, criteria: FlightSearchCriteria
    ) -> Result[FlightOfferResult]:
        ...

    async def search_roundtrip_flights(
        self, criteria: FlightSearchCriteria
    ) -> Result[FlightOfferResult]:
        ...
```

---

## 5. Estrategia de Resiliencia, Caché y Presupuesto de Créditos

Dado que cada consulta consume créditos de pago (2 créditos por búsqueda), el backend aplica cuatro capas de contención:

1. **Pre-filtrado Topológico sobre Grafo Local:** El motor de grafos evalúa todas las permutaciones teóricas y **solo invoca a FlightAPI para las 3 a 5 mejores rutas candidatas**, evitando el despilfarro de cuotas en trayectos inviables.
2. **Caché en Memoria con Redis (TTL de 30 minutos):** Las cotizaciones para una misma tupla `(origen, destino, fecha, cabina, pax)` se almacenan en Redis con un tiempo de vida (*TTL*) de 30 minutos. Las búsquedas concurrentes o repetidas se resuelven con latencia $< 10\text{ ms}$ y costo de $0$ créditos.
3. **Control de Cuotas Transaccional en Base de Datos:** Antes de ejecutar la llamada externa, el caso de uso descuenta los créditos de la cuenta del usuario (`credits_wallet`). Si el saldo es insuficiente, la petición se rechaza anticipadamente con `Result.failure(InsufficientCreditsError)`.
4. **Degradación Controlada (Circuit Breaker):** En caso de errores HTTP `402 Payment Required` (cuota general de la startup agotada) o `429 Too Many Requests`, el backend captura la excepción, notifica al administrador y sirve la última cotización en caché con una bandera visual de *precio referencial histórico*.
