## 4.2. Estructuras de Datos y Modelado en Memoria

Para garantizar tiempos de respuesta en el orden de milisegundos sin sobrecostos de serialización ni dependencias de motores de bases de datos de grafos externos, el sistema modela la red de rutas aéreas mediante estructuras de datos nativas en memoria RAM. El núcleo de representación se implementa en Python utilizando tipos fuertemente tipados e inmutables.

En la @tbl:estructuras-datos-algoritmos se resumen las estructuras de datos nucleares del motor algorítmico y sus funciones en el sistema.

| Estructura o Clase | Tipo | Ámbito | Propósito Técnico |
| :---: | :---: | :---: | :--- |
| AirportGraph | Agregado en RAM | Routing | Representación global de la red mediante listas de adyacencia y catálogos de búsqueda en tiempo constante $O(1)$. |
| Airport | Entidad inmutable | Routing | Vértice de la red identificado por código IATA, con coordenadas geográficas y metadatos de ciudad. |
| Edge | Objeto de valor | Routing | Arista dirigida ponderada por distancia ortodrómica Haversine y tiempo de vuelo estimado en minutos. |
| deque | Cola FIFO | Algoritmia | Estructura para la exploración por niveles en BFS con inserción y extracción en tiempo $O(1)$. |
| heapq | Cola de prioridad | Algoritmia | Min-heap ordenado por la función de evaluación $f(u) = g(u) + h(u)$ para la búsqueda óptima en A\*. |
| FlightOffer | Objeto de valor | Quotes | Registro de oferta comercial devuelta por el proveedor con precio total, duración y escalas. |
| RankedOffer | Objeto de valor | Quotes | Oferta evaluada con puntaje de equilibrio $S$ y porcentaje de afinidad para el podio de recomendaciones. |

: Estructuras de Datos y Clases del Núcleo Algorítmico {#tbl:estructuras-datos-algoritmos}

*Nota.* Estructuras de datos nativas en Python y modelos de dominio del motor de enrutamiento y cotización.

El agregado **AirportGraph** se instancia una única vez durante el arranque del servicio. Almacena los 3,354 vértices en una tabla de dispersión `airports: dict[IataCode, Airport]` y sus 37,326 conexiones dirigidas en `adjacency: dict[IataCode, list[Edge]]`. Esta organización permite acceder a las conexiones salientes de cualquier aeropuerto en tiempo $O(1)$. Cada arista (**Edge**) almacena el código del aeropuerto de destino, la distancia geodésica $d_H(u, v)$ en kilómetros y el peso temporal $w_t(u, v)$ en minutos, calculado a partir de la velocidad de crucero estándar de 800 km/h y una constante de 30 minutos por maniobras aeroportuarias.

Para soportar las búsquedas por ciudad en lugar de aeropuertos individuales, **AirportGraph** incorpora un índice invertido `cities: dict[CityKey, list[IataCode]]`. Este índice asocia cada área urbana con sus aeropuertos comerciales situados a un radio menor a 80 km, resolviendo casos de múltiples terminales por metrópoli.

En la capa de optimización comercial, el agregado **QuoteSearch** procesa las ofertas reales mediante colecciones en memoria. La entidad **FlightOffer** encapsula los tres atributos cuantitativos del problema multiobjetivo: el precio monetario, la duración del itinerario y la cantidad de escalas. La estructura **PreferenceWeights** define los coeficientes de ponderación $(\alpha, \beta, \gamma)$ que rigen la función de distancia cuadrática para ordenar las alternativas del podio final (**RankedOffer**).
