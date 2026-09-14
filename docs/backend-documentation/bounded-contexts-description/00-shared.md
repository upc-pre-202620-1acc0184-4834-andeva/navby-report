# Bounded Context Shared Kernel: Especificación Técnica de la Capa de Dominio (Domain Layer)

> **Módulo Canónico del Backend:** `app.shared.domain`  
> **Rol Arquitectónico:** Núcleo de Tipos y Abstracciones Fundacionales Transversales  
> **Pila Tecnológica:** Python 3.12+, `@dataclass(frozen=True)`, `typing` (`Generic`, `TypeVar`, `Self`), `decimal.Decimal` (`ROUND_HALF_EVEN`), `uuid.UUID` (restringido a eventos de dominio), `datetime.timezone.utc`.  
> **Documentos Relacionados:**  
> - Biblia de Producto: [../../navby-documentation.md](../../navby-documentation.md)  
> - Arquitectura de Plataforma: [../navby-platform-architecture.md](../navby-platform-architecture.md)  
> - Esquema de Base de Datos: [../navby-database-schema.md](../navby-database-schema.md)  
> - Guía Maestra de Diseño Táctico DDD: [../navby-tactical-ddd-guide.md](../navby-tactical-ddd-guide.md)  
> - Especificación Táctica Canónica: [../navby-backend-tactical-specification.md](../navby-backend-tactical-specification.md)  

---

## 1. Propósito, Límites de Responsabilidad y Lenguaje Ubicuo

### 1.1 Propósito y Límites de Aislamiento Arquitectónico

El Bounded Context **Shared Kernel** (`app.shared`) constituye el sustrato arquitectónico transversal de Navby Platform. A diferencia de los Bounded Contexts de negocio (`planning`, `network`, `quotes`, `iam`, `itineraries`, `credits`), el Shared Kernel no modela un subdominio funcional independiente ni contiene reglas de tarificación o cálculo de grafos aéreos. Su responsabilidad exclusiva es suministrar las primitivas enriquecidas de dominio, las clases base de agregados, los contratos inmutables de eventos, las mónadas funcionales de control de flujo y la taxonomía semántica de errores que son compartidos universalmente por todos los módulos del sistema.

En estricto cumplimiento de los principios de **Clean Architecture** y **Hexagonal Architecture**, la Capa de Dominio del Shared Kernel se rige por cuatro reglas inquebrantables:
1. **Aislamiento Absoluto de Frameworks (Pureza de Dominio):** Ninguna clase, función o tipo dentro de `app.shared.domain` importa librerías de persistencia (SQLAlchemy, Alembic), frameworks de transporte web (FastAPI, Starlette), librerías de serialización externa (Pydantic) o drivers de infraestructura (Redis, AsyncPG). El dominio se expresa exclusivamente en Python 3.12 estándar puro.
2. **Inmutabilidad por Defecto:** Todos los Value Objects, Domain Events e identificadores fuertemente tipados se implementan mediante `@dataclass(frozen=True)`. Cualquier intento de mutación de estado arroja `FrozenInstanceError`, forzando a los desarrolladores y agentes a respetar el reemplazo semántico de valores.
3. **Erradicación de Primitive Obsession:** Queda terminantemente prohibido representar conceptos de negocio críticos (coordenadas geográficas, códigos de aeropuerto, montos de dinero o identidades de usuario) mediante tipos escalares crudos (`float`, `str`, `int`). Todo concepto de dominio se encapsula en un Value Object autocontenido con validación de frontera en su inicialización.
4. **Control de Flujo Funcional con Monad `Result[T, E]`:** Se prohíbe el uso de excepciones (`raise Exception`) para gobernar el flujo de negocio anticipado o esperado. Los casos de uso y servicios retornan instancias de `Result.success(value)` o `Result.failure(error)`.

### 1.2 Decisiones Críticas de Arquitectura e Integración

#### 1.2.1 Decisión de Claves Primarias Enteras (`BIGINT`) vs. UUID
En estricta conformidad con la especificación física de `docs/backend-documentation/navby-database-schema.md` (línea 22), todas las tablas relacionales de negocio en PostgreSQL 16 utilizan claves primarias definidas como:
$$\text{id BIGINT GENERATED ALWAYS AS IDENTITY}$$

Esta decisión de ingeniería responde a fundamentos cuantitativos de almacenamiento y rendimiento:
- **Localidad de Caché en Índices B-Tree:** Las claves enteras monótonamente crecientes se insertan siempre en la hoja derecha del árbol B-Tree, previniendo el *page splitting* y reduciendo la fragmentación de índices a 0%.
- **Huella de Memoria Reducida:** Un entero de 64 bits (`BIGINT`) ocupa exactamente 8 bytes frente a los 16 bytes de un `UUID`, reduciendo el tamaño de las tablas y maximizando el número de filas retenidas en el *buffer pool* de PostgreSQL.
- **Envoltorios de Identidad en Dominio:** Los IDs de entidad (como `UserId`) se modelan como Value Objects inmutables sobre `int > 0`. La clase `uuid.UUID` (específicamente UUIDv4) se reserva **única y exclusivamente** para el atributo `event_id` de `DomainEvent`, donde la unicidad global no estructurada es indispensable para la deduplicación e idempotencia en memoria y mensajería Outbox.

#### 1.2.2 Decisión de Aritmética Financiera Exacta (`Decimal` y `ROUND_HALF_EVEN`)
El procesamiento de tarifas de pasajes aéreos y cotizaciones en el Value Object `Money` se ejecuta mediante `decimal.Decimal` con escala fija de dos decimales (`Decimal("0.01")`) y el modo de redondeo bancario estándar `ROUND_HALF_EVEN` (redondeo hacia el entero par más próximo). Esto previene sesgos acumulativos estadísticos y elimina los errores de precisión inherentes al estándar IEEE 754 de coma flotante (`float`).

#### 1.2.3 Decisión de Geolocalización Pura (Trigonometría Esférica de Haversine)
El Value Object `GeoPoint` implementa el cálculo ortodrómico de distancia entre dos pares de coordenadas WGS84 sobre la esfera terrestre con radio medio $R = 6371.0\text{ km}$, aplicando la formulación del Semiverseno (Haversine) de manera autónoma con el módulo `math` estándar, incorporando acotamiento numérico para evitar fallos de dominio trigonométrico causados por imprecisiones infinitesimales de coma flotante.

### 1.3 Matriz Formal del Lenguaje Ubicuo de Dominio Transversal

| Término en Inglés | Concepto en el Dominio Navby | Invariantes y Reglas de Negocio |
| :--- | :--- | :--- |
| **AggregateRoot** | Superclase abstracta base para entidades principales que definen un límite transaccional de consistencia. | Posee una identidad unívoca de tipo genérico `ID`. Acumula eventos de dominio en memoria (`_domain_events`). La igualdad y el valor hash dependen exclusivamente de su identidad técnica (`_id`). Desacoplada totalmente de ORMs. |
| **DomainEvent** | Registro inmutable de un suceso relevante que ha ocurrido en el pasado dentro de un agregado de negocio. | Inmutable (`frozen=True`). Posee un identificador `event_id` de tipo `UUID4` para deduplicación, marca temporal `occurred_on` en UTC estricto, `aggregate_id` y `event_type`. Exporta serialización determinista con `to_dict()`. |
| **GeoPoint** | Coordenada geográfica bidimensional bajo el elipsoide WGS84. | Inmutable. Latitud en $[-90.0, 90.0]$ y longitud en $[-180.0, 180.0]$. Provee cálculo de distancia en kilómetros mediante la fórmula trigonométrica esférica de Haversine ($R = 6371.0\text{ km}$). |
| **Money** | Importe monetario exacto asociado a una unidad de divisa soberana. | Inmutable. Cuantizado a 2 decimales mediante `ROUND_HALF_EVEN`. Importe no negativo ($\ge 0.00$). Operaciones de suma y resta restringen a divisas homogéneas (`CurrencyMismatchError`). Restas con saldo negativo lanzan `NegativeAmountError`. |
| **Currency** | Catálogo enumerado de divisas transaccionales e informativas reconocidas. | Subtipo de `StrEnum` que restringe los valores a `USD` (dólar estadounidense), `PEN` (sol peruano) y `EUR` (euro). |
| **IATACode** | Código de designación de 3 caracteres asignado por la Asociación Internacional de Transporte Aéreo a aeropuertos comerciales. | Inmutable. Exactamente 3 caracteres alfabéticos ASCII mayúsculos conformes al patrón regex `^[A-Z]{3}$`. |
| **EmailAddress** | Dirección de correo electrónico estandarizada utilizada como login principal de usuario. | Inmutable. Normalizada a minúsculas, longitud máxima de 150 caracteres y sujeta al patrón RFC 5322. |
| **Result** | Mónada funcional contenedora que expresa el resultado exitoso (`Success`) o fallido (`Failure`) de una operación en la Capa de Aplicación. | Inmutable (`app.shared.application.result`). Encapsula un valor de tipo `T` o un error tipado de tipo `E` (típicamente `ApplicationError`). Soporta encadenamiento seguro con `map()`, composición monádica con `bind()` y manejo exhaustivo con `match()`. |
| **ApplicationError** | Error semántico tipado de la Capa de Aplicación para modelar fallos anticipados en casos de uso. | Inmutable (`app.shared.application.result`). Encapsula código de error (`code`), mensaje descriptivo (`message`) y metadatos contextuales (`details`). Provee métodos de factoría semánticos (`not_found`, `conflict`, `bad_request`, etc.). |
| **DomainException** | Clase base de excepciones e infracciones de invariantes de la Capa de Dominio. | Inmutable (`app.shared.domain.exceptions`). Extiende `Exception`. Encapsula código de máquina (`code`), mensaje explicativo (`message`) y metadatos (`details`). Es lanzada exclusivamente ante violaciones de reglas de negocio en entidades y Value Objects. |

---

## 2. Domain Layer: Modelo de Agregados y Eventos de Dominio

### 2.1 `AbstractDomainAggregateRoot[ID]` y `DomainEvent`

```python
# app/shared/domain/model/aggregate_root.py
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
import uuid

ID = TypeVar("ID")


@dataclass(frozen=True)
class DomainEvent:
    """
    Evento de dominio base inmutable.
    Representa un suceso consumado en el pasado dentro de un agregado de negocio.
    Utiliza UUIDv4 exclusivamente para deduplicación e idempotencia de mensajería.
    """
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_on: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    aggregate_id: str = ""
    event_type: str = ""

    def __post_init__(self) -> None:
        if not self.event_type:
            object.__setattr__(self, "event_type", self.__class__.__name__)

    def to_dict(self) -> dict[str, Any]:
        """Serializa el evento a un diccionario inmutable para Outbox y mensajería."""
        return {
            "event_id": str(self.event_id),
            "occurred_on": self.occurred_on.isoformat(),
            "aggregate_id": self.aggregate_id,
            "event_type": self.event_type,
        }


class AbstractDomainAggregateRoot(ABC, Generic[ID]):
    """
    Raíz de agregado abstracta de dominio puro.
    Totalmente desacoplada de frameworks de persistencia (SQLAlchemy ORM) o transporte HTTP (FastAPI).
    Gestiona la acumulación en memoria de eventos de dominio generados durante la ejecución
    de invariantes de negocio y define la identidad única del agregado.
    """

    def __init__(self, id: ID) -> None:
        self._id: ID = id
        self._domain_events: list[DomainEvent] = []

    @property
    def id(self) -> ID:
        """Retorna el identificador unívoco de dominio del agregado."""
        return self._id

    def register_domain_event(self, event: DomainEvent) -> None:
        """Encola un evento de dominio consumado en la colección interna del agregado."""
        self._domain_events.append(event)

    def domain_events(self) -> tuple[DomainEvent, ...]:
        """Retorna una instantánea inmutable (tupla) de los eventos de dominio acumulados."""
        return tuple(self._domain_events)

    def clear_domain_events(self) -> None:
        """Limpia la colección interna de eventos acumulados tras su despacho."""
        self._domain_events.clear()

    def pull_domain_events(self) -> tuple[DomainEvent, ...]:
        """Extrae de manera atómica todos los eventos acumulados y vacía la colección interna."""
        events = tuple(self._domain_events)
        self._domain_events.clear()
        return events

    def __eq__(self, other: Any) -> bool:
        """Dos agregados son idénticos si pertenecen a la misma clase y comparten el mismo ID."""
        if not isinstance(other, self.__class__):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """El hash del agregado deriva exclusivamente de su identidad técnica de dominio."""
        return hash((self.__class__, self._id))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self._id!r})>"
```

---

## 3. Domain Layer: Taxonomía de Value Objects Transversales

### 3.1 `GeoPoint` (Geolocalización WGS84 y Haversine Puro)

La distancia ortodrómica o de gran círculo entre dos coordenadas sobre la superficie de una esfera se calcula aplicando la ley trigonométrica del Semiverseno (Haversine):
$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \varphi}{2}\right) + \cos(\varphi_1)\cos(\varphi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
donde $\varphi_1, \varphi_2$ corresponden a las latitudes en radianes, $\Delta \varphi = \varphi_2 - \varphi_1$, $\Delta \lambda = \lambda_2 - \lambda_1$ representan las diferencias angulares, y $R = 6371.0\text{ km}$ define el radio medio de la Tierra.

```python
# app/shared/domain/value_objects/geo_point.py
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from app.shared.domain.exceptions.domain_exceptions import InvalidCoordinatesException


@dataclass(frozen=True)
class GeoPoint:
    """
    Coordenada geográfica en estándar geodésico WGS84.
    Encapsula latitud y longitud y proporciona el cálculo de distancia ortodrómica
    mediante la fórmula pura de Haversine (trigonometría esférica con radio medio R = 6371.0 km).
    """
    latitude: float
    longitude: float

    EARTH_RADIUS_KM: float = 6371.0

    def __post_init__(self) -> None:
        if not isinstance(self.latitude, (int, float)) or isinstance(self.latitude, bool):
            raise InvalidCoordinatesException(
                code="INVALID_COORDINATES",
                message=f"La latitud debe ser un número decimal; se recibió: {type(self.latitude).__name__}.",
                details={"latitude": self.latitude, "longitude": self.longitude}
            )
        if not isinstance(self.longitude, (int, float)) or isinstance(self.longitude, bool):
            raise InvalidCoordinatesException(
                code="INVALID_COORDINATES",
                message=f"La longitud debe ser un número decimal; se recibió: {type(self.longitude).__name__}.",
                details={"latitude": self.latitude, "longitude": self.longitude}
            )
        lat_float = float(self.latitude)
        lon_float = float(self.longitude)
        if not (-90.0 <= lat_float <= 90.0):
            raise InvalidCoordinatesException(
                code="INVALID_COORDINATES",
                message=f"Latitud fuera del rango geodésico válido [-90.0, 90.0]: {self.latitude}.",
                details={"latitude": self.latitude, "longitude": self.longitude}
            )
        if not (-180.0 <= lon_float <= 180.0):
            raise InvalidCoordinatesException(
                code="INVALID_COORDINATES",
                message=f"Longitud fuera del rango geodésico válido [-180.0, 180.0]: {self.longitude}.",
                details={"latitude": self.latitude, "longitude": self.longitude}
            )
        object.__setattr__(self, "latitude", lat_float)
        object.__setattr__(self, "longitude", lon_float)

    def haversine_distance_km_to(self, other: GeoPoint) -> float:
        """
        Calcula la distancia geodésica del gran círculo en kilómetros hacia otro GeoPoint.
        Aplica acotamiento numérico a [0.0, 1.0] para evitar math domain error por imprecisión flotante.
        """
        if not isinstance(other, GeoPoint):
            raise TypeError(f"El destino debe ser una instancia de GeoPoint; se recibió: {type(other).__name__}.")

        phi1 = math.radians(self.latitude)
        phi2 = math.radians(other.latitude)
        delta_phi = math.radians(other.latitude - self.latitude)
        delta_lambda = math.radians(other.longitude - self.longitude)

        sin_half_dphi = math.sin(delta_phi / 2.0)
        sin_half_dlambda = math.sin(delta_lambda / 2.0)

        a = (sin_half_dphi ** 2) + math.cos(phi1) * math.cos(phi2) * (sin_half_dlambda ** 2)
        clamped_a = min(1.0, max(0.0, a))
        c = 2.0 * math.atan2(math.sqrt(clamped_a), math.sqrt(1.0 - clamped_a))

        return self.EARTH_RADIUS_KM * c

    def is_same_location(self, other: GeoPoint, tolerance_km: float = 0.01) -> bool:
        """Determina si dos coordenadas coinciden dentro de un radio de tolerancia (default 10 metros)."""
        return self.haversine_distance_km_to(other) <= tolerance_km

    def to_tuple(self) -> tuple[float, float]:
        """Retorna la tupla escalar (latitud, longitud)."""
        return (self.latitude, self.longitude)

    def __str__(self) -> str:
        return f"({self.latitude:.6f}, {self.longitude:.6f})"
```

### 3.2 `Money` y `Currency` (Precisión Financiera Bancaria)

```python
# app/shared/domain/value_objects/money.py
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN
from enum import StrEnum
from typing import Any

from app.shared.domain.exceptions.domain_exceptions import CurrencyMismatchException, NegativeAmountException


class Currency(StrEnum):
    """Monedas transaccionales soportadas por Navby."""
    USD = "USD"
    PEN = "PEN"
    EUR = "EUR"


@dataclass(frozen=True)
class Money:
    """
    Objeto de Valor inmutable con precisión bancaria y aritmética exacta.
    Utiliza decimal.Decimal con cuantización a dos posiciones decimales ('0.01')
    y redondeo bancario ROUND_HALF_EVEN para eliminar sesgos aritméticos.
    """
    amount: Decimal
    currency: Currency = Currency.USD

    _CENT: Decimal = Decimal("0.01")

    def __post_init__(self) -> None:
        if isinstance(self.amount, (int, float, str)):
            quantized = Decimal(str(self.amount)).quantize(self._CENT, rounding=ROUND_HALF_EVEN)
            object.__setattr__(self, "amount", quantized)
        elif isinstance(self.amount, Decimal):
            quantized = self.amount.quantize(self._CENT, rounding=ROUND_HALF_EVEN)
            object.__setattr__(self, "amount", quantized)
        else:
            raise TypeError(f"Monto debe ser de tipo Decimal, int, float o str; se recibió: {type(self.amount).__name__}.")

        if not isinstance(self.currency, Currency):
            if isinstance(self.currency, str):
                try:
                    object.__setattr__(self, "currency", Currency(self.currency.upper()))
                except ValueError:
                    raise CurrencyMismatchException(
                        code="CURRENCY_MISMATCH",
                        message=f"Moneda no soportada: '{self.currency}'. Monedas válidas: {[c.value for c in Currency]}.",
                        details={"currency": self.currency}
                    )
            else:
                raise TypeError(f"Divisa debe ser una instancia de Currency; se recibió: {type(self.currency).__name__}.")

        if self.amount < Decimal("0.00"):
            raise NegativeAmountException(
                code="NEGATIVE_AMOUNT",
                message=f"El importe monetario no puede ser estrictamente negativo; se recibió: {self.amount}.",
                details={"amount": str(self.amount), "currency": self.currency.value}
            )

    @classmethod
    def zero(cls, currency: Currency = Currency.USD) -> Money:
        """Factoría para crear un importe de valor cero."""
        return cls(amount=Decimal("0.00"), currency=currency)

    @classmethod
    def from_float(cls, amount: float, currency: Currency = Currency.USD) -> Money:
        """Factoría para convertir valores de punto flotante de forma segura mediante string."""
        return cls(amount=Decimal(str(amount)), currency=currency)

    @classmethod
    def from_cents(cls, cents: int, currency: Currency = Currency.USD) -> Money:
        """Factoría a partir de centavos enteros (ej. 1050 centavos -> 10.50)."""
        return cls(amount=(Decimal(cents) / Decimal("100")).quantize(cls._CENT, rounding=ROUND_HALF_EVEN), currency=currency)

    def _assert_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchException(
                code="CURRENCY_MISMATCH",
                message=f"Conflicto de monedas: no se pueden operar {self.currency.value} con {other.currency.value}.",
                details={"currency_a": self.currency.value, "currency_b": other.currency.value}
            )

    def add(self, other: Money) -> Money:
        """Suma aritmética de dos valores monetarios de la misma divisa."""
        if not isinstance(other, Money):
            raise TypeError(f"El operando debe ser una instancia de Money; se recibió: {type(other).__name__}.")
        self._assert_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: Money) -> Money:
        """Resta aritmética de dos valores monetarios de la misma divisa."""
        if not isinstance(other, Money):
            raise TypeError(f"El operando debe ser una instancia de Money; se recibió: {type(other).__name__}.")
        self._assert_same_currency(other)
        new_amount = self.amount - other.amount
        if new_amount < Decimal("0.00"):
            raise NegativeAmountException(
                code="NEGATIVE_AMOUNT",
                message=f"La resta resulta en un saldo negativo no permitido: {new_amount} {self.currency.value}.",
                details={"current_amount": str(self.amount), "deduct_amount": str(other.amount)}
            )
        return Money(amount=new_amount, currency=self.currency)

    def multiply(self, factor: Decimal | int | float) -> Money:
        """Multiplica el importe por un factor escalar numérico no negativo."""
        if isinstance(factor, (int, float, str)):
            dec_factor = Decimal(str(factor))
        elif isinstance(factor, Decimal):
            dec_factor = factor
        else:
            raise TypeError(f"El factor debe ser numérico; se recibió: {type(factor).__name__}.")

        if dec_factor < Decimal("0.00"):
            raise NegativeAmountException(
                code="NEGATIVE_AMOUNT",
                message=f"El factor multiplicativo no puede ser negativo: {dec_factor}.",
                details={"factor": str(dec_factor)}
            )
        return Money(amount=self.amount * dec_factor, currency=self.currency)

    def divide(self, divisor: Decimal | int) -> Money:
        """Divide el importe por un divisor escalar estrictamente positivo."""
        if isinstance(divisor, (int, str)):
            dec_divisor = Decimal(str(divisor))
        elif isinstance(divisor, Decimal):
            dec_divisor = divisor
        else:
            raise TypeError(f"El divisor debe ser de tipo int o Decimal; se recibió: {type(divisor).__name__}.")

        if dec_divisor <= Decimal("0.00"):
            raise ValueError(f"El divisor debe ser estrictamente positivo (> 0); se recibió: {dec_divisor}.")
        return Money(amount=self.amount / dec_divisor, currency=self.currency)

    def is_zero(self) -> bool:
        """Determina si el importe es exactamente cero."""
        return self.amount == Decimal("0.00")

    def is_positive(self) -> bool:
        """Determina si el importe es estrictamente superior a cero."""
        return self.amount > Decimal("0.00")

    def is_greater_than(self, other: Money) -> bool:
        """Compara si este importe es mayor que otro de la misma divisa."""
        self._assert_same_currency(other)
        return self.amount > other.amount

    def is_less_than(self, other: Money) -> bool:
        """Compara si este importe es menor que otro de la misma divisa."""
        self._assert_same_currency(other)
        return self.amount < other.amount

    def __add__(self, other: Money) -> Money:
        return self.add(other)

    def __sub__(self, other: Money) -> Money:
        return self.subtract(other)

    def __mul__(self, factor: Decimal | int | float) -> Money:
        return self.multiply(factor)

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency.value}"
```

### 3.3 `IATACode`, `EmailAddress` y `UserId`

```python
# app/shared/domain/value_objects/identifiers.py
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from app.shared.domain.exceptions.domain_exceptions import (
    InvalidEmailAddressException,
    InvalidIATACodeException,
    InvalidUserIdException,
)


@dataclass(frozen=True)
class IATACode:
    """
    Código de aeropuerto estándar IATA (International Air Transport Association).
    Representa una secuencia inmutable de exactamente 3 caracteres alfabéticos en mayúsculas.
    """
    value: str

    _REGEX = re.compile(r"^[A-Z]{3}$")

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidIATACodeException(
                code="INVALID_IATA_CODE",
                message=f"El código IATA debe ser una cadena de texto; se recibió: {type(self.value).__name__}.",
                details={"provided_value": self.value}
            )
        sanitized = self.value.strip().upper()
        if not self._REGEX.match(sanitized):
            raise InvalidIATACodeException(
                code="INVALID_IATA_CODE",
                message=f"Código IATA inválido: '{self.value}'. Debe contener exactamente 3 letras del alfabeto inglés.",
                details={"provided_value": self.value, "normalized": sanitized}
            )
        object.__setattr__(self, "value", sanitized)

    @classmethod
    def from_string(cls, code: str) -> IATACode:
        """Factoría estática que normaliza y construye un IATACode."""
        return cls(value=code)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class EmailAddress:
    """
    Dirección de correo electrónico canónica y normalizada (RFC 5322).
    Encapsula el identificador principal de inicio de sesión de usuario en Navby.
    """
    value: str

    _REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidEmailAddressException(
                code="INVALID_EMAIL_ADDRESS",
                message=f"El correo electrónico debe ser una cadena de texto; se recibió: {type(self.value).__name__}.",
                details={"provided_value": self.value}
            )
        sanitized = self.value.strip().lower()
        if len(sanitized) > 150 or not self._REGEX.match(sanitized):
            raise InvalidEmailAddressException(
                code="INVALID_EMAIL_ADDRESS",
                message=f"Dirección de correo electrónico inválida: '{self.value}'. Formato RFC 5322 requerido (máx 150 caracteres).",
                details={"provided_value": self.value, "normalized": sanitized}
            )
        object.__setattr__(self, "value", sanitized)

    @classmethod
    def from_string(cls, email: str) -> EmailAddress:
        """Factoría estática que normaliza a minúsculas y valida."""
        return cls(value=email)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class UserId:
    """
    Identificador fuertemente tipado de usuario.
    En estricta conformidad con el esquema físico de base de datos de PostgreSQL
    (BIGINT GENERATED ALWAYS AS IDENTITY), este Value Object encapsula un número
    entero positivo estricto (> 0), garantizando máxima localidad en árboles B-Tree
    y eliminando la fragmentación de índices.
    """
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or isinstance(self.value, bool):
            raise InvalidUserIdException(
                code="INVALID_USER_ID",
                message=f"El identificador de usuario debe ser un entero válido; se recibió: {type(self.value).__name__}.",
                details={"provided_value": self.value}
            )
        if self.value <= 0:
            raise InvalidUserIdException(
                code="INVALID_USER_ID",
                message=f"El identificador de usuario debe ser un entero estrictamente positivo (> 0); se recibió: {self.value}.",
                details={"provided_value": self.value}
            )

    @classmethod
    def from_int(cls, val: int) -> UserId:
        """Factoría estática canónica a partir de un entero primitivo."""
        return cls(value=val)

    def to_int(self) -> int:
        """Retorna el valor escalar entero primitivo."""
        return self.value

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)
```

---

## 4. Control de Flujo Funcional (Application Layer) vs. Invariantes y Excepciones (Domain Layer)

### 4.1 Principio de Segregación Arquitectónica: Flujo Funcional vs. Invariantes de Dominio

En estricta conformidad con los principios de **Clean Architecture** y las directrices tácticas de `navby-tactical-ddd-guide.md` (§3.3), Navby Platform establece una delimitación arquitectónica rigurosa entre el control de flujo en la Capa de Aplicación y la preservación de invariantes en la Capa de Dominio:

1. **Capa de Aplicación (`app.shared.application.result`): Mónada `Result[T, E]` y `ApplicationError`**
   - La mónada `Result[T, E]` y los errores semánticos tipados `ApplicationError` pertenecen **estrictamente a la Capa de Aplicación** (`app/shared/application/result/result.py`).
   - Gobiernan el flujo funcional (*Railway-Oriented Programming*) para la orquestación de casos de uso habituales o anticipados (entidades no encontradas, conflictos de concurrencia, credenciales inválidas, autorizaciones denegadas o validaciones de formato de entrada).
   - Erradican el uso de excepciones no controladas (`raise Exception`) para ramificaciones operativas esperadas, retornando de manera determinista instancias de `Result.success(value)` o `Result.failure(error)`.

2. **Capa de Dominio (`app.shared.domain.exceptions`): Jerarquía de `DomainException`**
   - En la Capa de Dominio, las entidades, raíces de agregados y objetos de valor protegen sus invariantes estructurales y fronteras matemáticas levantando de forma inmediata excepciones tipadas derivadas de `DomainException` (`InvalidCoordinatesException`, `NegativeAmountException`, `CurrencyMismatchException`, etc.).
   - Un agregado o Value Object **nunca** retorna un `Result` al construirse o validar sus invariantes fundamentales: si las coordenadas geográficas son ilegales o el importe monetario es negativo, el objeto simplemente **no puede existir**, por lo que lanza su correspondiente `DomainException`.
   - Cuando estas excepciones emergen durante la ejecución de un caso de uso, los manejadores de aplicación (`CommandHandler`, `QueryHandler`) o los interceptores perimetrales (`GlobalExceptionHandler`) las capturan y traducen a respuestas de error estructuradas conforme al estándar RFC 7807.

---

### 4.2 Contenedor Monádico `Result[T, E]` y `ApplicationError` en la Capa de Aplicación

```python
# app/shared/application/result/result.py
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")


class ResultStatus(StrEnum):
    """Estado categórico de la mónada funcional Result."""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass(frozen=True)
class ApplicationError:
    """
    Error semántico inmutable tipado de la Capa de Aplicación.
    Modela condiciones de fallo anticipadas durante la orquestación de casos de uso.
    """
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def not_found(cls, resource: str, identifier: Any) -> ApplicationError:
        """Construye un error semántico de recurso no encontrado."""
        return cls(
            code="NOT_FOUND",
            message=f"{resource} con identificador '{identifier}' no fue encontrado.",
            details={"resource": resource, "identifier": str(identifier)},
        )

    @classmethod
    def conflict(cls, message: str, details: dict[str, Any] | None = None) -> ApplicationError:
        """Construye un error de conflicto de estado o colisión de concurrencia."""
        return cls(code="CONFLICT", message=message, details=details or {})

    @classmethod
    def bad_request(cls, message: str, details: dict[str, Any] | None = None) -> ApplicationError:
        """Construye un error de parámetros o precondiciones de caso de uso inválidas."""
        return cls(code="BAD_REQUEST", message=message, details=details or {})

    @classmethod
    def unauthorized(cls, message: str = "Credenciales inválidas o token expirado.") -> ApplicationError:
        """Construye un error de autenticación perimetral requerida o fallida."""
        return cls(code="UNAUTHORIZED", message=message)

    @classmethod
    def forbidden(cls, message: str = "Permisos insuficientes para ejecutar esta operación.") -> ApplicationError:
        """Construye un error de autorización o acceso denegado a nivel de aplicación."""
        return cls(code="FORBIDDEN", message=message)

    @classmethod
    def unprocessable_entity(cls, message: str, details: dict[str, Any] | None = None) -> ApplicationError:
        """Construye un error semántico de entidad no procesable por reglas de aplicación."""
        return cls(code="UNPROCESSABLE_ENTITY", message=message, details=details or {})

    @classmethod
    def internal_error(cls, message: str = "Error interno no controlado en el caso de uso.") -> ApplicationError:
        """Construye un error de aplicación para condiciones no recuperables."""
        return cls(code="INTERNAL_SERVER_ERROR", message=message)


@dataclass(frozen=True)
class Result(Generic[T, E]):
    """
    Mónada funcional Result[T, E] para modelar operaciones que culminan en éxito (T)
    o en fallo semántico tipado (E, típicamente ApplicationError).
    Erradica el uso de excepciones descontroladas para el flujo de negocio habitual.
    """
    _value: T | None = None
    _error: E | None = None
    _is_success: bool = True

    @classmethod
    def success(cls, value: T) -> Result[T, Any]:
        """Construye un resultado exitoso que encapsula un valor de tipo T."""
        return cls(_value=value, _error=None, _is_success=True)

    @classmethod
    def failure(cls, error: E) -> Result[Any, E]:
        """Construye un resultado fallido que encapsula un error tipado de tipo E."""
        return cls(_value=None, _error=error, _is_success=False)

    @property
    def is_success(self) -> bool:
        """Retorna True si la operación concluyó exitosamente."""
        return self._is_success

    @property
    def is_failure(self) -> bool:
        """Retorna True si la operación resultó en un error semántico."""
        return not self._is_success

    @property
    def value(self) -> T:
        """
        Retorna el valor exitoso.
        Lanza ValueError si se intenta acceder al valor de un resultado fallido.
        """
        if not self._is_success:
            raise ValueError(f"No se puede acceder al valor de un Result fallido: {self._error}")
        return self._value  # type: ignore[return-value]

    @property
    def error(self) -> E:
        """
        Retorna el error semántico del fallo.
        Lanza ValueError si se intenta acceder al error de un resultado exitoso.
        """
        if self._is_success:
            raise ValueError("No se puede acceder al error de un Result exitoso.")
        return self._error  # type: ignore[return-value]

    def value_or(self, default: T) -> T:
        """Retorna el valor exitoso o el valor predeterminado si fue fallo."""
        if self._is_success:
            return self._value  # type: ignore[return-value]
        return default

    def map(self, fn: Callable[[T], U]) -> Result[U, E]:
        """
        Aplica una función transformadora pura sobre el valor si es exitoso.
        Propaga el error intacto si es fallo.
        """
        if self._is_success:
            return Result.success(fn(self._value))  # type: ignore[arg-type]
        return Result.failure(self._error)  # type: ignore[arg-type]

    def bind(self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """
        Encadenamiento monádico (FlatMap): evalúa una función que retorna un nuevo Result[U, E].
        Permite secuenciar casos de uso y validaciones sin anidamiento condicional.
        """
        if self._is_success:
            return fn(self._value)  # type: ignore[arg-type]
        return Result.failure(self._error)  # type: ignore[arg-type]

    def match(self, on_success: Callable[[T], Any], on_failure: Callable[[E], Any]) -> Any:
        """Evalúa exhaustivamente una bifurcación de éxito o fallo."""
        if self._is_success:
            return on_success(self._value)  # type: ignore[arg-type]
        return on_failure(self._error)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        if self._is_success:
            return f"Result.success({self._value!r})"
        return f"Result.failure({self._error!r})"
```

---

### 4.3 Jerarquía de Excepciones de Dominio `DomainException` (Domain Layer)

```python
# app/shared/domain/exceptions/domain_exceptions.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DomainException(Exception):
    """
    Clase base inmutable para todas las excepciones y transgresiones de invariantes de negocio.
    Extiende Exception para permitir trazabilidad pero encapsula códigos legibles por máquina.
    """
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        object.__setattr__(self, "code", code)
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "details", details if details is not None else {})

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


@dataclass(frozen=True)
class InvalidCoordinatesException(DomainException):
    """Lanzada cuando una latitud o longitud viola el rango geodésico WGS84."""

    def __init__(
        self,
        code: str = "INVALID_COORDINATES",
        message: str = "Coordenadas geográficas fuera del rango válido [-90, 90] o [-180, 180].",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details)


@dataclass(frozen=True)
class NegativeAmountException(DomainException):
    """Lanzada cuando un importe monetario o saldo resultante es estrictamente negativo."""

    def __init__(
        self,
        code: str = "NEGATIVE_AMOUNT",
        message: str = "El importe monetario no puede ser estrictamente negativo.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details)


@dataclass(frozen=True)
class InvalidIATACodeException(DomainException):
    """Lanzada cuando una cadena no cumple con el estándar IATA de 3 letras alfabéticas."""

    def __init__(
        self,
        code: str = "INVALID_IATA_CODE",
        message: str = "El código de aeropuerto no cumple con el formato IATA de 3 letras mayúsculas.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details)


@dataclass(frozen=True)
class CurrencyMismatchException(DomainException):
    """Lanzada al intentar operar aritméticamente montos con divisas heterogéneas."""

    def __init__(
        self,
        code: str = "CURRENCY_MISMATCH",
        message: str = "No se pueden realizar operaciones aritméticas entre importes de distintas divisas.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details)


@dataclass(frozen=True)
class EntityNotFoundException(DomainException):
    """Lanzada cuando una entidad o agregado buscado no existe en el contexto."""

    def __init__(
        self,
        code: str = "ENTITY_NOT_FOUND",
        message: str = "La entidad solicitada no fue encontrada en el almacén de datos.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details)


@dataclass(frozen=True)
class InvalidEmailAddressException(DomainException):
    """Lanzada cuando un correo electrónico no satisface el estándar RFC 5322."""

    def __init__(
        self,
        code: str = "INVALID_EMAIL_ADDRESS",
        message: str = "El formato de correo electrónico no cumple con la especificación RFC 5322.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details)


@dataclass(frozen=True)
class InvalidUserIdException(DomainException):
    """Lanzada cuando un identificador de usuario no cumple con el formato BIGINT positivo."""

    def __init__(
        self,
        code: str = "INVALID_USER_ID",
        message: str = "El identificador de usuario debe ser un número entero estrictamente positivo (> 0).",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details)


# Alias de retrocompatibilidad arquitectónica
DomainError = DomainException
InvalidCoordinatesError = InvalidCoordinatesException
NegativeAmountError = NegativeAmountException
InvalidIATACodeError = InvalidIATACodeException
CurrencyMismatchError = CurrencyMismatchException
EntityNotFoundError = EntityNotFoundException
InvalidEmailAddressError = InvalidEmailAddressException
InvalidUserIdError = InvalidUserIdException
```

---

## 5. Diccionario Completo de Elementos Tácticos (Tabla IAM Gemela)

A continuación se presenta la matriz estructural exhaustiva con el estándar de 5 columnas del reporte de arquitectura:

| Clase o Estructura | Elemento | Firma o Tipo | Ámbito | Descripción, Relaciones y Reglas de Negocio |
| :--- | :---: | :--- | :---: | :--- |
| AbstractDomainAggregateRoot | Atributos protegidos | `_id: ID`<br>`_domain_events: list[DomainEvent]` | Protegido | Raíz de agregado abstracta genérica.<br>Encapsula la identidad unívoca y la cola en memoria de eventos consumados.<br>Desacoplada de SQLAlchemy ORM. |
| AbstractDomainAggregateRoot | Propiedad id | `id -> ID` | Público | Retorna el identificador unívoco de dominio del agregado. |
| AbstractDomainAggregateRoot | Métodos de gestión de eventos | `register_domain_event(event: DomainEvent) -> None`<br>`domain_events() -> tuple[DomainEvent, ...]`<br>`clear_domain_events() -> None`<br>`pull_domain_events() -> tuple[DomainEvent, ...]` | Público | Invariantes:<br>- register_domain_event encola eventos durante la ejecución de reglas de negocio.<br>- pull_domain_events extrae de forma atómica y vacía la cola en una única operación para el repositorio de infraestructura. |
| AbstractDomainAggregateRoot | Métodos de identidad y hash | `__eq__(other: Any) -> bool`<br>`__hash__() -> int`<br>`__repr__() -> str` | Público | Dos agregados son idénticos si pertenecen exactamente a la misma clase y comparten el mismo valor de identidad _id. |
| DomainEvent | Atributos inmutables | `event_id: UUID`<br>`occurred_on: datetime`<br>`aggregate_id: str`<br>`event_type: str` | Público | Evento de dominio base inmutable.<br>Invariantes:<br>- event_id autogenerado con uuid.uuid4().<br>- occurred_on sellado en tiempo real con datetime.now(timezone.utc).<br>- event_type toma por defecto el nombre de la clase hija. |
| DomainEvent | Método de serialización | `to_dict() -> dict[str, Any]` | Público | Serializa el evento a un diccionario primitivo inmutable para su integración en tablas Outbox o mensajería de infraestructura. |
| GeoPoint | Atributos inmutables | `latitude: float`<br>`longitude: float`<br>`EARTH_RADIUS_KM: float = 6371.0` | Público | Coordenada geográfica WGS84 inmutable.<br>Invariantes validadas en __post_init__:<br>- latitud en [-90.0, 90.0] y longitud en [-180.0, 180.0].<br>- Rechaza valores booleanos o tipos no numéricos lanzando InvalidCoordinatesException. |
| GeoPoint | Métodos geodésicos | `haversine_distance_km_to(other: GeoPoint) -> float`<br>`is_same_location(other: GeoPoint, tolerance_km: float) -> bool`<br>`to_tuple() -> tuple[float, float]` | Público | Invariantes:<br>- Computa la distancia ortodrómica esférica mediante la fórmula pura de Haversine con R = 6371.0 km.<br>- Incorpora acotamiento numérico min(1.0, max(0.0, a)) para eliminar excepciones de dominio matemático. |
| Currency | Valores enumerados | `USD = "USD"`<br>`PEN = "PEN"`<br>`EUR = "EUR"` | Público | Subtipo de StrEnum que define las tres monedas oficiales admitidas en Navby para cotizaciones y pagos. |
| Money | Atributos inmutables | `amount: Decimal`<br>`currency: Currency` | Público | Objeto de Valor inmutable para cuantificación financiera.<br>Invariantes en __post_init__:<br>- Cuantizado forzoso a 2 decimales (Decimal("0.01")) con redondeo bancario ROUND_HALF_EVEN.<br>- Valida que amount ≥ Decimal("0.00") lanzando NegativeAmountException. |
| Money | Métodos factoría | `zero(currency: Currency) -> Money`<br>`from_float(amount: float, currency: Currency) -> Money`<br>`from_cents(cents: int, currency: Currency) -> Money` | Público | Factorías estáticas canónicas.<br>- from_float convierte de manera segura vía str para mitigar imprecisiones binarias.<br>- from_cents convierte enteros centesimales a escala decimal. |
| Money | Métodos aritméticos | `add(other: Money) -> Money`<br>`subtract(other: Money) -> Money`<br>`multiply(factor: Decimal \| int \| float) -> Money`<br>`divide(divisor: Decimal \| int) -> Money` | Público | Invariantes:<br>- add y subtract validan coincidencia estricta de currency mediante _assert_same_currency (lanza CurrencyMismatchException).<br>- subtract valida que el saldo remanente no sea < 0 (lanza NegativeAmountException).<br>- divide exige divisor estrictamente positivo. |
| Money | Métodos de comparación | `is_zero() -> bool`<br>`is_positive() -> bool`<br>`is_greater_than(other: Money) -> bool`<br>`is_less_than(other: Money) -> bool` | Público | Comparadores semánticos booleanos.<br>Las comparaciones relativas exigen coincidencia de divisa. |
| IATACode | Atributo canónico y factoría | `value: str`<br>`from_string(code: str) -> IATACode` | Público | Value Object inmutable para código de aeropuerto IATA.<br>Invariantes en __post_init__:<br>- Normaliza eliminando espacios en blanco y forzando mayúsculas.<br>- Valida coincidencia estricta con el patrón ^[A-Z]{3}$.<br>- Transgresiones arrojan InvalidIATACodeException. |
| EmailAddress | Atributo canónico y factoría | `value: str`<br>`from_string(email: str) -> EmailAddress` | Público | Value Object inmutable para correo electrónico.<br>Invariantes en __post_init__:<br>- Normaliza a minúsculas.<br>- Longitud ≤ 150 caracteres.<br>- Validación sintáctica conforme a RFC 5322.<br>- Fallos lanzan InvalidEmailAddressException. |
| UserId | Atributo de identidad y factoría | `value: int`<br>`from_int(val: int) -> UserId`<br>`to_int() -> int` | Público | Identificador fuertemente tipado de usuario alineado con BIGINT GENERATED ALWAYS AS IDENTITY de PostgreSQL.<br>Invariantes en __post_init__:<br>- Rechaza tipos no enteros, booleanos y valores ≤ 0 arrojando InvalidUserIdException. |
| Result[T, E] | Atributos privados | `_value: T \| None`<br>`_error: E \| None`<br>`_is_success: bool` | Privado | Mónada funcional genérica para orquestación de operaciones de negocio sin lanzamiento descontrolado de excepciones. |
| Result[T, E] | Factorías estáticas | `success(value: T) -> Result[T, Any]`<br>`failure(error: E) -> Result[Any, E]` | Público | Constructores canónicos de mónadas de éxito o fracaso semántico. |
| Result[T, E] | Propiedades de acceso | `is_success -> bool`<br>`is_failure -> bool`<br>`value -> T`<br>`error -> E`<br>`value_or(default: T) -> T` | Público | Invariantes:<br>- Acceder a .value en un estado de fallo o a .error en un estado de éxito arroja ValueError.<br>- value_or provee un valor fallback seguro. |
| Result[T, E] | Operaciones monádicas | `map(fn: Callable[[T], U]) -> Result[U, E]`<br>`bind(fn: Callable[[T], Result[U, E]]) -> Result[U, E]` | Público | map aplica transformación sobre el valor encapsulado en éxito.<br>bind efectúa composición monádica secuencial propagando el fallo intacto. |
| DomainException | Jerarquía de excepciones | `code: str`<br>`message: str`<br>`details: dict[str, Any]` | Público | Superclase inmutable de excepciones de dominio con códigos legibles por máquina.<br>Heredan: InvalidCoordinatesException, NegativeAmountException, InvalidIATACodeException, CurrencyMismatchException, EntityNotFoundException, InvalidEmailAddressException, InvalidUserIdException. |

---

### 6. Bounded Context Software Architecture Code Level Diagrams

En esta sección, el equipo de arquitectura presenta y fundamenta los diagramas que exhiben el máximo nivel de detalle sobre la implementación estática y táctica de los componentes de software en el Bounded Context **Shared Kernel**. En estricta concordancia con la rúbrica de evaluación arquitectónica del proyecto, esta sección desglosa formalmente el **Bounded Context Domain Layer Class Diagrams**, exponiendo con absoluta rigurosidad técnica las clases, interfaces, enumeraciones, objetos de valor, raíces de agregado en memoria y la jerarquía de excepciones de dominio puro que residen en el paquete canónico `app.shared.domain`.

---

### 6.1 Bounded Context Domain Layer Class Diagrams

El diagrama de clases de la Capa de Dominio modela la estructura fundamental en memoria de las abstracciones transversales del sistema Navby Platform. En estricto apego a los principios de **Clean Architecture** y **Domain-Driven Design Táctico**, todos los componentes aquí modelados son puros: presentan cero dependencias hacia frameworks de persistencia relacional (SQLAlchemy ORM), motores de serialización externa (Pydantic) o bibliotecas de transporte HTTP (FastAPI).

El nivel de detalle incluye la totalidad de los miembros de cada componente (atributos privados, protegidos y públicos, factorías estáticas, propiedades de consulta `{query}`, métodos de comportamiento de negocio y sobrecargas de operadores canónicos), con visibilidad explícita, tipado fuerte bajo Python 3.12 y calificación semántica de relaciones mediante dirección, nombres de rol y multiplicidades explícitas (`1`, `*`, `0..1`).

#### 6.1.1 Artefacto Visual Compilado (Diagram-as-Code)

La siguiente figura ilustra el modelo de clases estático compilado automáticamente a través del pipeline de integración reproducible (`make class-diagrams`) a partir de su especificación PlantUML canónica:

![Diagrama de Clases UML - Bounded Context Shared Kernel (Domain Layer)](../../../report/assets/class-diagrams/class-diagram-shared.png)

---

#### 6.1.2 Catálogo Taxonómico Táctico de la Capa de Dominio (Estándar Atelier)

A continuación, se detalla la taxonomía general de los 13 tipos canónicos estructurados que integran la Capa de Dominio del Shared Kernel, organizados según su rol táctico en la arquitectura del sistema:

| Clase o Tipo de Dominio | Categoría Táctica DDD | Paquete Canónico | Propósito en la Arquitectura de Dominio |
| :--- | :---: | :--- | :--- |
| **AbstractDomainAggregateRoot[ID]** | Raíz de Agregado Base (`<<AggregateBase>>`) | `app.shared.domain.model.aggregate_root` | Superclase abstracta genérica que salvaguarda la identidad unívoca y orquesta la acumulación y drenaje atómico de eventos de dominio en memoria. |
| **DomainEvent** | Evento de Dominio (`<<DomainEvent>>`) | `app.shared.domain.model.aggregate_root` | Contrato inmutable universal que registra sucesos consumados en el pasado con sellado temporal UTC y UUIDv4 para deduplicación e idempotencia Outbox. |
| **GeoPoint** | Objeto de Valor (`<<ValueObject>>`) | `app.shared.domain.value_objects.geo_point` | Coordenada geográfica WGS84 inmutable que encapsula cálculos ortodrómicos esféricos puros basados en la fórmula trigonométrica del Haversine. |
| **Currency** | Enumeración de Dominio (`<<Enum>>`) | `app.shared.domain.value_objects.money` | Catálogo tipado de divisas soberanas autorizadas para cotizaciones y transacciones comerciales en Navby Platform (`USD`, `PEN`, `EUR`). |
| **Money** | Objeto de Valor (`<<ValueObject>>`) | `app.shared.domain.value_objects.money` | Magnitud dineraria inmutable con escala a 2 decimales, redondeo bancario legal `ROUND_HALF_EVEN` y operaciones aritméticas seguras con divisa homogénea. |
| **IATACode** | Objeto de Valor (`<<ValueObject>>`) | `app.shared.domain.value_objects.iata_code` | Código alfanumérico normalizado de 3 caracteres asignado por IATA a aeropuertos comerciales, validado contra el estándar `^[A-Z]{3}$`. |
| **EmailAddress** | Objeto de Valor (`<<ValueObject>>`) | `app.shared.domain.value_objects.email_address` | Dirección de correo electrónico normalizada a minúsculas y validada estrictamente bajo el estándar RFC 5322 (máximo 150 caracteres). |
| **UserId** | Identificador Tipado (`<<TypedId>>`) | `app.shared.domain.value_objects.user_id` | Identificador fuertemente tipado de usuario que encapsula un entero positivo de 64 bits (`BIGINT > 0`), alineado con la clave primaria de PostgreSQL. |
| **Result[T, E]** | Mónada Funcional (`<<Monad>>`) | `app.shared.application.result.result` | Contenedor funcional inmutable para orquestar flujos de negocio deterministas, encapsulando valores de éxito (`T`) o fallos semánticos tipados (`E`). |
| **DomainException** | Excepción Base (`<<DomainException>>`) | `app.shared.domain.exceptions.domain_exceptions` | Superclase inmutable de excepciones de dominio portadora de código unívoco de máquina (`code`), mensaje legible y diccionario de metadatos contextuales. |
| **InvalidCoordinatesException** | Excepción Especializada (`<<DomainException>>`) | `app.shared.domain.exceptions.domain_exceptions` | Infracción disparada cuando una coordenada espacial viola los rangos geodésicos [-90.0, 90.0] o [-180.0, 180.0], o recibe tipos no numéricos. |
| **NegativeAmountException** | Excepción Especializada (`<<DomainException>>`) | `app.shared.domain.exceptions.domain_exceptions` | Infracción disparada cuando una operación monetaria o inicialización intenta instanciar un monto financiero negativo ((*amount* < 0.00)). |
| **InvalidIATACodeException** | Excepción Especializada (`<<DomainException>>`) | `app.shared.domain.exceptions.domain_exceptions` | Infracción disparada ante códigos de aeropuerto que no cumplen estrictamente con 3 caracteres alfabéticos ASCII mayúsculos. |
| **CurrencyMismatchException** | Excepción Especializada (`<<DomainException>>`) | `app.shared.domain.exceptions.domain_exceptions` | Infracción disparada cuando se intenta ejecutar una operación de adición, sustracción o comparación relativa entre importes de divisas incompatibles. |
| **EntityNotFoundException** | Excepción Especializada (`<<DomainException>>`) | `app.shared.domain.exceptions.domain_exceptions` | Infracción semántica disparada cuando una entidad o agregado requerido no existe en el contexto operativo del dominio. |
| **InvalidEmailAddressException** | Excepción Especializada (`<<DomainException>>`) | `app.shared.domain.exceptions.domain_exceptions` | Infracción disparada cuando una cadena no cumple la sintaxis del RFC 5322 o supera el límite de longitud de 150 caracteres. |
| **InvalidUserIdException** | Excepción Especializada (`<<DomainException>>`) | `app.shared.domain.exceptions.domain_exceptions` | Infracción disparada ante valores de identificador de usuario no enteros, booleanos o con magnitud escalar (*value* ≤ 0). |

---

#### 6.1.3 Tablas Explicativas Detalladas de Miembros, Visibilidad y Reglas de Negocio

Siguiendo el estándar de desglose analítico de Atelier, las siguientes tablas estructuran pormenorizadamente cada subsistema del modelo táctico, detallando el nombre del miembro, su tipo o firma operativa, su ámbito o visibilidad formal (`+` público, `-` privado, `#` protegido), y la totalidad de sus reglas de negocio e invariantes asociadas:

##### Tabla 6.1: Miembros de la Superclase Base de Agregados y Contrato de Eventos de Dominio

| Componente | Miembro (Atributo o Método) | Firma o Tipo Completo | Ámbito | Descripción, Relaciones e Invariantes de Negocio |
| :--- | :--- | :--- | :---: | :--- |
| **AbstractDomainAggregateRoot[ID]** | `_id` (Atributo) | `ID` | `# Protegido` | Almacena el identificador unívoco de dominio del agregado. Invariante: asignado en el constructor y desacoplado de IDs de base de datos. |
| **AbstractDomainAggregateRoot[ID]** | `_domain_events` (Atributo) | `list[DomainEvent]` | `# Protegido` | Colección interna mutable en memoria que acumula los eventos de dominio ocurridos durante el ciclo transaccional activo. |
| **AbstractDomainAggregateRoot[ID]** | `__init__` (Método) | `(id: ID) -> None` | `+ Público` | Constructor que inicializa el agregado con su clave unívoca e inicializa la lista interna de eventos como colección vacía. |
| **AbstractDomainAggregateRoot[ID]** | `id` (Propiedad) | `() -> ID` | `+ Público` | Descriptor de solo lectura (`@property`) que expone la identidad inmutable del agregado hacia repositorios y casos de uso. |
| **AbstractDomainAggregateRoot[ID]** | `register_domain_event` (Método) | `(event: DomainEvent) -> None` | `+ Público` | Encola un evento consumado en la colección `_domain_events`. Regla: invocado internamente ante cualquier mutación de estado válida. |
| **AbstractDomainAggregateRoot[ID]** | `domain_events` (Método) | `() -> tuple[DomainEvent, ...]` | `+ Público` | Retorna una instantánea inmutable (tupla de solo lectura) de los eventos acumulados, impidiendo mutaciones externas fuera del agregado. |
| **AbstractDomainAggregateRoot[ID]** | `clear_domain_events` (Método) | `() -> None` | `+ Público` | Purga la colección de eventos en memoria. Regla: ejecutado tras la confirmación atómica de la persistencia o despacho al broker. |
| **AbstractDomainAggregateRoot[ID]** | `pull_domain_events` (Método) | `() -> tuple[DomainEvent, ...]` | `+ Público` | Extrae de manera atómica la tupla de eventos acumulados y vacía la cola interna en una sola operación segura para el patrón Transactional Outbox. |
| **AbstractDomainAggregateRoot[ID]** | `__eq__` (Método) | `(other: Any) -> bool` | `+ Público` | Igualdad de identidad técnica de dominio: dos agregados son idénticos si pertenecen exactamente a la misma clase y comparten el mismo `_id`. |
| **AbstractDomainAggregateRoot[ID]** | `__hash__` (Método) | `() -> int` | `+ Público` | Computa el hash unívoco a partir de `(self.__class__, self._id)`, garantizando coherencia absoluta con `__eq__` en colecciones tipo `set` o `dict`. |
| **AbstractDomainAggregateRoot[ID]** | `__repr__` (Método) | `() -> str` | `+ Público` | Formato determinista de depuración textual: `<NombreClase(id=...)>`. |
| **DomainEvent** | `event_id` (Atributo) | `UUID` | `+ Público` | Identificador global unívoco del evento autogenerado con `uuid.uuid4()`. Garantiza idempotencia y deduplicación en almacenamiento Outbox. |
| **DomainEvent** | `occurred_on` (Atributo) | `datetime` | `+ Público` | Marca temporal inmutable sellada en UTC estricto (`datetime.now(timezone.utc)`), libre de ambigüedades horarias de servidores locales. |
| **DomainEvent** | `aggregate_id` (Atributo) | `str` | `+ Público` | Representación textual de la identidad unívoca del agregado emisor, empleada para particionamiento en brokers de mensajería (Kafka/RabbitMQ). |
| **DomainEvent** | `event_type` (Atributo) | `str` | `+ Público` | Calificador semántico del tipo de evento. Si no se suministra, se autoasigna en `__post_init__` con el nombre dinámico de la subclase. |
| **DomainEvent** | `__post_init__` (Método) | `() -> None` | `+ Público` | Valida y asegura que `event_type` contenga el descriptor canónico de la clase derivada para deserialización polimórfica en consumidores. |
| **DomainEvent** | `to_dict` (Método) | `() -> dict[str, Any]` | `+ Público` | Serializa el evento a un diccionario primitivo con marcas ISO-8601 y strings para inserción directa en la tabla de infraestructura `outbox_events`. |

---

##### Tabla 6.2: Miembros de los Objetos de Valor e Identificadores Tipados Transversales

| Componente | Miembro (Atributo o Método) | Firma o Tipo Completo | Ámbito | Descripción, Relaciones e Invariantes de Negocio |
| :--- | :--- | :--- | :---: | :--- |
| **GeoPoint** | `latitude` (Atributo) | `float` | `+ Público` | Latitud geodésica WGS84 en grados decimales. Invariante: acotada estrictamente a [-90.0, 90.0]. |
| **GeoPoint** | `longitude` (Atributo) | `float` | `+ Público` | Longitud geodésica WGS84 en grados decimales. Invariante: acotada estrictamente a [-180.0, 180.0]. |
| **GeoPoint** | `EARTH_RADIUS_KM` (Constante) | `float = 6371.0` | `+ Público {static}` | Radio medio volumétrico de la Tierra en kilómetros conforme a estándares geodésicos IUGG. |
| **GeoPoint** | `__post_init__` (Método) | `() -> None` | `+ Público` | Valida que los argumentos sean numéricos (rechaza booleanos) y cumplan los rangos geodésicos. Lanza InvalidCoordinatesException ante infracciones. |
| **GeoPoint** | `haversine_distance_km_to` (Método) | `(other: GeoPoint) -> float` | `+ Público` | Computa la distancia ortodrómica del gran círculo mediante Haversine puro. Aplica acotamiento min(1.0, max(0.0, a)) para evitar errores de dominio trigonométrico. |
| **GeoPoint** | `is_same_location` (Método) | `(other: GeoPoint, tolerance_km: float = 0.01) -> bool` | `+ Público` | Evalúa coincidencia espacial de dos puntos dentro de un radio de tolerancia geodésica (default: 10 metros). |
| **GeoPoint** | `to_tuple` (Método) | `() -> tuple[float, float]` | `+ Público` | Retorna la tupla de coordenadas primitivas (latitude, longitude). |
| **GeoPoint** | `__str__` (Método) | `() -> str` | `+ Público` | Representación formateada con 6 decimales de precisión: (latitud, longitud). |
| **Currency** | `USD`, `PEN`, `EUR` (Literales) | `str` | `+ Público` | Constantes enumeradas bajo StrEnum que restringen las tres divisas legales autorizadas en la plataforma. |
| **Money** | `amount` (Atributo) | `Decimal` | `+ Público` | Cuantía numérica inmutable del importe dinerario cuantizada a 2 decimales. Invariante: ≥ 0.00. |
| **Money** | `currency` (Atributo) | `Currency` | `+ Público` | Divisa oficial asociada a la magnitud monetaria. Composición obligatoria 1 → 1. |
| **Money** | `_CENT` (Constante) | `Decimal = Decimal("0.01")` | `- Privado {static}` | Constante escalar utilizada para la cuantización forzosa a dos cifras centesimales. |
| **Money** | `__post_init__` (Método) | `() -> None` | `+ Público` | Cuantiza amount con ROUND_HALF_EVEN a 2 decimales y verifica no negatividad. Lanza NegativeAmountException si amount < 0.00. |
| **Money** | `of` (Método) | `(amount: Decimal, currency: Currency) -> Money` | `+ Público {static}` | Factoría estática canónica de instanciación con cuantización automática. |
| **Money** | `zero` (Método) | `(currency: Currency) -> Money` | `+ Público {static}` | Factoría estática que construye un importe neutro 0.00 en la divisa solicitada. |
| **Money** | `from_float` (Método) | `(amount: float, currency: Currency) -> Money` | `+ Público {static}` | Factoría segura desde float que convierte mediante str para neutralizar imprecisiones binarias IEEE 754. |
| **Money** | `from_cents` (Método) | `(cents: int, currency: Currency) -> Money` | `+ Público {static}` | Convierte una magnitud entera en centavos al formato monetario decimal cuantizado. |
| **Money** | `_assert_same_currency` (Método) | `(other: Money) -> None` | `- Privado` | Valida compatibilidad estricta de divisa. Lanza CurrencyMismatchException si las divisas no coinciden exactamente. |
| **Money** | `add` (Método) | `(other: Money) -> Money` | `+ Público` | Suma dos magnitudes monetarias. Requiere divisas homogéneas. Sobrecargado en __add__. |
| **Money** | `subtract` (Método) | `(other: Money) -> Money` | `+ Público` | Resta dos magnitudes. Requiere divisas homogéneas y saldo remanente ≥ 0.00 (lanza NegativeAmountException si resulta < 0). Sobrecargado en __sub__. |
| **Money** | `multiply` (Método) | `(factor: Decimal \| int \| float) -> Money` | `+ Público` | Multiplica el importe por un factor numérico escalar con cuantización bancaria ROUND_HALF_EVEN. Sobrecargado en __mul__. |
| **Money** | `divide` (Método) | `(divisor: Decimal \| int) -> Money` | `+ Público` | Divide el importe por un divisor estrictamente positivo, cuantizando centavos resultantes. |
| **Money** | `is_zero`, `is_positive` (Métodos) | `() -> bool` | `+ Público` | Evaluadores semánticos booleanos que determinan si el importe es nulo o estrictamente positivo. |
| **Money** | `is_greater_than`, `is_less_than` | `(other: Money) -> bool` | `+ Público` | Comparadores relativos entre magnitudes monetarias con verificación obligatoria de divisa homogénea. |
| **Money** | `__str__` (Método) | `() -> str` | `+ Público` | Formato estándar de presentación financiera: "USD 120.50". |
| **IATACode** | `value` (Atributo) | `str` | `+ Público` | Código alfabético normalizado de 3 letras mayúsculas. |
| **IATACode** | `_REGEX` (Constante) | `Pattern` | `- Privado {static}` | Expresión regular precompilada ^[A-Z]{3}$ para validación formal de códigos de aeropuerto. |
| **IATACode** | `__post_init__` (Método) | `() -> None` | `+ Público` | Elimina espacios, convierte a mayúsculas y valida contra _REGEX. Lanza InvalidIATACodeException si no cumple el estándar. |
| **IATACode** | `from_string` (Método) | `(code: str) -> IATACode` | `+ Público {static}` | Factoría estática de conveniencia para construcción a partir de entradas de usuario o DTOs. |
| **EmailAddress** | `value` (Atributo) | `str` | `+ Público` | Cadena normalizada de la dirección de correo electrónico en minúsculas. |
| **EmailAddress** | `_REGEX` (Constante) | `Pattern` | `- Privado {static}` | Expresión regular precompilada conforme al estándar de formato sintáctico RFC 5322. |
| **EmailAddress** | `__post_init__` (Método) | `() -> None` | `+ Público` | Normaliza a minúsculas, valida longitud ≤ 150 caracteres y comprueba el patrón RFC 5322. Lanza InvalidEmailAddressException en caso de fallo. |
| **EmailAddress** | `from_string` (Método) | `(email: str) -> EmailAddress` | `+ Público {static}` | Factoría canónica estática para crear direcciones de correo validadas. |
| **UserId** | `value` (Atributo) | `int` | `+ Público` | Identificador escalar de usuario que encapsula un entero positivo de 64 bits (BIGINT > 0). |
| **UserId** | `__post_init__` (Método) | `() -> None` | `+ Público` | Valida que value sea de tipo int (rechazando booleanos explícitamente) y que sea > 0. Lanza InvalidUserIdException si es ≤ 0. |
| **UserId** | `from_int` (Método) | `(val: int) -> UserId` | `+ Público {static}` | Factoría estática canónica alineada con las claves primarias autogeneradas de PostgreSQL. |
| **UserId** | `to_int`, `__int__` (Métodos) | `() -> int` | `+ Público` | Retorna el entero escalar primitivo para su enlace en adaptadores de persistencia relacional. |

---

##### Tabla 6.3: Miembros de la Mónada Funcional de Control de Flujo (`Result[T, E]`)

| Componente | Miembro (Atributo o Método) | Firma o Tipo Completo | Ámbito | Descripción, Relaciones e Invariantes de Negocio |
| :--- | :--- | :--- | :---: | :--- |
| **Result[T, E]** | `_value` (Atributo) | `T \| None` | `- Privado` | Valor encapsulado en operaciones que culminan con éxito transaccional. Default: None. |
| **Result[T, E]** | `_error` (Atributo) | `E \| None` | `- Privado` | Instancia de DomainException encapsulada en operaciones que culminan en fallo. Default: None. |
| **Result[T, E]** | `_is_success` (Atributo) | `bool` | `- Privado` | Bandera booleana de estado de la mónada (True para éxito, False para fallo semántico). |
| **Result[T, E]** | `success` (Método) | `(value: T) -> Result[T, Any]` | `+ Público {static}` | Factoría que construye una mónada en estado de éxito, encapsulando el valor resultante. |
| **Result[T, E]** | `failure` (Método) | `(error: E) -> Result[Any, E]` | `+ Público {static}` | Factoría que construye una mónada en estado de fallo, encapsulando una excepción de dominio. |
| **Result[T, E]** | `is_success` (Propiedad) | `() -> bool` | `+ Público {query}` | Retorna True si la operación concluyó exitosamente. Permite discriminación condicional segura. |
| **Result[T, E]** | `is_failure` (Propiedad) | `() -> bool` | `+ Público {query}` | Retorna True si la operación resultó en un error o infracción semántica de dominio. |
| **Result[T, E]** | `value` (Propiedad) | `() -> T` | `+ Público {query}` | Retorna el valor encapsulado. Regla: lanza ValueError si se intenta invocar sobre un Result fallido. |
| **Result[T, E]** | `error` (Propiedad) | `() -> E` | `+ Público {query}` | Retorna el error encapsulado. Regla: lanza ValueError si se invoca sobre un Result exitoso. |
| **Result[T, E]** | `value_or` (Método) | `(default: T) -> T` | `+ Público` | Retorna el valor encapsulado si la operación fue exitosa, o el valor fallback default si fue fallo. |
| **Result[T, E]** | `map` (Método) | `(fn: Callable[[T], U]) -> Result[U, E]` | `+ Público` | Aplica una función pura sobre el valor si es éxito, o propaga el error E intacto si es fallo. |
| **Result[T, E]** | `bind` (Método) | `(fn: Callable[[T], Result[U, E]]) -> Result[U, E]` | `+ Público` | Encadenamiento monádico (FlatMap): evalúa una función que retorna un nuevo Result, secuenciando lógica sin condicionales anidados. |
| **Result[T, E]** | `match` (Método) | `(on_success: Callable[[T], R], on_failure: Callable[[E], R]) -> R` | `+ Público` | Evaluación exhaustiva bifactorial tipo pattern matching que ejecuta la rama correspondiente según el estado monádico. |

---

##### Tabla 6.4: Miembros de la Jerarquía Semántica de Excepciones de Dominio (`DomainException`)

| Componente | Miembro (Atributo o Método) | Firma o Tipo Completo | Ámbito | Descripción, Relaciones e Invariantes de Negocio |
| :--- | :--- | :--- | :---: | :--- |
| **DomainException** | `code` (Atributo) | `str` | `+ Público` | Descriptor de error unívoco en mayúsculas snake-case (e.g., `INVALID_COORDINATES`), utilizado por clientes de API y mapeo HTTP. |
| **DomainException** | `message` (Atributo) | `str` | `+ Público` | Mensaje descriptivo legible en lenguaje de negocio que explica la causa del rechazo o infracción. |
| **DomainException** | `details` (Atributo) | `dict[str, Any]` | `+ Público` | Diccionario serializable de metadatos contextuales (campos fallidos, valores rechazados, límites violados). |
| **DomainException** | `__init__` (Método) | `(code: str, message: str, details: dict[str, Any] \| None = None) -> None` | `+ Público` | Inicializador inmutable. Si details es nulo, inicializa un diccionario vacío inmutable. |
| **DomainException** | `__str__` (Método) | `() -> str` | `+ Público` | Formato determinista de cadena: `[{code}] {message}`. |
| **InvalidCoordinatesException** | `__init__` (Método) | `(code: str = "INVALID_COORDINATES", message: str = ..., details: dict \| None = None) -> None` | `+ Público` | Disparada por GeoPoint ante violaciones de rango [-90.0, 90.0] o [-180.0, 180.0]. Hereda de DomainException. |
| **NegativeAmountException** | `__init__` (Método) | `(code: str = "NEGATIVE_AMOUNT", message: str = ..., details: dict \| None = None) -> None` | `+ Público` | Disparada por Money ante instanciación o sustracciones que conduzcan a importes negativos. Hereda de DomainException. |
| **InvalidIATACodeException** | `__init__` (Método) | `(code: str = "INVALID_IATA_CODE", message: str = ..., details: dict \| None = None) -> None` | `+ Público` | Disparada por IATACode cuando la cadena de aeropuerto no coincide exactamente con el patrón ^[A-Z]{3}$. Hereda de DomainException. |
| **CurrencyMismatchException** | `__init__` (Método) | `(code: str = "CURRENCY_MISMATCH", message: str = ..., details: dict \| None = None) -> None` | `+ Público` | Disparada por Money ante operaciones aritméticas o comparativas entre importes con divisas heterogéneas. Hereda de DomainException. |
| **EntityNotFoundException** | `__init__` (Método) | `(code: str = "ENTITY_NOT_FOUND", message: str = ..., details: dict \| None = None) -> None` | `+ Público` | Disparada ante búsquedas insatisfechas de agregados en el contexto operativo. Hereda de DomainException. |
| **InvalidEmailAddressException** | `__init__` (Método) | `(code: str = "INVALID_EMAIL_ADDRESS", message: str = ..., details: dict \| None = None) -> None` | `+ Público` | Disparada por EmailAddress ante formatos no conformes con RFC 5322 o longitudes > 150 caracteres. Hereda de DomainException. |
| **InvalidUserIdException** | `__init__` (Método) | `(code: str = "INVALID_USER_ID", message: str = ..., details: dict \| None = None) -> None` | `+ Público` | Disparada por UserId ante valores escalares ≤ 0, no numéricos o booleanos. Hereda de DomainException. |

---

#### 6.1.4 Código Fuente Canónico PlantUML DSL (`class-diagram-shared.puml`)

El código fuente PlantUML DSL canónico que define este diagrama se almacena y versiona en `report/assets/diagram-sources/class-diagrams/class-diagram-shared.puml`. Su estructura es reproducible de forma determinista mediante el comando `make class-diagrams`:

```plantuml
@startuml class-diagram-shared
title <size:18>Diagrama de Clases UML - Bounded Context Shared Kernel (Domain Layer)</size>\n<size:12>Paquete Canónico: app.shared.domain</size>

' Configuraciones visuales y de diseño profesional
skinparam classAttributeIconSize 0
skinparam monochrome false
skinparam shadowing false
skinparam roundcorner 6
skinparam linetype ortho
skinparam nodesep 24
skinparam ranksep 28
skinparam defaultFontName "Helvetica", "Arial", sans-serif
skinparam defaultFontSize 10
skinparam defaultFontColor #2C3E50
skinparam arrowColor #34495E
skinparam arrowThickness 1.2
skinparam packageBorderColor #7F8C8D
skinparam packageFontSize 11
skinparam packageFontStyle bold

' Estilos específicos por categoría táctica
skinparam class {
    BackgroundColor #FFFFFF
    BorderColor #2C3E50
    HeaderBackgroundColor #EAEDED
}
skinparam class<<AggregateBase>> {
    BackgroundColor #E8F8F5
    BorderColor #16A085
    HeaderBackgroundColor #A3E4D7
}
skinparam class<<ValueObject>> {
    BackgroundColor #FEF9E7
    BorderColor #D68910
    HeaderBackgroundColor #FAD7A0
}
skinparam class<<TypedId>> {
    BackgroundColor #EBF5FB
    BorderColor #2980B9
    HeaderBackgroundColor #AED6F1
}
skinparam class<<DomainEvent>> {
    BackgroundColor #F4ECF7
    BorderColor #8E44AD
    HeaderBackgroundColor #D2B4DE
}
skinparam class<<DomainException>> {
    BackgroundColor #FDEDEC
    BorderColor #C0392B
    HeaderBackgroundColor #F5B7B1
}
skinparam enum {
    BackgroundColor #FCF3CF
    BorderColor #B7950B
    HeaderBackgroundColor #F9E79F
}

' Evitar anidamiento automático por puntos en los nombres de paquetes
set separator none

' ==============================================================================
' 1. TIER 1 (SUPERIOR): MODELO BASE DE AGREGADOS Y EVENTOS DE DOMINIO
' ==============================================================================
package "app.shared.domain.model" as model #FDFEFE {

    abstract class "AbstractDomainAggregateRoot<ID>" as AbstractDomainAggregateRoot <<AggregateBase>> {
        # _id: ID
        # _domain_events: list<DomainEvent>
        + __init__(id: ID): void
        + id: ID {query}
        + register_domain_event(event: DomainEvent): void
        + domain_events(): tuple<DomainEvent, ...> {query}
        + clear_domain_events(): void
        + pull_domain_events(): tuple<DomainEvent, ...>
        + __eq__(other: Any): bool
        + __hash__(): int
        + __repr__(): str
    }

    class DomainEvent <<DomainEvent>> {
        + event_id: UUID
        + occurred_on: datetime
        + aggregate_id: str
        + event_type: str
        + __post_init__(): void
        + to_dict(): dict<str, Any>
    }

    AbstractDomainAggregateRoot "1" o-- "*" DomainEvent : acumula en memoria >
    AbstractDomainAggregateRoot -[hidden]right-> DomainEvent
}

' ==============================================================================
' 2. TIER 2 (INTERMEDIO): VALUE OBJECTS, TYPED IDS Y ENUMERACIONES
' ==============================================================================
package "app.shared.domain.value_objects" as value_objects #FDFEFE {

    class GeoPoint <<ValueObject>> {
        + latitude: float
        + longitude: float
        {static} + EARTH_RADIUS_KM: float = 6371.0
        + __post_init__(): void
        + haversine_distance_km_to(other: GeoPoint): float
        + is_same_location(other: GeoPoint, tolerance_km: float = 0.01): bool
        + to_tuple(): tuple<float, float>
        + __str__(): str
    }

    class IATACode <<ValueObject>> {
        + value: str
        {static} - _REGEX: Pattern
        + __post_init__(): void
        {static} + from_string(code: str): IATACode
        + __str__(): str
    }

    class Money <<ValueObject>> {
        + amount: Decimal
        + currency: Currency
        {static} - _CENT: Decimal = Decimal("0.01")
        + __post_init__(): void
        {static} + of(amount: Decimal, currency: Currency): Money
        {static} + zero(currency: Currency): Money
        {static} + from_float(amount: float, currency: Currency): Money
        {static} + from_cents(cents: int, currency: Currency): Money
        - _assert_same_currency(other: Money): void
        + add(other: Money): Money
        + subtract(other: Money): Money
        + multiply(factor: Decimal | int | float): Money
        + divide(divisor: Decimal | int): Money
        + is_zero(): bool
        + is_positive(): bool
        + is_greater_than(other: Money): bool
        + is_less_than(other: Money): bool
        + __add__(other: Money): Money
        + __sub__(other: Money): Money
        + __mul__(factor: Decimal | int | float): Money
        + __str__(): str
    }

    enum Currency <<Enum>> {
        USD
        PEN
        EUR
    }

    class EmailAddress <<ValueObject>> {
        + value: str
        {static} - _REGEX: Pattern
        + __post_init__(): void
        {static} + from_string(email: str): EmailAddress
        + __str__(): str
    }

    class UserId <<TypedId>> {
        + value: int
        + __post_init__(): void
        {static} + from_int(val: int): UserId
        + to_int(): int
        + __int__(): int
        + __str__(): str
    }

    Money "1" *-- "1" Currency : expresado en >

    ' Disposición en 3 columnas compactas
    GeoPoint -[hidden]down-> IATACode
    Money -[hidden]down-> Currency
    EmailAddress -[hidden]down-> UserId

    GeoPoint -[hidden]right-> Money
    Money -[hidden]right-> EmailAddress
}

' Enlazar Tier 1 verticalmente con Tier 2
model -[hidden]down-> value_objects

' ==============================================================================
' 3. TIER 3 (INFERIOR): JERARQUÍA SEMÁNTICA DE EXCEPCIONES DE DOMINIO
' ==============================================================================
package "app.shared.domain.exceptions" as exceptions #FDFEFE {

    class DomainException <<DomainException>> {
        + code: str
        + message: str
        + details: dict<str, Any>
        + __init__(code: str, message: str, details: dict[str, Any] | None = None): void
        + __str__(): str
    }

    class InvalidCoordinatesException <<DomainException>> {
        + __init__(code: str = "INVALID_COORDINATES", message: str = ..., details: dict[str, Any] | None = None): void
    }

    class NegativeAmountException <<DomainException>> {
        + __init__(code: str = "NEGATIVE_AMOUNT", message: str = ..., details: dict[str, Any] | None = None): void
    }

    class InvalidIATACodeException <<DomainException>> {
        + __init__(code: str = "INVALID_IATA_CODE", message: str = ..., details: dict[str, Any] | None = None): void
    }

    class CurrencyMismatchException <<DomainException>> {
        + __init__(code: str = "CURRENCY_MISMATCH", message: str = ..., details: dict[str, Any] | None = None): void
    }

    class EntityNotFoundException <<DomainException>> {
        + __init__(code: str = "ENTITY_NOT_FOUND", message: str = ..., details: dict[str, Any] | None = None): void
    }

    class InvalidEmailAddressException <<DomainException>> {
        + __init__(code: str = "INVALID_EMAIL_ADDRESS", message: str = ..., details: dict[str, Any] | None = None): void
    }

    class InvalidUserIdException <<DomainException>> {
        + __init__(code: str = "INVALID_USER_ID", message: str = ..., details: dict[str, Any] | None = None): void
    }

    ' Herencia hacia DomainException
    InvalidCoordinatesException --|> DomainException
    NegativeAmountException --|> DomainException
    InvalidIATACodeException --|> DomainException
    CurrencyMismatchException --|> DomainException
    EntityNotFoundException --|> DomainException
    InvalidEmailAddressException --|> DomainException
    InvalidUserIdException --|> DomainException

    ' Grilla balanceada de 3 columnas para excepciones
    DomainException -[hidden]down-> InvalidCoordinatesException
    InvalidCoordinatesException -[hidden]down-> NegativeAmountException
    NegativeAmountException -[hidden]down-> InvalidIATACodeException

    DomainException -[hidden]down-> CurrencyMismatchException
    CurrencyMismatchException -[hidden]down-> EntityNotFoundException

    DomainException -[hidden]down-> InvalidEmailAddressException
    InvalidEmailAddressException -[hidden]down-> InvalidUserIdException

    InvalidCoordinatesException -[hidden]right-> CurrencyMismatchException
    CurrencyMismatchException -[hidden]right-> InvalidEmailAddressException
}

' Enlazar Tier 2 verticalmente con Tier 3
value_objects -[hidden]down-> exceptions

' ==============================================================================
' RELACIONES TRANSVERSALES DE DOMINIO
' ==============================================================================
GeoPoint .down.> InvalidCoordinatesException : lanza ante coordenadas ilegales >
Money .down.> NegativeAmountException : lanza ante saldos negativos >
Money .down.> CurrencyMismatchException : lanza ante divisas incompatibles >
IATACode .down.> InvalidIATACodeException : lanza ante código no ISO >
EmailAddress .down.> InvalidEmailAddressException : lanza ante formato no RFC >
UserId .down.> InvalidUserIdException : lanza ante ID <= 0 o no entero >

@enduml
```

---

#### 6.1.5 Tabla de Trazabilidad de Estereotipos Tácticos UML

En la siguiente matriz se normalizan los estereotipos visuales aplicados en el diagrama de clases, correlacionando su semántica arquitectónica DDD con la paleta de diseño profesional adoptada:

| Estereotipo UML | Semántica Táctica DDD | Color de Fondo | Color de Borde | Tipos Mapeados en el Shared Kernel |
| :---: | :--- | :---: | :---: | :--- |
| <<AggregateBase>> | Superclase abstracta de raíz de agregado con acumulación en memoria y drenaje atómico de eventos | `#E8F8F5` | `#16A085` | `AbstractDomainAggregateRoot[ID]` |
| <<DomainEvent>> | Evento inmutable de dominio con marca temporal en UTC y UUIDv4 para deduplicación e idempotencia | `#F4ECF7` | `#8E44AD` | `DomainEvent` |
| <<ValueObject>> | Objeto de valor inmutable modelado por sus atributos sin identidad conceptual propia | `#FEF9E7` | `#D68910` | `GeoPoint`, `Money`, `IATACode`, `EmailAddress` |
| <<TypedId>> | Wrapper inmutable de identidad técnica relacional alineado con claves `BIGINT > 0` de PostgreSQL | `#EBF5FB` | `#2980B9` | `UserId` |
| <<Enum>> | Enumeración tipada de dominio basada en `StrEnum` que restringe catálogos cerrados | `#FCF3CF` | `#B7950B` | `Currency` |
| <<DomainException>> | Jerarquía inmutable de excepciones de dominio con códigos de error legibles por máquina para RFC 7807 | `#FDEDEC` | `#C0392B` | `DomainException`, `InvalidCoordinatesException`, `NegativeAmountException`, `InvalidIATACodeException`, `CurrencyMismatchException`, `EntityNotFoundException`, `InvalidEmailAddressException`, `InvalidUserIdException` |

---

## 7. Interface Layer: Arquitectura de Adaptadores Primarios, Recursos REST y Esquemas Inmutables

### 7.1 Propósito, Principios Rectores y Estándar OpenAPI / RFC 7807

La **Capa de Interfaz** (`app.shared.interfaces`) actúa como el adaptador primario de conducción (*Driving Adapter*) en la arquitectura hexagonal de Navby Platform. Su responsabilidad fundamental es doble:
1. **Desacoplar el protocolo de transporte HTTP de las reglas de negocio:** Convertir las peticiones entrantes de FastAPI en comandos inmutables de aplicación, y transformar las proyecciones y mónadas funcionales de dominio en representaciones JSON serializables.
2. **Estandarizar los contratos de comunicación y resiliencia perimetral:** Imponer contratos vivos autovalidados mediante esquemas inmutables de Pydantic v2, unificar la taxonomía de respuestas de error bajo el estándar RFC 7807 (*Problem Details for HTTP APIs*), y gobernar el flujo perimetral mediante middlewares de trazabilidad asíncrona (`contextvars`), seguridad OWASP y limitación de tasa basada en Redis 7.

De acuerdo con el Décimo Mandamiento Arquitectónico de Navby Platform, ningún agregado ni entidad de dominio cruza directamente la frontera del transporte web. Los recursos de entrada y salida (*Resources* / DTOs) garantizan inmutabilidad absoluta y rechazo de sobreasignación de datos (*over-posting*) mediante la configuración `model_config = ConfigDict(frozen=True, extra="forbid")`.

### 7.2 Esquema de Detalle de Error Inmutable: `InvalidParam` y `ErrorResource` (RFC 7807)

```python
# app/shared/interfaces/rest/resources/error_resource.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from app.shared.domain.exceptions.domain_exceptions import DomainException, DomainError


class InvalidParam(BaseModel):
    """
    Sub-esquema inmutable para detallar infracciones de validación campo por campo.
    Cumple rigurosamente con las extensiones estándar de RFC 7807 para parámetros inválidos.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(
        description="Nombre o ruta calificada del parámetro o atributo infractor (ej. 'body.email', 'query.page')."
    )
    reason: str = Field(
        description="Descripción semántica y legible del motivo de la invalidación o restricción violada."
    )


class ErrorResource(BaseModel):
    """
    Esquema inmutable universal de respuesta de error conforme al estándar RFC 7807 Problem Details.
    Garantiza una estructura predecible para clientes REST y erradica la fuga de trazas internas.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    type: str = Field(
        default="about:blank",
        description="URI canónica o identificador URN que categoriza unívocamente el tipo de problema."
    )
    title: str = Field(
        description="Resumen conciso y legible por humanos del tipo de error HTTP ocurrido."
    )
    status: int = Field(
        description="Código de estado HTTP devuelto por el servidor de origen para esta respuesta."
    )
    detail: str = Field(
        description="Explicación detallada de la transgresión específica acontecida en esta invocación."
    )
    instance: str | None = Field(
        default=None,
        description="URI relativa de la petición específica sobre la que aconteció el error."
    )
    code: str = Field(
        description="Código de error semántico de máquina estandarizado (ej. 'INVALID_COORDINATES', 'NOT_FOUND')."
    )
    invalid_params: list[InvalidParam] | None = Field(
        default=None,
        description="Colección granular de transgresiones atómicas en parámetros de entrada, si aplican."
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Marca de tiempo en formato UTC estricto en que aconteció el error."
    )

    @classmethod
    def of(
        cls,
        title: str,
        status: int,
        detail: str,
        code: str,
        instance: str | None = None,
        invalid_params: list[InvalidParam] | None = None,
        type_uri: str | None = None,
    ) -> ErrorResource:
        """
        Factoría estática general para instanciar recursos de error conformes a RFC 7807.
        Construye automáticamente la URN de tipo canónico si no es suministrada explícitamente.
        """
        resolved_type = (
            type_uri
            if type_uri is not None
            else f"urn:navby:error:{code.lower().replace('_', '-')}"
        )
        return cls(
            type=resolved_type,
            title=title,
            status=status,
            detail=detail,
            instance=instance,
            code=code,
            invalid_params=invalid_params,
            timestamp=datetime.now(timezone.utc),
        )

    @classmethod
    def from_domain_error(
        cls,
        error: DomainError,
        status_code: int,
        title: str,
        instance: str | None = None,
    ) -> ErrorResource:
        """
        Factoría especializada para transformar una anomalía de dominio en ErrorResource.
        Extrae el código y mensaje de la excepción de dominio sin exponer detalles de bajo nivel.
        """
        return cls.of(
            title=title,
            status=status_code,
            detail=error.message,
            code=error.code,
            instance=instance,
            invalid_params=None,
        )

    @classmethod
    def from_validation_error(
        cls,
        invalid_params: list[InvalidParam],
        instance: str | None = None,
        detail: str = "Los parámetros proporcionados en la solicitud contienen errores de validación de sintaxis o tipo.",
    ) -> ErrorResource:
        """
        Factoría especializada para errores de validación de parámetros o cuerpo Pydantic v2.
        """
        return cls.of(
            title="Unprocessable Entity",
            status=422,
            detail=detail,
            code="VALIDATION_ERROR",
            instance=instance,
            invalid_params=invalid_params,
        )
```

### 7.3 Esquema de Mensaje Simple de Confirmación: `MessageResource`

```python
# app/shared/interfaces/rest/resources/message_resource.py
from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field


class MessageResource(BaseModel):
    """
    Recurso REST inmutable para respuestas de confirmación operativa simple.
    Utilizado en comandos que no producen una nueva entidad de retorno (ej. logout, revocación de tokens).
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    message: str = Field(
        description="Mensaje informativo o de confirmación de la operación ejecutada."
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Marca temporal UTC del momento en que se emitió la confirmación."
    )

    @classmethod
    def of(cls, message: str) -> MessageResource:
        """Factoría concisa para instanciar confirmaciones informativas."""
        return cls(
            message=message,
            timestamp=datetime.now(timezone.utc),
        )
```

### 7.4 Esquemas Genéricos de Paginación: `PaginationParams` y `PagedResource[T]`

```python
# app/shared/interfaces/rest/resources/paged_resource.py
from __future__ import annotations

import math
from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Parámetros estandarizados de paginación para consultas GET mediante Query Params.
    Asegura límites defensivos para mitigar denegación de servicio por consultas masivas no acotadas.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    page: int = Field(
        default=1,
        ge=1,
        description="Número de página solicitado (1-indexado, mínimo 1)."
    )
    size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Cantidad máxima de elementos por página (mínimo 1, máximo 100)."
    )

    @property
    def offset(self) -> int:
        """Calcula el desplazamiento numérico de filas para sentencias SQL LIMIT/OFFSET."""
        return (self.page - 1) * self.size


class PagedResource(BaseModel, Generic[T]):
    """
    Recurso contenedor genérico e inmutable para respuestas de colecciones paginadas.
    Suministra metadatos exhaustivos para navegación y renderizado en clientes frontend.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    items: list[T] = Field(
        description="Colección de elementos correspondientes al segmento de la página actual."
    )
    page: int = Field(
        description="Índice de la página actual solicitada (1-indexado)."
    )
    size: int = Field(
        description="Cantidad de registros por página configurada en la consulta."
    )
    total_elements: int = Field(
        description="Cantidad total absoluta de registros que satisfacen los criterios de consulta."
    )
    total_pages: int = Field(
        description="Número total de páginas calculadas para el tamaño de página configurado."
    )
    has_next: bool = Field(
        description="Indicador booleano que señala si existe una página posterior disponible."
    )
    has_previous: bool = Field(
        description="Indicador booleano que señala si existe una página anterior disponible."
    )

    @classmethod
    def of(
        cls,
        items: list[T],
        page: int,
        size: int,
        total_elements: int,
    ) -> PagedResource[T]:
        """
        Factoría estática que calcula matemáticamente las páginas totales y los indicadores booleanos.
        """
        calculated_pages = math.ceil(total_elements / size) if size > 0 else 0
        return cls(
            items=items,
            page=page,
            size=size,
            total_elements=total_elements,
            total_pages=calculated_pages,
            has_next=page < calculated_pages,
            has_previous=page > 1 and calculated_pages > 0,
        )
```

---

## 8. Interface Layer: Transformadores y Ensambladores de Respuestas HTTP (REST Assemblers)

### 8.1 Desacoplamiento de Transporte y Desempaquetado Funcional de Mónadas

El diseño de ensambladores (*Assemblers*) en Navby Platform garantiza la separación estricta exigida por el Cuarto Mandamiento Arquitectónico. Los controladores REST (`APIRouter`) actúan como mediadores puros: reciben DTOs de entrada, invocan casos de uso de aplicación, reciben una mónada `Result[T, E]` y delegan su desempaquetado a `result_to_response` o `paged_result_to_response`.

```
[Cliente HTTP] 
      │ Petición JSON
      ▼
[FastAPI Router] ── (Schema -> Command) ──► [Use Case (Application)]
      │                                                │ Retorna Result[T, E]
      ▼                                                ▼
[result_to_response] ◄─────────────────────────────────┘
      │
      ├── [is_success] ──► Serializa DTO/Resource ──► HTTP 200/201/204
      └── [is_failure] ──► error_to_problem_details ──► HTTP 4xx/5xx (RFC 7807)
```

### 8.2 Mapeador Semántico Exhaustivo de Excepciones: `error_to_problem_details`

```python
# app/shared/interfaces/rest/transform/error_assembler.py
from __future__ import annotations

from fastapi import status
from starlette.responses import JSONResponse

from app.shared.domain.exceptions.domain_exceptions import DomainException, DomainError
from app.shared.interfaces.rest.resources.error_resource import ErrorResource


_ERROR_STATUS_CATALOG: dict[str, tuple[int, str]] = {
    # 404 Not Found: Entidades o recursos requeridos no localizados
    "ENTITY_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Resource Not Found"),
    "USER_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "User Not Found"),
    "ITINERARY_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Itinerary Not Found"),
    "AIRPORT_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Airport Not Found"),
    "ROUTE_NOT_FOUND": (status.HTTP_404_NOT_FOUND, "Route Not Found"),
    # 400 Bad Request: Transgresión de invariantes y formatos de entrada
    "INVALID_COORDINATES": (status.HTTP_400_BAD_REQUEST, "Invalid Geographic Coordinates"),
    "INVALID_IATA_CODE": (status.HTTP_400_BAD_REQUEST, "Invalid IATA Airport Code"),
    "INVALID_EMAIL_ADDRESS": (status.HTTP_400_BAD_REQUEST, "Invalid Email Address"),
    "INVALID_USER_ID": (status.HTTP_400_BAD_REQUEST, "Invalid User Identifier"),
    "BAD_REQUEST": (status.HTTP_400_BAD_REQUEST, "Bad Request"),
    # 422 Unprocessable Entity: Restricciones de negocio y semántica de dominio
    "NEGATIVE_AMOUNT": (status.HTTP_422_UNPROCESSABLE_ENTITY, "Negative Monetary Amount"),
    "CURRENCY_MISMATCH": (status.HTTP_422_UNPROCESSABLE_ENTITY, "Currency Mismatch"),
    "BUSINESS_RULE_VIOLATION": (status.HTTP_422_UNPROCESSABLE_ENTITY, "Business Rule Violation"),
    "VALIDATION_ERROR": (status.HTTP_422_UNPROCESSABLE_ENTITY, "Unprocessable Entity"),
    # 401 Unauthorized: Autenticación, firmas y expiración de tokens
    "UNAUTHORIZED": (status.HTTP_401_UNAUTHORIZED, "Unauthorized"),
    "INVALID_CREDENTIALS": (status.HTTP_401_UNAUTHORIZED, "Invalid Credentials"),
    "TOKEN_EXPIRED": (status.HTTP_401_UNAUTHORIZED, "Token Expired"),
    "TOKEN_REVOKED": (status.HTTP_401_UNAUTHORIZED, "Token Revoked"),
    # 403 Forbidden: Autorización y permisos insuficientes
    "FORBIDDEN": (status.HTTP_403_FORBIDDEN, "Forbidden"),
    "ACCESS_DENIED": (status.HTTP_403_FORBIDDEN, "Access Denied"),
    # 402 Payment Required: Agotamiento de créditos o saldos
    "INSUFFICIENT_CREDITS": (status.HTTP_402_PAYMENT_REQUIRED, "Insufficient Navby Credits"),
    "PAYMENT_REQUIRED": (status.HTTP_402_PAYMENT_REQUIRED, "Payment Required"),
    # 409 Conflict: Duplicidad de recursos e idempotencia
    "CONFLICT": (status.HTTP_409_CONFLICT, "Conflict"),
    "RESOURCE_ALREADY_EXISTS": (status.HTTP_409_CONFLICT, "Resource Already Exists"),
    # 429 Too Many Requests: Cuotas perimetrales
    "RATE_LIMIT_EXCEEDED": (status.HTTP_429_TOO_MANY_REQUESTS, "Too Many Requests"),
    "TOO_MANY_REQUESTS": (status.HTTP_429_TOO_MANY_REQUESTS, "Too Many Requests"),
}


def error_to_problem_details(
    error: DomainError,
    instance: str | None = None,
) -> JSONResponse:
    """
    Transforma un DomainError en una respuesta HTTP JSONResponse tipada bajo el estándar
    RFC 7807 Problem Details con Content-Type 'application/problem+json'.
    """
    http_status, title = _ERROR_STATUS_CATALOG.get(
        error.code,
        (status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error"),
    )
    error_resource = ErrorResource.from_domain_error(
        error=error,
        status_code=http_status,
        title=title,
        instance=instance,
    )
    return JSONResponse(
        status_code=http_status,
        content=error_resource.model_dump(mode="json"),
        media_type="application/problem+json",
    )
```

### 8.3 Ensambladores Canónicos de Colecciones y Entidades: `result_to_response` y `paged_result_to_response`

```python
# app/shared/interfaces/rest/transform/response_assembler.py
from __future__ import annotations

from typing import Any, Callable, TypeVar
from fastapi import status
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse, Response

from app.shared.domain.exceptions.domain_exceptions import DomainException, DomainError
from app.shared.domain.model.monads.result import Result
from app.shared.interfaces.rest.resources.paged_resource import PagedResource
from app.shared.interfaces.rest.transform.error_assembler import error_to_problem_details

T = TypeVar("T")
R = TypeVar("R")
E = TypeVar("E", bound=DomainException)


def result_to_response(
    result: Result[T, E],
    success_status: int = status.HTTP_200_OK,
    resource_assembler: Callable[[T], R] | None = None,
    instance: str | None = None,
) -> Response:
    """
    Desempaqueta funcionalmente un Result[T, E] de Dominio/Aplicación hacia el transporte HTTP.
    - Si el resultado es exitoso y el valor es None, emite HTTP 204 No Content.
    - Si el resultado es exitoso y posee valor, aplica la función ensambladora (si existe) y serializa a JSON.
    - Si el resultado es fallido, delega la conversión a error_to_problem_details para emitir RFC 7807.
    """
    if result.is_failure:
        return error_to_problem_details(result.error, instance=instance)

    value = result.value
    if value is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    transformed = resource_assembler(value) if resource_assembler is not None else value
    if hasattr(transformed, "model_dump"):
        payload = transformed.model_dump(mode="json")
    else:
        payload = jsonable_encoder(transformed)

    return JSONResponse(
        status_code=success_status,
        content=payload,
    )


def paged_result_to_response(
    result: Result[PagedResource[T], E],
    item_assembler: Callable[[T], R] | None = None,
    instance: str | None = None,
) -> Response:
    """
    Desempaqueta funcionalmente un Result que contiene un contenedor PagedResource[T].
    Transforma individualmente los elementos de la colección items preservando la metadata paginada.
    """
    if result.is_failure:
        return error_to_problem_details(result.error, instance=instance)

    paged_data = result.value
    transformed_items = [
        item_assembler(item) if item_assembler is not None else item
        for item in paged_data.items
    ]

    paged_resource = PagedResource[Any].of(
        items=transformed_items,
        page=paged_data.page,
        size=paged_data.size,
        total_elements=paged_data.total_elements,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=paged_resource.model_dump(mode="json"),
    )
```

---

## 9. Interface Layer: Manejador Global de Excepciones Web (Global Web Exception Handler)

### 9.1 Taxonomía de Excepciones Web y Captura Determinista

Para impedir que excepciones no controladas generen respuestas HTML nativas o fugas de stack traces en producción, se implementa una captura exhaustiva dividida en cuatro familias jerárquicas:
1. **`RequestValidationError`:** Errores de validación de sintaxis originados por FastAPI / Pydantic v2 al parsear el cuerpo o parámetros. Se transforman a HTTP 422 con array de `invalid_params`.
2. **`DomainError`:** Anomalías de reglas de negocio que alcanzaron la capa perimetral. Se delegan al catálogo semántico de `error_to_problem_details`.
3. **`StarletteHTTPException`:** Excepciones nativas del framework HTTP (404 Not Found de rutas inexistentes, 405 Method Not Allowed, 415 Unsupported Media Type). Se normalizan a RFC 7807.
4. **`Exception`:** Fallback global de último recurso. Registra el error en logs estructurados con `correlation_id` y stack trace completo para observabilidad interna, pero emite al cliente un HTTP 500 neutro y sanitizado.

### 9.2 Implementación Canónica de `setup_global_exception_handlers`

```python
# app/shared/interfaces/errors/global_exception_handler.py
from __future__ import annotations

import logging
from typing import Any
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.shared.domain.exceptions.domain_exceptions import DomainException, DomainError
from app.shared.interfaces.middleware.correlation_id_middleware import correlation_id_ctx
from app.shared.interfaces.rest.resources.error_resource import ErrorResource, InvalidParam
from app.shared.interfaces.rest.transform.error_assembler import error_to_problem_details

logger = logging.getLogger("navby.interfaces.errors")


def setup_global_exception_handlers(app: FastAPI) -> None:
    """
    Registra centralizadamente los manejadores de excepciones en la aplicación FastAPI.
    Captura y traduce deterministamente 4 familias de errores web hacia RFC 7807:
    1. RequestValidationError: Validaciones sintácticas y de esquema Pydantic v2 (422).
    2. DomainError: Infracciones de invariantes de negocio no capturadas por casos de uso (400-422).
    3. StarletteHTTPException: Errores HTTP de enrutamiento y transporte nativos (404, 405, 415, etc.).
    4. Exception: Fallback global de último recurso para prevenir fuga de información y stack traces (500).
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        invalid_params: list[InvalidParam] = []
        for error_dict in exc.errors():
            loc_parts = [str(part) for part in error_dict.get("loc", []) if part != ""]
            field_name = ".".join(loc_parts) if loc_parts else "body"
            reason_msg = error_dict.get("msg", "Valor de parámetro no conforme con el esquema.")
            invalid_params.append(InvalidParam(name=field_name, reason=reason_msg))

        error_resource = ErrorResource.from_validation_error(
            invalid_params=invalid_params,
            instance=request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_resource.model_dump(mode="json"),
            media_type="application/problem+json",
        )

    @app.exception_handler(DomainError)
    async def domain_exception_handler(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        return error_to_problem_details(error=exc, instance=request.url.path)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        code_map: dict[int, tuple[str, str]] = {
            status.HTTP_404_NOT_FOUND: ("NOT_FOUND", "Resource Not Found"),
            status.HTTP_405_METHOD_NOT_ALLOWED: ("METHOD_NOT_ALLOWED", "Method Not Allowed"),
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: ("UNSUPPORTED_MEDIA_TYPE", "Unsupported Media Type"),
            status.HTTP_403_FORBIDDEN: ("FORBIDDEN", "Forbidden"),
            status.HTTP_401_UNAUTHORIZED: ("UNAUTHORIZED", "Unauthorized"),
        }
        semantic_code, title = code_map.get(
            exc.status_code,
            ("HTTP_ERROR", "HTTP Protocol Error"),
        )
        detail = str(exc.detail) if exc.detail else "Ocurrió un error en el procesamiento del protocolo HTTP."
        error_resource = ErrorResource.of(
            title=title,
            status=exc.status_code,
            detail=detail,
            code=semantic_code,
            instance=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_resource.model_dump(mode="json"),
            media_type="application/problem+json",
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        correlation_id = correlation_id_ctx.get()
        logger.critical(
            "Excepción interna no controlada capturada por el manejador global. "
            "CorrelationId: %s, Path: %s, Error: %s",
            correlation_id,
            request.url.path,
            str(exc),
            exc_info=True,
        )
        error_resource = ErrorResource.of(
            title="Internal Server Error",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ha ocurrido un error interno imprevisto en la plataforma. Por favor reporte este incidente al equipo de soporte indicando su identificador de correlación.",
            code="INTERNAL_SERVER_ERROR",
            instance=request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_resource.model_dump(mode="json"),
            media_type="application/problem+json",
        )
```

---

## 10. Interface Layer: Middlewares Perimetrales de Trazabilidad, Seguridad y Rate Limiting

### 10.1 Trazabilidad Distribuida y Contexto Asíncrono: `CorrelationIdMiddleware` con `contextvars`

```python
# app/shared/interfaces/middleware/correlation_id_middleware.py
from __future__ import annotations

import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware perimetral para inyección y propagación de identificadores de correlación distribuidos.
    Extrae la cabecera X-Correlation-Id o genera un UUIDv4, vinculándolo a una variable de contexto
    asíncrona (ContextVar) y garantizando su retorno en los headers de la respuesta HTTP.
    """

    HEADER_NAME = "X-Correlation-Id"

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        incoming_id = request.headers.get(self.HEADER_NAME, "").strip()
        correlation_id = incoming_id if incoming_id else str(uuid.uuid4())

        token = correlation_id_ctx.set(correlation_id)
        request.state.correlation_id = correlation_id

        try:
            response = await call_next(request)
            response.headers[self.HEADER_NAME] = correlation_id
            return response
        finally:
            correlation_id_ctx.reset(token)
```

### 10.2 Medición de Latencia y Structured Logging: `RequestLoggingMiddleware`

```python
# app/shared/interfaces/middleware/logging_middleware.py
from __future__ import annotations

import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.shared.interfaces.middleware.correlation_id_middleware import correlation_id_ctx

logger = logging.getLogger("navby.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware perimetral para auditoría y medición de latencia de peticiones HTTP.
    Registra métricas con time.perf_counter(), capturando método, ruta, status, IP y correlación.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start_time = time.perf_counter()
        correlation_id = correlation_id_ctx.get()
        client_host = request.client.host if request.client else "unknown"

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        logger.info(
            "HTTP %s %s - Status: %d - Latency: %.2fms - Client: %s - CorrelationId: %s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            client_host,
            correlation_id,
            extra={
                "http_method": request.method,
                "http_path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": duration_ms,
                "client_ip": client_host,
                "correlation_id": correlation_id,
            },
        )
        return response
```

### 10.3 Hardening Perimetral OWASP: `SecurityHeadersMiddleware`

```python
# app/shared/interfaces/middleware/security_middleware.py
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware perimetral para hardening y protección de cabeceras HTTP según estándares OWASP.
    Inyecta defensas contra ataques de clickjacking, sniffing de tipos MIME y forzado de HTTPS.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return response
```

### 10.4 Control de Flujo Distribuido con Redis 7 y Resiliencia Fail-Open: `RateLimitMiddleware`

En estricta conformidad con las directrices de `redis-core` y `redis-best-practices`, el limitador de tasa utiliza claves delimitadas por dos puntos en el espacio de nombres `navby:ratelimit:{client_id}:{endpoint}`. Implementa una ventana atómica mediante pipeline (`INCR` y `TTL`), gestiona el rechazo inmediato mediante HTTP 429 con cabeceras estándar (`Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) y ofrece tolerancia a fallos mediante el modo **Fail-Open**:

```python
# app/shared/interfaces/middleware/rate_limit_middleware.py
from __future__ import annotations

import logging
from typing import Any
import redis.asyncio as aioredis
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.shared.interfaces.rest.resources.error_resource import ErrorResource

logger = logging.getLogger("navby.ratelimit")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware perimetral de limitación de tasa (Rate Limiting) basado en Redis 7.
    Aplica una ventana de conteo atómico con clave canónica 'navby:ratelimit:{client_id}:{endpoint}'.
    Responde con HTTP 429 Too Many Requests y cabeceras Retry-After ante excesos de cuota.
    Implementa resiliencia Fail-Open para garantizar disponibilidad continua si Redis falla.
    """

    def __init__(
        self,
        app: Any,
        redis_client: aioredis.Redis,
        rate_limit_per_minute: int = 60,
        window_seconds: int = 60,
        fail_open: bool = True,
    ) -> None:
        super().__init__(app)
        self._redis = redis_client
        self._rate_limit = rate_limit_per_minute
        self._window_seconds = window_seconds
        self._fail_open = fail_open

    def _resolve_client_id(self, request: Request) -> str:
        """Resuelve el identificador del cliente: UserId autenticado o IP remota segura."""
        if hasattr(request.state, "user_id") and request.state.user_id:
            return f"user:{request.state.user_id}"
        
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        client_host = request.client.host if request.client else "anonymous"
        return f"ip:{client_host}"

    def _normalize_endpoint(self, path: str) -> str:
        """Normaliza el prefijo del endpoint para consolidar claves de cuota."""
        segments = [seg for seg in path.strip("/").split("/") if seg]
        if not segments:
            return "root"
        return ":".join(segments[:3])

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        client_id = self._resolve_client_id(request)
        endpoint = self._normalize_endpoint(request.url.path)
        cache_key = f"navby:ratelimit:{client_id}:{endpoint}"

        try:
            pipe = self._redis.pipeline()
            pipe.incr(cache_key)
            pipe.ttl(cache_key)
            results = await pipe.execute()

            current_count: int = results[0]
            current_ttl: int = results[1]

            # Si la clave es nueva (TTL == -1), fijamos el tiempo de expiración
            if current_ttl == -1:
                await self._redis.expire(cache_key, self._window_seconds)
                current_ttl = self._window_seconds

            remaining = max(0, self._rate_limit - current_count)

            if current_count > self._rate_limit:
                logger.warning(
                    "Tasa de peticiones excedida para cliente %s en endpoint %s (Conteo: %d, Límite: %d)",
                    client_id,
                    endpoint,
                    current_count,
                    self._rate_limit,
                )
                retry_after_seconds = max(1, current_ttl)
                error_resource = ErrorResource.of(
                    title="Too Many Requests",
                    status=429,
                    detail=f"Se ha excedido el límite de {self._rate_limit} peticiones por minuto para este recurso. Por favor reintente en {retry_after_seconds} segundos.",
                    code="RATE_LIMIT_EXCEEDED",
                    instance=request.url.path,
                )
                return JSONResponse(
                    status_code=429,
                    content=error_resource.model_dump(mode="json"),
                    media_type="application/problem+json",
                    headers={
                        "Retry-After": str(retry_after_seconds),
                        "X-RateLimit-Limit": str(self._rate_limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(retry_after_seconds),
                    },
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self._rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(max(1, current_ttl))
            return response

        except RedisError as exc:
            logger.error(
                "Fallo de conexión en Redis al evaluar Rate Limiting: %s. Aplicando política Fail-Open=%s",
                str(exc),
                self._fail_open,
            )
            if self._fail_open:
                return await call_next(request)
            raise
```

---

## 11. Diccionario Completo de Atributos, Métodos y Componentes de la Capa de Interfaz

### 11.1 Matriz Estructural de 5 Columnas (Estándar Atelier IAM)

En la siguiente tabla se consolidan exhaustivamente los componentes, atributos, firmas operativas, ámbitos y reglas de negocio de la Capa de Interfaz del Bounded Context Shared Kernel:

| Clase o Estructura | Elemento | Firma o Tipo | Ámbito | Descripción, Relaciones y Reglas de Negocio |
| :---: | :---: | :--- | :---: | :--- |
| **InvalidParam** | Atributos | `str name`, `str reason` | Público | Sub-esquema inmutable Pydantic v2. Modela el campo infractor y la razón legible. Invariante: inmutable (`frozen=True, extra="forbid"`). |
| **ErrorResource** | Atributos RFC 7807 | `str type`, `str title`, `int status`, `str detail`, `str \| None instance`, `str code`, `list[InvalidParam] \| None invalid_params`, `datetime timestamp` | Público | DTO universal inmutable de error conforme a RFC 7807 Problem Details. Genera URNs semánticas (`urn:navby:error:<code_slug>`). Timestamp en UTC estricto. |
| **ErrorResource** | Factorías estáticas | `of(title, status, detail, code, instance, invalid_params, type_uri) -> ErrorResource`, `from_domain_error(error, status_code, title, instance) -> ErrorResource`, `from_validation_error(invalid_params, instance, detail) -> ErrorResource` | Público | Instanciación tipada de errores. Erradica la filtración de trazas internas o datos sensibles de persistencia hacia clientes web. |
| **MessageResource** | Atributos y factoría | `str message`, `datetime timestamp`, `of(message: str) -> MessageResource` | Público | DTO inmutable Pydantic v2 para respuestas 200 OK de confirmación en comandos asíncronos o de estado sin retorno de entidad. |
| **PaginationParams** | Atributos y propiedades | `int page = 1`, `int size = 20`, `int offset {query}` | Público | Parámetros query validados para paginación. Restricciones: `page >= 1`, `1 <= size <= 100`. Propiedad `offset = (page - 1) * size`. |
| **PagedResource[T]** | Atributos y factoría | `list[T] items`, `int page`, `int size`, `int total_elements`, `int total_pages`, `bool has_next`, `bool has_previous`, `of(items, page, size, total_elements) -> PagedResource[T]` | Público | Contenedor inmutable genérico. Factoría calcula matemáticamente `total_pages = ceil(total_elements / size)` e indicadores de navegación `has_next`/`has_previous`. |
| **error_to_problem_details** | Función transformadora | `(error: DomainError, instance: str \| None = None) -> JSONResponse` | Público | Mapea semánticamente códigos de `DomainError` a estados HTTP (400, 401, 402, 403, 404, 409, 422, 429, 500) retornando cabecera `Content-Type: application/problem+json`. |
| **result_to_response** | Función transformadora | `[T, R, E: DomainError](result: Result[T, E], success_status: int = 200, resource_assembler: Callable[[T], R] \| None = None, instance: str \| None = None) -> Response` | Público | Desempaqueta funcionalmente mónadas `Result[T, E]`. Si `is_success`: retorna 204 si `value is None`, o serializa mediante assembler/Pydantic a 200/201. Si `is_failure`: delega a `error_to_problem_details`. |
| **paged_result_to_response** | Función transformadora | `[T, R, E: DomainError](result: Result[PagedResource[T], E], item_assembler: Callable[[T], R] \| None = None, instance: str \| None = None) -> Response` | Público | Desempaqueta `Result` que encapsula colecciones paginadas. Transforma individualmente cada elemento de `items` preservando la metadata paginada intacta. |
| **setup_global_exception_handlers** | Procedimiento de registro | `(app: FastAPI) -> None` | Público | Configura interceptores globales en FastAPI para `RequestValidationError` (422), `DomainError` (dinámico RFC 7807), `StarletteHTTPException` (404/405/415) y `Exception` (500 sanitizado con log de `correlation_id`). |
| **correlation_id_ctx** | Variable de contexto | `ContextVar[str]` | Público | Contexto asíncrono seguro (`contextvars`) para almacenar y propagar el token de trazabilidad distribuida entre corrutinas concurrentes de asyncio. |
| **CorrelationIdMiddleware** | Dispatch perimetral | `dispatch(request: Request, call_next: RequestResponseEndpoint) -> Response` | Público | Extrae `X-Correlation-Id` o genera UUIDv4. Inyecta en `correlation_id_ctx`, `request.state.correlation_id` y en cabecera HTTP `X-Correlation-Id` de respuesta. |
| **RequestLoggingMiddleware** | Dispatch perimetral | `dispatch(request: Request, call_next: RequestResponseEndpoint) -> Response` | Público | Mide latencia con `time.perf_counter()`. Inyecta `X-Response-Time: <ms>ms`. Emite log estructurado con método, ruta, código HTTP, latencia, IP y correlation ID. |
| **SecurityHeadersMiddleware** | Dispatch perimetral | `dispatch(request: Request, call_next: RequestResponseEndpoint) -> Response` | Público | Hardening OWASP: inyecta `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1 mode=block`, `Strict-Transport-Security: max-age=31536000` y `Referrer-Policy`. |
| **RateLimitMiddleware** | Atributos y dispatch | `Redis _redis`, `int _rate_limit`, `int _window_seconds`, `bool _fail_open`, `dispatch(...) -> Response` | Privado / Público | Control de tasa en Redis 7 (`navby:ratelimit:{client_id}:{endpoint}`). Pipeline atómico `INCR` + `TTL`. Emite HTTP 429 con `Retry-After` y cabeceras `X-RateLimit-*`. Modo Fail-Open tolerante a caídas de Redis. |

---

## 12. Especificación del Diagrama de Clases y Componentes en PlantUML (Interface Layer)

### 12.1 Código Fuente Canónico PlantUML (`class-diagram-shared-interfaces.puml`)

El código fuente PlantUML canónico que modela los componentes, esquemas inmutables, transformadores y middlewares perimetrales de la Capa de Interfaz del Shared Kernel se reproduce íntegramente a continuación y se encuentra versionado en `report/assets/diagram-sources/class-diagrams/class-diagram-shared-interfaces.puml`:

```plantuml
@startuml class-diagram-shared-interfaces
title <size:18>Diagrama de Componentes y Clases UML - Bounded Context Shared Kernel (Interface Layer)</size>\n<size:12>Paquete Canónico: app.shared.interfaces</size>

' Configuraciones visuales y de diseño profesional
skinparam classAttributeIconSize 0
skinparam monochrome false
skinparam shadowing false
skinparam roundcorner 6
skinparam linetype ortho
skinparam nodesep 28
skinparam ranksep 32
skinparam defaultFontName "Helvetica", "Arial", sans-serif
skinparam defaultFontSize 10
skinparam defaultFontColor #2C3E50
skinparam arrowColor #34495E
skinparam arrowThickness 1.2
skinparam packageBorderColor #7F8C8D
skinparam packageFontSize 11
skinparam packageFontStyle bold

' Estilos específicos por categoría táctica de interfaz
skinparam class {
    BackgroundColor #FFFFFF
    BorderColor #2C3E50
    HeaderBackgroundColor #EAEDED
}
skinparam class<<RESTResource>> {
    BackgroundColor #E8F8F5
    BorderColor #16A085
    HeaderBackgroundColor #A3E4D7
}
skinparam class<<Assembler>> {
    BackgroundColor #FEF9E7
    BorderColor #D68910
    HeaderBackgroundColor #FAD7A0
}
skinparam class<<ExceptionHandler>> {
    BackgroundColor #FDEDEC
    BorderColor #C0392B
    HeaderBackgroundColor #F5B7B1
}
skinparam class<<Middleware>> {
    BackgroundColor #EBF5FB
    BorderColor #2980B9
    HeaderBackgroundColor #AED6F1
}
skinparam class<<ExternalFramework>> {
    BackgroundColor #F2F4F4
    BorderColor #95A5A6
    HeaderBackgroundColor #BDC3C7
}
skinparam class<<Monad>> {
    BackgroundColor #EAECEE
    BorderColor #5D6D7E
    HeaderBackgroundColor #D5D8DC
}
skinparam class<<ApplicationError>> {
    BackgroundColor #FDEDEC
    BorderColor #C0392B
    HeaderBackgroundColor #F5B7B1
}
skinparam class<<DomainException>> {
    BackgroundColor #FDEDEC
    BorderColor #C0392B
    HeaderBackgroundColor #F5B7B1
}

' Evitar anidamiento automático por puntos en nombres de paquetes
set separator none

' ==============================================================================
' 1. TIER 1: RECURSOS REST Y ESQUEMAS PYDANTIC V2 INMUTABLES
' ==============================================================================
package "app.shared.interfaces.rest.resources" as resources #FDFEFE {

    class InvalidParam <<RESTResource>> {
        + name: str
        + reason: str
    }

    class ErrorResource <<RESTResource>> {
        + type: str
        + title: str
        + status: int
        + detail: str
        + instance: str | None
        + code: str
        + invalid_params: list<InvalidParam> | None
        + timestamp: datetime
        {static} + of(title: str, status: int, detail: str, code: str, ...): ErrorResource
        {static} + from_application_error(error: ApplicationError, status_code: int, ...): ErrorResource
        {static} + from_domain_exception(exc: DomainException, status_code: int, ...): ErrorResource
        {static} + from_validation_error(invalid_params: list<InvalidParam>, ...): ErrorResource
    }

    class MessageResource <<RESTResource>> {
        + message: str
        + timestamp: datetime
        {static} + of(message: str): MessageResource
    }

    class PaginationParams <<RESTResource>> {
        + page: int
        + size: int
        + offset: int {query}
    }

    class "PagedResource<T>" as PagedResource <<RESTResource>> {
        + items: list<T>
        + page: int
        + size: int
        + total_elements: int
        + total_pages: int
        + has_next: bool
        + has_previous: bool
        {static} + of(items: list<T>, page: int, size: int, total_elements: int): PagedResource<T>
    }

    ErrorResource o-- "0..*" InvalidParam : contiene detalles >

    ' Disposición en columnas balanceadas
    ErrorResource -[hidden]down-> InvalidParam
    PaginationParams -[hidden]down-> PagedResource

    ErrorResource -[hidden]right-> MessageResource
    MessageResource -[hidden]right-> PaginationParams
}

' ==============================================================================
' 2. TIER 2: TRANSFORMADORES, MANEJADORES DE EXCEPCIONES Y TIPOS BASE
' ==============================================================================
package "app.shared.interfaces.rest.transform" as transform #FDFEFE {

    class ErrorAssembler <<Assembler>> {
        {static} + error_to_problem_details(error: ApplicationError, instance: str | None): JSONResponse
        {static} + domain_exception_to_problem_details(exc: DomainException, instance: str | None): JSONResponse
    }

    class ResponseAssembler <<Assembler>> {
        {static} + result_to_response(result: Result<T, E>, success_status: int, ...): Response
        {static} + paged_result_to_response(result: Result<PagedResource<T>, E>, ...): Response
    }

    ErrorAssembler -[hidden]down-> ResponseAssembler
}

package "app.shared.interfaces.errors" as errors #FDFEFE {

    class GlobalExceptionHandler <<ExceptionHandler>> {
        {static} + setup_global_exception_handlers(app: FastAPI): void
        - validation_exception_handler(request: Request, exc: RequestValidationError): JSONResponse
        - domain_exception_handler(request: Request, exc: DomainException): JSONResponse
        - http_exception_handler(request: Request, exc: StarletteHTTPException): JSONResponse
        - unhandled_exception_handler(request: Request, exc: Exception): JSONResponse
    }

}

package "app.shared.application.result" as app_result #FDFEFE {
    class "Result<T, E>" as Result <<Monad>>
    class "ApplicationError" as ApplicationError <<ApplicationError>>
    Result -[hidden]down-> ApplicationError
}

package "app.shared.domain.exceptions" as domain_exceptions #FDFEFE {
    class "DomainException" as DomainException <<DomainException>>
}

resources -[hidden]down-> transform
transform -[hidden]right-> errors
errors -[hidden]right-> app_result
app_result -[hidden]right-> domain_exceptions

' ==============================================================================
' 3. TIER 3: MIDDLEWARES PERIMETRALES
' ==============================================================================
package "app.shared.interfaces.middleware" as middleware #FDFEFE {

    class CorrelationIdMiddleware <<Middleware>> {
        + HEADER_NAME: str = "X-Correlation-Id"
        + dispatch(request: Request, call_next: RequestResponseEndpoint): Response
    }

    class RequestLoggingMiddleware <<Middleware>> {
        + dispatch(request: Request, call_next: RequestResponseEndpoint): Response
    }

    class SecurityHeadersMiddleware <<Middleware>> {
        + dispatch(request: Request, call_next: RequestResponseEndpoint): Response
    }

    class RateLimitMiddleware <<Middleware>> {
        - _redis: Redis
        - _rate_limit: int
        - _window_seconds: int
        - _fail_open: bool
        + __init__(app: Any, redis_client: Redis, rate_limit_per_minute: int, ...): void
        - _resolve_client_id(request: Request): str
        - _normalize_endpoint(path: str): str
        + dispatch(request: Request, call_next: RequestResponseEndpoint): Response
    }

    ' Disposición en grilla 2x2
    CorrelationIdMiddleware -[hidden]down-> RequestLoggingMiddleware
    SecurityHeadersMiddleware -[hidden]down-> RateLimitMiddleware
    CorrelationIdMiddleware -[hidden]right-> SecurityHeadersMiddleware
}

transform -[hidden]down-> middleware

' ==============================================================================
' 4. TIER 4: ABSTRACCIONES EXTERNAS Y RUNTIME
' ==============================================================================
package "External / Runtime Abstractions" as runtime #F4F6F6 {
    class "BaseHTTPMiddleware" as BaseHTTPMiddleware <<ExternalFramework>>
    class "Request" as Request <<ExternalFramework>>
    class "Response" as Response <<ExternalFramework>>
    class "JSONResponse" as JSONResponse <<ExternalFramework>>
    class "FastAPI" as FastAPI <<ExternalFramework>>
    class "ContextVar<str>" as ContextVar <<ExternalFramework>>
    class "redis.asyncio.Redis" as Redis <<ExternalFramework>>

    BaseHTTPMiddleware -[hidden]down-> FastAPI
    Request -[hidden]down-> Response
    Response -[hidden]down-> JSONResponse
    ContextVar -[hidden]down-> Redis

    BaseHTTPMiddleware -[hidden]right-> Request
    Request -[hidden]right-> ContextVar
}

middleware -[hidden]down-> runtime

' ==============================================================================
' RELACIONES Y DEPENDENCIAS ESTRUCTURALES
' ==============================================================================
' Relaciones hacia esquemas de recursos (hacia arriba)
ErrorAssembler .up.> ErrorResource : instancia esquema RFC 7807 >
ResponseAssembler .up.> PagedResource : emite colecciones paginadas >
GlobalExceptionHandler .up.> ErrorResource : construye respuestas de error >
RateLimitMiddleware .up.> ErrorResource : construye HTTP 429 RFC 7807 >

' Relaciones internas de ensamble y delegación
ResponseAssembler -> ErrorAssembler : delega fallos >
GlobalExceptionHandler -> ErrorAssembler : reutiliza mapeo RFC 7807 >

' Dependencias de contratos de aplicación y dominio
ErrorAssembler ..> ApplicationError : traduce semántica a HTTP >
ErrorAssembler ..> DomainException : traduce invariante a HTTP >
ResponseAssembler ..> Result : desempaqueta estado funcional >
GlobalExceptionHandler ..> DomainException : intercepta en frontera >

' Herencia e integración con framework web (hacia abajo)
CorrelationIdMiddleware -down-|> BaseHTTPMiddleware
RequestLoggingMiddleware -down-|> BaseHTTPMiddleware
SecurityHeadersMiddleware -down-|> BaseHTTPMiddleware
RateLimitMiddleware -down-|> BaseHTTPMiddleware

CorrelationIdMiddleware -down-> ContextVar : almacena correlation_id >
RequestLoggingMiddleware -down-> ContextVar : consulta correlation_id >
GlobalExceptionHandler -down-> ContextVar : extrae correlation_id para logging >
RateLimitMiddleware -down-> Redis : evalúa contadores y TTLs >
GlobalExceptionHandler -down-> FastAPI : registra interceptores >

@enduml
```

### 12.2 Tabla de Trazabilidad de Estereotipos UML de la Capa de Interfaz

| Estereotipo UML | Semántica Arquitectónica | Color de Fondo | Color de Borde | Componentes Modelados en la Capa de Interfaz |
| :---: | :--- | :---: | :---: | :--- |
| <<RESTResource>> | Esquema Pydantic v2 inmutable para transporte HTTP perimetral | `#E8F8F5` | `#16A085` | `ErrorResource`, `InvalidParam`, `MessageResource`, `PaginationParams`, `PagedResource<T>` |
| <<Assembler>> | Transformador funcional de desacoplamiento entre Mónadas/Dominio y HTTP | `#FEF9E7` | `#D68910` | `error_to_problem_details`, `result_to_response`, `paged_result_to_response` |
| <<ExceptionHandler>> | Interceptor global centralizado de excepciones web hacia RFC 7807 | `#FDEDEC` | `#C0392B` | `setup_global_exception_handlers` (`RequestValidationError`, `DomainException`, `StarletteHTTPException`, `Exception`) |
| <<Middleware>> | Filtro perimetral asíncrono para trazabilidad, auditoría, hardening y cuotas | `#EBF5FB` | `#2980B9` | `CorrelationIdMiddleware`, `RequestLoggingMiddleware`, `SecurityHeadersMiddleware`, `RateLimitMiddleware` |
| <<ExternalFramework>> | Dependencia de framework Starlette, FastAPI, ContextVars o Redis | `#F2F4F4` | `#95A5A6` | `BaseHTTPMiddleware`, `FastAPI`, `Request`, `Response`, `JSONResponse`, `ContextVar`, `Redis` |
| <<Monad>> | Mónada funcional importada desde la Capa de Aplicación (`app.shared.application.result`) | `#EAECEE` | `#5D6D7E` | `Result<T, E>` |
| <<ApplicationError>> | Error semántico importado desde la Capa de Aplicación (`app.shared.application.result`) | `#FDEDEC` | `#C0392B` | `ApplicationError` |
| <<DomainException>> | Excepción de invariante importada desde la Capa de Dominio (`app.shared.domain.exceptions`) | `#FDEDEC` | `#C0392B` | `DomainException` |

---

## 13. Application Layer: Arquitectura de Orquestación, Aislamiento Hexagonal y Registro Semántico de Errores

### 13.1 Propósito, Principios Rectores y Aislamiento de Frameworks

La **Capa de Aplicación** (`app.shared.application`) del Bounded Context Shared Kernel constituye el núcleo orquestador del sistema (*Application Core*). Su propósito es coordinar la ejecución de los flujos de negocio transversales y específicos de Navby Platform, operando como puente desintermediado entre los adaptadores primarios de conducción (*Driving Adapters*, tales como controladores HTTP en `app.shared.interfaces`) y los modelos puros de dominio (*Domain Layer* en `app.shared.domain`).

En estricta observancia de los preceptos de **Clean Architecture**, **Hexagonal Architecture** y **Domain-Driven Design (DDD)** táctico, la Capa de Aplicación se rige por las siguientes restricciones fundamentales:

1. **Aislamiento Radical de Persistencia y Transporte:** Queda terminantemente prohibido importar librerías de persistencia relacional (SQLAlchemy ORM, Alembic, psycopg) o frameworks de transporte web (FastAPI, Starlette, Pydantic) dentro de cualquier módulo de `app.shared.application`. Toda comunicación con bases de datos o brokers externos se realiza exclusivamente mediante puertos abstractos (*Protocols*).
2. **Segregación CQRS-lite Asíncrona:** Toda operación del sistema se clasifica estrictamente como un **Comando** (intención de mutar estado transaccional, coordinar agregados y emitir eventos de dominio) o una **Consulta** (recuperación optimizada de proyecciones de lectura sin efectos secundarios).
3. **Flujo de Control Monádico (Railway-Oriented Programming):** Los manejadores de casos de uso no emplean excepciones de Python (`raise Exception`) para gobernar el flujo de negocio habitual o anticipado. Todas las operaciones retornan deterministamente instancias de `Result[R, ApplicationError]`.
4. **Resiliencia y Determinismo en Despacho:** Los comandos y consultas se despachan de forma unívoca 1-a-1 mediante mediadores en memoria (`CommandBus`, `QueryBus`). La publicación de eventos de dominio (`DomainEventPublisher`) soporta multi-suscripción 1-a-N con aislamiento de excepciones, garantizando que el fallo de un suscriptor secundario jamás aborte la transacción principal.

---

### 13.2 Registro Semántico de Errores de Aplicación: `ApplicationError`

Los errores que emergen durante la orquestación de casos de uso (tales como la ausencia de una entidad solicitada, colisiones de concurrencia, autorizaciones denegadas o restricciones perimetrales) se modelan mediante la clase inmutable `ApplicationError`.

Como lo prescribe `navby-tactical-ddd-guide.md` (§3.3), `ApplicationError` constituye una abstracción semántica independiente de las excepciones de dominio, interoperando de forma nativa con la mónada `Result[T, ApplicationError]` y facilitando su posterior transformación hacia respuestas RFC 7807 en la Capa de Interfaz.

```python
# app/shared/application/result/result.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ApplicationError:
    """
    Error semántico especializado para la Capa de Aplicación de Navby Platform.
    Representa fallos acontecidos durante la orquestación de casos de uso,
    tales como entidades inexistentes, colisiones de estado, credenciales inválidas,
    permisos insuficientes o transgresiones en validaciones perimetrales.
    """
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        object.__setattr__(self, "code", code)
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "details", details if details is not None else {})

    @classmethod
    def not_found(cls, resource: str, identifier: Any) -> ApplicationError:
        """
        Construye un error de entidad no encontrada.
        Indica que el recurso solicitado no existe en los repositorios de persistencia.
        """
        return cls(
            code="NOT_FOUND",
            message=f"{resource} con identificador '{identifier}' no fue encontrado.",
            details={"resource": resource, "identifier": str(identifier)},
        )

    @classmethod
    def conflict(cls, message: str, details: dict[str, Any] | None = None) -> ApplicationError:
        """
        Construye un error de colisión de estado o concurrencia.
        Indica violaciones de unicidad de negocio o conflictos de versión optimista.
        """
        return cls(code="CONFLICT", message=message, details=details)

    @classmethod
    def bad_request(cls, message: str, details: dict[str, Any] | None = None) -> ApplicationError:
        """
        Construye un error de petición mal formada o parámetros inconsistentes.
        Indica sintaxis incorrecta o violación de reglas de entrada en el caso de uso.
        """
        return cls(code="BAD_REQUEST", message=message, details=details)

    @classmethod
    def unauthorized(
        cls,
        message: str = "Credenciales inválidas o sesión no autenticada.",
        details: dict[str, Any] | None = None,
    ) -> ApplicationError:
        """
        Construye un error de autenticación ausente o inválida.
        Indica falta de identidad verificada para invocar el caso de uso.
        """
        return cls(code="UNAUTHORIZED", message=message, details=details)

    @classmethod
    def forbidden(
        cls,
        message: str = "Acceso denegado. No posee los permisos requeridos.",
        details: dict[str, Any] | None = None,
    ) -> ApplicationError:
        """
        Construye un error de autorización insuficiente.
        Indica que el usuario autenticado carece de roles o privilegios requeridos.
        """
        return cls(code="FORBIDDEN", message=message, details=details)

    @classmethod
    def unprocessable_entity(
        cls,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> ApplicationError:
        """
        Construye un error de entidad no procesable.
        Indica que la instrucción es sintácticamente válida pero transgrede invariantes de aplicación.
        """
        return cls(code="UNPROCESSABLE_ENTITY", message=message, details=details)

    @classmethod
    def internal_error(
        cls,
        message: str = "Error interno imprevisto al orquestar el caso de uso.",
        details: dict[str, Any] | None = None,
    ) -> ApplicationError:
        """
        Construye un error de fallo no recuperable de aplicación.
        Indica excepciones de infraestructura no controladas o fallos graves de sistema.
        """
        return cls(code="INTERNAL_SERVER_ERROR", message=message, details=details)
```

---

## 14. Modelos Canónicos de Paginación de Capa de Aplicación

### 14.1 Sentido de Ordenamiento (`SortDirection`) y Consulta Paginada (`PagedQuery`)

Las operaciones de lectura paginada requieren una parametrización homogénea y determinista que defina el número de página solicitada, el tamaño de lote, la clave de ordenamiento y el sentido vectorial de la consulta. La estructura `PagedQuery` provee una base inmutable con validación defensiva en `__post_init__`, calculando dinámicamente las cotas relacionales `offset` y `limit` consumidas por adaptadores SQL sin exponerlos al exterior.

```python
# app/shared/application/pagination/paged_query.py
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SortDirection(StrEnum):
    """
    Enumeración inmutable para definir el sentido de ordenamiento en consultas.
    Garantiza que únicamente se utilicen valores canónicos compatibles con SQL.
    """
    ASC = "ASC"
    DESC = "DESC"


@dataclass(frozen=True)
class PagedQuery:
    """
    Estructura inmutable base para la especificación de consultas de lectura paginada.
    Totalmente agnóstica de frameworks web (FastAPI/Starlette) y de ORMs (SQLAlchemy).
    Encapsula el número de página, el tamaño de lote, el atributo de ordenamiento y su sentido.
    """
    page: int = 1
    size: int = 20
    sort_by: str = "id"
    sort_direction: SortDirection = SortDirection.ASC

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError(f"El número de página debe ser mayor o igual a 1. Recibido: {self.page}")
        if self.size < 1 or self.size > 100:
            raise ValueError(
                f"El tamaño de página (size) debe situarse en el intervalo [1, 100]. Recibido: {self.size}"
            )

    @property
    def offset(self) -> int:
        """Calcula el desplazamiento numérico de registros para sentencias SQL relacionales."""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Retorna la cota máxima de elementos por consulta correspondiente al tamaño de página."""
        return self.size
```

---

### 14.2 Contenedor Paginado Genérico (`PagedResult[T]`) y Mapeo Monádico

La estructura genérica `PagedResult[T]` encapsula la colección resultante de elementos leídos y la totalidad de los metadatos cuantitativos calculados conforme al estándar de paginación de Navby Platform. Emplea internamente una `tuple[T, ...]` inmutable para salvaguardar la integridad de los datos en memoria y provee el operador funcional `map()` para transformar colecciones de agregados en DTOs o representaciones semánticas sin alterar la metadata paginada.

```python
# app/shared/application/pagination/paged_result.py
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Generic, Iterable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


@dataclass(frozen=True)
class PagedResult(Generic[T]):
    """
    Contenedor inmutable de resultados paginados de la Capa de Aplicación.
    Almacena los elementos proyectados en una tupla pura inmutable y encapsula
    los metadatos de paginación calculados conforme a la aritmética canónica.
    Provee una operación funcional .map() para transformar proyecciones.
    """
    items: tuple[T, ...]
    page: int
    size: int
    total_elements: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def of(
        cls,
        items: Iterable[T],
        page: int,
        size: int,
        total_elements: int,
    ) -> PagedResult[T]:
        """
        Factoría canónica para la construcción validada de un resultado paginado.
        Calcula rigurosamente el total de páginas mediante math.ceil y determina
        la existencia de páginas previa y posterior.
        """
        items_tuple: tuple[T, ...] = tuple(items)
        computed_total_pages: int = math.ceil(total_elements / size) if size > 0 else 0
        computed_has_next: bool = page < computed_total_pages
        computed_has_previous: bool = page > 1 and computed_total_pages > 0

        return cls(
            items=items_tuple,
            page=page,
            size=size,
            total_elements=total_elements,
            total_pages=computed_total_pages,
            has_next=computed_has_next,
            has_previous=computed_has_previous,
        )

    def map(self, transform: Callable[[T], R]) -> PagedResult[R]:
        """
        Aplica una función transformadora pura sobre cada elemento conservando
        inmutables e idénticos los metadatos de paginación originales.
        """
        transformed_items: tuple[R, ...] = tuple(transform(item) for item in self.items)
        return PagedResult[R](
            items=transformed_items,
            page=self.page,
            size=self.size,
            total_elements=self.total_elements,
            total_pages=self.total_pages,
            has_next=self.has_next,
            has_previous=self.has_previous,
        )
```

---

### 14.3 Desacoplamiento Arquitectónico con `PagedResource[T]` de Interfaces

Existe una frontera arquitectónica intencional entre la estructura de aplicación `PagedResult[T]` y el esquema de transporte `PagedResource[T]` (definido en `app.shared.interfaces.rest.resources.pagination_resource`):

| Criterio de Comparación | `PagedResult[T]` (Capa de Aplicación) | `PagedResource[T]` (Capa de Interfaz) |
| :--- | :--- | :--- |
| **Módulo Canónico** | `app.shared.application.pagination.paged_result` | `app.shared.interfaces.rest.resources.pagination_resource` |
| **Tecnología Base** | Python 3.12 estándar `@dataclass(frozen=True)` puro. | Pydantic v2 `BaseModel` con `ConfigDict(frozen=True)`. |
| **Estructura de Items** | `tuple[T, ...]` inmutable (previene mutaciones en memoria). | `list[T]` serializable hacia JSON por FastAPI. |
| **Propósito Arquitectónico** | Transporte agnóstico interno entre repositorios y use cases. | Esquema público OpenAPI/REST expuesto a clientes HTTP. |
| **Transformador Puente** | N/A (modelo fuente). | `paged_result_to_response(result, status_code=200)`. |

---

## 15. Contratos Base Transversales para CQRS (Handlers Asíncronos)

### 15.1 Filosofía CQRS-lite y Segregación de Responsabilidades

Navby Platform implementa **CQRS-lite** (*Command Query Responsibility Segregation* sin separación física de bases de datos, pero con bifurcación lógica y conceptual estricta):

1. **Comandos (`Command`):** Representan intenciones de alterar el estado persistido del sistema. Invocan invariantes en raíces de agregado (`AggregateRoot`), persisten cambios transaccionales a través de repositorios, acumulan y emiten eventos de dominio, y retornan deterministamente un `Result[R, ApplicationError]` (o `Result[None, ApplicationError]` en comandos de tipo void).
2. **Consultas (`Query`):** Representan peticiones de lectura pura de información. Bypasean las raíces de agregado cuando es conveniente para consultar proyecciones optimizadas o vistas desnormalizadas, garantizan cero efectos secundarios y retornan `Result[R, ApplicationError]`.
3. **Manejadores de Eventos (`DomainEventHandler`):** Consumidores reactivos que procesan eventos de dominio consumados (`DomainEvent`), orquestando efectos secundarios asíncronos (tales como invalidación de cachés en Redis, emisión de auditorías o encolamiento en el Transactional Outbox).

---

### 15.2 Protocolos para Comandos: `CommandHandler[C, R]` y `VoidCommandHandler[C]`

```python
# app/shared/application/handlers/command_handler.py
from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

from app.shared.application.result import ApplicationError, Result

C = TypeVar("C")
R = TypeVar("R")


@runtime_checkable
class CommandHandler(Protocol[C, R]):
    """
    Protocolo asíncrono para manejadores de comandos que producen una carga útil de retorno.
    Orquestan raíces de agregado, validan invariantes, coordinan repositorios y
    retornan deterministamente un Result[R, ApplicationError].
    """

    async def handle(self, command: C) -> Result[R, ApplicationError]:
        """Ejecuta la orquestación del comando de negocio de forma asíncrona."""
        raise NotImplementedError("Los manejadores de comando deben implementar handle().")


@runtime_checkable
class VoidCommandHandler(Protocol[C]):
    """
    Protocolo asíncrono para comandos que mutan estado sin producir valor de retorno de negocio.
    Retorna deterministamente un Result[None, ApplicationError] indicando éxito o transgresión.
    """

    async def handle(self, command: C) -> Result[None, ApplicationError]:
        """Ejecuta la orquestación del comando de negocio sin retorno de datos."""
        raise NotImplementedError("Los manejadores void de comando deben implementar handle().")
```

---

### 15.3 Protocolo para Consultas: `QueryHandler[Q, R]`

El protocolo de consulta define el contrato para operaciones idempotentes de lectura que retornan proyecciones tipadas.

```python
# app/shared/application/handlers/query_handler.py
from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

from app.shared.application.result import ApplicationError, Result

Q = TypeVar("Q")
R = TypeVar("R")


@runtime_checkable
class QueryHandler(Protocol[Q, R]):
    """
    Protocolo asíncrono para manejadores de consultas de lectura.
    Recuperan proyecciones optimizadas sin mutar estado ni disparar invariantes transaccionales,
    retornando deterministamente un Result[R, ApplicationError].
    """

    async def handle(self, query: Q) -> Result[R, ApplicationError]:
        """Ejecuta la consulta de lectura de datos de forma asíncrona."""
        raise NotImplementedError("Los manejadores de consulta deben implementar handle().")
```

---

### 15.4 Protocolo para Eventos de Dominio: `DomainEventHandler[E]`

```python
# app/shared/application/handlers/event_handler.py
from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

from app.shared.domain.model.aggregate_root import DomainEvent

E_contra = TypeVar("E_contra", bound=DomainEvent, contravariant=True)


@runtime_checkable
class DomainEventHandler(Protocol[E_contra]):
    """
    Protocolo asíncrono para consumidores y suscriptores de eventos de dominio en memoria.
    Reaccionan ante eventos de dominio consumados ejecutando efectos secundarios desacoplados
    (actualización de proyecciones, notificaciones o encolamiento en Outbox).
    """

    async def handle(self, event: E_contra) -> None:
        """Procesa el evento de dominio de forma asíncrona y no bloqueante."""
        raise NotImplementedError("Los manejadores de eventos deben implementar handle().")
```

---

## 16. Mediadores y Buses Asíncronos en Memoria

### 16.1 Jerarquía de Excepciones del Bus

Para salvaguardar la robustez del sistema y detectar fallos de configuración durante el arranque (*bootstrap*) del servidor, los buses de aplicación definen una jerarquía de excepciones perimetrales:

```python
# app/shared/application/bus/exceptions.py
from __future__ import annotations

from typing import Any


class BusError(Exception):
    """Excepción base para anomalías de enrutamiento o configuración en los buses de aplicación."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class HandlerNotFoundError(BusError):
    """Lanzada cuando un mensaje (comando o consulta) carece de un manejador registrado."""

    def __init__(self, message_type: type[Any]) -> None:
        super().__init__(f"No se encontró ningún manejador registrado para el tipo '{message_type.__name__}'.")
        self.message_type = message_type


class DuplicateHandlerRegistrationError(BusError):
    """Lanzada cuando se intenta registrar más de un manejador para un comando o consulta unívoco."""

    def __init__(self, message_type: type[Any]) -> None:
        super().__init__(
            f"El tipo de mensaje '{message_type.__name__}' ya posee un manejador registrado. "
            "CQRS-lite impone una correspondencia unívoca 1-a-1 para comandos y consultas."
        )
        self.message_type = message_type
```

---

### 16.2 Mediador de Comandos: `CommandBus` (Despacho Unívoco 1-a-1)

El `CommandBus` actúa como mediador asíncrono centralizado para mutaciones de negocio. Garantiza que exista exactamente un único manejador por cada tipo de comando y provee tipado estricto en tiempo de compilación y ejecución.

```python
# app/shared/application/bus/command_bus.py
from __future__ import annotations

from typing import Any

from app.shared.application.bus.exceptions import (
    DuplicateHandlerRegistrationError,
    HandlerNotFoundError,
)
from app.shared.application.handlers.command_handler import CommandHandler, VoidCommandHandler
from app.shared.domain.exceptions.domain_exceptions import DomainException
from app.shared.domain.model.monads.result import Result


class CommandBus:
    """
    Mediador asíncrono en memoria para el despacho determinista de comandos (CQRS-lite).
    Garantiza unívocamente una relación 1-a-1 entre el tipo de comando y su manejador.
    Rechaza registros duplicados y despachos hacia tipos no suscritos.
    """

    def __init__(self) -> None:
        self._handlers: dict[type[Any], CommandHandler[Any, Any] | VoidCommandHandler[Any]] = {}

    def register[C, R](
        self,
        command_type: type[C],
        handler: CommandHandler[C, R] | VoidCommandHandler[C],
    ) -> None:
        """
        Registra unívocamente un manejador para un tipo concreto de comando.
        Lanza DuplicateHandlerRegistrationError si ya existe un handler registrado.
        """
        if command_type in self._handlers:
            raise DuplicateHandlerRegistrationError(command_type)
        self._handlers[command_type] = handler

    async def dispatch[C, R](self, command: C) -> Result[R, DomainException]:
        """
        Despacha un comando hacia su manejador registrado de forma asíncrona.
        Lanza HandlerNotFoundError si el comando no ha sido configurado previamente.
        Retorna deterministamente el Result del manejador.
        """
        command_type = type(command)
        handler = self._handlers.get(command_type)
        if handler is None:
            raise HandlerNotFoundError(command_type)

        result: Result[R, DomainException] = await handler.handle(command)
        return result
```

---

### 16.3 Mediador de Consultas: `QueryBus` (Despacho Unívoco 1-a-1)

El `QueryBus` orquesta la ejecución desacoplada de consultas de lectura. Impone una correspondencia unívoca 1-a-1 y garantiza la recuperación asíncrona de proyecciones optimizadas.

```python
# app/shared/application/bus/query_bus.py
from __future__ import annotations

from typing import Any

from app.shared.application.bus.exceptions import (
    DuplicateHandlerRegistrationError,
    HandlerNotFoundError,
)
from app.shared.application.handlers.query_handler import QueryHandler
from app.shared.domain.exceptions.domain_exceptions import DomainException
from app.shared.domain.model.monads.result import Result


class QueryBus:
    """
    Mediador asíncrono en memoria para el despacho determinista de consultas de lectura.
    Impone una relación unívoca 1-a-1 entre el tipo de consulta y su manejador.
    Desacopla la invocación de lectura de la infraestructura subyacente.
    """

    def __init__(self) -> None:
        self._handlers: dict[type[Any], QueryHandler[Any, Any]] = {}

    def register[Q, R](
        self,
        query_type: type[Q],
        handler: QueryHandler[Q, R],
    ) -> None:
        """
        Registra unívocamente un manejador para un tipo concreto de consulta.
        Lanza DuplicateHandlerRegistrationError si ya existe un handler registrado.
        """
        if query_type in self._handlers:
            raise DuplicateHandlerRegistrationError(query_type)
        self._handlers[query_type] = handler

    async def ask[Q, R](self, query: Q) -> Result[R, DomainException]:
        """
        Despacha una consulta hacia su manejador registrado de forma asíncrona.
        Lanza HandlerNotFoundError si la consulta no posee un manejador asociado.
        Retorna deterministamente el Result de la proyección solicitada.
        """
        query_type = type(query)
        handler = self._handlers.get(query_type)
        if handler is None:
            raise HandlerNotFoundError(query_type)

        result: Result[R, DomainException] = await handler.handle(query)
        return result
```

---

### 16.4 Puerto de Emisión y Despachador en Memoria: `DomainEventPublisher` e `InMemoryEventBus` (Despacho 1-a-N)

A diferencia de los comandos y consultas, los eventos de dominio representan hechos que ya han ocurrido y pueden interesar a múltiples suscriptores simultáneos (relación 1-a-N). 

El puerto abstracto `DomainEventPublisher` define el contrato de emisión, mientras que `InMemoryEventBus` provee la implementación en memoria con **aislamiento de fallos por suscriptor**: si un suscriptor específico arroja una excepción, el error es registrado mediante logging estructurado pero no interrumpe la ejecución de los restantes suscriptores ni aborta el flujo transaccional que originó el evento.

```python
# app/shared/application/bus/event_bus.py
from __future__ import annotations

import logging
from typing import Any, Iterable, Protocol, runtime_checkable

from app.shared.application.handlers.event_handler import DomainEventHandler
from app.shared.domain.model.aggregate_root import DomainEvent

logger = logging.getLogger(__name__)


@runtime_checkable
class DomainEventPublisher(Protocol):
    """
    Puerto abstracto de aplicación para la emisión y despacho de eventos de dominio.
    Permite publicar eventos individuales o colecciones de eventos emitidos por agregados.
    """

    async def publish(self, event: DomainEvent) -> None:
        """Publica un evento de dominio individual hacia los suscriptores registrados."""
        raise NotImplementedError("Los publicadores de eventos deben implementar publish().")

    async def publish_all(self, events: Iterable[DomainEvent]) -> None:
        """Publica una secuencia de eventos de dominio en el orden temporal de ocurrencia."""
        raise NotImplementedError("Los publicadores de eventos deben implementar publish_all().")


class InMemoryEventBus(DomainEventPublisher):
    """
    Implementación en memoria del despachador de eventos de dominio (1-a-N).
    Soporta múltiples suscriptores por evento, despacho asíncrono no bloqueante
    y aislamiento de excepciones por suscriptor para impedir abortos en cascada.
    """

    def __init__(self) -> None:
        self._subscribers: dict[type[DomainEvent], list[DomainEventHandler[Any]]] = {}

    def subscribe[E: DomainEvent](
        self,
        event_type: type[E],
        handler: DomainEventHandler[E],
    ) -> None:
        """
        Suscribe un manejador al catálogo de suscriptores para un tipo específico de evento.
        Admite N suscriptores independientes para un mismo evento de dominio.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """
        Despacha un evento de dominio hacia todos los suscriptores registrados para su tipo.
        Ejecuta los manejadores de forma asíncrona y captura excepciones individuales
        evitando que la falla de un consumidor interrumpa el procesamiento de los demás.
        """
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])
        if not handlers:
            return

        for handler in handlers:
            try:
                await handler.handle(event)
            except Exception as exc:
                logger.error(
                    "Error al procesar el evento '%s' (ID: %s) en el suscriptor '%s': %s",
                    event.event_type,
                    str(event.event_id),
                    handler.__class__.__name__,
                    str(exc),
                    exc_info=True,
                )

    async def publish_all(self, events: Iterable[DomainEvent]) -> None:
        """
        Publica secuencialmente una colección de eventos de dominio preservando su orden.
        """
        for event in events:
            await self.publish(event)
```

---

### 16.5 Desacoplamiento y Puente con el Patrón Transactional Outbox

El `InMemoryEventBus` se diseña primordialmente para reacciones intra-proceso dentro del mismo Bounded Context (por ejemplo, refresco de una caché en Redis o actualización inmediata de un modelo de lectura local).

Cuando un evento de dominio debe viajar hacia otros Bounded Contexts a través de la red o requiere garantías de entrega inquebrantables (*at-least-once delivery*), un suscriptor especializado de la Capa de Infraestructura persiste el evento serializado (`event.to_dict()`) en la tabla relacional `outbox_events` (definida en `docs/backend-documentation/navby-database-schema.md`, líneas 165-174) dentro de la misma transacción ACID de PostgreSQL en la que se guarda el agregado. Un proceso en segundo plano (*Outbox Relay Worker*) desacola periódicamente los registros pendientes con `FOR UPDATE SKIP LOCKED` y los publica hacia RabbitMQ o Kafka, desacoplando totalmente la consistencia transaccional del transporte asíncrono.

---

## 17. Diccionario Estructural de la Capa de Aplicación (Tabla Estándar Atelier IAM)

A continuación se detalla la matriz exhaustiva de 5 columnas para la totalidad de clases, estructuras, atributos, métodos y reglas de negocio que componen la Capa de Aplicación del Shared Kernel:

| Clase o Estructura | Elemento | Firma o Tipo | Ámbito | Descripción, Relaciones y Reglas de Negocio |
| :---: | :---: | :--- | :---: | :--- |
| **ApplicationError** | Dataclass | `@dataclass(frozen=True) class ApplicationError` | Público | Error semántico inmutable de la Capa de Aplicación. Modela fallos tipados de casos de uso para integrarse con `Result[T, E]`. |
| ApplicationError | `code` | `str` | Público | Código semántico de máquina estandarizado (`NOT_FOUND`, `CONFLICT`, etc.). |
| ApplicationError | `message` | `str` | Público | Mensaje legible explicativo de la condición perimetral o error ocurrido. |
| ApplicationError | `details` | `dict[str, Any]` | Público | Metadatos y contexto estructurado adicional de la transgresión de aplicación. |
| ApplicationError | `__init__` | `(code: str, message: str, details: dict[str, Any] \| None = None) -> None` | Público | Constructor canónico con inmutabilidad estricta. |
| ApplicationError | `not_found` | `(resource: str, identifier: Any) -> ApplicationError` | Público | Factoría estática. Construye error con código `NOT_FOUND` y metadatos del recurso ausente. |
| ApplicationError | `conflict` | `(message: str, details: dict[str, Any] \| None = None) -> ApplicationError` | Público | Factoría estática. Construye error con código `CONFLICT` ante choques de concurrencia. |
| ApplicationError | `bad_request` | `(message: str, details: dict[str, Any] \| None = None) -> ApplicationError` | Público | Factoría estática. Construye error con código `BAD_REQUEST` ante parámetros inválidos. |
| ApplicationError | `unauthorized` | `(message: str = ..., details: dict[str, Any] \| None = None) -> ApplicationError` | Público | Factoría estática. Construye error con código `UNAUTHORIZED` ante sesiones ausentes. |
| ApplicationError | `forbidden` | `(message: str = ..., details: dict[str, Any] \| None = None) -> ApplicationError` | Público | Factoría estática. Construye error con código `FORBIDDEN` ante privilegios insuficientes. |
| ApplicationError | `unprocessable_entity` | `(message: str, details: dict[str, Any] \| None = None) -> ApplicationError` | Público | Factoría estática. Construye error con código `UNPROCESSABLE_ENTITY` ante transgresiones perimetrales. |
| ApplicationError | `internal_error` | `(message: str = ..., details: dict[str, Any] \| None = None) -> ApplicationError` | Público | Factoría estática. Construye error con código `INTERNAL_SERVER_ERROR` ante fallos críticos no recuperables. |
| **SortDirection** | Enumeración | `class SortDirection(StrEnum)` | Público | Catálogo inmutable de sentidos de ordenamiento para consultas relacionales. |
| SortDirection | `ASC` | `"ASC"` | Público | Valor escalar para ordenamiento ascendente en sentencias SQL. |
| SortDirection | `DESC` | `"DESC"` | Público | Valor escalar para ordenamiento descendente en sentencias SQL. |
| **PagedQuery** | Dataclass | `@dataclass(frozen=True) class PagedQuery` | Público | Parámetros canónicos inmutables de consulta paginada. Agnóstico a frameworks web. |
| PagedQuery | `page` | `int = 1` | Público | Número ordinal de página solicitada. Invariante: debe ser $\ge 1$. |
| PagedQuery | `size` | `int = 20` | Público | Cantidad de elementos por lote. Invariante: $1 \le \text{size} \le 100$. |
| PagedQuery | `sort_by` | `str = "id"` | Público | Nombre del campo o columna utilizado para el ordenamiento de los registros. |
| PagedQuery | `sort_direction` | `SortDirection = SortDirection.ASC` | Público | Sentido direccional del ordenamiento (`ASC` o `DESC`). |
| PagedQuery | `__post_init__` | `() -> None` | Privado | Valida las invariantes de rango en `page` y `size`. Lanza `ValueError` si son inválidas. |
| PagedQuery | `offset` | `property -> int` | Público | Propiedad calculada: `(page - 1) * size`. Desplazamiento numérico para SQL. |
| PagedQuery | `limit` | `property -> int` | Público | Propiedad calculada: retorna el tamaño `size` para delimitar cotas SQL. |
| **PagedResult[T]** | Dataclass Genérico | `@dataclass(frozen=True) class PagedResult(Generic[T])` | Público | Contenedor inmutable de elementos leídos y metadatos cuantitativos calculados. |
| PagedResult[T] | `items` | `tuple[T, ...]` | Público | Colección inmutable de elementos proyectados. Inmune a mutaciones en memoria. |
| PagedResult[T] | `page` | `int` | Público | Número de página actual correspondiente al lote de datos devuelto. |
| PagedResult[T] | `size` | `int` | Público | Tamaño de página o cota máxima configurada en la consulta. |
| PagedResult[T] | `total_elements` | `int` | Público | Cardinalidad total absoluta de elementos que cumplen con el filtro de lectura. |
| PagedResult[T] | `total_pages` | `int` | Público | Cantidad total de páginas calculadas mediante $\lceil \text{total\_elements} / \text{size} \rceil$. |
| PagedResult[T] | `has_next` | `bool` | Público | Booleano que indica si existe una página posterior disponible (`page < total_pages`). |
| PagedResult[T] | `has_previous` | `bool` | Público | Booleano que indica si existe una página previa disponible (`page > 1 and total_pages > 0`). |
| PagedResult[T] | `of` | `(items: Iterable[T], page: int, size: int, total_elements: int) -> PagedResult[T]` | Público | Factoría canónica. Ejecuta la matemática de paginación y construye la tupla inmutable. |
| PagedResult[T] | `map` | `(transform: Callable[[T], R]) -> PagedResult[R]` | Público | Operación funcional. Transforma cada elemento conservando intactos los metadatos de paginación. |
| **CommandHandler[C, R]** | Protocolo | `@runtime_checkable class CommandHandler(Protocol[C, R])` | Público | Contrato asíncrono para orquestadores de comandos con retorno de carga útil. |
| CommandHandler[C, R] | `handle` | `async (command: C) -> Result[R, ApplicationError]` | Público | Ejecuta la orquestación del comando retornando deterministamente un `Result`. |
| **VoidCommandHandler[C]** | Protocolo | `@runtime_checkable class VoidCommandHandler(Protocol[C])` | Público | Contrato asíncrono para comandos que mutan estado sin retorno de datos. |
| VoidCommandHandler[C] | `handle` | `async (command: C) -> Result[None, ApplicationError]` | Público | Ejecuta el comando de mutación retornando `Result[None, ApplicationError]`. |
| **QueryHandler[Q, R]** | Protocolo | `@runtime_checkable class QueryHandler(Protocol[Q, R])` | Público | Contrato asíncrono para consultas de lectura optimizada sin efectos secundarios. |
| QueryHandler[Q, R] | `handle` | `async (query: Q) -> Result[R, ApplicationError]` | Público | Ejecuta la consulta de lectura retornando deterministamente un `Result`. |
| **DomainEventHandler[E]** | Protocolo | `@runtime_checkable class DomainEventHandler(Protocol[E_contra])` | Público | Contrato asíncrono para suscriptores reactivos a eventos de dominio en memoria. |
| DomainEventHandler[E] | `handle` | `async (event: E_contra) -> None` | Público | Procesa el evento de dominio consumado ejecutando efectos secundarios aislados. |
| **CachePort** | Protocolo | `@runtime_checkable class CachePort(Protocol)` | Público | Puerto abstracto de la Capa de Aplicación (`app.shared.application.ports.cache`) para operaciones de caché distribuida. |
| CachePort | `get` | `async [T](key: str, namespace: str = "default") -> T \| None` | Público | Recupera un elemento tipado de la caché. Retorna `None` si la clave no existe o expiró. |
| CachePort | `set` | `async [T](key: str, value: T, ttl_seconds: int = 300, namespace: str = "default") -> bool` | Público | Persiste un elemento en caché con TTL obligatorio en segundos. Retorna `True` si fue exitoso. |
| CachePort | `delete` | `async (key: str, namespace: str = "default") -> bool` | Público | Elimina una clave del espacio de nombres en caché. Retorna `True` si fue removida. |
| CachePort | `exists` | `async (key: str, namespace: str = "default") -> bool` | Público | Comprueba si una clave específica se encuentra vigente en el espacio de nombres de caché. |
| **BusError** | Excepción | `class BusError(Exception)` | Público | Excepción base para fallos de registro o despacho en la infraestructura de mediación. |
| BusError | `message` | `str` | Público | Mensaje descriptivo de la anomalía de enrutamiento o configuración del bus. |
| BusError | `__init__` | `(message: str) -> None` | Público | Inicializa la excepción base del bus. |
| **HandlerNotFoundError** | Excepción | `class HandlerNotFoundError(BusError)` | Público | Lanzada cuando se despacha un comando o consulta sin manejador suscrito. |
| HandlerNotFoundError | `message_type` | `type[Any]` | Público | Tipo de dato de comando o consulta que carece de manejador registrado. |
| HandlerNotFoundError | `__init__` | `(message_type: type[Any]) -> None` | Público | Inicializa el error indicando el nombre de la clase de mensaje no encontrada. |
| **DuplicateHandlerRegistrationError** | Excepción | `class DuplicateHandlerRegistrationError(BusError)` | Público | Lanzada al registrar un segundo manejador para un comando o consulta unívoco. |
| DuplicateHandlerRegistrationError | `message_type` | `type[Any]` | Público | Tipo de mensaje sobre el cual se intentó violar la correspondencia 1-a-1. |
| DuplicateHandlerRegistrationError | `__init__` | `(message_type: type[Any]) -> None` | Público | Inicializa el error indicando el mensaje de transgresión de unicidad CQRS-lite. |
| **CommandBus** | Clase | `class CommandBus` | Público | Mediador asíncrono en memoria para despacho unívoco 1-a-1 de comandos. |
| CommandBus | `_handlers` | `dict[type[Any], CommandHandler[Any, Any] \| VoidCommandHandler[Any]]` | Privado | Diccionario interno que asocia cada tipo de comando con su único manejador. |
| CommandBus | `register` | `[C, R](command_type: type[C], handler: CommandHandler[C, R] \| VoidCommandHandler[C]) -> None` | Público | Registra el manejador para un comando. Lanza `DuplicateHandlerRegistrationError` si ya existe. |
| CommandBus | `dispatch` | `async [C, R](command: C) -> Result[R, ApplicationError]` | Público | Despacha asíncronamente el comando. Lanza `HandlerNotFoundError` si no está registrado. |
| **QueryBus** | Clase | `class QueryBus` | Público | Mediador asíncrono en memoria para despacho unívoco 1-a-1 de consultas. |
| QueryBus | `_handlers` | `dict[type[Any], QueryHandler[Any, Any]]` | Privado | Diccionario interno que asocia cada tipo de consulta con su único manejador. |
| QueryBus | `register` | `[Q, R](query_type: type[Q], handler: QueryHandler[Q, R]) -> None` | Público | Registra el manejador para una consulta. Lanza `DuplicateHandlerRegistrationError` si ya existe. |
| QueryBus | `ask` | `async [Q, R](query: Q) -> Result[R, ApplicationError]` | Público | Despacha asíncronamente la consulta. Lanza `HandlerNotFoundError` si no está registrada. |
| **DomainEventPublisher** | Protocolo | `@runtime_checkable class DomainEventPublisher(Protocol)` | Público | Puerto de aplicación para la publicación de eventos de dominio individuales o masivos. |
| DomainEventPublisher | `publish` | `async (event: DomainEvent) -> None` | Público | Publica un evento de dominio hacia los suscriptores registrados. |
| DomainEventPublisher | `publish_all` | `async (events: Iterable[DomainEvent]) -> None` | Público | Publica una secuencia temporal de eventos de dominio hacia los suscriptores. |
| **InMemoryEventBus** | Clase | `class InMemoryEventBus(DomainEventPublisher)` | Público | Despachador en memoria multi-suscriptor (1-a-N) con aislamiento de excepciones. |
| InMemoryEventBus | `_subscribers` | `dict[type[DomainEvent], list[DomainEventHandler[Any]]]` | Privado | Diccionario interno que mapea cada tipo de evento a su lista de manejadores. |
| InMemoryEventBus | `subscribe` | `[E: DomainEvent](event_type: type[E], handler: DomainEventHandler[E]) -> None` | Público | Suscribe un manejador al catálogo de un evento. Permite N suscriptores por evento. |
| InMemoryEventBus | `publish` | `async (event: DomainEvent) -> None` | Público | Despacha el evento a los suscriptores. Captura y loguea excepciones individuales. |
| InMemoryEventBus | `publish_all` | `async (events: Iterable[DomainEvent]) -> None` | Público | Publica iterativamente una colección de eventos respetando su orden de emisión. |

---

## 18. Diagrama de Clases UML de la Capa de Aplicación (Diagram-as-Code)

### 18.1 Código Fuente PlantUML (`class-diagram-shared-application.puml`)

A continuación se detalla el código fuente PlantUML canónico para el diagrama de clases y mediadores de la Capa de Aplicación, diseñado con ortogonalidad rigurosa, estereotipos coloreados y compatibilidad total con `make class-diagrams`:

```plantuml
@startuml class-diagram-shared-application
title <size:18>Diagrama de Componentes y Clases UML - Bounded Context Shared Kernel (Application Layer)</size>\n<size:12>Paquete Canónico: app.shared.application</size>

' Configuraciones visuales y de diseño profesional
skinparam classAttributeIconSize 0
skinparam monochrome false
skinparam shadowing false
skinparam roundcorner 6
skinparam linetype ortho
skinparam nodesep 28
skinparam ranksep 32
skinparam defaultFontName "Helvetica", "Arial", sans-serif
skinparam defaultFontSize 10
skinparam defaultFontColor #2C3E50
skinparam arrowColor #34495E
skinparam arrowThickness 1.2
skinparam packageBorderColor #7F8C8D
skinparam packageFontSize 11
skinparam packageFontStyle bold

' Estilos específicos por categoría táctica de aplicación
skinparam class {
    BackgroundColor #FFFFFF
    BorderColor #2C3E50
    HeaderBackgroundColor #EAEDED
}
skinparam class<<Monad>> {
    BackgroundColor #EAECEE
    BorderColor #5D6D7E
    HeaderBackgroundColor #D5D8DC
}
skinparam class<<ApplicationError>> {
    BackgroundColor #FDEDEC
    BorderColor #C0392B
    HeaderBackgroundColor #F5B7B1
}
skinparam class<<ApplicationPort>> {
    BackgroundColor #E8F8F5
    BorderColor #16A085
    HeaderBackgroundColor #A3E4D7
}
skinparam class<<PaginationModel>> {
    BackgroundColor #EAECEE
    BorderColor #5D6D7E
    HeaderBackgroundColor #D5D8DC
}
skinparam class<<CommandHandler>> {
    BackgroundColor #E8F8F5
    BorderColor #16A085
    HeaderBackgroundColor #A3E4D7
}
skinparam class<<QueryHandler>> {
    BackgroundColor #FEF9E7
    BorderColor #D68910
    HeaderBackgroundColor #FAD7A0
}
skinparam class<<EventHandler>> {
    BackgroundColor #F4ECF7
    BorderColor #8E44AD
    HeaderBackgroundColor #D7BDE2
}
skinparam class<<MessageBus>> {
    BackgroundColor #EBF5FB
    BorderColor #2980B9
    HeaderBackgroundColor #AED6F1
}
skinparam class<<DomainCore>> {
    BackgroundColor #FDFEFE
    BorderColor #7F8C8D
    HeaderBackgroundColor #EAEDED
}
skinparam enum {
    BackgroundColor #FCF3CF
    BorderColor #B7950B
    HeaderBackgroundColor #F9E79F
}

' Evitar anidamiento automático por puntos en nombres de paquetes
set separator none

' ==============================================================================
' 1. TIER 1: CONTROL DE FLUJO FUNCIONAL Y MODELOS DE PAGINACIÓN
' ==============================================================================
package "app.shared.application.result" as result_pkg #FDFEFE {

    enum ResultStatus <<Enum>> {
        SUCCESS
        FAILURE
    }

    class "Result<T, E>" as Result <<Monad>> {
        - _value: T | None
        - _error: E | None
        - _status: ResultStatus
        {static} + success(value: T): Result<T, Any>
        {static} + failure(error: E): Result<Any, E>
        + is_success: bool {query}
        + is_failure: bool {query}
        + value: T {query}
        + error: E {query}
        + value_or(default: T): T
        + map(fn: Callable[[T], U]): Result<U, E>
        + bind(fn: Callable[[T], Result<U, E>]): Result<U, E>
        + match(on_success: Callable[[T], R], on_failure: Callable[[E], R]): R
        + __repr__(): str
    }

    class ApplicationError <<ApplicationError>> {
        + code: str
        + message: str
        + details: dict<str, Any>
        + __init__(code: str, message: str, details: dict[str, Any] | None = None): void
        {static} + not_found(resource: str, identifier: Any): ApplicationError
        {static} + conflict(message: str, details: dict[str, Any] | None = None): ApplicationError
        {static} + bad_request(message: str, details: dict[str, Any] | None = None): ApplicationError
        {static} + unauthorized(message: str, details: dict[str, Any] | None = None): ApplicationError
        {static} + forbidden(message: str, details: dict[str, Any] | None = None): ApplicationError
        {static} + unprocessable_entity(message: str, details: dict[str, Any] | None = None): ApplicationError
        {static} + internal_error(message: str, details: dict[str, Any] | None = None): ApplicationError
    }

    Result --> ResultStatus : clasifica estado >
    Result o-- "0..1" ApplicationError : encapsula fallo >

    ResultStatus -[hidden]down-> Result
    Result -[hidden]down-> ApplicationError
}

package "app.shared.application.pagination" as pagination_pkg #FDFEFE {

    enum SortDirection <<PaginationModel>> {
        ASC
        DESC
    }

    class PagedQuery <<PaginationModel>> {
        + page: int
        + size: int
        + sort_by: str
        + sort_direction: SortDirection
        + __post_init__(): void
        + offset: int {query}
        + limit: int {query}
    }

    class "PagedResult<T>" as PagedResult <<PaginationModel>> {
        + items: tuple<T, ...>
        + page: int
        + size: int
        + total_elements: int
        + total_pages: int
        + has_next: bool
        + has_previous: bool
        {static} + of(items: Iterable<T>, page: int, size: int, total_elements: int): PagedResult<T>
        + map(transform: Callable[[T], R]): PagedResult<R>
    }

    PagedQuery --> SortDirection : especifica orientación >
    SortDirection -[hidden]down-> PagedQuery
    PagedQuery -[hidden]down-> PagedResult
}

result_pkg -[hidden]right-> pagination_pkg

' ==============================================================================
' 2. TIER 2: CONTRATOS CQRS-LITE Y PUERTOS DE APLICACIÓN
' ==============================================================================
package "app.shared.application.handlers" as handlers_pkg #FDFEFE {

    interface "CommandHandler<C, R>" as CommandHandler <<CommandHandler>> {
        + {abstract} handle(command: C): Result<R, ApplicationError>
    }

    interface "VoidCommandHandler<C>" as VoidCommandHandler <<CommandHandler>> {
        + {abstract} handle(command: C): Result<None, ApplicationError>
    }

    interface "QueryHandler<Q, R>" as QueryHandler <<QueryHandler>> {
        + {abstract} handle(query: Q): Result<R, ApplicationError>
    }

    interface "DomainEventHandler<E>" as DomainEventHandler <<EventHandler>> {
        + {abstract} handle(event: E): void
    }

    CommandHandler -[hidden]down-> VoidCommandHandler
    VoidCommandHandler -[hidden]down-> QueryHandler
    QueryHandler -[hidden]down-> DomainEventHandler
}

package "app.shared.application.ports.cache" as cache_ports_pkg #FDFEFE {

    interface CachePort <<ApplicationPort>> {
        + {abstract} get<T>(key: str, namespace: str): T | None
        + {abstract} set<T>(key: str, value: T, ttl_seconds: int, namespace: str): bool
        + {abstract} delete(key: str, namespace: str): bool
        + {abstract} exists(key: str, namespace: str): bool
    }

}

result_pkg -[hidden]down-> handlers_pkg
pagination_pkg -[hidden]down-> cache_ports_pkg
handlers_pkg -[hidden]right-> cache_ports_pkg

' ==============================================================================
' 3. TIER 3: MEDIADORES Y BUSES ASÍNCRONOS EN MEMORIA
' ==============================================================================
package "app.shared.application.bus" as bus_pkg #FDFEFE {

    class BusError <<MessageBus>> {
        + message: str
        + __init__(message: str): void
    }

    class HandlerNotFoundError <<MessageBus>> {
        + message_type: type
        + __init__(message_type: type): void
    }

    class DuplicateHandlerRegistrationError <<MessageBus>> {
        + message_type: type
        + __init__(message_type: type): void
    }

    HandlerNotFoundError --|> BusError
    DuplicateHandlerRegistrationError --|> BusError

    class CommandBus <<MessageBus>> {
        - _handlers: dict<type, CommandHandler | VoidCommandHandler>
        + __init__(): void
        + register(command_type: type<C>, handler: CommandHandler<C, R>): void
        + dispatch(command: C): Result<R, ApplicationError>
    }

    class QueryBus <<MessageBus>> {
        - _handlers: dict<type, QueryHandler>
        + __init__(): void
        + register(query_type: type<Q>, handler: QueryHandler<Q, R>): void
        + ask(query: Q): Result<R, ApplicationError>
    }

    interface DomainEventPublisher <<MessageBus>> {
        + {abstract} publish(event: DomainEvent): void
        + {abstract} publish_all(events: Iterable<DomainEvent>): void
    }

    class InMemoryEventBus <<MessageBus>> {
        - _subscribers: dict<type<DomainEvent>, list<DomainEventHandler>>
        + __init__(): void
        + subscribe(event_type: type<E>, handler: DomainEventHandler<E>): void
        + publish(event: DomainEvent): void
        + publish_all(events: Iterable<DomainEvent>): void
    }

    InMemoryEventBus ..|> DomainEventPublisher

    ' Columna 1: Jerarquía de Errores de Bus
    BusError -[hidden]down-> HandlerNotFoundError
    HandlerNotFoundError -[hidden]down-> DuplicateHandlerRegistrationError

    ' Columna 2: Buses CQRS
    CommandBus -[hidden]down-> QueryBus

    ' Columna 3: Event Bus
    DomainEventPublisher -[hidden]down-> InMemoryEventBus

    BusError -[hidden]right-> CommandBus
    CommandBus -[hidden]right-> DomainEventPublisher
}

handlers_pkg -[hidden]down-> bus_pkg

' ==============================================================================
' 4. TIER 4: CONEXIÓN CON TIPOS FUNDACIONALES DE LA CAPA DE DOMINIO
' ==============================================================================
package "app.shared.domain.model" as domain_layer #FDFEFE {
    class DomainEvent <<DomainCore>> {
        + event_id: UUID
        + occurred_on: datetime
        + aggregate_id: str
        + event_type: str
    }
}

bus_pkg -[hidden]down-> domain_layer

' ==============================================================================
' RELACIONES Y DEPENDENCIAS ESTRUCTURALES
' ==============================================================================
CommandHandler .up.> Result : retorna estado monádico >
CommandHandler .up.> ApplicationError : especifica error tipado >
VoidCommandHandler .up.> Result : retorna estado monádico >
QueryHandler .up.> Result : retorna estado monádico >

CommandBus -up-> CommandHandler : despacha comando 1-a-1 >
CommandBus -up-> VoidCommandHandler : despacha comando 1-a-1 >
QueryBus -up-> QueryHandler : despacha consulta 1-a-1 >

CommandBus ..> HandlerNotFoundError : lanza si no existe handler >
CommandBus ..> DuplicateHandlerRegistrationError : lanza ante registro repetido >
QueryBus ..> HandlerNotFoundError : lanza si no existe handler >
QueryBus ..> DuplicateHandlerRegistrationError : lanza ante registro repetido >

InMemoryEventBus -up-> DomainEventHandler : despacha evento 1-a-N >
InMemoryEventBus -down-> DomainEvent : distribuye a suscriptores >
DomainEventHandler -down-> DomainEvent : procesa suceso consumado >
DomainEventPublisher -down-> DomainEvent : contrato de publicación >

@enduml
```

---

### 18.2 Tabla de Trazabilidad de Estereotipos UML de la Capa de Aplicación

| Estereotipo UML | Semántica Arquitectónica | Color de Fondo | Color de Borde | Componentes Modelados en la Capa de Aplicación |
| :---: | :--- | :---: | :---: | :--- |
| <<ApplicationError>> | Error semántico inmutable de caso de uso para control de flujo | `#FDEDEC` | `#C0392B` | `ApplicationError` |
| <<Monad>> | Mónada funcional inmutable de control de flujo para estados de éxito y fallo | `#EAECEE` | `#5D6D7E` | `Result<T, E>` |
| <<ApplicationPort>> | Protocolos e interfaces abstractas de aplicación para puertos conducidos | `#E8F8F5` | `#16A085` | `CachePort` |
| <<PaginationModel>> | Modelo inmutable agnóstico de infraestructura para paginación relacional | `#EAECEE` | `#5D6D7E` | `SortDirection`, `PagedQuery`, `PagedResult<T>` |
| <<CommandHandler>> | Protocolo asíncrono para mutaciones de negocio con o sin retorno | `#E8F8F5` | `#16A085` | `CommandHandler<C, R>`, `VoidCommandHandler<C>` |
| <<QueryHandler>> | Protocolo asíncrono para consultas optimizadas de lectura | `#FEF9E7` | `#D68910` | `QueryHandler<Q, R>` |
| <<EventHandler>> | Protocolo asíncrono para consumidores reactivos de eventos de dominio | `#F4ECF7` | `#8E44AD` | `DomainEventHandler<E>` |
| <<MessageBus>> | Mediadores, puertos y despachadores asíncronos en memoria | `#EBF5FB` | `#2980B9` | `BusError`, `HandlerNotFoundError`, `DuplicateHandlerRegistrationError`, `CommandBus`, `QueryBus`, `DomainEventPublisher`, `InMemoryEventBus` |
| <<DomainCore>> | Primitivas y eventos inmutables importados desde la Capa de Dominio | `#FDFEFE` | `#7F8C8D` | `DomainEvent` |
| <<Enum>> | Enumeraciones tipadas de aplicación | `#FCF3CF` | `#B7950B` | `ResultStatus` |

---

## 19. Infrastructure Layer: Persistencia Relacional Asíncrona con SQLAlchemy 2.0 y Metadatos Declarativos

### 19.1 Principios Rectores, Desacoplamiento Hexagonal y Aislamiento de Persistencia

En estricta observancia de los Mandamientos 1 y 4 de Tactical DDD de Navby Platform y los postulados de **Clean Architecture**, la Capa de Infraestructura (`app.shared.infrastructure`) asume el rol de proveedor de **Adaptadores Conducidos (Driven Adapters)** para los puertos de persistencia y servicios perimetrales.

La separación de responsabilidades se rige por las siguientes garantías arquitectónicas:
1. **Pureza de Dominio Preservada:** Los agregados de negocio (`app.shared.domain.model.aggregate_root.AbstractDomainAggregateRoot`) y sus entidades hijas no contienen decoradores de SQLAlchemy (`@mapped_column`), metadatos de tablas relacionales ni referencias a sesiones asíncronas. El dominio desconoce completamente si el sustrato físico es PostgreSQL, memoria o almacenamiento columnar.
2. **Entidades ORM Dedicadas:** La persistencia se ejecuta mediante modelos ORM específicos que heredan de `Base` y `AuditablePersistenceMixin`. Cada Bounded Context traduce bidireccionalmente entre sus agregados puros y sus entidades ORM de persistencia.
3. **Asincronía Nativa con `asyncpg`:** Todas las operaciones de E/S relacionales se ejecutan mediante el driver asíncrono nativo `asyncpg` y la extensión `sqlalchemy.ext.asyncio`, evitando bloqueos del bucle de eventos (`event loop`) de Python y maximizando la concurrencia bajo cargas I/O masivas.
4. **Determinismo Temporal en UTC:** Queda estrictamente erradicado el almacenamiento de marcas temporales sin zona horaria (`TIMESTAMP WITHOUT TIME ZONE`). Todo atributo temporal se almacena como `TIMESTAMPTZ` (`DateTime(timezone=True)`) con valores por defecto asignados por el reloj autoritativo del motor de base de datos (`server_default=func.now()`).

---

### 19.2 Mixin Canónico de Auditoría Temporal: `AuditablePersistenceMixin`

El mixin `AuditablePersistenceMixin` provee las columnas canónicas de auditoría temporal `created_at` y `updated_at` requeridas por el esquema de base de datos (`docs/backend-documentation/navby-database-schema.md`).

```python
# app/shared/infrastructure/db/audit_mixin.py
from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class AuditablePersistenceMixin:
    """
    Mixin de persistencia relacional para auditoría temporal estándar.
    Provee marcas temporales 'created_at' y 'updated_at' sincronizadas
    estrictamente en UTC mediante TIMESTAMPTZ y funciones del servidor PostgreSQL.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        sort_order=998,
        doc="Marca temporal de inserción del registro físico en UTC (inmutable).",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        sort_order=999,
        doc="Marca temporal de la última actualización física en UTC.",
    )

    def created_at_iso(self) -> str:
        """
        Retorna la marca temporal de creación formateada bajo la norma ISO 8601 en UTC.
        Garantiza representación unificada en APIs y contratos de mensajería.
        """
        dt = self.created_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()

    def updated_at_iso(self) -> str:
        """
        Retorna la marca temporal de actualización formateada bajo la norma ISO 8601 en UTC.
        Garantiza representación unificada en APIs y contratos de mensajería.
        """
        dt = self.updated_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
```

#### Fundamentación Matemática y de Integridad Temporal
El uso explícito de `DateTime(timezone=True)` junto a `server_default=func.now()` resuelve cuatro fallas estructurales clásicas en sistemas distribuidos:
1. **Inmunidad ante Horario de Verano (Daylight Saving Time - DST):** Al operar exclusivamente en UTC, se evitan saltos de hora que producen deltas temporales negativos o duplicidad horaria en métricas de latencia.
2. **Independencia del Reloj de la Aplicación:** Los contenedores de backend pueden presentar desincronizaciones de microsegundos mediante *clock drift*. La asignación mediante `func.now()` centraliza la autoridad temporal en el servidor PostgreSQL sincronizado vía NTP.
3. **Inmutabilidad de `created_at`:** La columna no define `onupdate`, impidiendo que mutaciones de negocio alteren la trazabilidad histórica original de la entidad.

---

### 19.3 Base Declarativa Unificada y Convención Estricta de Restricciones: `Base` y `MetaData`

Para garantizar la estabilidad de las migraciones autogeneradas con Alembic (`alembic revision --autogenerate`) y prevenir nombres anónimos de índices o restricciones dependientes de la versión del gestor, se establece la convención canónica `POSTGRES_NAMING_CONVENTION`.

```python
# app/shared/infrastructure/db/base.py
from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

# Convención de nombrado estricta de restricciones e índices relacionales
POSTGRES_NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(AsyncAttrs, DeclarativeBase):
    """
    Clase base declarativa unificada para todos los modelos ORM de persistencia de Navby Platform.
    Hereda de AsyncAttrs para permitir carga diferida asíncrona segura (await obj.awaitable_attrs.relacion)
    e incorpora un objeto MetaData con la convención canónica de nombrado de restricciones relacionales.
    """
    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)
```

#### Ventajas Arquitectónicas de la Convención de Nombres
- **Determinismo en Migraciones Alembic:** PostgreSQL no asigna identificadores aleatorios como `table_column_key` a las restricciones únicas o llaves foráneas; cada objeto posee una firma reproducible en entornos de testing, homologación y producción.
- **Operaciones de Alteración DDL Libres de Bloqueos:** Facilita la creación de scripts de migración `DROP CONSTRAINT` y `ALTER TABLE` seguros sin requerir inspecciones dinámicas de los catálogos del sistema (`pg_constraint`).

---

## 20. Gestión Transaccional y Ciclo de Vida de Conexiones (`DatabaseSessionManager`)

### 20.1 Arquitectura del Pool Asíncrono con PostgreSQL 16 y `asyncpg`

El acceso a PostgreSQL 16 se centraliza mediante `DatabaseSessionManager`. A diferencia de arquitecturas síncronas que abren hilos dedicados por conexión, el motor asíncrono gestiona las conexiones dentro del bucle de eventos mediante un pool de tamaño controlado, dimensionado específicamente para cargas asíncronas concurrentes:
- **`pool_size = 20`:** Conexiones TCP permanentes de reserva listas para ser utilizadas instantáneamente.
- **`max_overflow = 10`:** Conexiones adicionales que el pool puede aprovisionar ante picos de demanda.
- **`pool_timeout = 30.0`:** Tiempo máximo de espera en segundos antes de arrojar `TimeoutError` si el pool se satura.
- **`pool_recycle = 1800`:** Reciclaje obligatorio de conexiones tras 30 minutos de actividad, eliminando fugas de memoria en proxies intermedios o firewalls estatales.
- **`pool_pre_ping = True`:** Emisión de un sondeo ligero `SELECT 1` antes de entregar una conexión al caso de uso, descartando conexiones muertas por caídas de red o reinicios de base de datos sin generar excepciones 500 al cliente.

---

### 20.2 Implementación Canónica de `DatabaseSessionManager`

```python
# app/shared/infrastructure/db/session_manager.py
from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger("navby.shared.infrastructure.db")


class DatabaseSessionManager:
    """
    Gestor centralizado del ciclo de vida del AsyncEngine y async_sessionmaker de SQLAlchemy 2.0.
    Administra el pool de conexiones asíncronas con asyncpg para PostgreSQL 16, garantizando
    adquisición segura de sesiones, manejo transaccional ACID con rollback determinista y
    prevención de conexiones zombi mediante comprobaciones de salud 'pre-ping'.
    """

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    def init(
        self,
        db_url: str,
        echo: bool = False,
        pool_size: int = 20,
        max_overflow: int = 10,
        pool_timeout: float = 30.0,
        pool_recycle: int = 1800,
    ) -> None:
        """
        Inicializa el motor asíncrono y la fábrica de sesiones.
        Configura el pool optimizado para cargas concurrentes de producción.
        """
        if self._engine is not None:
            logger.warning("DatabaseSessionManager ya se encuentra inicializado. Reutilizando engine existente.")
            return

        self._engine = create_async_engine(
            db_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
        )

        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
        )
        logger.info(
            "DatabaseSessionManager inicializado exitosamente (pool_size=%d, max_overflow=%d).",
            pool_size,
            max_overflow,
        )

    async def close(self) -> None:
        """
        Cierra limpiamente el pool de conexiones y libera los descriptores de socket subyacentes.
        """
        if self._engine is None:
            logger.warning("DatabaseSessionManager no estaba inicializado al invocar close().")
            return

        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None
        logger.info("DatabaseSessionManager cerrado y conexiones liberadas.")

    def is_initialized(self) -> bool:
        """Indica si el gestor cuenta con un motor y fábrica de sesiones activos."""
        return self._engine is not None and self._sessionmaker is not None

    @property
    def engine(self) -> AsyncEngine:
        """
        Retorna la instancia del AsyncEngine activo o lanza RuntimeError si no ha sido inicializado.
        """
        if self._engine is None:
            raise RuntimeError(
                "DatabaseSessionManager no está inicializado. Ejecute init() antes de acceder al motor."
            )
        return self._engine

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provee una sesión asíncrona aislada para consultas o comandos con control manual.
        Garantiza el cierre determinista de la sesión al abandonar el bloque de contexto.
        """
        if self._sessionmaker is None:
            raise RuntimeError(
                "DatabaseSessionManager no está inicializado. Ejecute init() antes de solicitar sesiones."
            )

        session: AsyncSession = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager asíncrono para transacciones ACID atómicas.
        Inicia una transacción explícita sobre la sesión; si la corrutina finaliza con éxito
        ejecuta commit() de forma determinista. Si se lanza cualquier excepción no controlada,
        ejecuta rollback() inmediato y propaga el error.
        """
        if self._sessionmaker is None:
            raise RuntimeError(
                "DatabaseSessionManager no está inicializado. Ejecute init() antes de solicitar transacciones."
            )

        session: AsyncSession = self._sessionmaker()
        try:
            async with session.begin():
                yield session
        except Exception:
            raise
        finally:
            await session.close()


# Instancia singleton del gestor para inyección en el ciclo de vida de FastAPI
db_session_manager = DatabaseSessionManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Generador de sesión asíncrona compatible con FastAPI Depends().
    Apropiado para casos de uso de solo lectura (CQRS Queries).
    """
    async with db_session_manager.session() as session:
        yield session


async def get_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """
    Generador de transacción asíncrona compatible con FastAPI Depends().
    Apropiado para casos de uso de mutación de estado (CQRS Commands) con garantía ACID atómica.
    """
    async with db_session_manager.transaction() as session:
        yield session
```

---

## 21. Persistencia Garantizada y Consistencia Eventual: Patrón Transactional Outbox

### 21.1 Fundamentos Arquitectónicos del Patrón Outbox (*At-Least-Once Delivery*)

En la arquitectura de Navby Platform, la publicación de eventos inter-contexto no puede supeditarse a una llamada directa e inmediata a un broker de mensajería (RabbitMQ, Kafka) durante la ejecución del caso de uso. Si la mutación del agregado se confirma en PostgreSQL pero la red falla antes de alcanzar el broker, el resto del sistema nunca se enterará del cambio. Por el contrario, si se publica al broker primero y luego la base de datos falla al persistir, se emitirían eventos espurios de cambios inexistentes.

La solución canónica consiste en aplicar el patrón **Transactional Outbox**:
1. El caso de uso persiste los cambios del agregado y registra el evento de dominio en la tabla relacional `outbox_events` dentro de la **misma e idéntica transacción ACID relacional de PostgreSQL**.
2. Un proceso relay en segundo plano (*Outbox Relay Worker*) desacola periódicamente los eventos con estado `PENDING` utilizando `SELECT ... FOR UPDATE SKIP LOCKED` y los transmite al broker.
3. Al recibir la confirmación de recepción (*ACK*) del broker, el worker actualiza el registro en `outbox_events` a `PUBLISHED`. Si ocurren fallos transitorios, incrementa `retry_count` y actualiza `last_error`.

---

### 21.2 Estados del Outbox y Modelo Relacional `OutboxEventModel`

```python
# app/shared/infrastructure/outbox/models.py
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
import uuid

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Identity,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.db.audit_mixin import AuditablePersistenceMixin
from app.shared.infrastructure.db.base import Base


class OutboxStatus(StrEnum):
    """
    Catálogo de estados de procesamiento del evento dentro del pipeline Outbox.
    """
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class OutboxEventModel(Base, AuditablePersistenceMixin):
    """
    Modelo ORM de persistencia física para la tabla relacional 'outbox_events'.
    Almacena eventos de dominio generados por agregados dentro de la misma transacción ACID
    en la que se guardan los cambios de estado, garantizando consistencia eventual at-least-once.
    """
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
        doc="Identificador numérico secuencial de 64 bits para inserción monótona y ordenamiento.",
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        doc="Identificador universal del evento para deduplicación estricta e idempotencia.",
    )
    aggregate_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="Nombre formal del agregado emisor (ej. Itinerary, CreditWallet).",
    )
    aggregate_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="Identificador del agregado emisor representado como cadena.",
    )
    event_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        doc="Nombre de la clase del evento de dominio (ej. ItineraryCreatedEvent).",
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        doc="Cuerpo del evento serializado en formato JSON determinista.",
    )
    occurred_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Marca temporal en UTC en la que ocurrió el suceso dentro del agregado.",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=OutboxStatus.PENDING.value,
        server_default=text("'PENDING'"),
        doc="Estado actual del evento (PENDING, PUBLISHED, FAILED).",
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        doc="Número de intentos de publicación fallidos ejecutados por el worker.",
    )
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
        doc="Mensaje de error y traza registrada en el último intento de despacho.",
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        doc="Marca temporal en UTC en la que el evento fue despachado exitosamente.",
    )

    __table_args__ = (
        Index(
            "ix_outbox_events_status_occurred_on",
            "status",
            "occurred_on",
            postgresql_using="btree",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'PUBLISHED', 'FAILED')",
            name="chk_outbox_events_status",
        ),
        CheckConstraint(
            "retry_count >= 0",
            name="chk_outbox_events_retry_count",
        ),
    )
```

---

### 21.3 Repositorio Relacional: `SqlAlchemyOutboxRepository`

El repositorio encapsula las sentencias SQL de persistencia y sondeo con `FOR UPDATE SKIP LOCKED`. Esta cláusula de PostgreSQL 16 permite que múltiples réplicas del worker relay descolen lotes simultáneamente: si una fila ya está bloqueada por un hilo, los demás trabajadores la omiten de inmediato sin detenerse ni producir deadlocks.

```python
# app/shared/infrastructure/outbox/repository.py
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
import logging
from typing import Any

from sqlalchemy import case, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.model.aggregate_root import DomainEvent
from app.shared.infrastructure.outbox.models import OutboxEventModel, OutboxStatus

logger = logging.getLogger("navby.shared.infrastructure.outbox")


class SqlAlchemyOutboxRepository:
    """
    Repositorio relacional asíncrono para la persistencia, sondeo concurrente seguro y
    actualización de estado de eventos en la tabla 'outbox_events'.
    Implementa concurrencia libre de bloqueos mutuos mediante SELECT ... FOR UPDATE SKIP LOCKED.
    """

    async def save(self, session: AsyncSession, event: DomainEvent) -> OutboxEventModel:
        """
        Persiste un evento de dominio en la tabla 'outbox_events' dentro de la sesión
        transaccional activa de SQLAlchemy.
        Serializa el evento invocando su método canónico to_dict().
        """
        raw_dict = event.to_dict()
        record = OutboxEventModel(
            event_id=event.event_id,
            aggregate_type=raw_dict.get("aggregate_type", event.__class__.__module__.split(".")[-2].title()),
            aggregate_id=event.aggregate_id if event.aggregate_id else str(raw_dict.get("aggregate_id", "")),
            event_type=event.event_type if event.event_type else event.__class__.__name__,
            payload=raw_dict,
            occurred_on=event.occurred_on,
            status=OutboxStatus.PENDING.value,
            retry_count=0,
            last_error=None,
            processed_at=None,
        )
        session.add(record)
        logger.debug(
            "Evento de dominio registrado en outbox (ID: %s, Tipo: %s, Agregado: %s).",
            str(record.event_id),
            record.event_type,
            record.aggregate_id,
        )
        return record

    async def fetch_pending_events(
        self,
        session: AsyncSession,
        batch_size: int = 50,
    ) -> Sequence[OutboxEventModel]:
        """
        Recupera un lote de eventos en estado 'PENDING' ordenados cronológicamente por occurred_on.
        Aplica 'FOR UPDATE SKIP LOCKED' para garantizar que procesos concurrentes no bloqueen
        las mismas filas ni colisionen entre réplicas del worker relay.
        """
        stmt = (
            select(OutboxEventModel)
            .where(OutboxEventModel.status == OutboxStatus.PENDING.value)
            .order_by(OutboxEventModel.occurred_on.asc())
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(stmt)
        records = result.scalars().all()
        logger.debug("Recuperados %d eventos pendientes de outbox con SKIP LOCKED.", len(records))
        return records

    async def mark_as_published(self, session: AsyncSession, event_id: int) -> None:
        """
        Actualiza el estado de un evento a 'PUBLISHED' y registra la marca temporal
        de procesamiento exitoso en UTC.
        """
        now = datetime.now(timezone.utc)
        stmt = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(
                status=OutboxStatus.PUBLISHED.value,
                processed_at=now,
                last_error=None,
            )
        )
        await session.execute(stmt)
        logger.debug("Evento de outbox ID %d marcado como PUBLISHED a las %s.", event_id, now.isoformat())

    async def mark_as_failed(
        self,
        session: AsyncSession,
        event_id: int,
        error_message: str,
        max_retries: int = 5,
    ) -> None:
        """
        Registra un intento fallido de publicación. Incrementa retry_count y almacena last_error.
        Si el conteo de reintentos alcanza o excede max_retries, transmuta el estado a 'FAILED'.
        """
        stmt = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(
                retry_count=OutboxEventModel.retry_count + 1,
                last_error=error_message[:2000],
                status=case(
                    (OutboxEventModel.retry_count + 1 >= max_retries, OutboxStatus.FAILED.value),
                    else_=OutboxStatus.PENDING.value,
                ),
            )
        )
        await session.execute(stmt)
        logger.warning("Evento de outbox ID %d actualizado con fallo de envío: %s", event_id, error_message[:200])
```

---

### 21.4 Adaptador de Publicación de Eventos: `OutboxDomainEventPublisherAdapter`

Este adaptador realiza el puerto `DomainEventPublisher` de `app.shared.application.bus.event_bus`. Al inyectarse en los casos de uso con la `AsyncSession` activa, desvía la emisión hacia la tabla `outbox_events`.

```python
# app/shared/infrastructure/outbox/publisher_adapter.py
from __future__ import annotations

from collections.abc import Iterable
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.application.bus.event_bus import DomainEventPublisher
from app.shared.domain.model.aggregate_root import DomainEvent
from app.shared.infrastructure.outbox.repository import SqlAlchemyOutboxRepository

logger = logging.getLogger("navby.shared.infrastructure.outbox")


class OutboxDomainEventPublisherAdapter(DomainEventPublisher):
    """
    Adaptador de infraestructura que realiza el puerto DomainEventPublisher de la Capa de Aplicación.
    Persiste atómicamente los eventos de dominio en la tabla relacional 'outbox_events'
    utilizando la sesión transaccional activa provista en su construcción, garantizando
    que ningún evento sea publicado si la transacción de negocio hace rollback.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: SqlAlchemyOutboxRepository | None = None,
    ) -> None:
        self._session = session
        self._repository = repository or SqlAlchemyOutboxRepository()

    async def publish(self, event: DomainEvent) -> None:
        """
        Persiste un evento de dominio individual en la tabla outbox dentro de la transacción activa.
        """
        await self._repository.save(self._session, event)
        logger.debug("Evento '%s' encolado en outbox para agregado '%s'.", event.event_type, event.aggregate_id)

    async def publish_all(self, events: Iterable[DomainEvent]) -> None:
        """
        Persiste secuencialmente una colección de eventos de dominio en la tabla outbox.
        """
        for event in events:
            await self.publish(event)
```

---

## 22. Conectividad Asíncrona y Caché Distribuida con Redis 7

### 22.1 Gestor de Conexiones: `RedisConnectionManager`

`RedisConnectionManager` gestiona el ciclo de vida del pool asíncrono con Redis 7 mediante `redis.asyncio`. Implementa timeouts estrictos y provee la sonda de salud perimétrica `ping()`.

```python
# app/shared/infrastructure/redis/connection_manager.py
from __future__ import annotations

import logging
import redis.asyncio as aioredis
from redis.exceptions import RedisError

logger = logging.getLogger("navby.shared.infrastructure.redis")


class RedisConnectionManager:
    """
    Gestor centralizado del ciclo de vida del ConnectionPool y cliente asíncrono de Redis 7.
    Configura sockets de baja latencia con timeouts estrictos y provee sondeo de salud (PING).
    """

    def __init__(self) -> None:
        self._pool: aioredis.ConnectionPool | None = None
        self._client: aioredis.Redis | None = None

    def init(
        self,
        redis_url: str,
        max_connections: int = 50,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 3.0,
        decode_responses: bool = True,
    ) -> None:
        """
        Inicializa el pool de conexiones asíncronas hacia Redis 7.
        """
        if self._pool is not None:
            logger.warning("RedisConnectionManager ya se encuentra inicializado. Reutilizando pool existente.")
            return

        self._pool = aioredis.ConnectionPool.from_url(
            redis_url,
            max_connections=max_connections,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            decode_responses=decode_responses,
        )
        self._client = aioredis.Redis(connection_pool=self._pool)
        logger.info("RedisConnectionManager inicializado exitosamente (max_connections=%d).", max_connections)

    def get_client(self) -> aioredis.Redis:
        """
        Retorna la instancia del cliente asíncrono de Redis.
        Lanza RuntimeError si el gestor no ha sido inicializado.
        """
        if self._client is None:
            raise RuntimeError(
                "RedisConnectionManager no está inicializado. Ejecute init() antes de solicitar el cliente."
            )
        return self._client

    async def ping(self) -> bool:
        """
        Ejecuta una sonda de salud perimétrica mediante el comando PING.
        Retorna True si Redis responde favorablemente, o False ante desconexión o fallo.
        """
        if self._client is None:
            return False
        try:
            response = await self._client.ping()
            return bool(response)
        except RedisError as exc:
            logger.error("Fallo en sonda de salud Redis (PING): %s", exc)
            return False

    async def close(self) -> None:
        """
        Cierra ordenadamente el cliente y desconecta el pool de conexiones.
        """
        if self._client is not None:
            await self._client.aclose()
            self._client = None

        if self._pool is not None:
            await self._pool.disconnect()
            self._pool = None

        logger.info("RedisConnectionManager cerrado y conexiones liberadas.")


# Instancia singleton del gestor de conexiones Redis
redis_connection_manager = RedisConnectionManager()
```

---

### 22.2 Contrato de Aplicación para Caché: Protocolo `CachePort`

```python
# app/shared/infrastructure/cache/cache_port.py
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CachePort(Protocol):
    """
    Puerto abstracto de aplicación para operaciones de almacenamiento temporal en caché.
    Define la interfaz canónica desacoplada del motor de almacenamiento subyacente.
    """

    async def get[T](self, key: str, namespace: str = "default") -> T | None:
        """
        Recupera un elemento tipado almacenado en caché bajo la clave y espacio de nombres dados.
        Retorna None si la clave no existe o ha expirado.
        """
        ...

    async def set[T](
        self,
        key: str,
        value: T,
        ttl_seconds: int = 300,
        namespace: str = "default",
    ) -> bool:
        """
        Almacena un elemento en caché con un tiempo de vida (TTL) obligatorio expresado en segundos.
        Retorna True si la persistencia fue exitosa.
        """
        ...

    async def delete(self, key: str, namespace: str = "default") -> bool:
        """
        Elimina la clave especificada del espacio de nombres en caché.
        Retorna True si la clave existía y fue removida.
        """
        ...

    async def exists(self, key: str, namespace: str = "default") -> bool:
        """
        Determina si una clave específica se encuentra presente y vigente en caché.
        """
        ...
```

---

### 22.3 Adaptador de Caché Resiliente con Fail-Open: `RedisCacheAdapter`

`RedisCacheAdapter` encapsula las operaciones de Redis aplicando tres principios de ingeniería:
1. **Prefijo Canónico de Claves:** `navby:cache:{namespace}:{key}`, estructurando el espacio de claves para inspección y auditoría de memoria en Redis.
2. **TTL Obligatorio en Segundos:** Queda prohibida la inserción de claves volátiles sin expiración (`ttl_seconds >= 1`, por defecto 300 segundos).
3. **Resiliencia Fail-Open:** Si Redis arroja una excepción (`RedisError`), el adaptador no la propaga como un error fatal 500; emite un log de advertencia estructurado y devuelve `None` en lecturas o `False` en escrituras, permitiendo que el flujo de negocio continúe consultando la base de datos de manera transparente (*degradación suave*).

```python
# app/shared/infrastructure/cache/redis_cache_adapter.py
from __future__ import annotations

import json
import logging
from typing import Any
import redis.asyncio as aioredis
from redis.exceptions import RedisError

from app.shared.infrastructure.cache.cache_port import CachePort

logger = logging.getLogger("navby.shared.infrastructure.cache")


class RedisCacheAdapter(CachePort):
    """
    Adaptador de caché distribuida sobre Redis 7 con resiliencia Fail-Open.
    Construye claves canónicas con formato 'navby:cache:{namespace}:{key}',
    exige TTL obligatorio en segundos para prevenir saturación de memoria,
    y captura excepciones de Redis para degradar suavemente hacia la base de datos.
    """

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client

    def _build_key(self, namespace: str, key: str) -> str:
        """
        Construye la clave canónica normalizada siguiendo las directrices de navby-database-schema.
        Formato: navby:cache:{namespace}:{key}
        """
        clean_namespace = namespace.strip().lower()
        clean_key = key.strip()
        return f"navby:cache:{clean_namespace}:{clean_key}"

    async def get[T](self, key: str, namespace: str = "default") -> T | None:
        """
        Recupera y deserializa un valor JSON desde Redis.
        Aplica Fail-Open: ante RedisError, emite advertencia y retorna None (Cache Miss seguro).
        """
        full_key = self._build_key(namespace, key)
        try:
            raw_value = await self._redis.get(full_key)
            if raw_value is None:
                return None
            return json.loads(raw_value)
        except RedisError as exc:
            logger.warning(
                "Fallo de lectura en Redis (Fail-Open activado) para la clave '%s': %s",
                full_key,
                str(exc),
            )
            return None
        except (json.JSONDecodeError, TypeError) as exc:
            logger.error(
                "Error de deserialización JSON para la clave de caché '%s': %s",
                full_key,
                str(exc),
            )
            return None

    async def set[T](
        self,
        key: str,
        value: T,
        ttl_seconds: int = 300,
        namespace: str = "default",
    ) -> bool:
        """
        Serializa a JSON y almacena un valor en Redis con TTL obligatorio.
        Invariante: ttl_seconds debe ser >= 1.
        Aplica Fail-Open: ante fallo de red o socket, retorna False sin arrojar excepción.
        """
        if ttl_seconds < 1:
            raise ValueError(
                f"El TTL de caché debe ser un entero positivo mayor o igual a 1 segundo (recibido: {ttl_seconds})."
            )

        full_key = self._build_key(namespace, key)
        try:
            payload = json.dumps(value, ensure_ascii=False, default=str)
            await self._redis.set(full_key, payload, ex=ttl_seconds)
            return True
        except RedisError as exc:
            logger.warning(
                "Fallo de escritura en Redis (Fail-Open activado) para la clave '%s': %s",
                full_key,
                str(exc),
            )
            return False
        except (TypeError, ValueError) as exc:
            logger.error(
                "Error al serializar a JSON el valor para la clave '%s': %s",
                full_key,
                str(exc),
            )
            return False

    async def delete(self, key: str, namespace: str = "default") -> bool:
        """
        Elimina una clave específica de Redis.
        Aplica Fail-Open: ante error de red, emite advertencia y retorna False.
        """
        full_key = self._build_key(namespace, key)
        try:
            deleted_count = await self._redis.delete(full_key)
            return deleted_count > 0
        except RedisError as exc:
            logger.warning(
                "Fallo al eliminar clave en Redis (Fail-Open activado) '%s': %s",
                full_key,
                str(exc),
            )
            return False

    async def exists(self, key: str, namespace: str = "default") -> bool:
        """
        Comprueba la existencia de una clave en Redis.
        Aplica Fail-Open: ante error de red, asume inexistencia (retorna False).
        """
        full_key = self._build_key(namespace, key)
        try:
            count = await self._redis.exists(full_key)
            return count > 0
        except RedisError as exc:
            logger.warning(
                "Fallo al verificar existencia en Redis (Fail-Open activado) '%s': %s",
                full_key,
                str(exc),
            )
            return False
```

---

## 23. Configuración Canónica y Tipada de Plataforma (`AppSettings`)

### 23.1 Inmutabilidad de Entorno y Tipado Estricto con `pydantic-settings`

El manejo de configuración en tiempo de ejecución se modela mediante `AppSettings`, implementada sobre `pydantic_settings.BaseSettings`. Para blindar la seguridad del proceso y prevenir sobreescrituras arbitrarias en tiempo de ejecución, la clase se declara inmutable con `SettingsConfigDict(frozen=True)`.

```python
# app/shared/infrastructure/config/settings.py
from __future__ import annotations

from functools import lru_cache
from typing import Literal
from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """
    Configuración tipada inmutable global para Navby Platform.
    Carga y valida variables de entorno desde el sistema o archivo '.env'.
    Cualquier mutación en tiempo de ejecución arroja error al configurarse 'frozen=True'.
    """
    model_config = SettingsConfigDict(
        frozen=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Entorno de Ejecución
    environment: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        description="Entorno activo de ejecución de la plataforma.",
    )

    # Persistencia Relacional PostgreSQL 16
    database_url: PostgresDsn = Field(
        default=...,
        description="Cadena DSN de conexión asíncrona hacia PostgreSQL 16 (ej. postgresql+asyncpg://user:pass@host:5432/navby).",
    )
    database_pool_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Tamaño base del pool de conexiones persistentes de SQLAlchemy.",
    )
    database_max_overflow: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Conexiones adicionales máximas que el pool puede abrir ante picos de demanda.",
    )
    database_echo: bool = Field(
        default=False,
        description="Bandera para volcado de sentencias SQL crudas en la consola de depuración.",
    )

    # Caché y Semáforos Redis 7
    redis_url: RedisDsn = Field(
        default=...,
        description="Cadena DSN de conexión hacia el clúster o nodo Redis 7 (ej. redis://localhost:6379/0).",
    )
    redis_max_connections: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Límite máximo de conexiones simultáneas en el ConnectionPool de Redis.",
    )

    # Seguridad y Criptografía JWT
    jwt_secret_key: str = Field(
        default=...,
        min_length=32,
        description="Clave criptográfica simétrica secreta de al menos 32 bytes para firma HMAC de tokens JWT.",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Algoritmo de firma digital empleado en los tokens de acceso.",
    )
    jwt_access_token_expire_minutes: int = Field(
        default=60,
        ge=5,
        le=1440,
        description="Ventana temporal de validez del token de acceso de usuario en minutos.",
    )

    # Orígenes Permitidos CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Lista blanca de orígenes HTTP con privilegios de Cross-Origin Resource Sharing.",
    )

    # Observabilidad y Registro Estructurado
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Umbral mínimo de severidad para emisión de logs estructurados.",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url_scheme(cls, v: PostgresDsn) -> PostgresDsn:
        """
        Garantiza que la cadena DSN de base de datos utilice explícitamente el driver asíncrono 'postgresql+asyncpg'.
        """
        scheme = v.scheme
        if scheme not in ("postgresql+asyncpg", "postgres+asyncpg"):
            raise ValueError(
                f"El esquema de la base de datos debe ser 'postgresql+asyncpg' para compatibilidad con asyncpg (recibido: '{scheme}')."
            )
        return v


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """
    Factoría con memoización 'lru_cache' para inyección de configuración singleton.
    Evita releer y validar variables de entorno en cada invocación de Depends().
    """
    return AppSettings()
```

---

## 24. Diccionario Estructural y Diagrama de Clases UML de la Capa de Infraestructura (Estándar Atelier IAM y PlantUML)

### 24.1 Matriz Estructural de 5 Columnas (Estándar Atelier IAM)

A continuación se detalla la matriz exhaustiva de 5 columnas para la totalidad de clases, estructuras, atributos, métodos y reglas de negocio que componen la Capa de Infraestructura del Shared Kernel:

| Clase o Estructura | Elemento | Firma o Tipo | Ámbito | Descripción, Relaciones y Reglas de Negocio |
| :---: | :---: | :--- | :---: | :--- |
| **AuditablePersistenceMixin** | Mixin ORM | `class AuditablePersistenceMixin` | Público | Mixin relacional para auditoría temporal estándar con soporte de marcas UTC e inmutabilidad. |
| AuditablePersistenceMixin | `created_at` | `Mapped[datetime]` | Público | Columna `TIMESTAMPTZ`, no nula, inmutable. `server_default=func.now()`, `sort_order=998`. |
| AuditablePersistenceMixin | `updated_at` | `Mapped[datetime]` | Público | Columna `TIMESTAMPTZ`, no nula. Actualizada automáticamente mediante `onupdate=func.now()`. |
| AuditablePersistenceMixin | `created_at_iso` | `() -> str` | Público | Formatea `created_at` a cadena estándar ISO 8601 en UTC para contratos de API y mensajería. |
| AuditablePersistenceMixin | `updated_at_iso` | `() -> str` | Público | Formatea `updated_at` a cadena estándar ISO 8601 en UTC para contratos de API y mensajería. |
| **POSTGRES_NAMING_CONVENTION** | Constante | `dict[str, str]` | Público | Diccionario canónico de patrones de nombrado para restricciones relacionales en PostgreSQL (`ix`, `uq`, `ck`, `fk`, `pk`). |
| **Base** | Clase Base ORM | `class Base(AsyncAttrs, DeclarativeBase)` | Público | Clase base declarativa unificada con soporte de carga diferida asíncrona segura y metadatos con convención estricta. |
| Base | `metadata` | `MetaData` | Público | Registro central de metadatos de SQLAlchemy configurado con `POSTGRES_NAMING_CONVENTION`. |
| **DatabaseSessionManager** | Clase Gestora | `class DatabaseSessionManager` | Público | Gestor centralizado del ciclo de vida del `AsyncEngine` y `async_sessionmaker` para PostgreSQL 16 con `asyncpg`. |
| DatabaseSessionManager | `_engine` | `AsyncEngine \| None` | Privado | Instancia del motor asíncrono configurado con pool de conexiones y sondeo `pre-ping`. |
| DatabaseSessionManager | `_sessionmaker` | `async_sessionmaker[AsyncSession] \| None` | Privado | Fábrica de sesiones asíncronas configuradas sin autoflush ni expiración en commit. |
| DatabaseSessionManager | `__init__` | `() -> None` | Público | Constructor. Inicializa las referencias de motor y fábrica en estado desconectado (`None`). |
| DatabaseSessionManager | `init` | `(db_url: str, echo: bool = False, pool_size: int = 20, max_overflow: int = 10, pool_timeout: float = 30.0, pool_recycle: int = 1800) -> None` | Público | Configura y aprovisiona el motor asíncrono y el pool de conexiones optimizado para producción. |
| DatabaseSessionManager | `close` | `async () -> None` | Público | Cierra limpiamente el pool de conexiones mediante `await engine.dispose()`. |
| DatabaseSessionManager | `is_initialized` | `() -> bool` | Público | Retorna `True` si el gestor cuenta con motor y fábrica de sesiones activos. |
| DatabaseSessionManager | `engine` | `property -> AsyncEngine` | Público | Acceso de solo lectura al `AsyncEngine` activo. Arroja `RuntimeError` si no está inicializado. |
| DatabaseSessionManager | `session` | `async () -> AsyncGenerator[AsyncSession, None]` | Público | Context manager asíncrono. Provee una `AsyncSession` aislada con cierre determinista en bloque `finally`. |
| DatabaseSessionManager | `transaction` | `async () -> AsyncGenerator[AsyncSession, None]` | Público | Context manager asíncrono para transacciones ACID atómicas. Ejecuta `commit()` al finalizar o `rollback()` ante fallos. |
| **db_session_manager** | Instancia Global | `DatabaseSessionManager` | Público | Singleton global para inyección de sesiones y transacciones en el ciclo de vida de FastAPI. |
| **get_db_session** | Función Proveedora | `async () -> AsyncGenerator[AsyncSession, None]` | Público | Dependencia para FastAPI `Depends()`. Provee una `AsyncSession` de lectura/escritura manual. |
| **get_db_transaction** | Función Proveedora | `async () -> AsyncGenerator[AsyncSession, None]` | Público | Dependencia para FastAPI `Depends()`. Provee una `AsyncSession` transaccional ACID con commit/rollback atómico. |
| **OutboxStatus** | Enumeración | `class OutboxStatus(StrEnum)` | Público | Catálogo enumerado inmutable de estados de procesamiento del evento en el pipeline de Transactional Outbox. |
| OutboxStatus | `PENDING` | `"PENDING"` | Público | Evento registrado en base de datos esperando ser recuperado y despachado por el worker relay. |
| OutboxStatus | `PUBLISHED` | `"PUBLISHED"` | Público | Evento despachado y confirmado exitosamente por el broker de mensajería externo. |
| OutboxStatus | `FAILED` | `"FAILED"` | Público | Evento que agotó el número máximo de reintentos de envío, archivado para intervención humana. |
| **OutboxEventModel** | Modelo ORM | `class OutboxEventModel(Base, AuditablePersistenceMixin)` | Público | Entidad relacional mapeada a la tabla física `outbox_events` para publicación atómica y consistencia eventual. |
| OutboxEventModel | `id` | `Mapped[int]` | Público | Clave primaria: `BIGINT GENERATED ALWAYS AS IDENTITY`. Inserción monótona secuencial. |
| OutboxEventModel | `event_id` | `Mapped[uuid.UUID]` | Público | Identificador UUIDv4 único e indexado para deduplicación estricta e idempotencia externa. |
| OutboxEventModel | `aggregate_type` | `Mapped[str]` | Público | Nombre formal del tipo de agregado emisor (`VARCHAR(64)`). |
| OutboxEventModel | `aggregate_id` | `Mapped[str]` | Público | Identificador del agregado emisor serializado como cadena alfanumérica (`VARCHAR(64)`). |
| OutboxEventModel | `event_type` | `Mapped[str]` | Público | Nombre de la clase del evento de dominio (`VARCHAR(128)`). |
| OutboxEventModel | `payload` | `Mapped[dict[str, Any]]` | Público | Cuerpo del evento serializado en formato binario estructurado `JSONB`. |
| OutboxEventModel | `occurred_on` | `Mapped[datetime]` | Público | Marca temporal de ocurrencia original del evento en UTC (`TIMESTAMPTZ`). |
| OutboxEventModel | `status` | `Mapped[str]` | Público | Estado actual del evento (`VARCHAR(20)`), default `"PENDING"`. Restringido por check constraint. |
| OutboxEventModel | `retry_count` | `Mapped[int]` | Público | Contador de intentos de envío fallidos (`INTEGER`), default `0`. Invariante: $\ge 0$. |
| OutboxEventModel | `last_error` | `Mapped[str \| None]` | Público | Mensaje y traza del último fallo registrado durante el despacho (`TEXT`, nullable). |
| OutboxEventModel | `processed_at` | `Mapped[datetime \| None]` | Público | Marca temporal en UTC en que el evento fue confirmado como publicado (`TIMESTAMPTZ`, nullable). |
| OutboxEventModel | `__table_args__` | `tuple` | Público | Metadatos DDL: índice compuesto `ix_outbox_events_status_occurred_on` y restricciones `CHECK`. |
| **SqlAlchemyOutboxRepository** | Clase Repositorio | `class SqlAlchemyOutboxRepository` | Público | Repositorio asíncrono para inserción, polling seguro con `SKIP LOCKED` y actualización de `outbox_events`. |
| SqlAlchemyOutboxRepository | `save` | `async (session: AsyncSession, event: DomainEvent) -> OutboxEventModel` | Público | Serializa un `DomainEvent` y lo añade a la transacción activa de la sesión relacional. |
| SqlAlchemyOutboxRepository | `fetch_pending_events` | `async (session: AsyncSession, batch_size: int = 50) -> Sequence[OutboxEventModel]` | Público | Consulta eventos en estado `PENDING` ordenados por `occurred_on ASC` aplicando `FOR UPDATE SKIP LOCKED`. |
| SqlAlchemyOutboxRepository | `mark_as_published` | `async (session: AsyncSession, event_id: int) -> None` | Público | Actualiza el estado a `PUBLISHED` y fija `processed_at = now()` en UTC. |
| SqlAlchemyOutboxRepository | `mark_as_failed` | `async (session: AsyncSession, event_id: int, error_message: str, max_retries: int = 5) -> None` | Público | Incrementa `retry_count`, registra `last_error` y transfiere a `FAILED` si supera `max_retries`. |
| **OutboxDomainEventPublisherAdapter** | Clase Adaptadora | `class OutboxDomainEventPublisherAdapter(DomainEventPublisher)` | Público | Adaptador que implementa el puerto `DomainEventPublisher` persistiendo eventos en `outbox_events`. |
| OutboxDomainEventPublisherAdapter | `_session` | `AsyncSession` | Privado | Sesión transaccional activa inyectada en el caso de uso. |
| OutboxDomainEventPublisherAdapter | `_repository` | `SqlAlchemyOutboxRepository` | Privado | Repositorio relacional utilizado para persistir los modelos de eventos outbox. |
| OutboxDomainEventPublisherAdapter | `__init__` | `(session: AsyncSession, repository: SqlAlchemyOutboxRepository \| None = None) -> None` | Público | Constructor. Vincula la sesión transaccional y el repositorio de outbox. |
| OutboxDomainEventPublisherAdapter | `publish` | `async (event: DomainEvent) -> None` | Público | Realiza el contrato del puerto emitiendo el evento hacia la tabla outbox dentro de la transacción activa. |
| OutboxDomainEventPublisherAdapter | `publish_all` | `async (events: Iterable[DomainEvent]) -> None` | Público | Realiza el contrato del puerto emitiendo una colección de eventos en orden de ocurrencia. |
| **RedisConnectionManager** | Clase Gestora | `class RedisConnectionManager` | Público | Gestor centralizado del pool de conexiones asíncronas hacia Redis 7 (`redis.asyncio`). |
| RedisConnectionManager | `_pool` | `aioredis.ConnectionPool \| None` | Privado | Pool de conexiones persistentes con límites configurables y decodificación de cadenas. |
| RedisConnectionManager | `_client` | `aioredis.Redis \| None` | Privado | Cliente asíncrono para despacho de comandos hacia Redis. |
| RedisConnectionManager | `__init__` | `() -> None` | Público | Constructor. Inicializa las referencias en estado desconectado (`None`). |
| RedisConnectionManager | `init` | `(redis_url: str, max_connections: int = 50, socket_timeout: float = 5.0, socket_connect_timeout: float = 3.0, decode_responses: bool = True) -> None` | Público | Inicializa el `ConnectionPool` asíncrono y aprovisiona el cliente singleton de Redis. |
| RedisConnectionManager | `get_client` | `() -> aioredis.Redis` | Público | Retorna el cliente de Redis activo. Arroja `RuntimeError` si el gestor no ha sido inicializado. |
| RedisConnectionManager | `ping` | `async () -> bool` | Público | Ejecuta un comando `PING` perimétrico. Retorna `True` si responde o `False` ante fallos. |
| RedisConnectionManager | `close` | `async () -> None` | Público | Cierra limpiamente el cliente y desconecta el pool de conexiones liberando recursos de socket. |
| **redis_connection_manager** | Instancia Global | `RedisConnectionManager` | Público | Singleton global para acceso y gestión del ciclo de vida de Redis en la plataforma. |
| **CachePort** | Protocolo de Aplicación | `class CachePort(Protocol)` | Público | Protocolo abstracto tipado para operaciones de caché distribuida en la aplicación. |
| CachePort | `get` | `async [T](key: str, namespace: str = "default") -> T \| None` | Público | Recupera un elemento tipado de la caché. Retorna `None` si la clave no existe o expiró. |
| CachePort | `set` | `async [T](key: str, value: T, ttl_seconds: int = 300, namespace: str = "default") -> bool` | Público | Persiste un elemento en caché con TTL obligatorio en segundos. Retorna `True` si fue exitoso. |
| CachePort | `delete` | `async (key: str, namespace: str = "default") -> bool` | Público | Elimina una clave del espacio de nombres en caché. Retorna `True` si fue removida. |
| CachePort | `exists` | `async (key: str, namespace: str = "default") -> bool` | Público | Comprueba si una clave específica se encuentra vigente en el espacio de nombres de caché. |
| **RedisCacheAdapter** | Clase Adaptadora | `class RedisCacheAdapter(CachePort)` | Público | Adaptador sobre Redis 7 con claves canónicas `navby:cache:{namespace}:{key}` y política Fail-Open. |
| RedisCacheAdapter | `_redis` | `aioredis.Redis` | Privado | Cliente asíncrono de Redis inyectado para ejecución de comandos. |
| RedisCacheAdapter | `__init__` | `(redis_client: aioredis.Redis) -> None` | Público | Constructor. Recibe el cliente asíncrono de Redis. |
| RedisCacheAdapter | `_build_key` | `(namespace: str, key: str) -> str` | Privado | Normaliza y formatea la clave bajo la convención canónica `navby:cache:{namespace}:{key}`. |
| RedisCacheAdapter | `get` | `async [T](key: str, namespace: str = "default") -> T \| None` | Público | Lee y deserializa JSON desde Redis. Captura `RedisError` retornando `None` (Fail-Open). |
| RedisCacheAdapter | `set` | `async [T](key: str, value: T, ttl_seconds: int = 300, namespace: str = "default") -> bool` | Público | Serializa a JSON y escribe en Redis con TTL obligatorio. Captura `RedisError` retornando `False` (Fail-Open). |
| RedisCacheAdapter | `delete` | `async (key: str, namespace: str = "default") -> bool` | Público | Elimina la clave de Redis. Captura `RedisError` retornando `False` (Fail-Open). |
| RedisCacheAdapter | `exists` | `async (key: str, namespace: str = "default") -> bool` | Público | Verifica presencia de la clave en Redis. Captura `RedisError` retornando `False` (Fail-Open). |
| **AppSettings** | Configuración Base | `class AppSettings(BaseSettings)` | Público | Modelo de configuración global inmutable fuertemente tipado mediante Pydantic Settings v2. |
| AppSettings | `model_config` | `SettingsConfigDict` | Público | Metadatos de configuración: inmutabilidad estricta (`frozen=True`), archivo `.env` UTF-8. |
| AppSettings | `environment` | `Literal["development", "staging", "production", "test"]` | Público | Entorno activo de ejecución, restringido a valores canónicos. Default `"development"`. |
| AppSettings | `database_url` | `PostgresDsn` | Público | Cadena DSN de conexión PostgreSQL, validada para requerir driver `postgresql+asyncpg`. |
| AppSettings | `database_pool_size` | `int` | Público | Tamaño base del pool de conexiones persistentes de SQLAlchemy ($1 \le \text{pool} \le 100$). Default `20`. |
| AppSettings | `database_max_overflow` | `int` | Público | Conexiones adicionales de desborde ($0 \le \text{overflow} \le 50$). Default `10`. |
| AppSettings | `database_echo` | `bool` | Público | Indicador de volcado de sentencias SQL en consola de depuración. Default `False`. |
| AppSettings | `redis_url` | `RedisDsn` | Público | Cadena DSN de conexión hacia el servidor o clúster Redis 7. Requerida. |
| AppSettings | `redis_max_connections` | `int` | Público | Capacidad máxima del pool de conexiones hacia Redis ($1 \le \text{conn} \le 200$). Default `50`. |
| AppSettings | `jwt_secret_key` | `str` | Público | Secreto criptográfico para firma HMAC de tokens de autenticación (longitud mínima 32 caracteres). |
| AppSettings | `jwt_algorithm` | `str` | Público | Algoritmo criptográfico de firma digital para tokens JWT. Default `"HS256"`. |
| AppSettings | `jwt_access_token_expire_minutes` | `int` | Público | Ventana temporal de validez del token de acceso ($5 \le \text{min} \le 1440$). Default `60`. |
| AppSettings | `cors_origins` | `list[str]` | Público | Lista de dominios y orígenes autorizados para solicitudes CORS de navegadores web. |
| AppSettings | `log_level` | `Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]` | Público | Umbral de registro para el formateador de logs estructurados. Default `"INFO"`. |
| AppSettings | `validate_database_url_scheme` | `classmethod (v: PostgresDsn) -> PostgresDsn` | Público | Validador de campo que rechaza cadenas DSN sin esquema asíncrono `postgresql+asyncpg`. |
| **get_settings** | Factoría Singleton | `() -> AppSettings` | Público | Factoría memoizada con `@lru_cache(maxsize=1)` para inyección de configuración sin relecturas de disco. |

---

### 24.2 Código Fuente Canónico PlantUML (`class-diagram-shared-infrastructure.puml`)

```plantuml
@startuml class-diagram-shared-infrastructure
title <size:18>Diagrama de Componentes y Clases UML - Bounded Context Shared Kernel (Infrastructure Layer)</size>\n<size:12>Paquete Canónico: app.shared.infrastructure</size>

' Configuraciones visuales y de diseño profesional
skinparam classAttributeIconSize 0
skinparam monochrome false
skinparam shadowing false
skinparam roundcorner 6
skinparam linetype ortho
skinparam nodesep 28
skinparam ranksep 32
skinparam defaultFontName "Helvetica", "Arial", sans-serif
skinparam defaultFontSize 10
skinparam defaultFontColor #2C3E50
skinparam arrowColor #34495E
skinparam arrowThickness 1.2
skinparam packageBorderColor #7F8C8D
skinparam packageFontSize 11
skinparam packageFontStyle bold

' Estilos específicos por categoría táctica de infraestructura
skinparam class {
    BackgroundColor #FFFFFF
    BorderColor #2C3E50
    HeaderBackgroundColor #EAEDED
}
skinparam class<<ORMBase>> {
    BackgroundColor #E8F8F5
    BorderColor #16A085
    HeaderBackgroundColor #A3E4D7
}
skinparam class<<DatabaseManager>> {
    BackgroundColor #FEF9E7
    BorderColor #D68910
    HeaderBackgroundColor #FAD7A0
}
skinparam class<<OutboxModel>> {
    BackgroundColor #F4ECF7
    BorderColor #8E44AD
    HeaderBackgroundColor #D7BDE2
}
skinparam class<<OutboxRepository>> {
    BackgroundColor #EBF5FB
    BorderColor #2980B9
    HeaderBackgroundColor #AED6F1
}
skinparam class<<CacheAdapter>> {
    BackgroundColor #FDEDEC
    BorderColor #C0392B
    HeaderBackgroundColor #F5B7B1
}
skinparam class<<Configuration>> {
    BackgroundColor #EAECEE
    BorderColor #5D6D7E
    HeaderBackgroundColor #D5D8DC
}
skinparam class<<ApplicationPort>> {
    BackgroundColor #E8F8F5
    BorderColor #16A085
    HeaderBackgroundColor #A3E4D7
}
skinparam class<<DomainCore>> {
    BackgroundColor #FDFEFE
    BorderColor #7F8C8D
    HeaderBackgroundColor #EAEDED
}
skinparam enum {
    BackgroundColor #FCF3CF
    BorderColor #B7950B
    HeaderBackgroundColor #F9E79F
}

' Evitar anidamiento automático por puntos en nombres de paquetes
set separator none

' ==============================================================================
' 1. TIER 1: CONFIGURACIÓN Y PERSISTENCIA BASE
' ==============================================================================
package "app.shared.infrastructure.config" as config_pkg #FDFEFE {

    class AppSettings <<Configuration>> {
        + environment: Literal["development", "staging", "production", "test"]
        + database_url: PostgresDsn
        + database_pool_size: int
        + database_max_overflow: int
        + database_echo: bool
        + redis_url: RedisDsn
        + redis_max_connections: int
        + jwt_secret_key: str
        + jwt_algorithm: str
        + jwt_access_token_expire_minutes: int
        + cors_origins: list<str>
        + log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        + {static} validate_database_url_scheme(v: PostgresDsn): PostgresDsn
    }

}

package "app.shared.infrastructure.db" as db_pkg #FDFEFE {

    class Base <<ORMBase>> {
        + {static} metadata: MetaData
    }

    class AuditablePersistenceMixin <<ORMBase>> {
        + created_at: Mapped<datetime>
        + updated_at: Mapped<datetime>
        + created_at_iso(): str
        + updated_at_iso(): str
    }

    class DatabaseSessionManager <<DatabaseManager>> {
        - _engine: AsyncEngine | None
        - _sessionmaker: async_sessionmaker<AsyncSession> | None
        + __init__(): void
        + init(db_url: str, echo: bool, pool_size: int, max_overflow: int): void
        + close(): void
        + is_initialized(): bool
        + engine: AsyncEngine {query}
        + session(): AsyncGenerator<AsyncSession, None>
        + transaction(): AsyncGenerator<AsyncSession, None>
    }

    Base -[hidden]right-> AuditablePersistenceMixin
    Base -[hidden]down-> DatabaseSessionManager
}

config_pkg -[hidden]right-> db_pkg

' ==============================================================================
' 2. TIER 2: PATRÓN TRANSACTIONAL OUTBOX Y CONECTIVIDAD REDIS / CACHÉ
' ==============================================================================
package "app.shared.infrastructure.outbox" as outbox_pkg #FDFEFE {

    enum OutboxStatus <<OutboxModel>> {
        PENDING
        PUBLISHED
        FAILED
    }

    class OutboxEventModel <<OutboxModel>> {
        + id: Mapped<int>
        + event_id: Mapped<UUID>
        + aggregate_type: Mapped<str>
        + aggregate_id: Mapped<str>
        + event_type: Mapped<str>
        + payload: Mapped<dict<str, Any>>
        + occurred_on: Mapped<datetime>
        + status: Mapped<str>
        + retry_count: Mapped<int>
        + last_error: Mapped<str | None>
        + processed_at: Mapped<datetime | None>
    }

    class SqlAlchemyOutboxRepository <<OutboxRepository>> {
        + save(session: AsyncSession, event: DomainEvent): OutboxEventModel
        + fetch_pending_events(session: AsyncSession, batch_size: int): Sequence<OutboxEventModel>
        + mark_as_published(session: AsyncSession, event_id: int): void
        + mark_as_failed(session: AsyncSession, event_id: int, error_message: str, max_retries: int): void
    }

    class OutboxDomainEventPublisherAdapter <<OutboxRepository>> {
        - _session: AsyncSession
        - _repository: SqlAlchemyOutboxRepository
        + __init__(session: AsyncSession, repository: SqlAlchemyOutboxRepository | None): void
        + publish(event: DomainEvent): void
        + publish_all(events: Iterable<DomainEvent>): void
    }

    OutboxStatus -[hidden]right-> OutboxEventModel
    OutboxEventModel -[hidden]down-> SqlAlchemyOutboxRepository
    SqlAlchemyOutboxRepository -[hidden]down-> OutboxDomainEventPublisherAdapter
}

package "app.shared.infrastructure.redis" as redis_pkg #FDFEFE {

    class RedisConnectionManager <<DatabaseManager>> {
        - _pool: ConnectionPool | None
        - _client: Redis | None
        + __init__(): void
        + init(redis_url: str, max_connections: int, socket_timeout: float): void
        + get_client(): Redis
        + ping(): bool
        + close(): void
    }

}

package "app.shared.infrastructure.cache" as cache_pkg #FDFEFE {

    class RedisCacheAdapter <<CacheAdapter>> {
        - _redis: Redis
        + __init__(redis_client: Redis): void
        - _build_key(namespace: str, key: str): str
        + get<T>(key: str, namespace: str): T | None
        + set<T>(key: str, value: T, ttl_seconds: int, namespace: str): bool
        + delete(key: str, namespace: str): bool
        + exists(key: str, namespace: str): bool
    }

}

redis_pkg -[hidden]down-> cache_pkg
outbox_pkg -[hidden]right-> redis_pkg
db_pkg -[hidden]down-> outbox_pkg

' ==============================================================================
' 3. TIER 3: PUERTOS DE APLICACIÓN Y EVENTOS DE DOMINIO
' ==============================================================================
package "app.shared.application.bus" as bus_ports_pkg #FDFEFE {
    interface DomainEventPublisher <<ApplicationPort>> {
        + {abstract} publish(event: DomainEvent): void
        + {abstract} publish_all(events: Iterable<DomainEvent>): void
    }
}

package "app.shared.application.ports.cache" as cache_ports_pkg #FDFEFE {
    interface CachePort <<ApplicationPort>> {
        + {abstract} get<T>(key: str, namespace: str): T | None
        + {abstract} set<T>(key: str, value: T, ttl_seconds: int, namespace: str): bool
        + {abstract} delete(key: str, namespace: str): bool
        + {abstract} exists(key: str, namespace: str): bool
    }
}

package "app.shared.domain.model" as domain_layer #FDFEFE {
    class DomainEvent <<DomainCore>> {
        + event_id: UUID
        + occurred_on: datetime
        + aggregate_id: str
        + event_type: str
    }
}

bus_ports_pkg -[hidden]right-> cache_ports_pkg
cache_ports_pkg -[hidden]right-> domain_layer
outbox_pkg -[hidden]down-> bus_ports_pkg

' ==============================================================================
' RELACIONES Y DEPENDENCIAS ESTRUCTURALES
' ==============================================================================
' Persistencia relacional y Outbox
OutboxEventModel -up-|> Base
OutboxEventModel -up-|> AuditablePersistenceMixin
OutboxEventModel --> OutboxStatus : clasifica estado >
SqlAlchemyOutboxRepository ..> OutboxEventModel : persiste y consulta SKIP LOCKED >
OutboxDomainEventPublisherAdapter --> SqlAlchemyOutboxRepository : delega almacenamiento >

' Conexión Redis y Adaptador de Caché
RedisCacheAdapter ..|> CachePort : realiza puerto conducido >
RedisCacheAdapter --> RedisConnectionManager : utiliza cliente asíncrono >

' Realización de puertos y serialización de eventos
OutboxDomainEventPublisherAdapter ..|> DomainEventPublisher : realiza puerto conducido >
OutboxDomainEventPublisherAdapter ..> DomainEvent : procesa y serializa >
SqlAlchemyOutboxRepository ..> DomainEvent : extrae metadatos y payload >

' Parametrización desde configuración
DatabaseSessionManager ..> AppSettings : parametriza pool y DSN >
RedisConnectionManager ..> AppSettings : parametriza conexión y sockets >

@enduml
```

---

### 24.3 Tabla de Trazabilidad de Estereotipos UML de la Capa de Infraestructura

| Estereotipo UML | Semántica Arquitectónica | Color de Fondo | Color de Borde | Componentes Modelados en la Capa de Infraestructura |
| :---: | :--- | :---: | :---: | :--- |
| <<ORMBase>> | Clases base y mixins declarativos de persistencia relacional SQLAlchemy 2.0 | `#E8F8F5` | `#16A085` | `AuditablePersistenceMixin`, `Base` |
| <<DatabaseManager>> | Gestores de ciclo de vida de pools y motores asíncronos de persistencia | `#FEF9E7` | `#D68910` | `DatabaseSessionManager`, `RedisConnectionManager` |
| <<OutboxModel>> | Modelos relacionales ORM y enumeraciones del patrón Transactional Outbox | `#F4ECF7` | `#8E44AD` | `OutboxStatus`, `OutboxEventModel` |
| <<OutboxRepository>> | Repositorios relacionales con polling `SKIP LOCKED` y adaptadores de publicación | `#EBF5FB` | `#2980B9` | `SqlAlchemyOutboxRepository`, `OutboxDomainEventPublisherAdapter` |
| <<CacheAdapter>> | Adaptadores de caché distribuida con resiliencia Fail-Open y expiración | `#FDEDEC` | `#C0392B` | `RedisCacheAdapter` |
| <<Configuration>> | Modelos de configuración inmutables tipados para variables de entorno | `#EAECEE` | `#5D6D7E` | `AppSettings` |
| <<ApplicationPort>> | Protocolos e interfaces abstractas definidas por las capas internas de la aplicación | `#FDFEFE` | `#7F8C8D` | `CachePort`, `DomainEventPublisher` |
| <<DomainCore>> | Primitivas y eventos inmutables provistos por el núcleo de la Capa de Dominio | `#FDFEFE` | `#7F8C8D` | `DomainEvent` |

---

## 25. Bounded Context Database Diagram

En esta sección, el equipo de arquitectura presenta y fundamenta el **Bounded Context Database Diagram** para el Bounded Context **Shared Kernel**, en estricta conformidad con la rúbrica de evaluación arquitectónica del proyecto (`docs/project-statement.md`, líneas 437–444). 

Aunque los modelos tácticos de dominio del Shared Kernel (`Money`, `GeoPoint`, `Result[T, E]`) residen puramente en memoria como tipos de valor y mónadas inmutables, la Capa de Infraestructura (`app.shared.infrastructure`) gobierna la base de la persistencia física de todo el ecosistema Navby Platform sobre el motor relacional **PostgreSQL 16** (contenedor Docker en VM de Azure). En este nivel se formalizan dos objetos arquitectónicos cardinales:
1. **El Arquetipo de Auditoría Temporal Estándar (`AuditablePersistenceMixin`):** Mixin físico relacional heredado transversalmente por todas las entidades persistentes de la plataforma (`user_accounts`, `itineraries`, `credit_wallets`, `credit_purchase_orders` y `outbox_events`), garantizando marcas temporales `created_at` y `updated_at` sincronizadas en UTC a nivel de servidor de base de datos.
2. **La Tabla Física del Patrón Transactional Outbox (`outbox_events`):** Tabla relacional dedicada que materializa el patrón de diseño arquitectónico **Transactional Outbox**, erradicando el problema de escrituras duales (*dual-write problem*) y asegurando consistencia eventual y entrega *at-least-once* de eventos de dominio hacia brokers y consumidores asíncronos mediante sondeo no bloqueante con `FOR UPDATE SKIP LOCKED`.

---

### 25.1 Artefacto Visual Compilado (Diagram-as-Code)

La siguiente figura ilustra el Diagrama Entidad-Relación (ERD) formal de la persistencia gobernada por el Shared Kernel, generado deterministamente mediante el target `make db-diagrams` del Makefile a partir de su especificación PlantUML DSL:

![Diagrama de Base de Datos (ERD) - Bounded Context Shared Kernel (PostgreSQL 16)](../../../report/assets/database-diagrams/database-diagram-shared.png)

---

### 25.2 Catálogo Detallado de Tablas y Componentes de Base de Datos

Siguiendo el estándar analítico de desglose técnico de Atelier, la siguiente tabla detalla la totalidad de los atributos físicos, tipos de datos en PostgreSQL 16, restricciones de integridad y reglas de negocio del almacenamiento del Shared Kernel:

| Tabla o Estructura | Columna o Elemento | Tipo de Dato Físico | Llave o Restricción | Descripción, Relaciones y Reglas de Negocio |
| :--- | :--- | :--- | :---: | :--- |
| **auditable_persistence_mixin** | `created_at` | `TIMESTAMPTZ` | `NOT NULL, DEFAULT NOW()` | Marca temporal de inserción física del registro en PostgreSQL expresada en UTC estricto. Invariable e inmutable tras la creación. |
| **auditable_persistence_mixin** | `updated_at` | `TIMESTAMPTZ` | `NOT NULL, DEFAULT NOW()` | Marca temporal de última modificación física en PostgreSQL expresada en UTC. Actualizada automáticamente vía `onupdate=func.now()` de SQLAlchemy. |
| **outbox_events** | `id` | `BIGINT GENERATED ALWAYS AS IDENTITY` | `PRIMARY KEY (PK)` | Identificador técnico numérico secuencial monótono de 64 bits. Garantiza óptima localidad espacial en el árbol B-Tree y orden determinista de inserción. |
| **outbox_events** | `event_id` | `UUID` | `UNIQUE (UK), NOT NULL` | Identificador universal único del evento autogenerado en memoria (`uuid.uuid4()`). Utilizado por los consumidores para deduplicación idempotente estricta. |
| **outbox_events** | `aggregate_type` | `VARCHAR(64)` | `NOT NULL` | Nombre formal de la clase de la raíz de agregado que originó el suceso (ej. `'UserAccount'`, `'Itinerary'`, `'CreditWallet'`). Indexado para trazabilidad. |
| **outbox_events** | `aggregate_id` | `VARCHAR(64)` | `NOT NULL` | Identificador único del agregado emisor serializado como cadena. Permite particionamiento y orden causal de sucesos por entidad de negocio. |
| **outbox_events** | `event_type` | `VARCHAR(128)` | `NOT NULL` | Calificador semántico del evento de dominio (ej. `'UserRegisteredEvent'`, `'ItineraryCreatedEvent'`). Soporta deserialización polimórfica en los suscriptores. |
| **outbox_events** | `payload` | `JSONB` | `NOT NULL` | Representación serializada estructurada del estado del evento en formato JSON binario nativo de PostgreSQL. Permite indexación GIN y consultas de atributos sin deserialización previa. |
| **outbox_events** | `occurred_on` | `TIMESTAMPTZ` | `NOT NULL` | Marca temporal inmutable en UTC en la que aconteció la mutación de estado dentro del agregado. |
| **outbox_events** | `status` | `VARCHAR(20)` | `NOT NULL, DEFAULT 'PENDING'` | Estado de publicación en el ciclo de vida del Outbox (`'PENDING'`, `'PUBLISHED'`, `'FAILED'`). Restringido por la restricción `chk_outbox_events_status`. |
| **outbox_events** | `retry_count` | `INTEGER` | `NOT NULL, DEFAULT 0` | Contador de intentos de despacho fallidos ejecutados por el *Outbox Relay Worker*. Restringido por `chk_outbox_events_retry_count >= 0`. |
| **outbox_events** | `last_error` | `TEXT` | `NULL` | Traza textual legible y mensaje de excepción capturado en el último intento fallido de despacho asíncrono. |
| **outbox_events** | `processed_at` | `TIMESTAMPTZ` | `NULL` | Marca temporal en UTC en la que el worker recibió confirmación exitosa de recepción (*ACK*) y finalizó la publicación del evento. |
| **outbox_events** | `created_at` | `TIMESTAMPTZ` | `NOT NULL, DEFAULT NOW()` | Marca temporal de inserción física heredada del arquetipo `AuditablePersistenceMixin`. |
| **outbox_events** | `updated_at` | `TIMESTAMPTZ` | `NOT NULL, DEFAULT NOW()` | Marca temporal de última modificación física heredada del arquetipo `AuditablePersistenceMixin`. |

---

### 25.3 Matriz de Restricciones (Constraints) e Índices Físicos de Rendimiento

Para garantizar la integridad referencial lógica y un rendimiento óptimo de sondeo concurrente en PostgreSQL 16, la tabla `outbox_events` incorpora las siguientes restricciones e índices B-Tree:

| Objeto Físico | Identificador Técnico | Tipo de Objeto | Definición DDL / Columnas Mapeadas | Propósito Operativo y Justificación Arquitectónica |
| :--- | :--- | :---: | :--- | :--- |
| outbox_events | `pk_outbox_events` | Restricción | `PRIMARY KEY (id)` | Identidad unívoca del registro basada en enteros monótonos de 64 bits para indexación eficiente. |
| outbox_events | `uk_outbox_events_event_id` | Restricción | `UNIQUE (event_id)` | Erradica colisiones y duplicidades de eventos a nivel de almacenamiento físico. |
| outbox_events | `chk_outbox_events_status` | Restricción | `CHECK (status IN ('PENDING', 'PUBLISHED', 'FAILED'))` | Impone el ciclo de vida cerrado del patrón Transactional Outbox. |
| outbox_events | `chk_outbox_events_retry_count` | Restricción | `CHECK (retry_count >= 0)` | Salvaguarda que el contador de reintentos nunca admita magnitudes negativas. |
| outbox_events | `ix_outbox_events_status_occurred_on` | Índice B-Tree | `(status, occurred_on ASC)` | **Índice crítico de alta selectividad:** Optimiza la consulta del *Outbox Relay Worker* (`SELECT ... WHERE status = 'PENDING' ORDER BY occurred_on ASC LIMIT N FOR UPDATE SKIP LOCKED`), eliminando table scans y reduciendo la latencia de desacolado a valores submilisegundo. |
| outbox_events | `ix_outbox_events_aggregate` | Índice B-Tree | `(aggregate_type, aggregate_id)` | Permite búsquedas rápidas para auditoría histórica de eventos emitidos por una entidad específica. |
| outbox_events | `ix_outbox_events_event_type` | Índice B-Tree | `(event_type)` | Facilita tareas de mantenimiento operacional, reenvío selectivo o análisis forense por tipología de evento. |

---

### 25.4 Fundamentos de Ingeniería y Resiliencia del Transactional Outbox

A partir de la persistencia formalizada en el diagrama relacional, se identifican cuatro pilares de ingeniería de software que garantizan la resiliencia del ecosistema Navby:
1. **Erradicación del Problema de Doble Escritura (*Dual-Write Problem*):** Cuando un caso de uso muta el estado de una entidad (ej. registro de usuario en `IAM` o creación de itinerario en `Itineraries`), tanto la fila de negocio como el evento de dominio en `outbox_events` se persisten dentro de la **misma y única transacción ACID de PostgreSQL**. Si la base de datos confirma (*COMMIT*), ambos registros quedan asegurados; si ocurre una falla o aborto (*ROLLBACK*), ninguno se persiste, imposibilitando inconsistencias transaccionales.
2. **Entrega Confiable Garantizada (*At-Least-Once Delivery*):** El despacho hacia consumidores externos o suscriptores en memoria no ocurre durante la petición HTTP, sino a través del *Outbox Relay Worker*. Incluso ante caídas catastróficas del servidor o cortes de conectividad externa, los eventos permanecen persistidos en `outbox_events` y serán retomados automáticamente al restablecerse el servicio.
3. **Sondeo Concurrente No Bloqueante con `FOR UPDATE SKIP LOCKED`:** PostgreSQL 16 permite que múltiples réplicas del worker descolen eventos simultáneamente sin producir interbloqueos (*deadlocks*). La cláusula `SKIP LOCKED` instruye al motor a omitir de inmediato cualquier fila bloqueada por otra transacción activa, permitiendo escalabilidad horizontal del procesamiento de eventos.
4. **Desacoplamiento Modular y Autonomía de Bounded Contexts:** La tabla `outbox_events` no establece llaves foráneas (*Foreign Keys*) rígidas contra las tablas de los demás módulos (`user_accounts`, `itineraries`, `credit_wallets`). En su lugar, emplea el patrón de referencia polimórfica desacoplada `(aggregate_type, aggregate_id)`, preservando la independencia de despliegue y la modularidad exigida por Domain-Driven Design.

---

### 25.5 Código Fuente Canónico PlantUML DSL (`database-diagram-shared.puml`)

El código fuente PlantUML DSL reproducible que genera este diagrama de base de datos se mantiene en `report/assets/diagram-sources/database-diagrams/database-diagram-shared.puml` y se reproduce íntegramente a continuación:

```plantuml
@startuml database-diagram-shared
title <size:16>Diagrama de Base de Datos (ERD) - Bounded Context Shared Kernel</size>\n<size:11>Persistencia Relacional Transversal: PostgreSQL 16 (Navby Platform Backend)</size>

' Configuraciones visuales y de diseño profesional
hide circle
skinparam monochrome false
skinparam shadowing false
skinparam roundcorner 6
skinparam linetype ortho
skinparam nodesep 100
skinparam ranksep 60
skinparam defaultFontName "Helvetica", "Arial", sans-serif
skinparam defaultFontSize 11
skinparam defaultFontColor #2C3E50
skinparam arrowColor #34495E
skinparam arrowThickness 1.3
skinparam packageBorderColor #7F8C8D
skinparam packageFontSize 12
skinparam packageFontStyle bold

skinparam entity {
    BackgroundColor #FFFFFF
    BorderColor #34495E
    HeaderBackgroundColor #EAEDED
}

' ==============================================================================
' POSTGRESQL 16 (NAVBY PLATFORM BACKEND PERSISTENCE)
' ==============================================================================
package "PostgreSQL 16 (Navby Platform - Backend Relacional)" as pg_backend #F8F9F9 {

    entity "auditable_persistence_mixin" as auditable_persistence_mixin <<mixin, SQLAlchemy>> #E8F8F5 {
        * created_at : TIMESTAMPTZ <<DEFAULT NOW()>>
        * updated_at : TIMESTAMPTZ <<DEFAULT NOW(), onupdate NOW()>>
        --
        <b>Propiedades del Arquetipo:</b>
        + Marcas temporales UTC inmutables y trazables
        + Sincronización a nivel de motor PostgreSQL
        + Reutilizado transversalmente por todas las tablas
    }

    entity "outbox_events" as outbox_events <<table, PostgreSQL>> #EBF5FB {
        * id : BIGINT GENERATED ALWAYS AS IDENTITY <<PK>>
        --
        * event_id : UUID <<UK>>
        * aggregate_type : VARCHAR(64)
        * aggregate_id : VARCHAR(64)
        * event_type : VARCHAR(128)
        * payload : JSONB
        * occurred_on : TIMESTAMPTZ
        * status : VARCHAR(20) <<DEFAULT 'PENDING'>>
        * retry_count : INTEGER <<DEFAULT 0>>
        last_error : TEXT
        processed_at : TIMESTAMPTZ
        * created_at : TIMESTAMPTZ <<DEFAULT NOW()>>
        * updated_at : TIMESTAMPTZ <<DEFAULT NOW()>>
        --
        <b>Restricciones (Constraints):</b>
        + pk_outbox_events : PRIMARY KEY (id)
        + uk_outbox_events_event_id : UNIQUE (event_id)
        + chk_outbox_events_status : CHECK (status IN ('PENDING', 'PUBLISHED', 'FAILED'))
        + chk_outbox_events_retry_count : CHECK (retry_count >= 0)
        --
        <b>Índices Físicos (B-Tree):</b>
        + ix_outbox_events_status_occurred_on : (status, occurred_on ASC)
        + ix_outbox_events_aggregate : (aggregate_type, aggregate_id)
        + ix_outbox_events_event_type : (event_type)
    }

    entity "domain_aggregates_sample\n(e.g., itineraries / credit_wallets)" as domain_aggregates <<table, PostgreSQL>> #FFFFFF {
        * id : BIGINT GENERATED ALWAYS AS IDENTITY <<PK>>
        --
        * user_id : BIGINT <<FK>>
        * status : VARCHAR(20)
        * created_at : TIMESTAMPTZ
        * updated_at : TIMESTAMPTZ
        --
        <b>Herencia de Persistencia:</b>
        + Hereda físicamente las columnas de auditoría
        + Entidad raíz transaccional de negocio
    }

    auditable_persistence_mixin <|-- domain_aggregates : "hereda mixin físico\n(SQLAlchemy Mapped)"
    auditable_persistence_mixin <|-- outbox_events : "hereda mixin físico\n(AuditablePersistenceMixin)"
    domain_aggregates "1   " ||--o{ "0..* " outbox_events : "persiste eventos en misma TX ACID\n(Transactional Outbox Pattern)"
}

@enduml
```

