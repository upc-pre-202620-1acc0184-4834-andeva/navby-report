## 3.2. Técnicas Algorítmicas Seleccionadas

La propuesta se limita a tres técnicas, que son las que se implementan y se evalúan. Cada una responde una pregunta distinta del problema, como se resume en la @tbl:tecnicas-principales.

|                    Técnica                     | Pregunta que responde                                                                                                                                  |
| :--------------------------------------------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------- |
|           Búsqueda en anchura (BFS)            | ¿Existe una ruta con dos escalas como máximo entre origen y destino y cuál es el mínimo de escalas posible? Si no existe, la búsqueda se detiene sin costo. |
|                 Algoritmo A\*                  | ¿Cuál es la ruta físicamente más rápida? Su duración sirve como referencia mínima y su trazado se muestra en el mapa mientras se obtienen las tarifas.     |
|           Optimización multicriterio           | ¿Cuáles son las tres mejores ofertas reales? Combina precio, duración y escalas en un único puntaje [@shovan2025parallel].                                 |

: Técnicas Algorítmicas de la Solución {#tbl:tecnicas-principales}

_Nota._ Las tres técnicas se ejecutan en memoria principal durante cada búsqueda.

BFS y A\* trabajan sobre el grafo de OpenFlights, que indica qué rutas existen pero no sus precios ni horarios. La optimización multicriterio trabaja sobre las ofertas reales obtenidas del mercado. La validación consistirá en medir el desempeño de estas mismas tres técnicas, sin incorporar algoritmos adicionales.
