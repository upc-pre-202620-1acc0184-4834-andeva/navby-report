# Guía Maestra de Diseño Táctico DDD y Estándar de Arquitectura (Navby Platform)

> **Rol en el pipeline documental:** Esta guía es el **estándar supremo de ingeniería** para el backend de Navby (`navby-platform`), desarrollado en **Python 3.12 + FastAPI + uv**. Establece las directrices normativas, los patrones tácticos (Clean Architecture, Hexagonal, CQRS, ACL, OHS y Functional Result Monad) y el código canónico del Shared Kernel que todo desarrollador, agente de IA y módulo debe implementar rigurosamente.
>
> **Documentos relacionados:**
> - Biblia de producto: [../navby-documentation.md](../navby-documentation.md)
> - Arquitectura de plataforma: [navby-platform-architecture.md](navby-platform-architecture.md)
> - Esquema de base de datos: [navby-database-schema.md](navby-database-schema.md)
> - Especificación táctica canónica: [navby-backend-tactical-specification.md](navby-backend-tactical-specification.md)

---

## 1. Los 10 Mandamientos Arquitectónicos de Navby Platform

Inspirados en los estándares de excelencia técnica de la arquitectura de referencia (`learning-center-platform`) y adaptados idiomáticamente a **Python 3.12 + FastAPI + uv**, se establecen como normas inquebrantables los siguientes 10 principios:

1. **Inmutabilidad Absoluta en Casos de Uso:** Todos los Commands, Queries, Value Objects y Domain Events son inmutables mediante `@dataclass(frozen=True)`. Sus constructores o métodos `__post_init__` validan precondiciones (no nulos, formatos válidos, rangos numéricos y longitudes).
2. **Hexagonal Persistence Decoupling:** Las entidades y raíces de agregado del dominio **nunca importan SQLAlchemy ni librerías de infraestructura**. Heredan de `AbstractDomainAggregateRoot`. Los modelos ORM de persistencia residen exclusivamente en `infrastructure/persistence/entities/` y son transformados bidireccionalmente mediante ensambladores de persistencia (`infrastructure/persistence/assemblers/`).
3. **Control de Flujo Funcional (`Result[T]`):** Se prohíbe el uso de excepciones (`raise Exception`) para el control de flujo de negocio ordinario (recursos no encontrados, saldos insuficientes, conflictos o validaciones). Los casos de uso retornan `Result.success(value)` o `Result.failure(ApplicationError)`.
4. **Separación Estricta de Transporte (Assemblers):** Los controladores REST de FastAPI nunca reciben ni devuelven agregados de dominio ni modelos ORM. Emplean ensambladores (`interfaces/rest/assemblers/`) para transformar el esquema Pydantic entrante en un `Command`, invocar el caso de uso y transformar el resultado en un esquema Pydantic de respuesta.
5. **Aislamiento Físico entre Bounded Contexts (No Foreign Keys Cruzadas):** Queda terminantemente prohibido definir relaciones de Foreign Key físicas en PostgreSQL (`FOREIGN KEY`) entre tablas que pertenecen a distintos Bounded Contexts. La vinculación inter-contexto se realiza exclusivamente mediante **Value Objects de ID lógico** (`UserId`, `IATACode`).
6. **Open Host Service (OHS) para Consultas Síncronas:** Todo Bounded Context que deba proveer información o servicios a otro dentro del monolito expone una fachada pública en su paquete `interfaces/acl/facade/` (ej. `AirportCatalogFacade`, `IamContextFacade`, `CreditAuthorizerFacade`), tipada con `typing.Protocol`.
7. **Anti-Corruption Layer (ACL) para Consumo Externo:** Todo consumo de APIs de terceros (Flight API, Mercado Pago, Google Identity, Resend) se desacopla definiendo puertos en `application/acl/ports/` e implementando adaptadores en `infrastructure/adapters/`. Ningún JSON crudo del proveedor cruza hacia la capa de dominio o aplicación.
8. **Coreografía de Eventos de Dominio:** Cuando un agregado muta de estado, registra un evento mediante `self.register_domain_event(event)`. El adaptador de repositorio en infraestructura extrae estos eventos al persistir y los inserta en `outbox_events` (Transactional Outbox).
9. **Auditoría Transversal Estandarizada:** Todas las tablas físicas mutables integran las columnas `created_at` y `updated_at` en formato `TIMESTAMPTZ` mediante el mixin `AuditablePersistenceMixin` de SQLAlchemy.
10. **Contratos Vivos OpenAPI:** Cada endpoint REST expuesto en FastAPI cuenta con tipado estricto mediante Pydantic v2, generando de forma automática la especificación OpenAPI 3.1 viva y validada para los clientes frontend.

---

## 2. Estructura de Paquetes Canónica por Bounded Context

Cada módulo de negocio vive en un paquete autocontenido bajo `app/modules/<context>/` respetando estrictamente la jerarquía de 4 capas:

```
app/modules/<context>/                      # ej. app/modules/iam
├── domain/                                 # Capa de Dominio (Python puro, cero dependencias)
│   ├── model/
│   │   ├── aggregates/                     #   Raíces de agregado (AbstractDomainAggregateRoot)
│   │   ├── entities/                       #   Entidades dependientes internas
│   │   ├── value_objects/                  #   Value objects específicos y Typed IDs (int > 0)
│   │   ├── enums/                          #   Enumeraciones discretas de dominio (StrEnum)
│   │   └── events/                         #   Eventos de dominio internos inmutables (DomainEvent)
│   ├── repositories/                       #   Contratos puros de persistencia (typing.Protocol)
│   ├── services/                           #   Servicios de dominio (lógica de negocio pura)
│   └── exceptions/                         #   Jerarquía semántica de errores (*Exception)
│
├── application/                            # Capa de Aplicación (Casos de uso y orquestación)
│   ├── commands/                           #   DTOs de comandos de escritura (Command)
│   ├── queries/                            #   DTOs de consultas de lectura (Query)
│   ├── handlers/                           #   Manejadores de casos de uso:
│   │   ├── command_handlers/               #     Manejadores de comandos (retornan Result)
│   │   ├── query_handlers/                 #     Manejadores de consultas (retornan Result)
│   │   └── event_handlers/                 #     Manejadores de eventos de dominio internos
│   ├── services/                           #   Servicios de aplicación orquestadores
│   └── acl/                                #   Outbound ACL Services (puertos hacia servicios externos):
│       └── ports/                          #     Protocolos abstractos (EmailService, PaymentGateway)
│
├── interfaces/                             # Capa de Interfaces (Adaptadores primarios)
│   ├── rest/
│   │   ├── controllers/                    #   Clases controladoras OOP (<<RestController>>)
│   │   ├── resources/                      #   DTOs Pydantic v2 inmutables de entrada y salida:
│   │   │   ├── requests/                   #     Esquemas de solicitud (*RequestResource)
│   │   │   └── responses/                  #     Esquemas de respuesta (*ResponseResource)
│   │   └── assemblers/                     #     DTO Assemblers (Resource <-> Command/Query)
│   ├── webhooks/                           #   Controladores de webhooks externos entrantes:
│   │   ├── controllers/                    #     Ej: MercadoPagoWebhookController
│   │   └── resources/                      #     DTOs del payload crudo del proveedor
│   ├── events/                             #   Eventos de integración y consumidores:
│   │   ├── published/                      #     Integration Events (Published Language)
│   │   └── consumers/                      #     Consumidores de brokers asíncronos (si aplica)
│   ├── acl/                                #   Open Host Service (OHS) / Inbound ACL Facade:
│   │   ├── facade/                         #     Fachadas expuestas a otros contextos
│   │   └── dtos/                           #     DTOs públicos inter-contexto
│   └── security/                           #   Guardias de seguridad perimetral HTTP (si aplica)
│
└── infrastructure/                         # Capa de Infraestructura (Adaptadores secundarios)
    ├── persistence/                        #   Persistencia relacional / ORM:
    │   ├── entities/                       #     Modelos ORM físicos (SQLAlchemy Mapped)
    │   ├── converters/                     #     TypeDecorators de SQLAlchemy (GeoPointType, etc.)
    │   ├── repositories/                   #     Consultas de infraestructura (si aplica)
    │   ├── adapters/                       #     Implementaciones concretas (*RepositoryImpl)
    │   └── assemblers/                     #     Mapeadores ORM Entity <-> Agregado de Dominio
    ├── adapters/                           #   Implementaciones de Outbound ACL Services:
    │   ├── email/                          #     ResendEmailAdapter (HTTPS 443)
    │   ├── oauth/                          #     GoogleOAuthAdapter (OIDC)
    │   └── payments/                       #     MercadoPagoPaymentAdapter (Checkout Pro)
    ├── cache/                              #   Adaptadores de caché distribuida:
    │   └── redis/                          #     Adaptadores Redis con scripts Lua atómicos
    └── security/                           #   Servicios concretos de cifrado y tokens:
        ├── hashing/                        #     BCryptPasswordHasher (coste 12 rondas)
        └── tokens/                         #     JwtTokenService (PyJWT HS256)
```

---

## 3. Artefactos Canónicos del Shared Kernel (Python 3.12)

A continuación se detalla la implementación completa de las clases fundacionales del sistema.

### 3.1 Domain Layer: `AbstractDomainAggregateRoot` y `DomainEvent`

```python
# app/shared/domain/model/aggregate_root.py
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass(frozen=True)
class DomainEvent:
    """Evento de dominio base inmutable."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_on: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AbstractDomainAggregateRoot(ABC):
    """
    Raíz de agregado de dominio base.
    Gestiona la acumulación en memoria de eventos de dominio producidos
    durante la ejecución de operaciones de negocio.
    """

    def __init__(self) -> None:
        self._domain_events: list[DomainEvent] = []

    def register_domain_event(self, event: DomainEvent) -> None:
        """Registra un evento consumado en la cola interna del agregado."""
        self._domain_events.append(event)

    def domain_events(self) -> tuple[DomainEvent, ...]:
        """Retorna una tupla inmutable de los eventos acumulados."""
        return tuple(self._domain_events)

    def clear_domain_events(self) -> None:
        """Limpia la colección de eventos tras su despacho efectivo."""
        self._domain_events.clear()
```

### 3.2 Value Objects Transversales: `IATACode` y `GeoPoint` con Haversine

```python
# app/shared/domain/value_objects/geo_point.py
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class IATACode:
    """Código IATA de tres letras mayúsculas normalizado."""
    value: str

    def __post_init__(self) -> None:
        if not self.value or len(self.value.strip()) != 3 or not self.value.strip().isalpha():
            raise ValueError(f"Código IATA inválido: '{self.value}'. Debe contener exactamente 3 letras.")
        object.__setattr__(self, "value", self.value.strip().upper())


@dataclass(frozen=True)
class GeoPoint:
    """
    Coordenada geográfica en estándar WGS84.
    Implementa la fórmula matemática pura del Semiverseno (Haversine).
    """
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError(f"Latitud fuera de rango [-90, 90]: {self.latitude}")
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValueError(f"Longitud fuera de rango [-180, 180]: {self.longitude}")

    def distance_to_in_kilometers(self, other: GeoPoint) -> float:
        """Calcula la distancia geodésica ortodrómica en kilómetros."""
        earth_radius_km = 6371.0
        lat1_rad = math.radians(self.latitude)
        lat2_rad = math.radians(other.latitude)
        delta_lat = math.radians(other.latitude - self.latitude)
        delta_lon = math.radians(other.longitude - self.longitude)

        a = (
            math.sin(delta_lat / 2.0) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return earth_radius_km * c
```

### 3.3 Application Layer: Mónada `Result[T]` y `ApplicationError`

```python
# app/shared/application/result/result.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class ApplicationError:
    """Error semántico tipado de aplicación."""
    code: str
    message: str
    details: tuple[str, ...] = ()

    @classmethod
    def not_found(cls, resource: str, identifier: Any) -> ApplicationError:
        return cls("NOT_FOUND", f"{resource} con id '{identifier}' no fue encontrado.")

    @classmethod
    def conflict(cls, message: str) -> ApplicationError:
        return cls("CONFLICT", message)

    @classmethod
    def bad_request(cls, message: str, details: tuple[str, ...] = ()) -> ApplicationError:
        return cls("BAD_REQUEST", message, details)

    @classmethod
    def unauthorized(cls, message: str = "Credenciales inválidas o token expirado.") -> ApplicationError:
        return cls("UNAUTHORIZED", message)

    @classmethod
    def payment_required(cls, message: str = "Saldo insuficiente de créditos Navby.") -> ApplicationError:
        return cls("PAYMENT_REQUIRED", message)


@dataclass(frozen=True)
class Result(Generic[T]):
    """Mónada funcional que representa éxito o fallo."""
    value: T | None = None
    error: ApplicationError | None = None

    @classmethod
    def success(cls, value: T) -> Result[T]:
        return cls(value=value)

    @classmethod
    def failure(cls, error: ApplicationError) -> Result[T]:
        return cls(error=error)

    @property
    def is_success(self) -> bool:
        return self.error is None

    @property
    def is_failure(self) -> bool:
        return self.error is not None
```

### 3.4 Interfaces Layer: Ensamblador de Respuestas HTTP y Errores RFC 7807

```python
# app/shared/interfaces/rest/response_assembler.py
from __future__ import annotations

from typing import Any, Callable, TypeVar
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.shared.application.result.result import ApplicationError, Result

T = TypeVar("T")
R = TypeVar("R", bound=BaseModel)


def result_to_response(
    result: Result[T],
    resource_assembler: Callable[[T], R] | None = None,
    success_status: int = status.HTTP_200_OK,
) -> JSONResponse:
    """
    Transforma un Result funcional en una respuesta HTTP estandarizada
    con el código de estado adecuado y contrato RFC 7807 ante fallos.
    """
    if result.is_success:
        if result.value is None:
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
        payload = (
            resource_assembler(result.value).model_dump(mode="json")
            if resource_assembler
            else (result.value.model_dump(mode="json") if hasattr(result.value, "model_dump") else result.value)
        )
        return JSONResponse(status_code=success_status, content=payload)

    err = result.error
    status_map = {
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "CONFLICT": status.HTTP_409_CONFLICT,
        "BAD_REQUEST": status.HTTP_400_BAD_REQUEST,
        "UNAUTHORIZED": status.HTTP_401_UNAUTHORIZED,
        "FORBIDDEN": status.HTTP_403_FORBIDDEN,
        "PAYMENT_REQUIRED": status.HTTP_402_PAYMENT_REQUIRED,
    }
    http_code = status_map.get(err.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JSONResponse(
        status_code=http_code,
        content={
            "code": err.code,
            "message": err.message,
            "details": list(err.details),
        },
    )
```

---

## 4. Plantillas Canónicas para Desarrollar un Bounded Context

### 4.1 Plantilla de Caso de Uso (Command / Query Handler)

```python
# app/modules/planning/application/use_cases/plan_trip_use_case.py
from __future__ import annotations

from app.modules.planning.domain.model.commands.plan_trip_command import PlanTripCommand
from app.modules.planning.domain.model.value_objects.route_candidate import RouteCandidate
from app.modules.planning.domain.repositories.route_graph_port import RouteGraphPort
from app.modules.planning.domain.services.route_planning_service import RoutePlanningService
from app.shared.application.result.result import ApplicationError, Result


class PlanTripUseCase:
    """Caso de uso orquestador para el cálculo óptimo de rutas."""

    def __init__(
        self,
        route_graph: RouteGraphPort,
        planning_service: RoutePlanningService,
    ) -> None:
        self._graph = route_graph
        self._service = planning_service

    async def execute(self, command: PlanTripCommand) -> Result[list[RouteCandidate]]:
        # 1. Validación de existencia de nodos
        if not self._graph.contains_airport(command.origin_iata):
            return Result.failure(ApplicationError.not_found("Aeropuerto origen", command.origin_iata.value))
        if not self._graph.contains_airport(command.destination_iata):
            return Result.failure(ApplicationError.not_found("Aeropuerto destino", command.destination_iata.value))

        # 2. Ejecución algorítmica pura
        candidates = self._service.find_best_routes(
            origin=command.origin_iata,
            destination=command.destination_iata,
            strategy=command.strategy,
        )

        if not candidates:
            return Result.failure(ApplicationError.not_found("Ruta viable", f"{command.origin_iata.value}->{command.destination_iata.value}"))

        return Result.success(candidates)
```

### 4.2 Plantilla de Puerto de Repositorio (Dominio)

```python
# app/modules/planning/domain/repositories/route_graph_port.py
from __future__ import annotations

from typing import Protocol
from app.shared.domain.value_objects.geo_point import IATACode


class RouteGraphPort(Protocol):
    """Puerto de salida de consulta del grafo aéreo en memoria."""

    def contains_airport(self, code: IATACode) -> bool:
        ...

    def get_neighbors(self, code: IATACode) -> list[IATACode]:
        ...

    def get_edge_estimated_minutes(self, origin: IATACode, destination: IATACode) -> int:
        ...
```

### 4.3 Plantilla de Adaptador en Memoria (Infrastructure)

```python
# app/modules/planning/infrastructure/persistence/in_memory_route_graph_adapter.py
from __future__ import annotations

from app.modules.planning.domain.repositories.route_graph_port import RouteGraphPort
from app.shared.domain.value_objects.geo_point import IATACode


class InMemoryRouteGraphAdapter(RouteGraphPort):
    """
    Adaptador de grafo en memoria para producción y pruebas unitarias rápidas.
    """

    def __init__(self, adjacency_list: dict[str, list[str]], edge_weights: dict[tuple[str, str], int]) -> None:
        self._adj = adjacency_list
        self._weights = edge_weights

    def contains_airport(self, code: IATACode) -> bool:
        return code.value in self._adj

    def get_neighbors(self, code: IATACode) -> list[IATACode]:
        return [IATACode(dest) for dest in self._adj.get(code.value, [])]

    def get_edge_estimated_minutes(self, origin: IATACode, destination: IATACode) -> int:
        return self._weights.get((origin.value, destination.value), 999999)
```

### 4.4 Plantilla de Fachada Open Host Service (OHS)

```python
# app/modules/network/interfaces/acl/airport_catalog_facade.py
from __future__ import annotations

from typing import Protocol
from app.shared.domain.value_objects.geo_point import IATACode


class AirportCatalogFacade(Protocol):
    """
    Fachada pública del Bounded Context Flight Network para consumo de otros módulos.
    """

    def resolve_city_to_main_airport(self, city_name: str) -> IATACode | None:
        ...

    def airport_exists(self, code: IATACode) -> bool:
        ...
```

---

## 5. Pruebas Unitarias Aisladas (In-Memory Testing)

El objetivo central de la Arquitectura Hexagonal es posibilitar que cualquier caso de uso sea probado en **milisegundos sin dependencias externas**:

```python
# tests/unit/planning/test_plan_trip_use_case.py
import pytest
from app.modules.planning.application.use_cases.plan_trip_use_case import PlanTripUseCase
from app.modules.planning.domain.model.commands.plan_trip_command import PlanTripCommand
from app.modules.planning.domain.services.route_planning_service import RoutePlanningService
from app.modules.planning.infrastructure.persistence.in_memory_route_graph_adapter import InMemoryRouteGraphAdapter
from app.shared.domain.value_objects.geo_point import IATACode


@pytest.mark.asyncio
async def test_plan_trip_returns_success_when_route_exists() -> None:
    # Arrange: Grafo controlado en memoria (LIM -> CUZ)
    fake_adj = {"LIM": ["CUZ"], "CUZ": []}
    fake_weights = {("LIM", "CUZ"): 75}
    graph_port = InMemoryRouteGraphAdapter(fake_adj, fake_weights)
    service = RoutePlanningService(graph_port)
    use_case = PlanTripUseCase(graph_port, service)

    command = PlanTripCommand(
        origin_iata=IATACode("LIM"),
        destination_iata=IATACode("CUZ"),
    )

    # Act
    result = await use_case.execute(command)

    # Assert
    assert result.is_success
    assert len(result.value) == 1
    assert result.value[0].total_estimated_minutes == 75
```

---

## 6. Resumen de Integración y Servicios

| Servicio | Bounded Context | Patrón | Ubicación en el Código |
| :--- | :--- | :--- | :--- |
| **OpenFlights Datasets** | Flight Network | Repository / Loader | `app/modules/network/infrastructure/loaders/openflights_loader.py` |
| **Flight API** | Quotes | Outbound ACL Adapter | `app/modules/quotes/infrastructure/acl/flight_api_adapter.py` |
| **Mercado Pago SDK** | Credits & Payments | Outbound ACL Adapter | `app/modules/credits/infrastructure/acl/mercado_pago_adapter.py` |
| **Resend (HTTPS 443)** | IAM / Credits | Outbound ACL Adapter | `app/modules/iam/infrastructure/acl/resend_email_adapter.py` |
| **Google Identity (OIDC)** | IAM | Outbound ACL Adapter | `app/modules/iam/infrastructure/acl/google_token_verifier.py` |
| **Redis (Lua Scripts)** | Quotes / Credits / Shared | Cache & Fast-Path | `app/modules/credits/infrastructure/cache/redis_wallet_cache_adapter.py` |
| **PostgreSQL 16** | IAM / Itineraries / Quotes / Credits | SQLAlchemy Mappers | `app/modules/<context>/infrastructure/persistence/` |
