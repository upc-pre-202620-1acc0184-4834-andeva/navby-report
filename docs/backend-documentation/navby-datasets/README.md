# Datasets Canónicos y Limpios de Navby (OpenFlights)

Este directorio contiene los conjuntos de datos limpios, consolidados y estrictamente necesarios para el modelado algorítmico del grafo de rutas y la plataforma de backend de **Navby**.

---

## 1. Catálogo de Archivos Canónicos de Producción

En cumplimiento estricto del principio de anti-sobreingeniería y eficiencia de datos, el sistema retiene exclusivamente los tres conjuntos indispensables:

| Archivo | Filas (con cabecera) | Registros de Datos | Rol Arquitectónico en Navby Platform |
| :--- | :---: | :---: | :--- |
| **`airports.csv`** | 3,355 | **3,354** | **Vértices del Grafo ($|V|$):** Nodos aeroportuarios comerciales activos con código IATA válido de 3 letras, nombre oficial, ciudad de servicio, país y coordenadas ortodrómicas WGS84. |
| **`routes_unique.csv`** | 37,327 | **37,326** | **Aristas del Grafo ($|E|$):** Conexiones dirigidas únicas entre terminales comerciales con distancias ortodrómicas de Haversine ($R = 6371.0\text{ km}$) para los motores $A^*$ y BFS. |
| **`airlines.csv`** | 6,163 | **6,162** | **Metadatos de Operadores:** Catálogo referencial de aerolíneas comerciales (código IATA de 2 letras, nombre comercial y designador ICAO) para resolución y enriquecimiento visual de ofertas en la interfaz de usuario. |

*Nota.* Todo archivo redundante o auxiliar (multigrafos con arcos duplicados, catálogos mecánicos de turbinas de aeronaves o listados de terminales cerradas con $k=0$) ha sido purgado del repositorio para mantener un árbol de datos limpio, determinista y ligero (< 2 MB en total).

---

## 2. Pipeline de Depuración y Validación Matemática

Los datos provienen de la red global de OpenFlights y fueron sometidos a un pipeline de sanitización determinista en cuatro fases:

1. **Fase 1 (Filtrado por tipo de instalación):** Retención exclusiva de terminales aéreas comerciales (`type = "airport"`), descartando helipuertos, estaciones de trenes (`station`) y terminales fluviales o marítimas (`port`).
2. **Fase 2 (Validación de identificadores estándar IATA):** Exigencia estricta de códigos IATA alfanuméricos de 3 caracteres en mayúsculas (`^[A-Z]{3}$`), descartando registros sin identificador comercial asignado (`\N`).
3. **Fase 3 (Integridad referencial y colapso de multigrafo):** Depuración de rutas asegurando que tanto el aeropuerto de origen como el de destino existan dentro del universo comercial válido. El multigrafo inicial de 67,305 rutas multioperador concurrentes fue colapsado a un grafo simple dirigido de **37,326 aristas únicas**, computando la distancia geodésica ortodrómica exacta mediante la formulación de Haversine.
4. **Fase 4 (Poda topológica de nodos aislados):** Eliminación de 3,118 aeropuertos con grado de conectividad nulo ($k = 0$). El grafo final activo consolida exactamente **3,354 vértices** y **37,326 aristas dirigidas únicas**, superando holgadamente el requisito de la cátedra de Complejidad Algorítmica (2.2×).

---

## 3. Esquemas de Datos Canónicos

### `airports.csv` (Vértices del Grafo)
* `airport_id` (Entero): Identificador secuencial original de OpenFlights.
* `name` (Texto): Nombre oficial de la terminal aeroportuaria.
* `city` (Texto): Ciudad metropolitana servida (base del autocompletado en el buscador).
* `country` (Texto): País de ubicación geográfica.
* `iata` (Texto, 3 caracteres): Clave canónica unívoca del nodo ($u \in V$).
* `icao` (Texto, 4 caracteres): Código OACI de control de tráfico aéreo.
* `latitude` (Decimal WGS84): Coordenada latitudinal (-90.0 a 90.0).
* `longitude` (Decimal WGS84): Coordenada longitudinal (-180.0 a 180.0).
* `altitude` (Entero): Elevación sobre el nivel del mar en pies.
* `timezone` (Decimal): Desplazamiento horario respecto a UTC.
* `dst` (Carácter): Regla de horario de verano (E, A, S, O, Z, N).
* `tz_database_timezone` (Texto): Zona horaria canónica IANA (ej. `America/Lima`).

### `routes_unique.csv` (Aristas Ponderadas del Grafo)
* `source_airport` (Texto, 3 caracteres): Código IATA del nodo origen ($u$).
* `destination_airport` (Texto, 3 caracteres): Código IATA del nodo destino ($v$).
* `distance_km` (Decimal): Distancia física ortodrómica sobre la esfera terrestre WGS84 en kilómetros ($w_t = d_H(u, v)$).
* `operating_airlines` (Texto): Aerolíneas comerciales que operan el trayecto (separadas por `;`).
* `min_stops` (Entero): Paradas técnicas de la conexión (0 = tramo directo sin paradas).
* `equipment_types` (Texto): Designadores de aeronaves que sirven la ruta.

### `airlines.csv` (Catálogo de Aerolíneas)
* `airline_id` (Entero): Identificador OpenFlights.
* `name` (Texto): Razón social o nombre comercial de la aerolínea.
* `alias` (Texto): Nombre alternativo o comercial secundario.
* `iata` (Texto, 2 caracteres): Código IATA de la compañía aérea (ej. `LA` para LATAM, `IB` para Iberia).
* `icao` (Texto, 3 caracteres): Designador OACI de la aerolínea.
* `callsign` (Texto): Indicativo radiotelefónico de la tripulación.
* `country` (Texto): País de certificación y bandera de la aerolínea.
* `active` (Carácter): Indicador de actividad comercial (`Y` / `N`).
