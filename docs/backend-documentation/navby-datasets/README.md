# Datasets de OpenFlights

Datos depurados de [OpenFlights](https://openflights.org/data) con los que se construye el grafo de Navby. El backend carga **cuatro** archivos: el grafo y dos tablas pequeñas para buscar ciudades. El resto sirve para el análisis del informe.

## 1. Archivos

| Archivo | Registros | Uso | Rol |
| :--- | :---: | :---: | :--- |
| `airports.csv` | 3,354 | **Backend** | Vértices del grafo: aeropuertos comerciales con al menos una ruta. |
| `routes_unique.csv` | 37,326 | **Backend** | Aristas dirigidas únicas con distancia Haversine. |
| `city_aliases_es.csv` | 119 | **Backend** | Nombres en español de ciudades que difieren del inglés (`city`, `country`, `alias_es`). Curado a mano. |
| `airport_city_overrides.csv` | 1 | **Backend** | Corrige la ciudad de aeropuertos metropolitanos registrados con otro nombre (`iata`, `city`, `country`, `reason`). |
| `airports_commercial_all.csv` | 6,472 | Informe | Aeropuertos comerciales con IATA, antes de quitar los aislados (fase 2). |
| `routes.csv` | 67,305 | Informe | Multigrafo: una fila por aerolínea y ruta (fase 4). |
| `airlines.csv` | 6,162 | Informe | Catálogo de aerolíneas. Los nombres que ve el usuario vienen de FlightAPI. |
| `countries.csv` | 261 | Informe | Catálogo de países. |
| `planes.csv` | 246 | Informe | Catálogo de aeronaves. |

## 2. Pipeline de depuración

Coincide con la tabla de fases del informe ([`22-preprocessing-and-metrics.md`](../../../report/chapters/20-dataset-description/22-preprocessing-and-metrics.md)).

| Fase | Criterio | Entrada | Salida |
| :---: | :--- | :---: | :---: |
| 1 | Solo instalaciones `type = "airport"` (sin helipuertos, puertos ni estaciones). | 12,668 nodos | 11,072 nodos |
| 2 | Código IATA válido `^[A-Z]{3}$`. | 11,072 nodos | 6,472 nodos |
| 3 | Eliminar aeropuertos sin rutas comerciales (grado 0). | 6,472 nodos | 3,354 nodos |
| 4 | Rutas cuyo origen y destino existen en el catálogo filtrado. | 67,663 rutas | 67,305 rutas |
| 5 | Colapsar rutas paralelas de distintas aerolíneas en una arista dirigida única. | 67,305 rutas | 37,326 aristas |

## 3. Esquemas de los archivos del backend

### `airports.csv`

| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `airport_id` | int | ID original de OpenFlights. |
| `name` | texto | Nombre del aeropuerto. |
| `city` | texto | Ciudad servida (en inglés). Base del autocompletado. |
| `country` | texto | País. |
| `iata` | texto (3) | Identificador del nodo. |
| `icao` | texto (4) | Código OACI. |
| `latitude`, `longitude` | decimal | Coordenadas WGS84. |
| `altitude` | int | Elevación en pies. |
| `timezone` | decimal | Desfase UTC. |
| `dst` | carácter | Regla de horario de verano. |
| `tz_database_timezone` | texto | Zona IANA (p. ej. `America/Lima`). |

### `routes_unique.csv`

| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `source_airport` | texto (3) | IATA de origen `u`. |
| `destination_airport` | texto (3) | IATA de destino `v`. |
| `distance_km` | decimal | Distancia Haversine `d_H(u, v)` con R = 6,371 km. |
| `operating_airlines` | texto | Aerolíneas que operan la ruta, separadas por `;`. |
| `min_stops` | int | Paradas técnicas registradas (0 = directo). |
| `equipment_types` | texto | Aeronaves que sirven la ruta. |

El backend calcula el peso en minutos de cada arista al cargar el archivo: `w = distance_km / 800 · 60 + 30` (ver sección 5.2 de [navby-documentation.md](../../navby-documentation.md)).
