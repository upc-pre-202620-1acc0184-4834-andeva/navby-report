## 4.2. Estructuras de Datos y Modelado en Memoria

Para garantizar tiempos de respuesta en el orden de milisegundos sin sobrecostos de serialización ni dependencias de motores de bases de datos de grafos externos, el sistema modela la red aeroportuaria mediante estructuras nativas en memoria RAM. El diseño orientado a objetos encapsula la red en tipos inmutables y servicios de dominio desacoplados, como se ilustra en el diagrama de clases de la @fig:diagrama-clases-grafo.

![Diagrama de Clases del Modelo de Grafos en Memoria](report/assets/class-diagrams/routing-domain-model.png){#fig:diagrama-clases-grafo width=90%}

*Nota.* Diagrama de clases UML del núcleo de enrutamiento que ilustra las estructuras de datos, entidades y servicios de dominio en memoria RAM.

En la @tbl:estructuras-datos-algoritmos se describen las estructuras y clases nucleares del motor algorítmico, detallando sus complejidades y roles operativos.

| Estructura o Clase | Tipo | Complejidad | Propósito Técnico |
| :---: | :---: | :---: | :--- |
| AirportGraph | Agregado en RAM | $O(V + E)$ espacial | Mantenimiento del grafo global de 3,354 aeropuertos y acceso a adyacencia en tiempo constante $O(1)$. |
| Airport | Entidad inmutable | $O(1)$ | Vértice de la red identificado por código IATA, con coordenadas geográficas y metadatos de ciudad. |
| Edge | Objeto de valor | $O(1)$ | Arista dirigida ponderada por distancia ortodrómica Haversine y tiempo estimado de vuelo en minutos. |
| deque | Cola FIFO | $O(1)$ acceso | Exploración por niveles en BFS para verificar conectividad con inserción y extracción inmediata. |
| heapq | Cola de prioridad | $O(\log N)$ extracción | Min-heap ordenado por la función de evaluación $f(u) = g(u) + h(u)$ para la búsqueda óptima en A\*. |
| FlightOffer | Objeto de valor | $O(1)$ | Representación de la oferta comercial con precio total, duración y escalas devuelta por el proveedor. |
| RankedOffer | Objeto de valor | $O(1)$ | Oferta evaluada con puntaje de equilibrio $S$ y porcentaje de afinidad para el podio de recomendaciones. |

: Estructuras de Datos y Clases del Núcleo Algorítmico {#tbl:estructuras-datos-algoritmos}

*Nota.* Estructuras de datos nativas en Python y modelos de dominio del motor de enrutamiento y cotización.

El agregado **AirportGraph** se instancia una única vez durante el ciclo de vida del servicio. Almacena los 3,354 vértices en una tabla de dispersión `airports: dict[IataCode, Airport]` y sus 37,326 conexiones dirigidas en `adjacency: dict[IataCode, list[Edge]]`. Esta organización permite obtener los vecinos salientes de cualquier terminal en tiempo $O(1)$. Para resolver búsquedas urbanas, el índice invertido `cities: dict[CityKey, list[IataCode]]` agrupa los aeropuertos pertenecientes a una misma metrópoli situados a un radio menor a 80 km, habilitando al servicio **PairSelector** a identificar de forma determinista los pares comerciales viables antes de invocar a los algoritmos de búsqueda.
