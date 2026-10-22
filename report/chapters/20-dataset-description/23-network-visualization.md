## 2.3. Visualización del Grafo Aéreo

En la @fig:red-global-vuelos se muestra el grafo completo: 3,354 aeropuertos y 37,326 rutas directas. Cada ruta se dibuja como un arco de círculo máximo, que es la trayectoria más corta sobre la superficie terrestre y por eso aparece curvada en un mapa plano. La alta densidad de arcos en Europa, Norteamérica y el este de Asia refleja la concentración de rutas en grandes aeropuertos centrales.

![Red aerocomercial global de OpenFlights](report/assets/graphs/global-flight-network.png){#fig:red-global-vuelos width=82%}

_Nota._ Cada punto es un aeropuerto comercial y cada arco, una ruta directa.

Debido a que el grafo global es difícil de leer a esa escala, en la @fig:subgrafo-sudamerica se amplía el subgrafo de Sudamérica. En él se distingue con claridad qué representa cada elemento del modelo. Un **nodo** es un aeropuerto, identificado por su código IATA y sus coordenadas. Una **arista** es una ruta directa entre dos aeropuertos, con un peso igual al tiempo estimado de vuelo. Se observa también que São Paulo (GRU, 109 rutas dentro de la región), Bogotá (BOG, 96) y Lima (LIM, 74) concentran más conexiones que el resto y funcionan como puntos de transferencia.

![Subgrafo aerocomercial de Sudamérica](report/assets/graphs/south-america-flight-subgraph.png){#fig:subgrafo-sudamerica width=58%}

_Nota._ Cada punto es un aeropuerto sudamericano (nodo) y cada arco, una ruta directa entre ellos (arista).

\newpage
