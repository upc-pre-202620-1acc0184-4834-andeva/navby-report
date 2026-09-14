# Datasets Limpios y Definitivos de Navby (OpenFlights)

Este directorio contiene los conjuntos de datos limpios, validados y estructurados para el modelado algorítmico de grafos y la plataforma de backend de **Navby**.

---

## 1. Resumen de Archivos y Métricas

| Archivo | Filas (con cabecera) | Registros de Datos | Descripción y Rol en Navby |
| :--- | :---: | :---: | :--- |
| **`airports.csv`** | 3,355 | **3,354** | **Vértices del Grafo ($|V|$):** Aeropuertos comerciales con código IATA válido y grado de conectividad $k > 0$. |
| **`routes_unique.csv`** | 37,327 | **37,326** | **Aristas del Grafo ($|E|$):** Pares dirigidos únicos origen $\to$ destino con distancia Haversine calculada en kilómetros. |
| **`routes.csv`** | 67,306 | **67,305** | **Multigrafo de Rutas:** Conexiones comerciales activas considerando frecuencias y aerolíneas concurrentes. |
| **`airports_commercial_all.csv`** | 6,473 | **6,472** | Catálogo completo de aeropuertos comerciales con código IATA válido (incluye terminales sin vuelos comerciales activos en el dataset). |
| **`airlines.csv`** | 6,163 | **6,162** | Catálogo de aerolíneas mundiales (metadatos de nombre, alias, IATA, ICAO y estado activo). |
| **`countries.csv`** | 262 | **261** | Catálogo de países soberanos con códigos ISO y DAFIF para enriquecimiento contextual. |
| **`planes.csv`** | 247 | **246** | Catálogo de aeronaves comerciales con designadores IATA e ICAO. |

---

## 2. Proceso de Limpieza y Validación Matemática

Los datos originales provienen del repositorio oficial de OpenFlights (`docs/backend-documentation/datasets/`). La depuración siguió cuatro fases deterministas:

1. **Fase 1 (Tipo de instalación):** Filtrado de `airports-extended.dat` para retener exclusivamente terminales aéreas comerciales (`type = "airport"`), excluyendo estaciones de tren (`station`), puertos marítimos (`port`) y helipuertos.
2. **Fase 2 (Identificador estándar IATA):** Validación de códigos IATA de tres letras mayúsculas válidos (excluyendo valores nulos `\N`), resultando en **6,472 aeropuertos comerciales**.
3. **Fase 3 (Integridad referencial de aristas):** Validación de `routes.dat` exigiendo que tanto el aeropuerto de origen como el de destino existan dentro del universo de aeropuertos comerciales válidos, reteniendo **67,305 rutas comerciales activas**.
4. **Fase 4 (Poda de vértices aislados):** Eliminación de 3,118 terminales con grado de conectividad nulo ($k = 0$). El grafo final conectado comprende exactamente **3,354 vértices** y **37,326 aristas dirigidas únicas**, superando ampliamente el requisito mínimo de 1,500 nodos de la cátedra de Complejidad Algorítmica (2.2×).

---

## 3. Esquema de Datos por Archivo

### `airports.csv` / `airports_commercial_all.csv`
* `airport_id` (Entero): Identificador secuencial OpenFlights.
* `name` (Texto): Nombre oficial de la terminal aérea.
* `city` (Texto): Ciudad metropolitana servida.
* `country` (Texto): País donde se ubica la infraestructura.
* `iata` (Texto, 3 caracteres): Clave canónica del nodo.
* `icao` (Texto, 4 caracteres): Código OACI.
* `latitude` (Decimal WGS84): Coordenada latitudinal (-90.0 a 90.0).
* `longitude` (Decimal WGS84): Coordenada longitudinal (-180.0 a 180.0).
* `altitude` (Entero): Elevación sobre el nivel del mar en pies.
* `timezone` (Decimal): Desplazamiento respecto a UTC.
* `dst` (Carácter): Regla de horario de verano (E, A, S, O, Z, N).
* `tz_database_timezone` (Texto): Zona horaria canónica IANA (ej. `America/Lima`).

### `routes_unique.csv` (Aristas del Grafo)
* `source_airport` (Texto, 3): Código IATA origen ($u \in V$).
* `destination_airport` (Texto, 3): Código IATA destino ($v \in V$).
* `distance_km` (Decimal): Distancia ortodrómica calculada en kilómetros mediante la fórmula de Haversine ($R = 6371.0\text{ km}$).
* `operating_airlines` (Texto): Lista de códigos de aerolíneas separadas por `;`.
* `min_stops` (Entero): Mínimo número de paradas intermedias de la conexión (0 = vuelo sin paradas técnicas).
* `equipment_types` (Texto): Tipos de aeronaves que cubren el trayecto separados por `;`.

### `routes.csv` (Rutas Operativas)
* `airline`, `airline_id`, `source_airport`, `source_airport_id`, `destination_airport`, `destination_airport_id`, `codeshare`, `stops`, `equipment`.
